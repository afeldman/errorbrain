//! Rust/Cargo example: Exception handling

use errorbrain_sdk::{ErrorBrainClient, ErrorReport};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("ErrorBrain Rust SDK - Exception Example");
    println!("======================================\n");

    let client = ErrorBrainClient::default();

    // Simulate an error
    if let Err(e) = risky_operation() {
        println!("Caught error: {}\n", e);

        let report = ErrorReport::new("rust", "data-pipeline", &format!("Error: {}", e))
            .with_tags(vec!["cron".to_string(), "prod".to_string()])
            .with_traceback(format!("Backtrace: {}", std::backtrace::Backtrace::capture()));

        match client.send_error(&report).await {
            Ok(response) => {
                println!("✅ Error logged");
                println!("   ID: {}", response.id);
                println!("   Analysis: {}", response.explanation);
            }
            Err(err) => {
                eprintln!("❌ Failed to log error: {}", err);
            }
        }
    }

    Ok(())
}

fn risky_operation() -> Result<(), String> {
    let values = vec![1, 2, 3];
    let index = 10;

    values
        .get(index)
        .ok_or_else(|| "Array index out of bounds".to_string())?;

    Ok(())
}
