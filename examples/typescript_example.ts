/**
 * ErrorBrain TypeScript SDK - Example Usage
 *
 * This example demonstrates how to use the ErrorBrain TypeScript SDK
 * to send errors to the ErrorBrain API for AI analysis.
 */

import { ErrorBrainClient } from "../sdk-typescript/src";

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
    console.error(error);
    return;
  }

  // Send error
  try {
    const response = await client.sendError({
      language: "typescript",
      project: "billing-service",
      message: "Database connection timeout",
      traceback:
        "Error: connection timeout\n" +
        "  at Database.connect (db.ts:42:15)\n" +
        "  at BillingService.init (service.ts:18:22)",
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
    console.log(`Caught exception: ${(error as Error).message}\n`);

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
      project: "api-gateway",
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
 * Example 4: Promise rejection handling
 */
async function examplePromiseRejection(): Promise<void> {
  console.log("=".repeat(60));
  console.log("Example 4: Promise Rejection Handling");
  console.log("=".repeat(60));

  const client = new ErrorBrainClient();

  // Simulate a failing async operation
  const fetchData = async (): Promise<string> => {
    return Promise.reject(
      new Error("Network request failed: Connection refused")
    );
  };

  try {
    await fetchData();
  } catch (error) {
    console.log(`Caught rejection: ${(error as Error).message}\n`);

    try {
      const response = await client.sendException(
        error as Error,
        "user-service",
        {
          language: "typescript",
          tags: ["async", "network", "prod"],
          metadata: {
            operation: "fetchUserData",
            retry_count: 3,
          },
        }
      );

      console.log(`Error ID: ${response.id}`);
      console.log(`\nAI Explanation:\n${response.explanation}`);
    } catch (apiError) {
      console.error("Failed to send error:", apiError);
    }
  }
  console.log();
}

/**
 * Example 5: Using environment variable for API URL
 */
async function exampleEnvConfig(): Promise<void> {
  console.log("=".repeat(60));
  console.log("Example 5: Environment Variable Configuration");
  console.log("=".repeat(60));

  // Set environment variable (in production, this would be in .env file)
  process.env.ERRORBRAIN_API_URL = "http://localhost:8000";

  // Client will use ERRORBRAIN_API_URL automatically
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
 * Run all examples
 */
async function main(): Promise<void> {
  console.log("\n");
  console.log("█".repeat(60));
  console.log("ErrorBrain TypeScript SDK Examples");
  console.log("█".repeat(60));
  console.log("\n");

  await exampleBasic();
  await exampleException();
  await exampleWithMetadata();
  await examplePromiseRejection();
  await exampleEnvConfig();

  console.log("=".repeat(60));
  console.log("All examples completed!");
  console.log("=".repeat(60));
}

// Run examples
main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
