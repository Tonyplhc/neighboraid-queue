# NeighborAid Queue

A privacy-first Good Neighbor agent for food banks and community pantries. It turns a batch of minimized assistance requests into inventory-safe allocation plans, keeps an auditable record, and interrupts a coordinator only for a real decision: a shortage or a same-day request.

Why it matters

Small food banks often coordinate requests in spreadsheets and chat threads. Routine checks consume scarce volunteer time, while accidental over-allocation and unnecessary personal data create operational risk. NeighborAid handles the deterministic busywork end to end without contacting anyone or exposing personal details.

What is working

- A Strands `Agent` with three typed `@tool` functions.
- Consent, schema and data-minimization gates; direct PII is rejected.
- Inventory-aware allocation with no negative stock.
- Automatic routing of routine stocked requests.
- Human-review routing for shortages and same-day requests.
- Local, minimal audit output proving no external action occurred.
- Offline deterministic demo and test suite; no cloud credentials or paid services required.

Quick start

    uv venv
    uv pip install -e ".[dev]"
    .venv/Scripts/python -m pytest
    .venv/Scripts/neighboraid --requests examples/requests.json --inventory examples/inventory.json --output demo-output.json

Expected CLI summary:

    {"auto_ready": 1, "blocked": 1, "human_review": 1, "processed": 3}

How Strands is used

`build_agent()` registers `validate_request`, `plan_allocation`, and `create_audit_record` as Strands tools. `process_batch()` executes them through Strands' documented direct tool interface (`agent.tool.<name>`). This provides SDK tool schemas, argument validation, a clear path to model-directed orchestration, and a fully local demo that reviewers can reproduce without credentials. A production deployment can switch to Bedrock/AgentCore without changing the tools; AgentCore is optional under the hackathon rules.

Safety and privacy

This prototype uses synthetic data only. It rejects `name`, `email`, `phone`, and `address`; requires explicit consent; makes no external calls; and never auto-resolves shortages or same-day requests. It is a decision-support prototype, not a benefits eligibility system.

Project structure

- `src/neighboraid/tools.py` — typed Strands tools
- `src/neighboraid/agent.py` — agent and batch orchestration
- `src/neighboraid/cli.py` — reproducible CLI
- `tests/` — end-to-end and safety tests
- `examples/` — synthetic demo inputs
- `ARCHITECTURE.md` — diagram and trust boundaries
- `SUBMISSION.md` — ready-to-paste entry and video script

License

MIT. All project code and synthetic examples were created during the Agents for Humans submission period on 2026-09-07.
