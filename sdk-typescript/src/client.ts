/**
 * ErrorBrain TypeScript SDK - Client for error tracking API.
 *
 * This module provides a client for communicating with the ErrorBrain API
 * to submit errors for AI analysis and storage in Obsidian vault.
 *
 * @packageDocumentation
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

/**
 * Error report model matching the API schema.
 */
export interface ErrorReport {
  /** Programming language (e.g., typescript, javascript, python) */
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
  private client: AxiosInstance;
  private baseURL: string;

  /**
   * Initialize the ErrorBrain client.
   *
   * @param config - Configuration options. If not provided, uses ERRORBRAIN_API_URL
   *                 environment variable or defaults to http://localhost:8000
   */
  constructor(config?: ClientConfig) {
    this.baseURL = (
      config?.baseURL ||
      process.env.ERRORBRAIN_API_URL ||
      'http://localhost:8000'
    ).replace(/\/$/, '');

    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: config?.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...config?.headers,
      },
    });
  }

  /**
   * Check if the API is healthy.
   *
   * @returns Health check response with status and configuration
   * @throws {Error} If the API is not reachable or returns an error
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
      const response = await this.client.get<HealthResponse>('/healthz');
      return response.data;
    } catch (error) {
      this.handleError(error, 'Health check failed');
    }
  }

  /**
   * Send an error to ErrorBrain for analysis and storage.
   *
   * @param report - Error report to send
   * @returns ErrorResponse with explanation and saved path
   * @throws {Error} If the API request fails
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

      const response = await this.client.post<ErrorResponse>('/v1/errors', payload);
      return response.data;
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
   * @throws {Error} If the API request fails
   *
   * @example
   * ```typescript
   * try {
   *   // Some code that throws an error
   *   throw new Error('Connection timeout');
   * } catch (error) {
   *   const response = await client.sendException(error as Error, 'my-service', {
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
      language: options?.language || 'typescript',
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
   * @throws {Error} Always throws with detailed error information
   */
  private handleError(error: unknown, message: string): never {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        // Server responded with error
        throw new Error(
          `${message}: ${axiosError.response.status} - ${JSON.stringify(axiosError.response.data)}`
        );
      } else if (axiosError.request) {
        // No response received
        throw new Error(`${message}: No response from server (${this.baseURL})`);
      }
    }
    // Other errors
    throw new Error(`${message}: ${error instanceof Error ? error.message : String(error)}`);
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
