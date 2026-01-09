//! Rust/Cargo example: Basic error reporting

use errorbrain_sdk::{ErrorBrainClient, ErrorReport};
use std::collections::HashMap;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("ErrorBrain Rust SDK - Basic Example");
    println!("==================================\n");

    let client = ErrorBrainClient::new("http://localhost:8000".to_string());

    // Health check
    match client.health_check().await {
        Ok(health) => {
            println!("✅ API is healthy");
            println!("   Status: {}", health.status);
            println!("   LLM Configured: {}\n", health.llm_configured);
        }
        Err(e) => {
            eprintln!("❌ Health check failed: {}\n", e);
            return Err(e.into());
        }
    }

    // Create error report
    let mut metadata = HashMap::new();
    metadata.insert("user_id".to_string(), "12345".to_string());
    metadata.insert("request_id".to_string(), "abc-def".to_string());

    let report = ErrorReport::new("rust", "billing-service", "Database connection timeout")
        .with_traceback(
            "thread 'main' panicked at 'connection timeout'\n   at db/connection.rs:42:10"
                .to_string(),
        )
        .with_tags(vec!["prod".to_string(), "database".to_string()])
        .with_metadata(metadata);

    // Send error
    match client.send_error(&report).await {
        Ok(response) => {
            println!("✅ Error sent successfully");
            println!("   ID: {}", response.id);
            println!("   Explanation: {}", response.explanation);
            if let Some(path) = response.saved_path {
                println!("   Saved to: {}", path);
            }
        }
        Err(e) => {
            eprintln!("❌ Failed to send error: {}", e);
            return Err(e.into());
        }
    }

    Ok(())
}
