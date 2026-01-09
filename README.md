
# ErrorBrain – AI-powered Debugging Memory

**ErrorBrain** is a spec-driven analysis and reasoning engine for errors, incidents, and operational signals in distributed systems.

It ingests facts (events, logs, status, metrics), correlates them, and produces structured verdicts that explain what happened, why it likely happened, and what to do next.

> ErrorBrain is not an agent, not an SDK hub, and not an LLM product.
> It is a judgement system.

---

## License

This project is licensed under the [Apache License 2.0](LICENSE).

---

## Core Principles

- 📜 **Spec-first:** All contracts are explicit and versioned.
- ⚖️ **Verdicts, not vibes:** Structured, explainable outcomes instead of free-form text.
- 🧠 **Reasoning over data:** Deterministic rules by default, LLMs are optional.
- 🔌 **Adapters at the edges:** No business logic leaks into adapters or integrations.
- 🧩 **Second Brain ready:** Human knowledge and documentation live outside the core system.

---

## What problem does ErrorBrain solve?

Most systems can tell you *that* something failed.

ErrorBrain answers:

- **What exactly failed?**
- **What evidence supports this conclusion?**
- **What is the most likely root cause?**
- **What action should be taken next?**
- **How confident is the system in its judgement?**

All answers are delivered in a machine-readable, explainable, and reproducible format.

---

## Architecture Overview

ErrorBrain follows Clean Architecture (Ports & Adapters).

### Main Components

- **Core:** Contains all business logic for reasoning, correlation, and verdict generation. No adapters, no external dependencies.
- **API:** Pure HTTP adapter, translates requests and responses, no business logic.
- **Ports:** Defined interfaces for ingest, query, and other integrations.
- **Storage:** Internal only (e.g., in-memory), not exposed or coupled to external systems.
- **Extensions:** (e.g., Obsidian) consume verdicts, never part of the server runtime.
- **Docker:** Only runs the production server (Core + API), no SDKs, extensions, or legacy code.

```text
┌────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Client   │──→───│    SDKs     │──→───│    API      │──→───│   Core      │
└────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
        │
        ↓
      ┌─────────────┐
      │   Verdicts  │
      └─────────────┘
        ↓
      ┌─────────────┐
      │  Extensions │
      └─────────────┘
        ↓
      ┌─────────────┐
      │  Obsidian   │
      └─────────────┘
```

```text
spec/v1         → contracts (the law)
server/core     → reasoning & judgement
server/api      → HTTP adapter
server/ports    → interfaces
server/storage  → internal state
sdk/*           → ingestion clients
extensions/*    → optional consumers (e.g. Obsidian)
```

### Key Rules

- The **spec is the source of truth**
- The **core is the only place where decisions happen**
- APIs translate, they do not decide
- SDKs are **spec-loyal and AI-free**
- Extensions consume results, never influence them

---

## Verdicts

The primary output of errorbrain is a **Verdict**.

A verdict is:

- Structured (JSON, spec-defined)
- Deterministic
- Explainable
- Stable across implementations

It typically contains:

- Hypothesis (what likely happened)
- Confidence
- Impact & affected components
- Evidence references
- Recommended actions

Verdicts are **the only truth** in the system.

---

## Reasoning & LLMs

LLMs are **optional** and **strictly contained**.

### Design

- Rule-based reasoning is the default
- LLMs act as **advisors**, not judges
- Verdicts are always built deterministically
- LLMs never modify the spec or output schema

### Implementation

```text
server/core/reasoning/
├── rules.py       # deterministic reasoning
├── llm_anyllm.py  # optional LLM-backed reasoning
└── engine.py      # orchestration & fallback
```

### Configuration

```env
# Reasoning mode: rules or llm
ERRORBRAIN_REASONING_MODE=rules|llm

# LLM configuration (for LM Studio or any OpenAI-compatible endpoint)
LLM_HOST=http://127.0.0.1:1234/v1
LLM_MODEL=mistralai/ministral-3-3b
LLM_KEY=not-required-for-local
```

Local development works seamlessly with LM Studio via an OpenAI-compatible endpoint.

If LLMs are unavailable, errorbrain continues to function using rules only.

## Docker & Runtime

The Docker image represents production runtime only.

### Principles

Server-only (core + API)

- No SDKs
- No extensions
- No experiments
- No legacy code

### Entrypoint

```bash
python -m server.main
```

### docker-compose (example)

```yaml
services:
  errorbrain:
    image: errorbrain:latest
    ports:
      - "8080:8080"
    environment:
      ERRORBRAIN_REASONING_MODE: rules
    volumes:
      - ./obsidian-vault:/data/obsidian
```

Volumes are used **only at runtime**, e.g. for exporting results.

## Obsidian & Second Brain

errorbrain intentionally separates judgement from memory.

- errorbrain produces verdicts
- Humans reflect, learn, and document outcomes

This is supported via an optional extension:

```text
extensions/obsidian/
```

The Obsidian extension:

- Consumes verdicts
- Renders Markdown notes
- Acts as a Second Brain
- Never feeds back into the core

## Ecosystem

errorbrain is designed to work with adapters such as:

- fluxbrain – FluxCD / GitOps collector
- CI/CD collectors
- Runtime or application adapters

Adapters answer “what happened?”
errorbrain answers “why?”

---

## What errorbrain is NOT

- ❌ An agent framework
- ❌ A monitoring system
- ❌ A prompt playground
- ❌ A storage backend
- ❌ A replacement for human judgement

## Philosophy

- Rules ensure correctness.
- LLMs improve expression.
- Verdicts remain stable.
- Humans remain responsible.

## Status

- Architecture: ✅ Stable
- Spec: v1 (frozen)
- Core reasoning: rules + optional LLM
- Docker runtime: production-ready
- Extensions: optional and isolated

## License

Apacke 2.0

## Contributing

Contributions are welcome — but architecture rules are strict.

If a change:

- adds reasoning outside the core
- leaks LLM logic into APIs or SDKs
- weakens the spec contract

…it will be rejected.

## Final Note

errorbrain is built for clarity over cleverness.

If it ever becomes hard to explain why a verdict exists,
then something is wrong.
