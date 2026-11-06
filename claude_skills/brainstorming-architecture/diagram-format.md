# Architecture Diagram Format

All architecture diagrams are Unicode box-drawing text inside a ` ```text ` fence. They render in terminals, live in Markdown, and diff cleanly in Git.

## Palette

| Meaning | Characters |
|---|---|
| Flow between components | `──►` labelled: `── HTTPS ──►` |
| Reverse or two-way flow | `◄──`, `◄──►` |
| Vertical flow | `│`, then `▼` or `▲` |
| Step inside a component | `├──>`, last step `└──>`, continue with `│` |
| Grouping and branches | `├──`, `└──`, `┌──`, `┐`, `└`, `┘` |
| Approval or interactive loop | `⇄` |
| Component, data store, external system | `[ Name ]` |
| Annotation separator | ` · ` |

## Rules

1. Use spaces only (no tabs), and keep lines to 100 columns or fewer.
2. Put the entry layer (clients, triggers, API gateway) at the top or top-left. Flow reads top to bottom and left to right.
3. Wrap every component, data store, and external system in `[ ]` with a concrete name: `[ Postgres: orders ]`, `[ Redis: sessions ]`, `[ Stripe API ]`, not `[ DB ]`.
4. Label every edge that crosses a process, network, or trust boundary with its protocol or payload: `── gRPC ──►`, `── HTTPS + SSE ──►`, `── async: order.created ──►`.
5. Draw a multi-step pipeline as a numbered tree under its component (`├──> 1. Validate`). Put annotations to the right, separated by ` · `.
6. Draw failure paths as edges: `── on 5xx ──► [ Fallback Provider ]`, `── 5× failed ──► [ SQS: dlq ]`.
7. A full system diagram ends with two sections, in this order: `[ Infrastructure & Observability ]`, then `OFFLINE / CONTROL PLANES` (ingestion, admin and config, CI/CD and eval gates, batch jobs).
8. Draw only with the palette above. No `+---+` ASCII boxes, Mermaid, PlantUML, or images.
9. Mark anything not yet confirmed with `?`: `[ ? Analytics ]` for a component that may not exist, `── ? ──►` for a link whose protocol is still open.

## Diagram kinds

### Context sketch (Discovery turn)

The system is one box. Draw who uses it and what it talks to, as far as you know so far.

```text
Context · as understood so far
[ Partners ×40 ] ── webhooks ──► [ Ingestion (to design) ] ── calls ──► [ Billing API ]
                                             │
                                             ├── ? ──► [ ? Analytics warehouse ]
                                             └── ? ──► [ ? Raw event archive ]
```

### Full system (Design turn)

Layers from top to bottom: Edge & Ingress → Runtime & Orchestration → Storage & Memory → Egress & Gateways, then the two bottom sections. This is the reference template for an AI system. For a system without an LLM, keep the structure and replace the runtime steps with the service's own pipeline.

```text
[ Clients / Ingress ] ── CLI / Web UI ── HTTPS + SSE ──► [ API Gateway / Auth Gate ]
                                                                │
                                                                ▼
[ Agent Runtime / State Machine ] ◄── state checkpoints ──► [ State Store ]
       ├──> 0. Input Guardrail      Safety check · Prompt Injection Scan · Intent Schema
       ├──> 1. Context Assembly     Vector search + Cache lookup + User Preferences
       ├──> 2. Planning Loop        Task decomposition · Bounded retries
       ├──> 3. Tool Execution       Argument validation · Cost estimate · Permission check
       │       └──> Execution Sink  ──REST/gRPC──► [ Downstream APIs / Data Stores ]
       ├──> 4. Output Guardrail     PII masking · Secret scan · Size caps
       ├──> 5. Response Composer    Tone rules · Grounding check
       └──> 6. Approval Gate        Human-in-the-Loop (HITL) ⇄ User Approval

[ Infrastructure & Observability ]
  ├── Gateway:      Rate Limiter · Retry + Jitter · Fallback Provider
  └── Telemetry:    OTel Spans ──► Tracing Sink ; Metrics ──► Audit Storage

OFFLINE / CONTROL PLANES
[ Data Ingestion Pipeline ] ──► Validation & Embedding ──► [ Vector Store ]
[ Admin / Policy Control ]   ──► Configuration Updates ──► [ Rules Registry ]
[ CI/CD & Eval Framework ]   ──► Red-teaming & Benchmarks ──► Deployment Gate
```

### Option sketch (Options and Comparison turns)

At most 15 lines, with a title line. Show only the parts where the options differ, plus their direct neighbours. Collapse shared parts into one box, such as `[ App (shared) ]`.

```text
Option B · Queue + workers
[ Partner webhooks ] ── HTTPS ──► [ Ingest API ] ── enqueue ──► [ SQS: events ]
                                  replies 202 at once                  │
                                                                       ▼  async
                           [ Postgres: events ] ◄── upsert ── [ Worker pool ×N ]
                                                                │
                                                                └── 5× failed ──► [ SQS: dlq ]
```

### Change delta (Change turn)

Redraw only the affected region. Mark each line with `(+)` added, `(~)` changed, or `(-)` removed, and say what it was before.

```text
[ Ingest API ] ── enqueue ──► [ SQS: events ]
   └── (+) ── check key ──► [ Redis: seen-keys ]   TTL 24 h · drops duplicate webhooks
[ Worker pool ×N ]
   ├──> 1. Parse & validate
   ├──> (~) 2. Write            was: INSERT · now: upsert ON CONFLICT DO NOTHING
   └──> (-) 3. Send email       moved to [ Notifier ] ── async ──► [ SES ]
```

### Component zoom (Zoom turn)

```text
[ Worker ]
   ├──> 1. Parse & validate     JSON schema · bad payload ──► [ SQS: dlq ]
   ├──> 2. Enrich               ── gRPC ──► [ Customer Service ]  timeout 300 ms · breaker
   │       ├──> 2a. Cache hit   [ Redis: customers ]
   │       └──> 2b. Cache miss  fetch, then write-through
   └──> 3. Persist              ── upsert ──► [ Postgres: events ]
```
