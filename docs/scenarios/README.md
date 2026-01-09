# errorbrain Scenarios: Proof of Insight

Diese Szenarien demonstrieren, wie **errorbrain** realistische Fehler diagnostiziert.

> **Ziel:** Nach 5 Minuten verstehen, warum errorbrain existiert.

## Die Philosophie

```
Events      → ErrorEvent JSON (was ist passiert)
Evidence    → Beweise aus mehreren Quellen (logs, metrics, k8s events, ...)
Verdict     → Maschinenlesbares Urteil (spec/v1/verdict.json)
Explain     → Menschenlesbares Verständnis (immer aus Verdict abgeleitet)
```

**Zentrale Regel:** Das Verdict ist die einzige Wahrheit. Explain erklärt nur das, was im Verdict steht.

---

## Szenario 1: Flux Reconciliation Failed

**Typ:** Infrastruktur / GitOps
**Ort:** `/docs/scenarios/01-flux-reconciliation-failed/`

### Was ist passiert?

GitOps-Controller (Flux) kann eine Anwendung nicht deployen – ein erforderlicher Konfigurationsschlüssel fehlt.

### Warum ist das interessant?

Dieses Szenario zeigt, dass **errorbrain Koordinationsprobleme** zwischen Teams erkennt:

- **SecOps hat Geheimnisse rotiert** (richtig, aus Security-Sicht)
- **Infrastructure hat den Helm-Chart nicht angepasst** (Versehentnis)
- **Ergebnis:** Deployment blockiert

Das ist kein Code-Fehler, kein Infrastruktur-Bug – es ist ein Prozess-Fehler mit technischem Symptom.

### Dateien

| Datei | Bedeutung |
|---|---|
| `event.json` | Das ErrorEvent von Flux (was war der Fehler) |
| `evidence.json` | Kontext und Beweise (Git-History, K8s-Events, Logs) |
| `verdict.json` | errorbrain's Diagnose (was ist die Root Cause) |
| `explain.md` | Menschliche Erklärung (was soll der Operator tun) |

### Lesen Sie zuerst

1. `event.json` – Verstehen Sie, was Flux meldet
2. `explain.md` – Verstehen Sie, was errorbrain empfiehlt
3. `verdict.json` – Sehen Sie die Struktur der Diagnose

**Confidence:** 85% (hohes Vertrauen in die Diagnose)

---

## Szenario 2: CI Deployment Timeout

**Typ:** CI/CD
**Ort:** `/docs/scenarios/02-ci-deploy-timeout/`

### Was ist passiert?

Ein Deployment-Job hat sich nach 30 Minuten nicht durchgeführt. Pods konnten sich nicht initialisieren.

### Warum ist das interessant?

Dieses Szenario zeigt **zeitliche Konflikte**:

- **Das Deployment ist richtig.**
- **Die Datenbank-Wartung ist geplant und notwendig.**
- **Das Problem:** Sie passieren gleichzeitig (zeitlich zufällig).

Das ist **kein Code-Fehler**, kein Infrastruktur-Bug, kein Design-Problem. Es ist **Timing**.

Ohne gute Diagnose würden Sie Logs durchsuchen und nach Bugs suchen, die nicht existieren.
Mit errorbrain: In 5 Minuten ist klar, dass es um die Maintenance-Fenster geht.

### Dateien

| Datei | Bedeutung |
|---|---|
| `event.json` | Der Deployment-Timeout-Fehler |
| `evidence.json` | Timeline: Wann war die Wartung, wann der Deploy, was passiert dazwischen |
| `verdict.json` | Diagnose: "Deployment überlappte mit Maintenance" |
| `explain.md` | Handlungsempfehlungen |

### Lesen Sie zuerst

1. `event.json` – Der initiale Fehler
2. `evidence.json` → `verdict.json` – Die Timeline zeigt die Diagnose
3. `explain.md` – Warum Timing das Problem ist

**Confidence:** 85%

---

## Szenario 3: Runtime CrashLoop

**Typ:** Application Runtime
**Ort:** `/docs/scenarios/03-runtime-crashloop/`

### Was ist passiert?

Ein Pod startet nicht, crasht, wird neu gestartet, crasht wieder. CrashLoop. Der Grund: Ein erforderliches Kubernetes Secret fehlt.

### Warum ist das interessant?

Dieses Szenario zeigt **einfache, aber kritische Konfigurationsfehler**:

- **Technisch nicht komplex** (ein fehlender Secret)
- **Trotzdem kritisch** (ganze Payment-Systeme sind down)
- **Die Herausforderung:** Von 1000 möglichen Gründen den richtigen schnell finden

Dieses Szenario zeigt den **praktischen Wert** von errorbrain im Ops-Alltag:

> "Mein Pod crasht. Ist es ein Code-Bug? Ist es Kubernetes? Ist es Netzwerk?"
> **errorbrain:** "Das Secret 'stripe-secrets' fehlt. Erstelle es."
> **Operator:** "Ah, danke. 2 Minuten Fix." ✓

### Dateien

| Datei | Bedeutung |
|---|---|
| `event.json` | Die Crash-Fehlermeldung und Stack Trace |
| `evidence.json` | Kubernetes API sagt: Secret existiert nicht. Logs zeigen: Deployment vergass Secret zu erstellen |
| `verdict.json` | Diagnose mit konkretem `kubectl`-Befehl zur Behebung |
| `explain.md` | Warum das sicher zu beheben ist und wie man es wiederholt |

### Lesen Sie zuerst

1. `event.json` – Der Fehler
2. `explain.md` – Die einfache Lösung (ein kubectl-Befehl)
3. `verdict.json` – Die strukturierte Diagnose

**Confidence:** 85%

---

## Wie Sie diese Szenarien verwenden

### Option A: Manuell durcharbeiten

```bash
cd docs/scenarios/01-flux-reconciliation-failed
cat event.json        # Fehler verstehen
cat explain.md        # Diagnose verstehen
cat verdict.json      # Struktur sehen
```

### Option B: Die Szenarien durch errorbrain laufen lassen

Jedes `event.json` ist spec-konform und kann durch den errorbrain-Server geschickt werden:

```bash
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d @docs/scenarios/01-flux-reconciliation-failed/event.json
```

Das System wird ein Verdict generieren.

### Option C: Die Szenarien automatisiert validieren

```bash
cd server
PYTHONPATH=src uv run python -m pytest tests/  # Alle Tests, inklusive Szenarien
```

---

## Was diese Szenarien zeigen

| Aspekt | Szenario 1 | Szenario 2 | Szenario 3 |
|---|---|---|---|
| **Typ** | GitOps | CI/CD | Application |
| **Root Cause** | Koordinationsproblem (Teams) | Timing (zeitlicher Konflikt) | Konfiguration (fehlende Dependency) |
| **Komplexität** | Mittel | Mittel | Einfach |
| **Impact** | Hoch (Rollout blockiert) | Hoch (Deployment pausiert) | Kritisch (Service down) |
| **Was errorbrain unique macht** | Erkennt Teams-Koordination | Erkennt Timing-Konflikte | Schnelle Diagnose vs. Log-Suche |

---

## Qualitätskriterien ✓

Alle Szenarien erfüllen:

- ✓ `event.json` ist **spec-konform** (validiert gegen `spec/v1/error_event.schema.json`)
- ✓ `verdict.json` ist **spec-konform** (validiert gegen `spec/v1/verdict.schema.json`)
- ✓ `explain.md` ist **ausschließlich aus Verdict abgeleitet** (keine neuen Informationen, reine Erklärung)
- ✓ Jedes Szenario ist **standalone verständlich** (keine Abhängigkeiten zwischen Szenarien)
- ✓ **Confidence-Werte sind begründet** (nicht geraten):
  - 85% = hohes Vertrauen (mehrere unabhängige Beweise, kausale Verbindung klar)
- ✓ **Recommended Actions sind konkret und ausführbar**:
  - Nicht: "Überprüfe die Logs"
  - Sondern: "Erstelle Secret mit `kubectl create secret...` oder Rollback zu Commit X"

---

## Die mentale Modell

```
┌─────────────────────────────────────────────────┐
│  Events (was ist passiert)                      │
│  – Fehlermeldungen                              │
│  – Stack Traces                                 │
│  – Kontext (User, Request, Cluster)             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Evidence (Beweise aus vielen Quellen)          │
│  – Logs (App, System, Kubernetes)               │
│  – Metrics (Prometheus, CloudWatch)             │
│  – Events (K8s Events, Git History)             │
│  – APIs (Kubernetes, GitHub, etc.)              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  errorbrain Core (Reasoning)                    │
│  – Deterministische Regeln                      │
│  – Temporale und kausale Analyse                │
│  – Root Cause Bestimmung                        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Verdict (Diagnose, spec/v1, Wahrheit)         │
│  – Hypothese (was ist die Root Cause)           │
│  – Impact (welche Komponenten sind betroffen)   │
│  – Recommended Actions (konkrete Schritte)      │
│  – Confidence (0.0–1.0, begründet)              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Explain (menschlich lesbare Erklärung)         │
│  – Einfach Deutsch/Englisch                     │
│  – Basierend ausschließlich auf Verdict         │
│  – Keine neuen Informationen                    │
│  – Handlungsempfehlungen                        │
└─────────────────────────────────────────────────┘
```

**Der Schlüssel:** Das Verdict ist die einzige Wahrheit. Explain ist nur eine Präsentation.

---

## Weitere Ressourcen

- **Spec Definition:** `spec/v1/error_event.schema.json` und `spec/v1/verdict.schema.json`
- **Server Source:** `server/src/errorbrain_server/`
- **SDK:** `sdk/python/src/errorbrain/`

---

## Fragen?

Diese Szenarien wurden so designt, dass sie **ohne Code-Änderungen** lauffähig sind und **alle Spezifikationen einhalten**. Sie zeigen real existierende Probleme, die Teams in Produktion täglich beegnen.
