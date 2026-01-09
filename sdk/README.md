# ErrorBrain SDKs

SDKs für ErrorBrain in verschiedenen Sprachen und Runtimes.

Alle SDKs folgen der kanonischen **spec/** (Source of Truth) und implementieren denselben Vertrag, unabhängig von der Sprache.

## 📦 Available SDKs

### TypeScript / JavaScript

```bash
cd sdk/typescript
npm install
npm test
```

**Features:**

- ✅ Full TypeScript support
- ✅ Strongly typed from spec/error_event.schema.json
- ✅ Works with JavaScript (Node.js, browsers)
- ✅ Promise-based async/await API

[SDK/TypeScript README](typescript/README.md)

### Deno

```bash
cd sdk/deno
deno test --allow-env --allow-net src/
```

**Features:**

- ✅ Native Deno support (no node_modules)
- ✅ Deno's built-in fetch + AbortController
- ✅ TypeScript out-of-the-box
- ✅ Minimal permissions (`--allow-env`, `--allow-net`)

[SDK/Deno README](deno/README.md)

### Go

```bash
cd sdk/go
go test ./...
```

**Features:**

- ✅ Standard library only (no external dependencies)
- ✅ Strongly typed from spec/error_event.schema.json
- ✅ UUID v4 & ISO 8601 timestamps
- ✅ Idiomatic Go error handling

[SDK/Go README](go/README.md)

### Python

```bash
cd sdk/python
pip install -e .
pytest tests/
```

**Features:**

- ✅ Async support with asyncio
- ✅ Pydantic models from spec/
- ✅ Full type hints
- ✅ Easy integration with FastAPI, Django, etc.

[SDK/Python README](python/README.md)

### Rust

```bash
cd sdk/rust
cargo test
```

**Features:**

- ✅ Tokio async runtime
- ✅ serde + serde_json for JSON
- ✅ Type-safe error handling
- ✅ Zero-copy where possible

[SDK/Rust README](rust/README.md)

### C++

```bash
cd sdk/cpp
cmake . && make test
```

**Features:**

- ✅ Modern C++17/20
- ✅ Header-only option available
- ✅ nlohmann/json integration
- ✅ Conan package manager support

[SDK/C++ README](cpp/README.md)

## 🔗 Canonical Contract

All SDKs must conform to **spec/error_event.schema.json**:

```typescript
interface ErrorEvent {
  id: string;              // UUID
  timestamp: string;       // ISO 8601
  source: Source;          // Language, service, environment
  message: string;         // Error message
  stack_trace?: string;    // Stack trace
  error_type?: string;     // Exception class
  severity?: string;       // debug, info, warning, error, critical
  metadata?: object;       // Custom context
  evidence?: Evidence[];   // Logs, metrics, HTTP, etc.
}
```

## ✨ Key Principles

1. **Language-specific:** Each SDK is idiomatic to its language (use Promises in JS, async/await in Rust, etc.)
2. **Spec-driven:** All SDKs generate types from spec/ JSON Schemas
3. **No circular deps:** SDKs never import server code
4. **Minimal:** Focus on error capture, not processing (processing is server's job)
5. **Typed:** Strong types, compile-time safety where possible

## 🚀 Quick Start

### TypeScript

```typescript
import { ErrorBrainClient } from '@errorbrain/sdk-typescript';

const client = new ErrorBrainClient();
const response = await client.sendError({
  language: 'typescript',
  project: 'my-service',
  message: 'Database failed',
  tags: ['prod', 'database'],
  metadata: { user_id: '123' },
});
```

### Go

```go
import "github.com/afeldman/errorbrain/sdk/go"

client := errorbrain.NewClient()
response, err := client.SendError(&errorbrain.ErrorReport{
  Language: "go",
  Project:  "my-service",
  Message:  "database failed",
  Tags:     []string{"prod"},
  Metadata: map[string]interface{}{"user_id": "123"},
})
```

## 📋 Development Workflow

When adding a new SDK:

1. **Generate types** from spec/ schemas
2. **Implement client** conforming to spec/error_event.schema.json
3. **Add tests** (e.g., Jest for TS, Deno.test for Deno)
4. **Document** with examples for common patterns
5. **No server imports** – SDKs are standalone

## 🔄 Versioning

- **spec/**: Major version increments when schema breaks
- **sdk/\***: Follow spec version, increment minor for SDK-only features
- **server/**: Flexible internal versioning, strict spec adherence

Example:

```
spec          v1.2.0
sdk-typescript v1.2.1
sdk-deno      v1.2.0
server        v0.9.5
```
