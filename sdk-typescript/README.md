# ErrorBrain TypeScript/JavaScript SDK

TypeScript/JavaScript client for [ErrorBrain](https://github.com/errorbrain/errorbrain) - AI-powered debugging memory that captures, analyzes, and documents errors automatically.

## 🚀 Features

- ✅ **Full TypeScript support** with comprehensive type definitions
- ✅ **Works with JavaScript** (Node.js and modern browsers)
- ✅ **Promise-based API** using async/await
- ✅ **Error & Exception handling** - automatic stack trace extraction
- ✅ **Rich metadata** - attach context to every error
- ✅ **Configurable** - environment variables or direct config
- ✅ **Well-tested** - comprehensive test suite with Jest

## 📦 Installation

```bash
# Using npm
npm install @errorbrain/sdk

# Using yarn
yarn add @errorbrain/sdk

# Using pnpm
pnpm add @errorbrain/sdk
```

## 🔧 Quick Start

### TypeScript

```typescript
import { ErrorBrainClient } from '@errorbrain/sdk';

const client = new ErrorBrainClient({
  baseURL: 'http://localhost:8000',
});

// Send an error
const response = await client.sendError({
  language: 'typescript',
  project: 'my-service',
  message: 'Database connection failed',
  tags: ['prod', 'database'],
  metadata: { user_id: '12345' },
});

console.log(response.explanation); // AI-generated explanation
```

### JavaScript

```javascript
const { ErrorBrainClient } = require('@errorbrain/sdk');

const client = new ErrorBrainClient({
  baseURL: 'http://localhost:8000',
});

// Send an error
client.sendError({
  language: 'javascript',
  project: 'my-service',
  message: 'Connection timeout',
  tags: ['prod'],
}).then(response => {
  console.log(response.explanation);
});
```

## 📖 Usage Examples

### Basic Error Reporting

```typescript
import { ErrorBrainClient } from '@errorbrain/sdk';

const client = new ErrorBrainClient();

const response = await client.sendError({
  language: 'typescript',
  project: 'billing-service',
  message: 'Payment processing failed',
  traceback: 'Error: Payment gateway timeout\n  at processPayment (payment.ts:42:10)',
  tags: ['payment', 'critical', 'prod'],
  metadata: {
    payment_id: 'pay_123',
    amount: 99.99,
    currency: 'EUR',
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
  const response = await client.sendException(
    error as Error,
    'user-service',
    {
      tags: ['auth', 'prod'],
      metadata: { user_id: '12345' },
    }
  );
  
  console.log(`Logged error: ${response.id}`);
}
```

### Express.js Error Middleware

```typescript
import express from 'express';
import { ErrorBrainClient } from '@errorbrain/sdk';

const app = express();
const errorBrain = new ErrorBrainClient();

// Error middleware
app.use(async (err, req, res, next) => {
  // Log error to ErrorBrain
  await errorBrain.sendException(err, 'express-api', {
    tags: ['express', req.method.toLowerCase()],
    metadata: {
      method: req.method,
      path: req.path,
      ip: req.ip,
    },
  });
  
  res.status(500).json({ error: 'Internal server error' });
});
```

### Promise Rejection Handling

```typescript
process.on('unhandledRejection', async (reason, promise) => {
  await client.sendError({
    language: 'typescript',
    project: 'background-jobs',
    message: `Unhandled rejection: ${reason}`,
    tags: ['unhandled', 'critical'],
    metadata: {
      promise: String(promise),
      timestamp: new Date().toISOString(),
    },
  });
});
```

### Configuration with Environment Variables

```typescript
// Set in .env file:
// ERRORBRAIN_API_URL=http://localhost:8000

const client = new ErrorBrainClient(); // Uses ERRORBRAIN_API_URL automatically
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
  language: 'typescript',
  project: 'my-service',
  message: 'Error message',
  traceback: 'Stack trace...',
  tags: ['tag1', 'tag2'],
  metadata: { key: 'value' },
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
  throw new Error('Something went wrong');
} catch (error) {
  const response = await client.sendException(
    error as Error,
    'my-project',
    {
      language: 'typescript', // default: 'typescript'
      tags: ['error-type'],
      metadata: { context: 'info' },
    }
  );
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

```bash
# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Lint
npm run lint

# Format
npm run format
```

## 📝 License

MIT

## 🔗 Links

- [ErrorBrain Main Repository](https://github.com/errorbrain/errorbrain)
- [Documentation](https://github.com/errorbrain/errorbrain/tree/main/docs)
- [API Server](https://github.com/errorbrain/errorbrain/tree/main/api)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
