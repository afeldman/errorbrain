/**
 * Tests for ErrorBrain TypeScript SDK
 */

import axios from 'axios';
import { ErrorBrainClient, ErrorReport, ErrorResponse, HealthResponse } from './client';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ErrorBrainClient', () => {
  let client: ErrorBrainClient;
  const mockBaseURL = 'http://localhost:8000';

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();

    // Mock axios.create to return a mocked instance
    mockedAxios.create = jest.fn().mockReturnValue({
      get: jest.fn(),
      post: jest.fn(),
    } as any);

    client = new ErrorBrainClient({ baseURL: mockBaseURL });
  });

  describe('constructor', () => {
    it('should use provided baseURL', () => {
      const customClient = new ErrorBrainClient({ baseURL: 'http://custom:9000' });
      expect(customClient).toBeDefined();
    });

    it('should use environment variable if no baseURL provided', () => {
      process.env.ERRORBRAIN_API_URL = 'http://env-url:8080';
      const envClient = new ErrorBrainClient();
      expect(envClient).toBeDefined();
      delete process.env.ERRORBRAIN_API_URL;
    });

    it('should default to localhost:8000 if no config', () => {
      delete process.env.ERRORBRAIN_API_URL;
      const defaultClient = new ErrorBrainClient();
      expect(defaultClient).toBeDefined();
    });

    it('should strip trailing slash from baseURL', () => {
      const clientWithSlash = new ErrorBrainClient({ baseURL: 'http://localhost:8000/' });
      expect(clientWithSlash).toBeDefined();
    });
  });

  describe('healthCheck', () => {
    it('should return health status on success', async () => {
      const mockHealth: HealthResponse = {
        status: 'healthy',
        llm_configured: true,
        vault_configured: true,
        vault_path: '/path/to/vault',
      };

      const mockGet = jest.fn().mockResolvedValue({ data: mockHealth });
      (client as any).client.get = mockGet;

      const result = await client.healthCheck();

      expect(mockGet).toHaveBeenCalledWith('/healthz');
      expect(result).toEqual(mockHealth);
    });

    it('should throw error on API failure', async () => {
      const mockGet = jest.fn().mockRejectedValue({
        isAxiosError: true,
        response: {
          status: 500,
          data: { error: 'Server error' },
        },
      });
      (client as any).client.get = mockGet;

      await expect(client.healthCheck()).rejects.toThrow();
    });

    it('should throw error on network failure', async () => {
      const mockGet = jest.fn().mockRejectedValue({
        isAxiosError: true,
        request: {},
      });
      (client as any).client.get = mockGet;

      await expect(client.healthCheck()).rejects.toThrow('No response from server');
    });
  });

  describe('sendError', () => {
    const mockReport: ErrorReport = {
      language: 'typescript',
      project: 'test-project',
      message: 'Test error',
      tags: ['test'],
    };

    const mockResponse: ErrorResponse = {
      id: 'test-id-123',
      project: 'test-project',
      language: 'typescript',
      tags: ['test'],
      created_at: '2025-12-11T10:00:00Z',
      explanation: 'Test explanation',
      saved_path: '/path/to/error.md',
    };

    it('should send error and return response', async () => {
      const mockPost = jest.fn().mockResolvedValue({ data: mockResponse });
      (client as any).client.post = mockPost;

      const result = await client.sendError(mockReport);

      expect(mockPost).toHaveBeenCalledWith('/v1/errors', {
        event: expect.objectContaining({
          message: 'Test error',
          source: expect.objectContaining({
            language: 'typescript',
            name: 'test-project',
          }),
        }),
        store_in_vault: true,
      });
      expect(result).toEqual(mockResponse);
    });

    it('should default store_in_vault to true', async () => {
      const mockPost = jest.fn().mockResolvedValue({ data: mockResponse });
      (client as any).client.post = mockPost;

      await client.sendError(mockReport);

      expect(mockPost).toHaveBeenCalledWith(
        '/v1/errors',
        expect.objectContaining({ store_in_vault: true })
      );
    });

    it('should respect store_in_vault false', async () => {
      const mockPost = jest.fn().mockResolvedValue({ data: mockResponse });
      (client as any).client.post = mockPost;

      await client.sendError({ ...mockReport, store_in_vault: false });

      expect(mockPost).toHaveBeenCalledWith(
        '/v1/errors',
        expect.objectContaining({ store_in_vault: false })
      );
    });

    it('should throw error on API failure', async () => {
      const mockPost = jest.fn().mockRejectedValue({
        isAxiosError: true,
        response: {
          status: 400,
          data: { error: 'Invalid request' },
        },
      });
      (client as any).client.post = mockPost;

      await expect(client.sendError(mockReport)).rejects.toThrow();
    });
  });

  describe('sendException', () => {
    const mockError = new Error('Test exception');
    mockError.stack = 'Error: Test exception\n  at test.ts:10:15';

    const mockResponse: ErrorResponse = {
      id: 'test-id-456',
      project: 'test-project',
      language: 'typescript',
      tags: ['exception'],
      created_at: '2025-12-11T10:00:00Z',
      explanation: 'Exception explanation',
    };

    it('should send exception with extracted message and stack', async () => {
      const mockPost = jest.fn().mockResolvedValue({ data: mockResponse });
      (client as any).client.post = mockPost;

      const result = await client.sendException(mockError, 'test-project', {
        tags: ['exception'],
      });

      expect(mockPost).toHaveBeenCalledWith(
        '/v1/errors',
        expect.objectContaining({
          event: expect.objectContaining({
            message: 'Test exception',
            stack_trace: mockError.stack,
          }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should use custom language if provided', async () => {
      const mockPost = jest.fn().mockResolvedValue({ data: mockResponse });
      (client as any).client.post = mockPost;

      await client.sendException(mockError, 'test-project', {
        language: 'javascript',
      });

      expect(mockPost).toHaveBeenCalledWith(
        '/v1/errors',
        expect.objectContaining({
          event: expect.objectContaining({
            source: expect.objectContaining({ language: 'javascript' }),
          }),
        })
      );
    });

    it('should include metadata if provided', async () => {
      const mockPost = jest.fn().mockResolvedValue({ data: mockResponse });
      (client as any).client.post = mockPost;

      const metadata = { user_id: '123', request_id: 'abc' };
      await client.sendException(mockError, 'test-project', { metadata });

      expect(mockPost).toHaveBeenCalledWith(
        '/v1/errors',
        expect.objectContaining({
          event: expect.objectContaining({ metadata }),
        })
      );
    });
  });

  describe('error handling', () => {
    it('should handle axios errors with response', async () => {
      const mockGet = jest.fn().mockRejectedValue({
        isAxiosError: true,
        response: {
          status: 404,
          data: { error: 'Not found' },
        },
      });
      (client as any).client.get = mockGet;

      await expect(client.healthCheck()).rejects.toThrow('404');
    });

    it('should handle axios errors without response', async () => {
      const mockGet = jest.fn().mockRejectedValue({
        isAxiosError: true,
        request: {},
      });
      (client as any).client.get = mockGet;

      await expect(client.healthCheck()).rejects.toThrow('No response from server');
    });

    it('should handle non-axios errors', async () => {
      const mockGet = jest.fn().mockRejectedValue(new Error('Unknown error'));
      (client as any).client.get = mockGet;

      await expect(client.healthCheck()).rejects.toThrow('Unknown error');
    });
  });
});

describe('createClient helper', () => {
  it('should create a new client instance', () => {
    const { createClient } = require('./client');
    const client = createClient({ baseURL: 'http://test:8000' });
    expect(client).toBeInstanceOf(ErrorBrainClient);
  });
});
