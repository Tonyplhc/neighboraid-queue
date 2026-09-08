from __future__ import annotations

import json
from pathlib import Path
from strands import Agent
from .tools import create_audit_record, plan_allocation, validate_request


def _unwrap(result: object) -> str:
    """Extract text from a Strands direct-tool result."""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        content = result.get("content", [])
        if content and isinstance(content[0], dict) and "text" in content[0]:
            return str(content[0]["text"])
    raise TypeError(f"Unexpected Strands tool result: {result!r}")


def build_agent() -> Agent:
    """Build the Strands agent without invoking a remote model."""
    return Agent(
        name="NeighborAidQueue",
        description="Privacy-first food-bank intake and allocation agent",
        system_prompt=(
            "Minimize personal data, validate every request, reserve only available "
            "inventory, and surface only shortages or same-day decisions to a human."
        ),
        tools=[validate_request, plan_allocation, create_audit_record],
        callback_handler=None,
    )


def process_batch(requests_path: Path, inventory_path: Path, output_path: Path) -> dict:
    """Run a complete local batch through Strands' direct tool interface."""
    requests = json.loads(requests_path.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if not isinstance(requests, list) or not isinstance(inventory, dict):
        raise ValueError("requests must be a list and inventory must be an object")
    agent = build_agent()
    records = []
    for request in requests:
        validated = _unwrap(agent.tool.validate_request(request_json=json.dumps(request)))
        plan = _unwrap(agent.tool.plan_allocation(
            validated_request_json=validated,
            inventory_json=json.dumps(inventory),
        ))
        plan_obj = json.loads(plan)
        if plan_obj.get("status") in {"AUTO_READY", "HUMAN_REVIEW"}:
            for item, amount in plan_obj["allocations"].items():
                inventory[item] = inventory.get(item, 0) - amount
        audit = _unwrap(agent.tool.create_audit_record(plan_json=plan))
        records.append(json.loads(audit))
    summary = {
        "agent_framework": "Strands Agents SDK",
        "processed": len(records),
        "auto_ready": sum(r["status"] == "AUTO_READY" for r in records),
        "human_review": sum(r["status"] == "HUMAN_REVIEW" for r in records),
        "blocked": sum(r["status"] == "BLOCKED" for r in records),
        "remaining_inventory": dict(sorted(inventory.items())),
        "records": records,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary
