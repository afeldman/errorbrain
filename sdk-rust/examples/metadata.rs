//! Rust/Cargo example: Error with rich metadata

use errorbrain_sdk::{ErrorBrainClient, ErrorReport};
use std::collections::HashMap;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("ErrorBrain Rust SDK - Metadata Example");
    println!("====================================\n");

    let client = ErrorBrainClient::default();

    // Create comprehensive metadata
    let mut metadata = HashMap::new();
    metadata.insert("endpoint".to_string(), "/api/v1/users".to_string());
    metadata.insert("method".to_string(), "POST".to_string());
    metadata.insert("client_ip".to_string(), "203.0.113.42".to_string());
    metadata.insert(
        "requests_per_minute".to_string(),
        "1200".to_string(),
    );
    metadata.insert("limit".to_string(), "1000".to_string());
    metadata.insert("user_id".to_string(), "user_12345".to_string());

    let report = ErrorReport::new("rust", "api-gateway", "Rate limit exceeded")
        .with_tags(vec![
            "api".to_string(),
            "rate-limit".to_string(),
            "production".to_string(),
        ])
        .with_metadata(metadata)
        .with_store_in_vault(true);

    match client.send_error(&report).await {
        Ok(response) => {
            println!("✅ Error with metadata sent");
            println!("   ID: {}", response.id);
            println!("   Tags: {}", response.tags.join(", "));
            println!("   Analysis: {}", response.explanation);
        }
        Err(e) => {
            eprintln!("❌ Failed to send error: {}", e);
        }
    }

    Ok(())
}
