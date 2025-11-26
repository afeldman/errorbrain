# ErrorBrain - Migration von Makefile zu Taskfile

Das Projekt verwendet jetzt **Taskfile** (https://taskfile.dev) statt Makefile.

## Installation von Task

### macOS

```bash
brew install go-task
```

### Linux

```bash
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
```

### Go

```bash
go install github.com/go-task/task/v3/cmd/task@latest
```

## Verfügbare Commands

```bash
task --list  # Alle verfügbaren Tasks anzeigen
```

### Hauptbefehle

| Task           | Beschreibung                   |
| -------------- | ------------------------------ |
| `task install` | Alle Dependencies installieren |
| `task dev`     | API Development Server starten |
| `task test`    | Alle Tests ausführen           |
| `task lint`    | Alle Linter ausführen          |
| `task format`  | Code formatieren               |
| `task check`   | Format + Lint + Test           |
| `task docs`    | Dokumentation bauen            |
| `task clean`   | Build-Artefakte löschen        |

### Spezifische Tasks

#### Installation

- `task install-api` - Nur API Dependencies
- `task install-sdk-python` - Nur Python SDK Dependencies
- `task install-sdk-go` - Nur Go SDK Dependencies

#### Tests

- `task test-api` - Nur API Tests
- `task test-sdk-go` - Nur Go SDK Tests
- `task test-coverage` - Tests mit Coverage Report

#### Linting

- `task lint-api` - Nur API linting
- `task lint-sdk-python` - Nur Python SDK linting
- `task lint-sdk-go` - Nur Go SDK linting

#### Formatierung

- `task format-python` - Nur Python Code formatieren
- `task format-go` - Nur Go Code formatieren

#### Dokumentation

- `task docs-api` - API Sphinx Docs bauen
- `task docs-sdk-python` - Python SDK Sphinx Docs bauen
- `task docs-sdk-go` - godoc Server starten
- `task docs-open` - Dokumentation im Browser öffnen

#### Beispiele

- `task examples-python` - Python Beispiele ausführen
- `task examples-go` - Go Beispiele ausführen
- `task examples-terraform` - Terraform Beispiel anzeigen

#### Sonstiges

- `task git-hooks` - Pre-commit Hooks installieren
- `task dev-watch` - API mit Auto-Reload starten
- `task build-terraform` - Terraform Provider bauen

## Vorteile von Taskfile vs Makefile

1. **Plattformübergreifend**: Funktioniert auf Windows, macOS, Linux ohne Shell-spezifische Syntax
2. **YAML statt Makefile-Syntax**: Einfacher lesbar und wartbar
3. **Variablen und Templates**: `{{.API_DIR}}` statt `$(API_DIR)`
4. **Task-Dependencies**: Automatische Ausführung abhängiger Tasks
5. **Bessere Dokumentation**: `desc` Felder für jede Task
6. **Farbige Ausgabe**: Bessere CLI-Erfahrung
7. **Watch-Mode**: Built-in File-Watching für Auto-Reload

## Migration von make zu task

| Makefile               | Taskfile         |
| ---------------------- | ---------------- |
| `make install`         | `task install`   |
| `make test`            | `task test`      |
| `make lint`            | `task lint`      |
| `make format`          | `task format`    |
| `make dev-api`         | `task dev`       |
| `make check-all`       | `task check`     |
| `make docs`            | `task docs`      |
| `make clean`           | `task clean`     |
| `make setup-git-hooks` | `task git-hooks` |

## Beispiele

### Gesamtes Projekt prüfen

```bash
task check
```

### API entwickeln

```bash
task dev  # Server starten
# In anderem Terminal:
task test-api  # Tests ausführen
```

### Dokumentation bauen und öffnen

```bash
task docs
task docs-open
```

### Beispiele ausführen

```bash
# Python Beispiel
task examples-python

# Go Beispiel
task examples-go
```

## Makefile bleibt verfügbar

Das alte `Makefile` bleibt im Projekt, falls jemand es noch verwendet. Langfristig wird empfohlen, auf `task` umzusteigen.
