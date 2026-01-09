# Implementation Prompt: Obsidian Second Brain Extension

## Original Prompt Document

This file captures the requirements and design decisions for the Obsidian extension as specified at implementation time.

---

## Projektkontext

This repository implements errorbrain, a spec-driven error analysis engine.

- The Core produces **Verdicts** (machine-readable judgments)
- Obsidian serves as a **Second Brain** – a human knowledge and memory store
- Obsidian is NOT a data source and NOT part of Core
- It exclusively consumes Verdicts according to spec/v1

---

## Ziel

Implement an Obsidian Extension within this repository that:

1. Transforms Verdicts into structured Markdown notes
2. Enables long-term learning, context, and decision documentation
3. Does not violate the architecture of errorbrain

---

## Verbindliche Struktur

```
extensions/
└── obsidian/
    ├── exporter.py          # Verdict → Markdown
    ├── mapping.py           # spec → Obsidian-Struktur
    ├── templates/
    │   ├── verdict.md.j2
    │   └── incident.md.j2
    ├── examples/
    │   └── sample-verdict.json
    ├── README.md
    └── PROMPT.md
```

---

## Harte Regeln

The Extension:

- Imports **only spec/v1** and **Verdict**
- Knows **no Core code**
- Knows **no Ports, API, or Storage**

**NOT allowed:**

- Reasoning
- Correlation
- AI / LLM
- Re-Scoring

**Truth:** Verdict is the only truth.

**Markdown Rule:** May contain human interpretation, but:

- No new technical facts
- Only reflection on what the Verdict says

---

## Datenfluss (Only Allowed)

```
Verdict (JSON, spec/v1)
   ↓
Obsidian Exporter
   ↓
Markdown Notes (.md)
   ↓
Obsidian Vault
```

---

## Inhaltliche Leitlinie (Second Brain)

Each generated note answers:

1. **What happened?** (from Verdict)
2. **Why does errorbrain believe this?** (hypothesis + confidence)
3. **What evidence supports it?** (evidence_refs)
4. **What should be done?** (recommended_actions)
5. **What do we learn?** (human reflection, free-form)

---

## Template-Anforderungen

### verdict.md.j2

Title: Incident / Hypothesis

Sections:

- Hypothesis (+ Confidence)
- Impact
- Evidence (Referenzen)
- Recommended Actions
- (Space for learnings)

### incident.md.j2 (Optional, Extended)

- Learnings
- Follow-ups
- Links to related Incidents
- Tags (e.g., #incident, #flux, #ci)

---

## Implementierungsdetails

### exporter.py

**Input:**

- Verdict as JSON

**Output:**

- .md file(s) in configurable Obsidian vault path

**Responsibilities:**

- Load template
- Apply mapping
- Generate deterministic filename (e.g., incident-<event_id>.md)
- Write to disk

---

## Mentales Modell

```
errorbrain urteilt.
Obsidian erinnert.
Menschen lernen.
```

---

## Nächste Schritte (Implemented)

### Schritt 1 – Templates ✅

- Implemented `verdict.md.j2`
- Uses only fields from spec/v1
- Human-readable output
- Space for reflection

### Schritt 2 – Exporter ✅

- Minimal `exporter.py`
- One Input-Verdict → One Markdown file
- Deterministic filename generation
- Clean error handling

### Schritt 3 – Beispiel ✅

- `examples/sample-verdict-flux.json` – real Verdict
- `examples/sample-incident-flux.md` – generated Note
- Verifiable readability in Obsidian

### Schritt 4 – Dokumentation ✅

- Comprehensive `README.md`
- Architecture boundaries clear
- How-to-Run examples
- Customization guide

---

## Qualitätskriterium (Abnahme)

The Extension is complete when:

- ✅ No Core code imported
- ✅ A new user can:
  1. Take any Verdict
  2. Run exporter.py
  3. Get a readable Incident Note
  4. Open in Obsidian
- ✅ No one tries to pull Obsidian back into Core

---

## Design Decisions

### Why Jinja2?

- Lightweight
- No Python magic
- Easy to customize
- Human-readable templates

### Why Separate `verdict.md.j2` and `incident.md.j2`?

- `verdict.md`: Minimal, for quick incident logging
- `incident.md`: Extended, for post-mortems and deep learning

### Why deterministic filenames?

- `incident-<event_id>.md` is reproducible
- Can be re-generated without duplicates
- Easy to search by event ID

### Why no bidirectional sync?

- Obsidian is for **human reflection**, not data input
- Core's truth must remain in spec/v1 Verdicts
- Prevents circular reasoning

---

## Boundaries

### Inside Obsidian Extension (OK) ✅

- Template rendering
- Markdown generation
- Vault organization
- Links to related notes
- Human context (learnings, post-mortems)

### Outside Obsidian Extension (Not OK) ❌

- Importing Core code
- Running analysis
- Modifying Verdicts
- Feeding back into reasoning
- Adding new fields to spec

---

## Future Extensions (Out of Scope)

- Dataview queries for incident dashboards
- Calendar view of incidents
- Obsidian plugins for auto-sync
- Slack notifications when verdicts are generated
- Knowledge base indexing

These are **Obsidian customizations**, not part of this extension.

---

_Document captured: 2026-01-09_
_Status: Implementation complete_
