/**
 * ErrorBrain Deno SDK - Main export
 *
 * @module
 */

export {
  ErrorBrainClient,
  createClient,
  type ErrorReport,
  type ErrorResponse,
  type HealthResponse,
  type ClientConfig,
} from './client.ts';

export type { ErrorEvent, Source, Evidence } from './types.ts';
