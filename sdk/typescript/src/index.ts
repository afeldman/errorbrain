/**
 * ErrorBrain TypeScript SDK - Main export
 *
 * @packageDocumentation
 */

export {
  ErrorBrainClient,
  createClient,
  ErrorReport,
  ErrorResponse,
  HealthResponse,
  ClientConfig,
} from './client';

export type { ErrorEvent, Source, Evidence } from './types';
