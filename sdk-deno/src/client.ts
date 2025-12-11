/**
 * ErrorBrain Deno SDK - Client for error tracking API.
 *
 * This module provides a client for communicating with the ErrorBrain API
 * to submit errors for AI analysis and storage in Obsidian vault.
 * Uses Deno's built-in fetch API for HTTP requests.
 *
 * @module
 */

/**
 * Error report model matching the API schema.
 */
export interface ErrorReport {
  /** Programming language (e.g., typescript, javascript, go, python) */
  language: string;
  /** Project or service name */
  project: string;
  /** Error message or exception message */
  message: string;
  /** Optional stack trace */
  traceback?: string;
  /** List of tags for categorization (e.g., ['prod', 'cron']) */
  tags?: string[];
  /** Additional metadata dictionary */
  metadata?: Record<string, unknown>;
  /** Whether to save to Obsidian vault (default: true) */
  store_in_vault?: boolean;
}

/**
 * Response from the ErrorBrain API.
 */
export interface ErrorResponse {
  /** Unique error identifier */
  id: string;
  /** Project name */
  project: string;
  /** Programming language */
  language: string;
  /** List of tags */
  tags: string[];
  /** Timestamp of error creation */
  created_at: string;
  /** AI-generated explanation */
  explanation: string;
  /** Path where error was saved (if applicable) */
  saved_path?: string;
}

/**
 * Health check response from the API.
 */
export interface HealthResponse {
  status: string;
  llm_configured: boolean;
  vault_configured: boolean;
  vault_path?: string;
  [key: string]: unknown;
}

/**
 * Configuration options for the ErrorBrain client.
 */
export interface ClientConfig {
  /** Base URL of the ErrorBrain API */
  baseURL?: string;
  /** Request timeout in milliseconds (default: 30000) */
  timeout?: number;
  /** Additional headers to send with requests */
  headers?: Record<string, string>;
}

/**
 * Client for communicating with the ErrorBrain API.
 *
 * Uses Deno's built-in fetch API with AbortController for timeout handling.
 *
 * @example
 * ```typescript
 * const client = new ErrorBrainClient({ baseURL: 'http://localhost:8000' });
 *
 * const response = await client.sendError({
 *   language: 'typescript',
 *   project: 'my-service',
 *   message: 'Connection timeout',
 *   tags: ['prod', 'database'],
 * });
 *
 * console.log(response.explanation);
 * ```
 */
export class ErrorBrainClient {
  private baseURL: string;
  private timeout: number;
  private headers: Record<string, string>;

  /**
   * Initialize the ErrorBrain client.
   *
   * @param config - Configuration options. If not provided, uses ERRORBRAIN_API_URL
   *                 environment variable or defaults to http://localhost:8000
   */
  constructor(config?: ClientConfig) {
    this.baseURL = (
      config?.baseURL ||
      Deno.env.get("ERRORBRAIN_API_URL") ||
      "http://localhost:8000"
    ).replace(/\/$/, "");

    this.timeout = config?.timeout || 30000;
    this.headers = {
      "Content-Type": "application/json",
      ...config?.headers,
    };
  }

  /**
   * Make a fetch request with timeout support.
   *
   * @param url - The URL to fetch
   * @param options - Fetch options
   * @returns Promise resolving to the Response
   * @throws Error if the request times out or fails
   */
  private async fetchWithTimeout(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof TypeError && error.message.includes("abort")) {
        throw new Error(`Request timeout after ${this.timeout}ms`);
      }
      throw error;
    }
  }

  /**
   * Check if the API is healthy.
   *
   * @returns Health check response with status and configuration
   * @throws Error if the API is not reachable or returns an error
   *
   * @example
   * ```typescript
   * const health = await client.healthCheck();
   * console.log(`API Status: ${health.status}`);
   * console.log(`LLM Configured: ${health.llm_configured}`);
   * ```
   */
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await this.fetchWithTimeout(`${this.baseURL}/healthz`, {
        method: "GET",
        headers: this.headers,
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Health check returned ${response.status}: ${text}`);
      }

      return (await response.json()) as HealthResponse;
    } catch (error) {
      this.handleError(error, "Health check failed");
    }
  }

  /**
   * Send an error to ErrorBrain for analysis and storage.
   *
   * @param report - Error report to send
   * @returns ErrorResponse with explanation and saved path
   * @throws Error if the API request fails
   *
   * @example
   * ```typescript
   * const response = await client.sendError({
   *   language: 'typescript',
   *   project: 'billing-service',
   *   message: 'Database connection failed',
   *   traceback: 'Error: connection timeout\n  at db.connect()',
   *   tags: ['prod', 'database'],
   *   metadata: { user_id: '12345', request_id: 'abc-def' },
   * });
   *
   * console.log(`Error ID: ${response.id}`);
   * console.log(`Explanation: ${response.explanation}`);
   * ```
   */
  async sendError(report: ErrorReport): Promise<ErrorResponse> {
    try {
      const payload = {
        ...report,
        store_in_vault: report.store_in_vault ?? true,
        tags: report.tags || [],
      };

      const response = await this.fetchWithTimeout(
        `${this.baseURL}/v1/errors`,
        {
          method: "POST",
          headers: this.headers,
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`API returned ${response.status}: ${text}`);
      }

      return (await response.json()) as ErrorResponse;
    } catch (error) {
      this.handleError(error, "Failed to send error");
    }
  }

  /**
   * Send a JavaScript/TypeScript Error object to ErrorBrain.
   *
   * Automatically extracts message and stack trace from the Error object.
   *
   * @param error - The Error object
   * @param project - Project or service name
   * @param options - Additional options (language, tags, metadata, store_in_vault)
   * @returns ErrorResponse with explanation and saved path
   * @throws Error if the API request fails
   *
   * @example
   * ```typescript
   * try {
   *   throw new Error('Connection timeout');
   * } catch (error) {
   *   const response = await client.sendException(error, 'my-service', {
   *     tags: ['prod', 'critical'],
   *     metadata: { user_id: '12345' },
   *   });
   *   console.log(response.explanation);
   * }
   * ```
   */
  async sendException(
    error: Error,
    project: string,
    options?: {
      language?: string;
      tags?: string[];
      metadata?: Record<string, unknown>;
      store_in_vault?: boolean;
    }
  ): Promise<ErrorResponse> {
    const report: ErrorReport = {
      language: options?.language || "typescript",
      project,
      message: error.message,
      traceback: error.stack,
      tags: options?.tags,
      metadata: options?.metadata,
      store_in_vault: options?.store_in_vault,
    };

    return this.sendError(report);
  }

  /**
   * Handle errors from API requests.
   *
   * @param error - The error object
   * @param message - Custom error message
   * @throws Error Always throws with detailed error information
   */
  private handleError(error: unknown, message: string): never {
    if (error instanceof Error) {
      throw new Error(`${message}: ${error.message}`);
    }
    throw new Error(`${message}: ${String(error)}`);
  }
}

/**
 * Create a new ErrorBrain client instance.
 *
 * @param config - Configuration options
 * @returns A new ErrorBrainClient instance
 *
 * @example
 * ```typescript
 * const client = createClient({ baseURL: 'http://localhost:8000' });
 * ```
 */
export function createClient(config?: ClientConfig): ErrorBrainClient {
  return new ErrorBrainClient(config);
}
