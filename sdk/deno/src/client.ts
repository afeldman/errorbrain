/**
 * ErrorBrain Deno SDK - Client for error tracking API.
 *
 * This module provides a client for communicating with the ErrorBrain API
 * to submit errors for AI analysis and storage in Obsidian vault.
 * Uses Deno's built-in fetch API for HTTP requests.
 *
 * Strictly follows the spec defined in spec/v1/error_event.schema.json.
 * SDKs in other languages implement the same contract.
 *
 * @module
 */

import { ErrorEvent, Source } from './types.ts';

/**
 * Simple error report - gets converted to ErrorEvent by client.
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
  /** Error type/class name */
  error_type?: string;
  /** Error severity */
  severity?: 'debug' | 'info' | 'warning' | 'error' | 'critical';
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
      Deno.env.get('ERRORBRAIN_API_URL') ||
      'http://localhost:8000'
    ).replace(/\/$/, '');

    this.timeout = config?.timeout || 30000;
    this.headers = {
      'Content-Type': 'application/json',
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
      if (error instanceof TypeError && error.message.includes('abort')) {
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
        method: 'GET',
        headers: this.headers,
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Health check returned ${response.status}: ${text}`);
      }

      return (await response.json()) as HealthResponse;
    } catch (error) {
      this.handleError(error, 'Health check failed');
    }
  }

  /**
   * Send an error to ErrorBrain for analysis and storage.
   *
   * Converts ErrorReport to ErrorEvent conforming to spec/error_event.schema.json
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
      const errorEvent = this.buildErrorEvent(report);
      const payload = {
        event: errorEvent,
        store_in_vault: report.store_in_vault ?? true,
      };

      const response = await this.fetchWithTimeout(
        `${this.baseURL}/v1/errors`,
        {
          method: 'POST',
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
      this.handleError(error, 'Failed to send error');
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
      language: options?.language || 'deno',
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
   * Build a canonical ErrorEvent from a simplified ErrorReport.
   * This is where we construct the spec-compliant event.
   *
   * @param report - Simple error report
   * @returns ErrorEvent conforming to spec/error_event.schema.json
   */
  private buildErrorEvent(report: ErrorReport): ErrorEvent {
    const id = this.generateUUID();
    const timestamp = new Date().toISOString();

    const source: Source = {
      language: report.language as any,
      name: report.project,
      tags: report.tags,
    };

    return {
      id,
      timestamp,
      source,
      message: report.message,
      stack_trace: report.traceback,
      error_type: report.error_type,
      severity: report.severity || 'error',
      metadata: report.metadata,
      evidence: [],
    };
  }

  /**
   * Generate a UUID v4.
   *
   * @returns UUID string
   */
  private generateUUID(): string {
    const buffer = crypto.getRandomValues(new Uint8Array(16));
    buffer[6] = (buffer[6] & 0x0f) | 0x40;
    buffer[8] = (buffer[8] & 0x3f) | 0x80;

    const hex = Array.from(buffer, (byte) => byte.toString(16).padStart(2, '0')).join('');
    return [
      hex.slice(0, 8),
      hex.slice(8, 12),
      hex.slice(12, 16),
      hex.slice(16, 20),
      hex.slice(20),
    ].join('-');
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
