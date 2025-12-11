/**
 * ErrorBrain Deno SDK - Example Usage
 *
 * This example demonstrates how to use the ErrorBrain Deno SDK
 * to send errors to the ErrorBrain API for AI analysis.
 *
 * Run with:
 *   deno run --allow-env --allow-net examples/deno_example.ts
 */

import { ErrorBrainClient, type ErrorReport } from "../sdk-deno/src/mod.ts";

/**
 * Example 1: Basic error report
 */
async function exampleBasic(): Promise<void> {
  console.log("=".repeat(60));
  console.log("Example 1: Basic Error Report");
  console.log("=".repeat(60));

  const client = new ErrorBrainClient({ baseURL: "http://localhost:8000" });

  // Health check
  try {
    const health = await client.healthCheck();
    console.log("✓ API is healthy");
    console.log(`  Status: ${health.status}`);
    console.log(`  LLM Configured: ${health.llm_configured}`);
    console.log(`  Vault Configured: ${health.vault_configured}\n`);
  } catch (error) {
    console.error("❌ ErrorBrain API is not available");
    console.error(error instanceof Error ? error.message : error);
    return;
  }

  // Send error
  try {
    const response = await client.sendError({
      language: "typescript",
      project: "deno-api",
      message: "Database connection timeout",
      traceback:
        "Error: connection timeout\n" +
        "  at Database.connect (db.ts:42:15)\n" +
        "  at DenoService.init (service.ts:18:22)",
      tags: ["prod", "database", "critical"],
      metadata: {
        user_id: "12345",
        request_id: "abc-def",
        db_host: "db.prod.example.com",
      },
    });

    console.log(`Error ID: ${response.id}`);
    console.log(`\nAI Explanation:\n${response.explanation}`);
    if (response.saved_path) {
      console.log(`\nSaved to: ${response.saved_path}`);
    }
  } catch (error) {
    console.error("Failed to send error:", error);
  }
  console.log();
}

/**
 * Example 2: Capture exceptions automatically
 */
async function exampleException(): Promise<void> {
  console.log("=".repeat(60));
  console.log("Example 2: Exception Handling");
  console.log("=".repeat(60));

  const client = new ErrorBrainClient();

  try {
    // Provoke an error
    const divisor = 0;
    if (divisor === 0) {
      throw new Error("Division by zero");
    }
    const result = 10 / divisor;
    console.log(result);
  } catch (error) {
    console.log(
      `Caught exception: ${error instanceof Error ? error.message : error}\n`
    );

    try {
      const response = await client.sendException(
        error as Error,
        "data-pipeline",
        {
          tags: ["cron", "prod"],
          metadata: {
            job_id: "daily-report",
            timestamp: new Date().toISOString(),
          },
        }
      );

      console.log(`Error ID: ${response.id}`);
      console.log(`\nAI Explanation:\n${response.explanation}`);
    } catch (apiError) {
      console.error("Failed to send exception:", apiError);
    }
  }
  console.log();
}

/**
 * Example 3: Error with rich metadata
 */
async function exampleWithMetadata(): Promise<void> {
  console.log("=".repeat(60));
  console.log("Example 3: Error with Rich Metadata");
  console.log("=".repeat(60));

  const client = new ErrorBrainClient();

  try {
    const response = await client.sendError({
      language: "typescript",
      project: "deno-gateway",
      message: "Rate limit exceeded",
      tags: ["api", "rate-limit", "production"],
      metadata: {
        endpoint: "/api/v1/users",
        method: "POST",
        client_ip: "203.0.113.42",
        requests_per_minute: 1200,
        limit: 1000,
        user_id: "user_12345",
        timestamp: new Date().toISOString(),
      },
      store_in_vault: true,
    });

    console.log(`Error ID: ${response.id}`);
    console.log(`Tags: ${response.tags.join(", ")}`);
    console.log(`\nAI Explanation:\n${response.explanation}`);
    if (response.saved_path) {
      console.log(`\nSaved to: ${response.saved_path}`);
    }
  } catch (error) {
    console.error("Failed to send error:", error);
  }
  console.log();
}

/**
 * Example 4: Using environment variable for API URL
 */
async function exampleEnvConfig(): Promise<void> {
  console.log("=".repeat(60));
  console.log("Example 4: Environment Variable Configuration");
  console.log("=".repeat(60));

  // ERRORBRAIN_API_URL can be set via environment variable
  const client = new ErrorBrainClient();

  try {
    const health = await client.healthCheck();
    console.log("✓ API is healthy (configured via environment variable)");
    console.log(`  Status: ${health.status}\n`);
  } catch (error) {
    console.error("Failed to connect:", error);
  }
}

/**
 * Example 5: Deno-specific patterns - top-level await
 */
async function exampleTopLevelAwait(): Promise<void> {
  console.log("=".repeat(60));
  console.log("Example 5: Deno-specific Top-Level Await");
  console.log("=".repeat(60));

  const client = new ErrorBrainClient();

  try {
    // In Deno, we can use top-level await
    console.log("Demonstrating Deno features:");
    console.log(`- Deno version: ${Deno.version.deno}`);
    console.log(`- Runtime environment: ${Deno.mainModule}`);

    const report: ErrorReport = {
      language: "typescript",
      project: "deno-runtime",
      message: "Deno feature demonstration",
      tags: ["deno", "demo"],
      metadata: {
        deno_version: Deno.version.deno,
        runtime: "Deno",
      },
    };

    const response = await client.sendError(report);
    console.log(`\n✓ Error sent with ID: ${response.id}\n`);
  } catch (error) {
    console.error("Failed:", error);
  }
}

/**
 * Run all examples
 */
async function main(): Promise<void> {
  console.log("\n");
  console.log("█".repeat(60));
  console.log("ErrorBrain Deno SDK Examples");
  console.log("█".repeat(60));
  console.log("\n");

  await exampleBasic();
  await exampleException();
  await exampleWithMetadata();
  await exampleEnvConfig();
  await exampleTopLevelAwait();

  console.log("=".repeat(60));
  console.log("All examples completed!");
  console.log("=".repeat(60));
}

// Run examples with top-level await
await main();
