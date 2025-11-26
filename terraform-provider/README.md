# ErrorBrain Terraform Integration

Integration für Terraform, um Fehler beim `apply` automatisch zu erfassen und in ErrorBrain zu speichern.

## Variante 1: CLI Wrapper (Empfohlen)

Der CLI Wrapper fängt Terraform-Fehler ab und sendet sie an ErrorBrain.

### Installation

```bash
cd terraform-provider
go build -o terraform-errorbrain
sudo mv terraform-errorbrain /usr/local/bin/
```

### Verwendung

Anstatt `terraform apply` auszuführen:

```bash
export ERRORBRAIN_PROJECT="my-infrastructure"
export ERRORBRAIN_API_URL="http://localhost:8000"

terraform-errorbrain wrap apply
terraform-errorbrain wrap plan
terraform-errorbrain wrap destroy
```

### Alias (Optional)

Füge zu deiner `.zshrc` hinzu:

```bash
alias tf='terraform-errorbrain wrap'
```

Dann kannst du einfach verwenden:

```bash
tf apply
tf plan
```

## Variante 2: Terraform Provider (Experimentell)

Ein Terraform Provider, der Fehler während der Ausführung meldet.

### Installation

```bash
cd terraform-provider
go build -o terraform-provider-errorbrain
mkdir -p ~/.terraform.d/plugins/local/afeldman/errorbrain/0.1.0/darwin_arm64
mv terraform-provider-errorbrain ~/.terraform.d/plugins/local/afeldman/errorbrain/0.1.0/darwin_arm64/
```

### Verwendung in Terraform

```hcl
terraform {
  required_providers {
    errorbrain = {
      source  = "local/afeldman/errorbrain"
      version = "0.1.0"
    }
  }
}

provider "errorbrain" {
  api_url = "http://localhost:8000"
  project = "my-infrastructure"
  enabled = true
}
```

## Funktionsweise

Wenn ein `terraform apply` fehlschlägt:

1. Der Fehler wird erfasst (inkl. stderr)
2. An die ErrorBrain API gesendet
3. Von der KI analysiert
4. Als Markdown in deinem Obsidian Vault gespeichert

Die Fehlermeldungen enthalten:

- Operation (apply, plan, destroy)
- Resource (wenn identifizierbar)
- Vollständiger stderr output
- Metadata über das Terraform-Projekt

## Umgebungsvariablen

- `ERRORBRAIN_API_URL` - ErrorBrain API URL (default: `http://localhost:8000`)
- `ERRORBRAIN_PROJECT` - Projektname für Fehler-Tracking (default: `terraform-project`)
