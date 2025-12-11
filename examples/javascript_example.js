/**
 * ErrorBrain JavaScript SDK - Example Usage
 *
 * This example demonstrates how to use the ErrorBrain SDK in plain JavaScript.
 */

const { ErrorBrainClient } = require("../sdk-typescript/dist");

/**
 * Example 1: Basic error report (JavaScript)
 */
async function exampleBasic() {
  console.log("=".repeat(60));
  console.log("Example 1: Basic Error Report (JavaScript)");
  console.log("=".repeat(60));

  const client = new ErrorBrainClient({ baseURL: "http://localhost:8000" });

  // Health check
  try {
    const health = await client.healthCheck();
    console.log("✓ API is healthy");
    console.log(`  Status: ${health.status}\n`);
  } catch (error) {
    console.error("❌ ErrorBrain API is not available");
    return;
  }

  // Send error
  try {
    const response = await client.sendError({
      language: "javascript",
      project: "web-app",
      message: "TypeError: Cannot read property of undefined",
      traceback:
        "TypeError: Cannot read property 'name' of undefined\n" +
        "  at getUserInfo (app.js:15:23)\n" +
        "  at handleRequest (server.js:42:18)",
      tags: ["prod", "frontend"],
      metadata: {
        user_id: "67890",
        page: "/dashboard",
        browser: "Chrome 120",
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
 * Example 2: Exception handling in JavaScript
 */
async function exampleException() {
  console.log("=".repeat(60));
  console.log("Example 2: Exception Handling (JavaScript)");
  console.log("=".repeat(60));

  const client = new ErrorBrainClient();

  try {
    // Provoke an error
    JSON.parse("{ invalid json }");
  } catch (error) {
    console.log(`Caught exception: ${error.message}\n`);

    try {
      const response = await client.sendException(error, "json-parser", {
        language: "javascript",
        tags: ["parsing", "validation"],
        metadata: {
          input_length: 17,
        },
      });

      console.log(`Error ID: ${response.id}`);
      console.log(`\nAI Explanation:\n${response.explanation}`);
    } catch (apiError) {
      console.error("Failed to send exception:", apiError);
    }
  }
  console.log();
}

/**
 * Example 3: Express.js error middleware
 */
async function exampleExpressMiddleware() {
  console.log("=".repeat(60));
  console.log("Example 3: Express.js Error Middleware Pattern");
  console.log("=".repeat(60));

  const client = new ErrorBrainClient();

  // Simulated Express error middleware
  const errorMiddleware = async (err, req, res, next) => {
    console.log(`Handling Express error: ${err.message}`);

    try {
      const response = await client.sendException(err, "express-api", {
        language: "javascript",
        tags: ["express", "middleware", req.method.toLowerCase()],
        metadata: {
          method: req.method,
          path: req.path,
          ip: req.ip,
        },
      });

      console.log(`Error logged with ID: ${response.id}\n`);
    } catch (apiError) {
      console.error("Failed to log error:", apiError);
    }

    // In real middleware, you would send response to client here
    // res.status(500).json({ error: 'Internal server error' });
  };

  // Simulate an Express request
  const mockReq = {
    method: "POST",
    path: "/api/users",
    ip: "192.168.1.100",
  };

  const mockError = new Error("Database query failed");
  await errorMiddleware(mockError, mockReq, null, null);
  console.log();
}

/**
 * Run all examples
 */
async function main() {
  console.log("\n");
  console.log("█".repeat(60));
  console.log("ErrorBrain JavaScript SDK Examples");
  console.log("█".repeat(60));
  console.log("\n");

  await exampleBasic();
  await exampleException();
  await exampleExpressMiddleware();

  console.log("=".repeat(60));
  console.log("All examples completed!");
  console.log("=".repeat(60));
}

// Run examples
main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
