# ErrorBrain Helm Chart

This Helm chart deploys ErrorBrain on Kubernetes.

## Features

- Deploys the ErrorBrain server (core + API)
- Configurable environment variables for reasoning mode and LLM
- Optional persistent storage for Obsidian export
- Exposes service on port 8080

## Usage

### 1. Add and configure values

Edit `values.yaml` to set image, environment, and persistence options as needed.

### 2. Install the chart

```bash
helm install errorbrain ./deploy/helm/errorbrain
```

### 3. Upgrade

```bash
helm upgrade errorbrain ./deploy/helm/errorbrain -f values.yaml
```

### 4. Uninstall

```bash
helm uninstall errorbrain
```

## Example: Enable persistent storage

In `values.yaml`:

```yaml
persistence:
  enabled: true
  size: 2Gi
  mountPath: /data/obsidian
```

## Environment variables

Set LLM or reasoning mode via `values.yaml`:

```yaml
env:
  ERRORBRAIN_REASONING_MODE: llm
  LLM_HOST: "http://llm-service:1234/v1"
  LLM_MODEL: "mistralai/ministral-3-3b"
  LLM_KEY: "not-required-for-local"
```

## License

This chart is licensed under the Apache 2.0 License, see [LICENSE](../../../LICENSE).
