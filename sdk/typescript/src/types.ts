/**
 * Type definitions generated from spec/v1/error_event.schema.json
 * These are the canonical types that all SDKs must follow.
 *
 * @packageDocumentation
 */

/**
 * Source/Application metadata for error reporting.
 * This identifies where the error originated.
 */
export interface Source {
  /** Programming language or system (e.g., 'typescript', 'python', 'go') */
  language: 'python' | 'go' | 'typescript' | 'javascript' | 'deno' | 'rust' | 'cpp' | 'terraform' | 'other';
  /** Application or service name (e.g., 'billing-service') */
  name: string;
  /** Application version (semver recommended) */
  version?: string;
  /** Deployment environment */
  environment?: 'local' | 'development' | 'staging' | 'production';
  /** Hostname, container ID, or pod name */
  hostname?: string;
  /** Arbitrary tags for filtering and grouping */
  tags?: string[];
}

/**
 * Evidence item providing additional context for errors.
 * Examples: log lines, metrics, HTTP requests/responses, database queries.
 */
export interface Evidence {
  /** Type of evidence */
  type: 'log_line' | 'metric' | 'http_request' | 'http_response' | 'database_query' | 'event' | 'custom';
  /** Evidence payload (structure depends on type) */
  data: Record<string, unknown>;
  /** ISO 8601 timestamp when evidence was collected */
  timestamp?: string;
}

/**
 * Canonical error event format for ErrorBrain.
 * This is the standardized format that all SDKs must produce,
 * regardless of the language they're written in.
 *
 * @example
 * ```typescript
 * const errorEvent: ErrorEvent = {
 *   id: '550e8400-e29b-41d4-a716-446655440000',
 *   timestamp: '2026-01-09T10:30:00Z',
 *   source: {
 *     language: 'typescript',
 *     name: 'my-service',
 *     environment: 'production',
 *   },
 *   message: 'Database connection failed',
 *   stack_trace: 'Error: connection timeout\n  at db.connect()',
 *   error_type: 'TimeoutError',
 *   severity: 'error',
 *   metadata: { user_id: '12345' },
 *   evidence: [
 *     {
 *       type: 'log_line',
 *       data: { level: 'error', message: 'DB timeout' },
 *       timestamp: '2026-01-09T10:30:00Z',
 *     },
 *   ],
 * };
 * ```
 */
export interface ErrorEvent {
  /** Unique identifier for this error event (UUID) */
  id: string;
  /** ISO 8601 timestamp when error occurred */
  timestamp: string;
  /** Source of the error (application, service, system) */
  source: Source;
  /** Error message or exception message */
  message: string;
  /** Full stack trace (if available) */
  stack_trace?: string;
  /** Error type or exception class (e.g., ValueError, NullPointerException) */
  error_type?: string;
  /** Error severity level */
  severity?: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  /** Additional context (environment, user, request, etc.) */
  metadata?: Record<string, unknown>;
  /** Additional evidence items (logs, metrics, related events) */
  evidence?: Evidence[];
}
