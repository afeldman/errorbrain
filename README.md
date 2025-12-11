# ErrorBrain – AI-powered Debugging Memory

**Persistentes, durchsuchbares Second Brain für Fehler, Stacktraces & KI-Erklärungen.**

ErrorBrain erfasst Fehler aus deinen Anwendungen, analysiert sie mit einer KI (lokal via LM Studio oder Cloud) und speichert alles automatisch in deinem Engineering Second Brain (Obsidian Vault).

Jeder Fehler wird zu dauerhaftem, dokumentiertem und durchsuchbarem Wissen.

## 🚀 Features

- ✅ **6 SDKs** - Python, Go, TypeScript, Deno, Rust, C++
- ✅ **FastAPI Server** - Modern, async, fully typed
- ✅ **AI-Powered** - Fehleranalyse mit LM Studio (lokal) oder OpenAI
- ✅ **Obsidian Integration** - Automatische Second Brain Speicherung
- ✅ **Production-Ready** - Tests, CI/CD, Dokumentation
- ✅ **Open Source** - MIT License

## 📦 Schnellstart

### 1. Setup durchführen

```bash
./setup.sh
```

Dies installiert alle Dependencies für alle SDKs (Python, Go, Rust, TypeScript, Deno, C++).

### 2. .env konfigurieren

```bash
cd api
cp .env.example .env
# Bearbeite .env mit deinen Einstellungen
```

### 3. Server starten

```bash
./dev-server.sh
```

API läuft auf:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Health Check

```bash
./health-check.sh
```

## 🛠️ Verfügbare Befehle

### Shell Scripts (Einfach)

```bash
./setup.sh           # Setup durchführen
./dev-server.sh      # Entwicklungsserver starten
./run-tests.sh       # Alle Tests ausführen
./health-check.sh    # API-Gesundheit prüfen
./format-code.sh     # Code formatieren
```

### Make Targets (Shortcuts)

```bash
make setup    # Equivalent to: ./setup.sh
make dev      # Equivalent to: ./dev-server.sh
make test     # Equivalent to: ./run-tests.sh
make health   # Equivalent to: ./health-check.sh
make fmt      # Equivalent to: ./format-code.sh
```

### Task Runner (Advanced)

```bash
task test-all        # Teste alle SDKs
task build-all       # Baue alle SDKs
task lint            # Linting für alle
task fmt             # Code-Formatierung
task docs-all        # Dokumentation bauen
task clean-all       # Artefakte löschen
task --list-all      # Alle Tasks anzeigen
```

## 📁 Repository-Struktur

```
api/                    → FastAPI Server
sdk-python/             → Python SDK
sdk-go/                 → Go SDK
sdk-typescript/         → TypeScript/JavaScript SDK
sdk-deno/               → Deno SDK
sdk-rust/               → Rust SDK (async/tokio)
sdk-cpp/                → C++ SDK (modern C++17)
terraform-provider/     → Terraform CLI Wrapper
.github/workflows/      → GitHub Actions CI/CD
docs/                   → Sphinx & Doxygen Docs
examples/               → Code examples
tests/                  → Test suites
```

## 💻 SDK Beispiele

### Python

```python
from errorbrain import ErrorBrainClient

client = ErrorBrainClient()
response = client.send_exception(
    exc=my_exception,
    project="my-service",
    tags=["prod"]
)
print(f"Error ID: {response.id}")
```

### Go

```go
client := errorbrain.NewClient("")
response, err := client.SendError(&errorbrain.ErrorReport{
    Language: "go",
    Project:  "my-service",
    Message:  "database failed",
})
```

### TypeScript

```typescript
const client = new ErrorBrainClient();
const response = await client.sendException(error, "my-service", {
  tags: ["prod"],
});
```

### Deno

```typescript
import { ErrorBrainClient } from "./sdk-deno/src/mod.ts";
const client = new ErrorBrainClient();
const response = await client.sendException(error, "my-service");
```

### Rust

```rust
let client = ErrorBrainClient::new("http://localhost:8000".to_string());
let report = ErrorReport::new("rust", "my-service", "Error message")
    .with_tags(vec!["prod".to_string()]);
let response = client.send_error(&report).await?;
```

### C++

```cpp
ErrorBrain::ErrorBrainClient client("http://localhost:8000");
ErrorBrain::ErrorReport report("cpp", "my-service", "Something wrong");
auto response = client.send_error(report);
std::cout << "Error ID: " << response.id() << std::endl;
```

## 🌍 Umgebungsvariablen

Erstelle `.env` in `api/`:

```bash
# LM Studio (lokal, empfohlen für Tests)
ERRORBRAIN_LLM_PROVIDER=openai
ERRORBRAIN_LLM_MODEL=local-model
ERRORBRAIN_LLM_BASE_URL=http://localhost:1234/v1
ERRORBRAIN_LLM_API_KEY=lm-studio

# Obsidian Vault
ERRORBRAIN_OBSIDIAN_ENABLED=true
ERRORBRAIN_OBSIDIAN_PATH=/path/to/vault/errors

# Optional: Cloud LLM
# ERRORBRAIN_LLM_PROVIDER=openai
# ERRORBRAIN_LLM_API_KEY=sk-...
```

## 📋 LM Studio Setup

1. Lade [LM Studio](https://lmstudio.ai/) herunter & installiere
2. Gehe zu "Discover" und lade ein Modell:
   - `meta-llama-3.1-8b-instruct`
   - `mistral-7b-instruct-v0.2`
   - `phi-3-mini-4k-instruct`
3. Gehe zu "Local Server" und starte den Server
4. Server läuft auf: `http://localhost:1234`

Test:

```bash
curl http://localhost:1234/v1/models
```

## 📚 Dokumentation

### Generieren

```bash
# Sphinx + Doxygen
task docs-all

# Oder einzeln
task docs-python     # Sphinx (Python/Go)
task docs-cpp        # Doxygen (C++)
task docs-open       # Im Browser öffnen
```

### Code-Qualität Standards

Alle Komponenten folgen **Google-Style Docstrings**.

**Python:**

```python
def send_error(report: ErrorReport) -> ErrorResponse:
    """Send error report to ErrorBrain.

    Args:
        report: Error report to send.

    Returns:
        Error response with ID and explanation.
    """
```

**Go (Godoc):**

```go
// SendError sends an error report to ErrorBrain.
func (c *Client) SendError(ctx context.Context, report *ErrorReport) (*ErrorResponse, error) {
```

**Rust:**

```rust
/// Send error report to ErrorBrain.
///
/// # Arguments
/// * `report` - Error report to send
pub async fn send_error(&self, report: &ErrorReport) -> Result<ErrorResponse> {
```

**C++:**

```cpp
/// Send error report to ErrorBrain.
/// \param report Error report to send
ErrorResponse send_error(const ErrorReport& report) const;
```

## 🧪 Testing

```bash
# Alle Tests
./run-tests.sh
# oder
make test
# oder
task test-all

# Spezifische SDKs
task test-python
task test-rust
task test-cpp
task test-typescript
task test-deno
```

## 🔗 Links

- **GitHub**: https://github.com/afeldman/errorbrain
- **Issues**: https://github.com/afeldman/errorbrain/issues
- **LM Studio**: https://lmstudio.ai/
- **Obsidian**: https://obsidian.md/

## 📝 License

MIT - Siehe [LICENSE](./LICENSE)
