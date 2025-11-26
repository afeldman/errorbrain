# ErrorBrain – AI-powered Debugging Memory

**Persistentes, durchsuchbares Second Brain für Fehler, Stacktraces & KI-Erklärungen.**

ErrorBrain erfasst Fehler aus deinen Anwendungen, analysiert sie mit einer KI (lokal via LM Studio oder Cloud) und speichert alles automatisch in deinem Engineering Second Brain (Obsidian Vault).

Jeder Fehler wird zu dauerhaftem, dokumentiertem und durchsuchbarem Wissen.

## 🚀 Features

### ✅ Fehler aus jeder Sprache erfassen

- **Python SDK** - Client für FastAPI-Integration
- **Go SDK** - Client für Go-Services
- **Terraform CLI Wrapper** - Erfasst terraform apply-Fehler

### ✅ Auto-Analyse mit deiner KI

Funktioniert mit:

- **LM Studio** (lokal, empfohlen für Tests)
- OpenAI, Anthropic, Azure
- Beliebige OpenAI-kompatible Endpoints

### ✅ Automatische Speicherung im Second Brain

- Obsidian Markdown Vault
- Lokaler Markdown-Ordner
- Git Knowledge Repo

### ✅ Wiederverwendbares Engineering-Wissen

- Behebe denselben Fehler nie zweimal
- Onboarde Entwickler schneller
- Zentralisierte Incident-Dokumentation

## 🏗️ Architektur

```
Applications (Python, Go, Terraform)
        ↓
ErrorBrain SDK (send error + trace + metadata)
        ↓
ErrorBrain API (FastAPI)
        ↓
- LM Studio / LLM (explain)
- Obsidian Vault (store)
        ↓
Engineering Second Brain
```

## 📦 Repository Layout

```
api/                    → FastAPI Server (src/errorbrain_server)
sdk-python/             → Python SDK
sdk-go/                 → Go SDK
terraform-provider/     → Terraform CLI Wrapper
examples/               → Code examples for all languages
tests/                  → Test suites
.pre-commit-config.yaml → Git hooks configuration
Makefile                → Development commands
SETUP.md                → Detailed setup guide
```

## 🚀 Quick Start

### 1. LM Studio starten

1. Lade [LM Studio](https://lmstudio.ai/) herunter
2. Lade ein Modell (z.B. Llama 3.2, Mistral)
3. Starte den lokalen Server (Port 1234)

### 2. ErrorBrain API starten

```bash
cd api
uv sync --all-extras

# .env erstellen
cp .env.example .env
# Passe ERRORBRAIN_OBSIDIAN_PATH an!

# Server starten (Development)
uv run errorbrain-server-dev

# Oder mit Make
make dev-api
```

API läuft auf: `http://localhost:8000`

**Tests ausführen:**

```bash
cd api
uv run pytest tests/ -v

# Oder
make test
uv run errorbrain-dev
```

API läuft auf: `http://localhost:8000`

### 3. Python SDK verwenden

```bash
pip install -e ./sdk-python
```

```python
from errorbrain import ErrorBrainClient

client = ErrorBrainClient()

try:
    result = 1 / 0
except Exception as e:
    response = client.send_exception(
        exc=e,
        project="billing-service",
        tags=["prod"],
    )
    print(f"Error analyzed: {response.id}")
    print(f"Saved to: {response.saved_path}")
```

### 4. Go SDK verwenden

```bash
go get github.com/afeldman/errorbrain/sdk-go
```

```go
import errorbrain "github.com/afeldman/errorbrain/sdk-go"

client := errorbrain.NewClient("")

report := &errorbrain.ErrorReport{
    Language: "go",
    Project:  "payment-service",
    Message:  "redis connection failed",
    Tags:     []string{"prod"},
    StoreInVault: true,
}

response, err := client.SendError(report)
```

### 5. Terraform Wrapper

```bash
cd terraform-provider
go build -o terraform-errorbrain
sudo mv terraform-errorbrain /usr/local/bin/

# Verwenden
export ERRORBRAIN_PROJECT="my-infrastructure"
terraform-errorbrain wrap apply
```

## 📚 Vollständige Dokumentation

Siehe **[SETUP.md](./SETUP.md)** für:

- Detaillierte LM Studio-Konfiguration
- API-Konfiguration & Umgebungsvariablen
- SDK-Installation für alle Sprachen
- Obsidian-Integration & Dataview-Queries
- Troubleshooting & Best Practices

## 🧪 Beispiele

```bash
cd examples

# Python
python python_example.py

# Go
go run go_example.go
```

## 🛠️ Development

### Alle Dependencies installieren

```bash
make install
```

### Alle Tests ausführen

```bash
make test
```

### Code formatieren

```bash
make format
```

### Linting ausführen

```bash
make lint
```

### Alles prüfen (Format + Lint + Test)

```bash
make check-all
```

### Git Hooks installieren

```bash
make setup-git-hooks
# oder
pip install pre-commit
pre-commit install
```

## 📐 Code-Qualität

### Python (API + SDK)

- **Linting**: Ruff
- **Type Checking**: mypy
- **Testing**: pytest
- **Coverage**: pytest-cov
- **Docstrings**: Google Style

### Go (SDK + Terraform Provider)

- **Linting**: golangci-lint
- **Testing**: Go testing package
- **Documentation**: godoc
- **Formatting**: gofmt

## 📚 Dokumentation

- **[SETUP.md](./SETUP.md)** - Detaillierte Setup-Anleitung
- **[api/README.md](./api/README.md)** - API Dokumentation
- **[sdk-python/README.md](./sdk-python/README.md)** - Python SDK
- **[sdk-go/README.md](./sdk-go/README.md)** - Go SDK
- **[terraform-provider/README.md](./terraform-provider/README.md)** - Terraform Integration

Fehler werden automatisch gespeichert in:

```
/Users/anton.feldmann/lynq/errors/
├── 20241126-120534-billing-service-abc123.md
└── ...
```

Jede Datei enthält:

- Fehlermeldung & Stacktrace
- KI-Erklärung & Lösungsvorschläge
- Metadata (Tags, Projekt, Sprache)
- Frontmatter für Dataview-Queries

## 🧩 Roadmap

- [x] Python SDK v1
- [x] Go SDK v1
- [x] Terraform CLI Wrapper
- [ ] Web Dashboard
- [ ] Embedding-basierte Fehlersuche
- [ ] GitOps Vault Sync
- [ ] Slack/Discord Webhooks

## 🤝 Contributing

Pull Requests sind willkommen! Für größere Änderungen, öffne bitte zuerst ein Issue.

## 📄 License

MIT - Siehe [LICENSE](./LICENSE)

## 🔗 Links

- [LM Studio](https://lmstudio.ai/)
- [Obsidian](https://obsidian.md/)
- [FastAPI](https://fastapi.tiangolo.com/)
