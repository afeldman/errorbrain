# ErrorBrain – AI-powered Debugging Memory

A persistent, searchable Second Brain for errors, stacktraces & LLM explanations.

## 🚀 Overview

ErrorBrain captures runtime errors from your applications, enriches them with an LLM-generated explanation, and stores everything automatically in your Engineering Second Brain (Markdown vaults, Confluence, Notion, Git, etc.).

It turns every failure into permanent, documented, and searchable engineering knowledge.

## 🧠 Features
### ✓ Capture errors from any language

- Python SDK
- Go SDK
- Terraform wrapper
- Bash wrapper (planned)

### ✓ Auto-explain errors using your LLM

Works with:

- anyllm
- OpenAI-compatible local endpoints
- OpenAI, Anthropic, Azure

### ✓ Store everything automatically in a Second Brain

- Obsidian markdown vault
- Local markdown folder
- Git knowledge repo

### ✓ Build reusable engineering memory

- never fix the same error twice
- onboard devs faster
- centralized incident knowledge

## 🏗️ Architecture
```scss
Applications (Python, Go, Terraform)
        ↓
ErrorBrain SDK (send error + trace + metadata)
        ↓
ErrorBrain API (REST)
        ↓
- LLM provider (explain)
- Storage backend (markdown, confluence, etc.)
        ↓
Engineering Second Brain
```

## 📦 Repository Layout
```java
api/         → main API (Go)
sdk-python/  → Python SDK (uv-managed)
sdk-go/      → Go SDK
examples/    → usage samples
docker-compose.yml
```

## 🧪 Quick Start
1. Start the ErrorBrain API
   ```bash
   docker-compose up --build
   ````
2. Send an error via Python SDK
   ```bash
   from llmhelper import send_to_errorbrain

   try:
      1/0
   except Exception as e:
      send_to_errorbrain(e, project="billing-service")
   ```

Output is stored as ```.md``` files in ```data/errors/```.

## 🧩 Roadmap

- Python SDK v1
- Go SDK v1
- Terraform Wrapper CLI
- Web Dashboard
- Embedding-based search
- GitOps vault sync
