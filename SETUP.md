# ErrorBrain Setup-Anleitung

## Übersicht

ErrorBrain ist ein System, das Fehler aus Python, Go und Terraform erfasst, mit einer KI analysiert und in deinem Obsidian Second Brain speichert.

## Architektur

```
┌─────────────┐
│ Deine Apps  │
│ (Py/Go/TF)  │
└──────┬──────┘
       │
       v
┌──────────────┐      ┌──────────┐
│ ErrorBrain   ├─────>│ LM Studio│
│ FastAPI      │      │ (lokal)  │
└──────┬───────┘      └──────────┘
       │
       v
┌──────────────┐
│ Obsidian     │
│ Vault        │
│ (/lynq)      │
└──────────────┘
```

## 1. LM Studio einrichten

### Installation

1. Lade [LM Studio](https://lmstudio.ai/) herunter
2. Installiere die App
3. Öffne LM Studio

### Modell laden

1. Gehe zu "Discover" (🔍)
2. Suche nach einem Modell, z.B.:
   - `meta-llama-3.1-8b-instruct`
   - `mistral-7b-instruct-v0.2`
   - `phi-3-mini-4k-instruct`
3. Klicke "Download"

### Lokalen Server starten

1. Gehe zu "Local Server" (⚡)
2. Wähle dein heruntergeladenes Modell
3. Klicke "Start Server"
4. Der Server läuft nun auf `http://localhost:1234`

**Test:**

```bash
curl http://localhost:1234/v1/models
```

## 2. ErrorBrain API starten

### Installation

```bash
cd /Users/anton.feldmann/Projects/errorbrain/api

# Dependencies installieren
uv sync
```

### Konfiguration

Erstelle `.env` in `api/`:

```bash
# LM Studio (lokal)
ERRORBRAIN_LLM_PROVIDER=openai
ERRORBRAIN_LLM_MODEL=local-model
ERRORBRAIN_LLM_BASE_URL=http://localhost:1234/v1
ERRORBRAIN_LLM_API_KEY=lm-studio

# Obsidian Vault
ERRORBRAIN_OBSIDIAN_ENABLED=true
ERRORBRAIN_OBSIDIAN_PATH=/Users/anton.feldmann/lynq/errors
```

### Starten

```bash
# Development-Modus (mit Auto-Reload)
uv run errorbrain-dev

# Production-Modus
uv run errorbrain
```

API läuft auf: `http://localhost:8000`

**Test:**

```bash
curl http://localhost:8000/healthz
```

## 3. Python SDK verwenden

### Installation

```bash
cd /Users/anton.feldmann/Projects/errorbrain/sdk-python
uv sync
```

### In deinem Projekt

```bash
# Als lokales Paket
pip install -e /Users/anton.feldmann/Projects/errorbrain/sdk-python

# Oder direkt via uv
uv add --editable /Users/anton.feldmann/Projects/errorbrain/sdk-python
```

### Verwendung

```python
from errorbrain import ErrorBrainClient

client = ErrorBrainClient()

try:
    # Dein Code
    result = 1 / 0
except Exception as e:
    # Automatisch analysieren und speichern
    response = client.send_exception(
        exc=e,
        project="my-service",
        tags=["prod"],
    )
    print(f"Error analyzed: {response.id}")
    print(f"Saved to: {response.saved_path}")
```

## 4. Go SDK verwenden

### Installation

In deinem Go-Projekt:

```bash
go get github.com/afeldman/errorbrain/sdk-go
```

### Verwendung

```go
import errorbrain "github.com/afeldman/errorbrain/sdk-go"

func main() {
    client := errorbrain.NewClient("")

    // Fehler senden
    report := &errorbrain.ErrorReport{
        Language: "go",
        Project:  "my-service",
        Message:  "connection failed",
        Traceback: "...",
        Tags:     []string{"prod"},
        StoreInVault: true,
    }

    response, err := client.SendError(report)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("Error ID: %s\n", response.ID)
}
```

## 5. Terraform Integration

### CLI Wrapper bauen

```bash
cd /Users/anton.feldmann/Projects/errorbrain/terraform-provider
go build -o terraform-errorbrain
sudo mv terraform-errorbrain /usr/local/bin/
```

### Verwendung

```bash
export ERRORBRAIN_PROJECT="my-infrastructure"

# Anstatt 'terraform apply'
terraform-errorbrain wrap apply

# Oder alias in .zshrc:
alias tf='terraform-errorbrain wrap'
tf apply
```

## 6. Obsidian Vault einrichten

Die Fehler werden automatisch in deinem Vault gespeichert:

```
/Users/anton.feldmann/lynq/errors/
├── 20241126-120534-billing-service-abc123.md
├── 20241126-121045-payment-api-def456.md
└── ...
```

### Empfohlene Obsidian-Plugins

- **Dataview** - Für Fehler-Dashboards
- **Templater** - Für Custom-Templates
- **Calendar** - Zeitliche Übersicht

### Beispiel Dataview Query

Erstelle eine Datei `errors-dashboard.md`:

````markdown
# Error Dashboard

## Recent Errors

```dataview
TABLE language, project, tags
FROM "errors"
SORT created_at DESC
LIMIT 20
```

## Errors by Project

```dataview
TABLE rows.file.link as "Errors"
FROM "errors"
GROUP BY project
```
````

## 7. Testen

### Python Test

```bash
cd /Users/anton.feldmann/Projects/errorbrain/examples
python python_example.py
```

### Go Test

```bash
cd /Users/anton.feldmann/Projects/errorbrain/examples
go run go_example.go
```

### Prüfe Obsidian

Öffne deinen Vault und gehe zu `/errors/` - du solltest neue Markdown-Dateien sehen!

## Troubleshooting

### "Connection refused" beim API-Aufruf

- Prüfe, ob die API läuft: `curl http://localhost:8000/healthz`
- Starte die API neu: `uv run errorbrain-dev`

### LM Studio antwortet nicht

- Prüfe, ob der Server läuft: `curl http://localhost:1234/v1/models`
- Starte LM Studio neu und klicke "Start Server"

### Fehler werden nicht in Obsidian gespeichert

- Prüfe den Pfad in `.env`: `ERRORBRAIN_OBSIDIAN_PATH=/Users/anton.feldmann/lynq/errors`
- Erstelle den Ordner manuell: `mkdir -p /Users/anton.feldmann/lynq/errors`
- Prüfe Schreibrechte: `ls -la /Users/anton.feldmann/lynq/`

### Go SDK Import-Fehler

- Ersetze den Import: `replace github.com/afeldman/errorbrain/sdk-go => ../sdk-go` in `go.mod`
- Oder publish das SDK zuerst auf GitHub

## Nächste Schritte

1. **Automatisierung**: Integriere ErrorBrain in deine CI/CD Pipeline
2. **Alerting**: Füge Webhooks hinzu (Slack, Discord, etc.)
3. **Dashboard**: Baue ein Web-UI für Fehler-Statistiken
4. **Suche**: Implementiere Embedding-basierte Fehlersuche

## Umgebungsvariablen (Übersicht)

| Variable                   | Default                             | Beschreibung         |
| -------------------------- | ----------------------------------- | -------------------- |
| `ERRORBRAIN_API_URL`       | `http://localhost:8000`             | ErrorBrain API URL   |
| `ERRORBRAIN_LLM_PROVIDER`  | `openai`                            | LLM Provider         |
| `ERRORBRAIN_LLM_MODEL`     | `local-model`                       | Modellname           |
| `ERRORBRAIN_LLM_BASE_URL`  | `http://localhost:1234/v1`          | LM Studio URL        |
| `ERRORBRAIN_OBSIDIAN_PATH` | `/Users/anton.feldmann/lynq/errors` | Obsidian Speicherort |
| `ERRORBRAIN_PROJECT`       | `default`                           | Standard-Projektname |
