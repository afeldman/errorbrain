# errorbrain Obsidian Extension

```text
extensions/obsidian/
├── __init__.py
├── exporter.py              # Main: Verdict → Markdown
├── mapping.py               # spec/v1 → template context
├── templates/
│   ├── verdict.md.j2        # Minimal incident note
│   └── incident.md.j2       # Extended post-mortem template
├── examples/
│   ├── sample-verdict-flux.json      # Example spec/v1 Verdict
│   └── sample-incident-flux.md       # Generated Markdown
├── README.md                # This file
└── PROMPT.md                # Implementation prompt
    {
      "title": "...",
      "description": "...",
      "urgency": "high"
    }
  ],
  "evidence_refs": ["event-id#e0", "event-id#e1"],
  "created_at": "2026-01-09T14:32:30Z"
}
```

## 2. Processing

```python
from extensions.obsidian.exporter import ObsidianExporter

exporter = ObsidianExporter(vault_path="~/Obsidian/errorbrain")
output_path = exporter.export_from_file(
    "verdict.json",
    template_name="verdict.md.j2"
)
# → ~/Obsidian/errorbrain/incident-550e8400-....md
```

### 3. Output: Markdown Note

Human-readable, Obsidian-compatible:

```markdown
# GitOps reconciliation blocked by missing configuration dependency

**Incident ID:** `550e8400-...`
**Verdict ID:** `8cb91b15-...`
**Severity:** CRITICAL

## Hypothesis
Flux controller cannot deploy Helm chart because ...

## Impact
- Severity: CRITICAL
- Affected: flux-controller, app-api

## Recommended Actions
1. [HIGH] Restore missing ConfigMap key
2. [HIGH] Validate Helm chart compatibility
3. [MEDIUM] Coordinate with SecOps

## What Did We Learn?
_Space for reflection and lessons_
```

---

## Usage

### Programmatic (Python)

```python
import json
from extensions.obsidian.exporter import ObsidianExporter
from extensions.obsidian.mapping import verdict_to_template_context

# Load verdict
with open("verdict.json") as f:
    verdict = json.load(f)

# Initialize exporter
exporter = ObsidianExporter(vault_path="~/Obsidian/errorbrain")

# Export to Markdown
output_path = exporter.export_verdict(
    verdict,
    template_name="verdict.md.j2",
    filename="incident-2026-01-09.md"
)

print(f"Exported: {output_path}")
```

### CLI (Command-line)

```bash
cd errorbrain
python3 -m extensions.obsidian.exporter \
  --verdict verdict.json \
  --vault ~/Obsidian/errorbrain \
  --template verdict.md.j2
```

### Direct Integration

If using errorbrain's server, post-process verdicts:

```python
# After /events endpoint returns Verdict
verdict = response.json()

# Export to Obsidian
exporter = ObsidianExporter(vault_path=OBSIDIAN_PATH)
exporter.export_verdict(verdict)
```

---

## Templates

### `verdict.md.j2` (Minimal)

A lightweight, straightforward incident note:

- Title (hypothesis)
- Hypothesis with confidence
- Impact and affected components
- Evidence references
- Recommended actions
- Space for learnings
- Tags

**Use this for:** Quick incident logging, daily ops.

### `incident.md.j2` (Extended)

Comprehensive post-mortem template:

- Executive summary
- Timeline
- Root cause analysis
- Impact assessment
- Actions taken
- Prevention & learnings
- Follow-ups (checkboxes)
- Related incidents
- Tags

**Use this for:** Deep incident analysis, post-mortems, knowledge building.

---

## Customization

### Custom Template

Create your own `.md.j2` template in `extensions/obsidian/templates/`:

```jinja2
# {{ hypothesis.title }}

**Severity:** {{ impact.severity }}
**Confidence:** {{ "%.0f%%" % (hypothesis.confidence * 100) }}

...your custom structure...
```

Available template variables (from `mapping.py`):

```python
context = {
    "verdict_id": str,
    "event_id": str,
    "hypothesis": {
        "title": str,
        "description": str,
        "confidence": float,
    },
    "impact": {
        "severity": str,
        "affected_components": list[str],
    },
    "recommended_actions": list[{
        "title": str,
        "description": str,
        "urgency": str,
    }],
    "evidence_refs": list[str],
    "created_at": datetime,
}
```

### Custom Vault Path

```python
# Default: ~/Obsidian/errorbrain
exporter = ObsidianExporter(vault_path="/path/to/my/vault")
```

---

## Architecture Boundaries

### What This Extension Does ✅

- Parse spec/v1 Verdicts
- Map to template context
- Render Markdown
- Write to Obsidian vault
- Provide human-friendly incident notes

### What This Extension Does NOT Do ❌

- Reason about errors
- Correlate events
- Score verdicts differently
- Integrate with Core logic
- Generate new verdicts
- Use LLMs or AI
- Import Port or Storage code
- Re-implement analysis

**If you're tempted to add reasoning, stop.** That's the Core's job. The extension is a **view layer**, not a **logic layer**.

---

## Obsidian Integration

### Recommended Vault Structure

```
Obsidian Vault/
├── 90 - System/
│   ├── errorbrain/
│   │   ├── Templates/
│   │   │   └── incident.md          # Obsidian template
│   │   └── incident-*.md            # Generated notes
│   └── Meta.md
└── 10 - Logs/
    └── Daily Notes/
```

### Useful Plugins

- **Dataview:** Query incidents by severity, component, date
- **Backlinks:** Relate incidents to runbooks, postmortems
- **Calendar:** Timeline view of incidents
- **Tag Wrangler:** Organize by #incident, #critical, #flux, etc.

### Example Query (Dataview)

```dataview
TABLE severity, confidence, created_at
WHERE file.folder = "errorbrain"
AND severity = "critical"
SORT created_at DESC
```

---

## Testing

### Test Template Rendering

```bash
cd extensions/obsidian
python3 -c "
import json
from exporter import ObsidianExporter

exporter = ObsidianExporter('/tmp/test-vault')
verdict = json.load(open('examples/sample-verdict-flux.json'))
output = exporter.export_verdict(verdict)
print('✓ Rendered:', output)
"
```

### Verify Output

Generated notes are valid Markdown:

```bash
# Check for syntax
md-lint extensions/obsidian/examples/sample-incident-flux.md

# View in your editor
cat extensions/obsidian/examples/sample-incident-flux.md
```

---

## Quality Criteria ✓

This extension is complete when:

- ✅ No Core code is imported (only spec/v1 models)
- ✅ A new user can:
  1. Take any spec/v1 Verdict
  2. Run the exporter
  3. Get a readable Markdown note
  4. Open it in Obsidian
- ✅ Templates are human-friendly
- ✅ No one tries to add reasoning back into this layer

---

## Example: From Verdict to Obsidian

### Input Verdict

See `examples/sample-verdict-flux.json` – a real Flux GitOps incident.

### Generated Note

See `examples/sample-incident-flux.md` – the human-readable version.

**Open it in Obsidian and imagine:**

- You're reviewing past incidents
- You're debugging a similar problem
- You're learning from your incident history
- You're sharing context with your team

---

## Contributing

If you extend this extension:

1. **Respect the boundaries:** No Core code imports
2. **Expand templates, not logic:** New `.md.j2` files, not new analysis
3. **Keep it spec-conformant:** Only consume spec/v1 Verdicts
4. **Document tradeoffs:** Why this template design?

---

## License

Same as errorbrain.

---

## Questions?

- **What's a Verdict?** → See `spec/v1/verdict.schema.json`
- **How does errorbrain reason?** → See `server/core/reasoning.py`
- **Can Obsidian feed back into Core?** → No. It's a view layer only.

---

_This extension is part of the errorbrain ecosystem, but lives at the boundary. It consumes Verdicts, generates context, and returns nothing back to the core._
