from __future__ import annotations

import json
from datetime import date
from strands import tool

ALLOWED_ITEMS = {"baby_food", "canned_food", "hygiene_kit", "rice"}


@tool
def validate_request(request_json: str) -> str:
    """Validate and minimize a food-bank request before planning.

    Args:
        request_json: JSON object with request_id, household_size, items, urgency,
            consent, and optional notes. Names and contact details are rejected.
    """
    raw = json.loads(request_json)
    forbidden = {"name", "email", "phone", "address"}.intersection(raw)
    if forbidden:
        return json.dumps({"ok": False, "reason": "direct_pii_not_allowed", "fields": sorted(forbidden)})
    required = {"request_id", "household_size", "items", "urgency", "consent"}
    missing = sorted(required.difference(raw))
    if missing:
        return json.dumps({"ok": False, "reason": "missing_fields", "fields": missing})
    if raw["consent"] is not True:
        return json.dumps({"ok": False, "reason": "consent_required"})
    if not isinstance(raw["household_size"], int) or not 1 <= raw["household_size"] <= 20:
        return json.dumps({"ok": False, "reason": "invalid_household_size"})
    if raw["urgency"] not in {"routine", "soon", "today"}:
        return json.dumps({"ok": False, "reason": "invalid_urgency"})
    items = raw["items"]
    if not isinstance(items, dict) or not items:
        return json.dumps({"ok": False, "reason": "invalid_items"})
    unknown = sorted(set(items).difference(ALLOWED_ITEMS))
    invalid_qty = sorted(k for k, v in items.items() if not isinstance(v, int) or v < 1 or v > 20)
    if unknown or invalid_qty:
        return json.dumps({"ok": False, "reason": "invalid_item_request", "unknown": unknown, "invalid_quantity": invalid_qty})
    normalized = {
        "request_id": str(raw["request_id"]),
        "household_size": raw["household_size"],
        "items": dict(sorted(items.items())),
        "urgency": raw["urgency"],
        "notes": str(raw.get("notes", ""))[:240],
    }
    return json.dumps({"ok": True, "request": normalized}, sort_keys=True)


@tool
def plan_allocation(validated_request_json: str, inventory_json: str) -> str:
    """Create a deterministic reservation plan and escalate only real decisions.

    Args:
        validated_request_json: Output from validate_request.
        inventory_json: JSON object mapping item names to non-negative stock counts.
    """
    validation = json.loads(validated_request_json)
    if not validation.get("ok"):
        return json.dumps({"status": "BLOCKED", "reason": validation.get("reason", "invalid_request")})
    request = validation["request"]
    inventory = json.loads(inventory_json)
    allocations: dict[str, int] = {}
    shortages: dict[str, int] = {}
    for item, wanted in request["items"].items():
        available = inventory.get(item, 0)
        if not isinstance(available, int) or available < 0:
            return json.dumps({"status": "BLOCKED", "reason": "invalid_inventory", "item": item})
        allocations[item] = min(wanted, available)
        if wanted > available:
            shortages[item] = wanted - available
    needs_human = bool(shortages) or request["urgency"] == "today"
    return json.dumps({
        "status": "HUMAN_REVIEW" if needs_human else "AUTO_READY",
        "request_id": request["request_id"],
        "allocations": allocations,
        "shortages": shortages,
        "decision_reason": "shortage_or_same_day_request" if needs_human else "fully_in_stock_routine_request",
    }, sort_keys=True)


@tool
def create_audit_record(plan_json: str) -> str:
    """Create a tamper-evident-friendly audit record without personal data.

    Args:
        plan_json: Output from plan_allocation.
    """
    plan = json.loads(plan_json)
    return json.dumps({
        "schema_version": 1,
        "processed_on": date.today().isoformat(),
        "request_id": plan.get("request_id"),
        "status": plan.get("status"),
        "allocations": plan.get("allocations", {}),
        "shortages": plan.get("shortages", {}),
        "human_decision_required": plan.get("status") == "HUMAN_REVIEW",
        "external_action_taken": False,
    }, sort_keys=True)
