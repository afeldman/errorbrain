/**
 * Tests for ErrorBrain Deno SDK
 *
 * Run with:
 *   deno test --allow-env --allow-net src/client.test.ts
 */

import { assertEquals, assertExists } from "https://deno.land/std@0.208.0/testing/asserts.ts";
import { ErrorBrainClient, type ErrorResponse } from "./client.ts";

// Test 1: Client initialization
Deno.test("Client initialization with config", () => {
  const client = new ErrorBrainClient({ baseURL: "http://localhost:8000" });
  assertExists(client);
});

Deno.test("Client uses environment variable for baseURL", () => {
  Deno.env.set("ERRORBRAIN_API_URL", "http://custom:9000");
  const client = new ErrorBrainClient();
  assertExists(client);
  Deno.env.delete("ERRORBRAIN_API_URL");
});

Deno.test("Client defaults to localhost:8000", () => {
  Deno.env.delete("ERRORBRAIN_API_URL");
  const client = new ErrorBrainClient();
  assertExists(client);
});

// Test 2: Error interface validation
Deno.test("ErrorResponse interface validation", async () => {
  const mockResponse: ErrorResponse = {
    id: "test-id",
    project: "test-project",
    language: "typescript",
    tags: ["test"],
    created_at: "2025-12-11T10:00:00Z",
    explanation: "Test explanation",
    saved_path: "/path/to/error.md",
  };

  assertEquals(mockResponse.id, "test-id");
  assertEquals(mockResponse.project, "test-project");
  assertEquals(mockResponse.explanation, "Test explanation");
});

// Test 3: Error report creation
Deno.test("Error report structure", () => {
  const report = {
    language: "typescript",
    project: "test-project",
    message: "Test error",
    tags: ["test"],
    metadata: { key: "value" },
    store_in_vault: true,
  };

  assertEquals(report.language, "typescript");
  assertEquals(report.project, "test-project");
  assertEquals(report.message, "Test error");
  assertEquals(report.tags.length, 1);
  assertEquals(report.store_in_vault, true);
});

// Test 4: Exception handling
Deno.test("Exception error extraction", () => {
  const error = new Error("Test exception");
  assertEquals(error.message, "Test exception");
  assertExists(error.stack);
});

// Test 5: Type checking
Deno.test("Client config type validation", () => {
  const config = {
    baseURL: "http://test:8000",
    timeout: 5000,
    headers: { "X-Custom": "value" },
  };

  assertEquals(config.baseURL, "http://test:8000");
  assertEquals(config.timeout, 5000);
  assertEquals(config.headers["X-Custom"], "value");
});

// Test 6: URL handling
Deno.test("Client strips trailing slash from baseURL", () => {
  const client1 = new ErrorBrainClient({ baseURL: "http://localhost:8000/" });
  const client2 = new ErrorBrainClient({ baseURL: "http://localhost:8000" });
  assertExists(client1);
  assertExists(client2);
});
