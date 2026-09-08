# Devpost submission package

Project name

NeighborAid Queue

Track

Good Neighbor Agents

Tagline

A privacy-first Strands agent that clears food-bank busywork and surfaces only decisions that need a human.

Description

Food-bank coordinators lose volunteer hours checking incomplete requests, reconciling inventory, and deciding which cases need immediate attention. NeighborAid Queue turns minimized request data into inventory-safe allocation plans, creates an audit trail, and stays quiet unless there is a genuine decision: a shortage or a same-day request.

The working prototype is built with the Strands Agents SDK. Three typed Strands tools validate consent and reject direct personal data, plan allocations without allowing negative inventory, and create minimal local audit records. The batch orchestrator invokes each capability through Strands' direct tool interface. This is not a chatbot: it completes routine operational work end to end.

The included synthetic demo processes three cases. One fully stocked routine request becomes auto-ready; one same-day request with a shortage is routed to a coordinator; one request without consent is safely blocked. The test suite validates tool registration, end-to-end state transitions, inventory reconciliation, audit output, and PII blocking.

The current build is intentionally local and credential-free, so any nonprofit can evaluate it at no cost. The same tool contracts can later run with a model provider and Amazon Bedrock AgentCore while preserving the human gate. No eligibility decision, outbound message, purchase, or real-world reservation is automated.

Who it is for

Small food banks, community pantries, mutual-aid groups, and volunteer coordinators who need reliable triage without adding another dashboard to monitor.

Why it matters

Every minute recovered from repetitive reconciliation can return to people-facing support. Data minimization and explicit human escalation reduce privacy and operational risk at the same time.

Repository checklist

- Public repository URL: TO_BE_ADDED
- MIT license: included
- README: included
- Architecture diagram: ARCHITECTURE.md
- Setup and tests: included
- AWS Builder ID: TO_BE_ADDED
- Prepared local demo video: `demo/neighboraid-queue-demo.mp4` (109 seconds, H.264, 1280x720, captioned)
- Public video URL: TO_BE_ADDED_AFTER_AUTHORIZED_UPLOAD
- Local media verification: `demo/ffprobe.json`
- Reproducible video source: `demo/render_demo.py`, `demo/slides/`, and `demo/manifest.json`

Prepared demo video (1:49)

The script below has been rendered into the actual local file `demo/neighboraid-queue-demo.mp4`. It uses only the project's synthetic examples, contains burned-in captions, and was decoded end to end with FFmpeg. Publication remains intentionally gated; no public URL exists yet.

Demo video script

0:00-0:20 — Problem

“Small food banks often triage requests in spreadsheets and messages. Volunteers repeatedly check consent, requested items, and stock. NeighborAid Queue does that routine work and only interrupts a person for a real decision.”

0:20-0:40 — Architecture

Show ARCHITECTURE.md. “This Strands agent has three typed tools: request validation, inventory planning, and minimal audit creation. Direct personal information is rejected, and nothing is sent externally.”

0:40-1:20 — Working demo

Run:

    neighboraid --requests examples/requests.json --inventory examples/inventory.json --output demo-output.json

Open `demo-output.json`. Point out one AUTO_READY record, one HUMAN_REVIEW record caused by same-day urgency and a baby-food shortage, and one BLOCKED record caused by missing consent. Show that remaining stock never goes negative and every audit record says `external_action_taken: false`.

1:20-1:45 — Tests

Run `python -m pytest`. Show the passing tests. Briefly open `tests/test_agent.py` and highlight PII blocking and inventory reconciliation.

1:45-2:00 — Impact

“NeighborAid is intentionally quiet: routine requests flow through; ambiguous or urgent ones reach a coordinator. It gives small community organizations automation they can inspect, run locally, and later deploy through AgentCore.”

Exact submission sequence (do not perform without authorization)

1. Review the official rules and accept them only if desired.
2. Create or use a Devpost account and join Agents for Humans.
3. Create or use an AWS Builder ID.
4. Publish this directory as a public GitHub/GitLab/Bitbucket repository; ensure LICENSE is visible.
5. Upload the prepared `demo/neighboraid-queue-demo.mp4` publicly to YouTube or Vimeo and replace only the future-public-URL placeholder. No new recording is required.
6. On Devpost, choose Good Neighbor Agents; paste the text above; add repository, video, architecture, and AWS Builder ID.
7. Test every public link while logged out, then submit before 2026-09-14 17:00 PT.
