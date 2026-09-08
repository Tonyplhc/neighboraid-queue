# Architecture

```mermaid
flowchart LR
  A[Minimized request JSON] --> B[NeighborAid Strands Agent]
  I[Inventory JSON] --> B
  B --> T1[validate_request tool]
  T1 --> T2[plan_allocation tool]
  T2 --> T3[create_audit_record tool]
  T3 --> O[Local audit batch JSON]
  T2 -->|routine + stocked| R[Auto-ready queue]
  T2 -->|shortage or same-day| H[One human decision]
  T1 -->|PII / missing consent / invalid input| X[Blocked safely]
```

Trust boundaries:

- Input is local JSON; direct names, email, phone and address are rejected.
- Inventory changes happen only in the in-memory simulation and output file.
- No email, booking, purchase, reservation or other external action is performed.
- The three operational functions are registered as Strands Agent tools and executed through `agent.tool`.
