# ErrorBrain Deno SDK

Deno-Client für [ErrorBrain](https://github.com/errorbrain/errorbrain) - AI-powered debugging memory that captures, analyzes, and documents errors automatically.

## 🚀 Features

- ✅ **Native Deno support** mit TypeScript out-of-the-box
- ✅ **Fetch API basiert** - nutzt Denos eingebaute fetch-API
- ✅ **Promise-basierte API** mit async/await
- ✅ **Error & Exception handling** - automatische Stack-Trace-Extraktion
- ✅ **Rich metadata** - attach context zu jedem Error
- ✅ **Timeout-Unterstützung** - AbortController für Request-Timeouts
- ✅ **Permissions-aware** - benötigt nur `--allow-env` und `--allow-net`
- ✅ **Well-tested** - Umfassende Tests mit `Deno.test`

## 📦 Installation

### Lokal verwenden

```typescript
import {
  ErrorBrainClient,
  type ErrorReport,
  type ErrorResponse,
} from "./sdk-deno/src/mod.ts";
```

### Via deno.json importieren

```json
{
  "imports": {
    "errorbrain": "file:///path/to/sdk-deno/src/mod.ts"
  }
}
```

```typescript
import { ErrorBrainClient } from "errorbrain";
```

### Via GitHub

```typescript
import { ErrorBrainClient } from "https://raw.githubusercontent.com/errorbrain/errorbrain/main/sdk-deno/src/mod.ts";
```

## 🔧 Quick Start

```typescript
import { ErrorBrainClient } from "./sdk-deno/src/mod.ts";

const client = new ErrorBrainClient({
  baseURL: "http://localhost:8000",
});

// Send an error
const response = await client.sendError({
  language: "typescript",
  project: "my-service",
  message: "Database connection failed",
  tags: ["prod", "database"],
  metadata: { user_id: "12345" },
});

console.log(response.explanation); // AI-generated explanation
```

## 📖 Usage Examples

### Basic Error Reporting

```typescript
import { ErrorBrainClient } from "./sdk-deno/src/mod.ts";

const client = new ErrorBrainClient();

const response = await client.sendError({
  language: "typescript",
  project: "billing-service",
  message: "Payment processing failed",
  traceback:
    "Error: Payment gateway timeout\n  at processPayment (payment.ts:42:10)",
  tags: ["payment", "critical", "prod"],
  metadata: {
    payment_id: "pay_123",
    amount: 99.99,
    currency: "EUR",
  },
});

console.log(`Error ID: ${response.id}`);
console.log(`AI Explanation: ${response.explanation}`);
if (response.saved_path) {
  console.log(`Saved to Obsidian: ${response.saved_path}`);
}
```

### Exception Handling

```typescript
try {
  const result = await riskyOperation();
} catch (error) {
  const response = await client.sendException(error as Error, "user-service", {
    tags: ["auth", "prod"],
    metadata: { user_id: "12345" },
  });

  console.log(`Logged error: ${response.id}`);
}
```

### Top-Level Await

Deno unterstützt nativ Top-Level Await:

```typescript
import { ErrorBrainClient } from "./sdk-deno/src/mod.ts";

const client = new ErrorBrainClient();

// Direkt ohne wrapper function
const health = await client.healthCheck();
console.log(`API Status: ${health.status}`);
```

### Deno-spezifische Patterns

```typescript
import { ErrorBrainClient } from "./sdk-deno/src/mod.ts";

const client = new ErrorBrainClient();

// Mit Deno-Umgebungsvariablen
console.log(`Deno Version: ${Deno.version.deno}`);
console.log(`Runtime: ${Deno.mainModule}`);

// Mit Deno-Permissions
const response = await client.sendError({
  language: "typescript",
  project: "deno-runtime",
  message: "Deno feature demonstration",
  metadata: {
    deno_version: Deno.version.deno,
  },
});
```

### Configuration with Environment Variables

```bash
# .env oder System-Umgebungsvariablen
export ERRORBRAIN_API_URL=http://localhost:8000

# Verwendung im Code
const client = new ErrorBrainClient(); // Verwendet ERRORBRAIN_API_URL automatisch
```

## 🔌 API Reference

### `ErrorBrainClient`

Main client class for interacting with the ErrorBrain API.

#### Constructor

```typescript
new ErrorBrainClient(config?: ClientConfig)
```

**Parameters:**

- `config.baseURL` (optional): Base URL of the ErrorBrain API. Defaults to `ERRORBRAIN_API_URL` env var or `http://localhost:8000`
- `config.timeout` (optional): Request timeout in milliseconds. Default: `30000`
- `config.headers` (optional): Additional headers to send with requests

#### Methods

##### `healthCheck()`

Check if the API is healthy.

```typescript
const health = await client.healthCheck();
console.log(health.status); // "healthy"
console.log(health.llm_configured); // true
console.log(health.vault_configured); // true
```

**Returns:** `Promise<HealthResponse>`

##### `sendError(report)`

Send an error report for AI analysis.

```typescript
const response = await client.sendError({
  language: "typescript",
  project: "my-service",
  message: "Error message",
  traceback: "Stack trace...",
  tags: ["tag1", "tag2"],
  metadata: { key: "value" },
  store_in_vault: true, // default: true
});
```

**Parameters:**

- `report.language` (required): Programming language
- `report.project` (required): Project/service name
- `report.message` (required): Error message
- `report.traceback` (optional): Stack trace
- `report.tags` (optional): Array of tags
- `report.metadata` (optional): Additional context
- `report.store_in_vault` (optional): Save to Obsidian vault (default: true)

**Returns:** `Promise<ErrorResponse>`

##### `sendException(error, project, options?)`

Send a JavaScript/TypeScript Error object.

```typescript
try {
  throw new Error("Something went wrong");
} catch (error) {
  const response = await client.sendException(error as Error, "my-project", {
    language: "typescript", // default: 'typescript'
    tags: ["error-type"],
    metadata: { context: "info" },
  });
}
```

**Parameters:**

- `error` (required): Error object
- `project` (required): Project/service name
- `options.language` (optional): Language (default: 'typescript')
- `options.tags` (optional): Array of tags
- `options.metadata` (optional): Additional context
- `options.store_in_vault` (optional): Save to vault (default: true)

**Returns:** `Promise<ErrorResponse>`

### Types

#### `ErrorReport`

```typescript
interface ErrorReport {
  language: string;
  project: string;
  message: string;
  traceback?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
  store_in_vault?: boolean;
}
```

#### `ErrorResponse`

```typescript
interface ErrorResponse {
  id: string;
  project: string;
  language: string;
  tags: string[];
  created_at: string;
  explanation: string;
  saved_path?: string;
}
```

#### `HealthResponse`

```typescript
interface HealthResponse {
  status: string;
  llm_configured: boolean;
  vault_configured: boolean;
  vault_path?: string;
}
```

## 🧪 Development

### Running Tests

```bash
# Run all tests
deno test --allow-env --allow-net src/

# Run specific test file
deno test --allow-env --allow-net src/client.test.ts

# Run with coverage
deno test --allow-env --allow-net --coverage=coverage/ src/
```

### Code Quality

```bash
# Format
deno fmt src/

# Lint
deno lint src/

# Type check
deno check src/mod.ts
```

### Running Examples

```bash
# Basic example
deno run --allow-env --allow-net examples/deno_example.ts

# With custom API URL
ERRORBRAIN_API_URL=http://custom:8000 deno run --allow-env --allow-net examples/deno_example.ts
```

## 🔐 Permissions

Das SDK benötigt folgende Deno-Permissions:

```bash
--allow-env              # Für ERRORBRAIN_API_URL Umgebungsvariable
--allow-net              # Für HTTP-Requests zur API
```

Beispiel:

```bash
deno run --allow-env --allow-net my-script.ts
```

## 📝 License

MIT

## 🔗 Links

- [ErrorBrain Main Repository](https://github.com/errorbrain/errorbrain)
- [Deno Documentation](https://docs.deno.com/)
- [API Server](https://github.com/errorbrain/errorbrain/tree/main/api)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
