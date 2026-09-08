import json
from datetime import date
from pathlib import Path

from neighboraid.agent import build_agent, process_batch


def test_strands_tools_registered():
    agent = build_agent()
    assert set(agent.tool_names) == {"validate_request", "plan_allocation", "create_audit_record"}


def test_end_to_end_batch(tmp_path: Path):
    requests = [
        {"request_id": "A-100", "household_size": 2, "items": {"rice": 2}, "urgency": "routine", "consent": True},
        {"request_id": "A-101", "household_size": 4, "items": {"hygiene_kit": 3}, "urgency": "today", "consent": True},
        {"request_id": "A-102", "household_size": 1, "items": {"canned_food": 1}, "urgency": "routine", "consent": False},
    ]
    inventory = {"rice": 5, "hygiene_kit": 2, "canned_food": 10, "baby_food": 0}
    rp, ip, op = tmp_path / "requests.json", tmp_path / "inventory.json", tmp_path / "out.json"
    rp.write_text(json.dumps(requests), encoding="utf-8")
    ip.write_text(json.dumps(inventory), encoding="utf-8")
    result = process_batch(rp, ip, op)
    assert result["processed"] == 3
    assert (result["auto_ready"], result["human_review"], result["blocked"]) == (1, 1, 1)
    assert result["remaining_inventory"]["rice"] == 3
    assert result["remaining_inventory"]["hygiene_kit"] == 0
    assert result["records"][0]["processed_on"] == date.today().isoformat()
    assert all(record["external_action_taken"] is False for record in result["records"])
    assert json.loads(op.read_text(encoding="utf-8")) == result


def test_pii_is_blocked(tmp_path: Path):
    rp, ip, op = tmp_path / "r.json", tmp_path / "i.json", tmp_path / "o.json"
    rp.write_text(json.dumps([{"request_id":"X","name":"Private Person","household_size":1,"items":{"rice":1},"urgency":"routine","consent":True}]), encoding="utf-8")
    ip.write_text(json.dumps({"rice":1}), encoding="utf-8")
    result = process_batch(rp, ip, op)
    assert result["blocked"] == 1
    assert result["records"][0]["request_id"] is None
