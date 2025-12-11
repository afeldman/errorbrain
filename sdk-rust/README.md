# ErrorBrain Rust SDK

High-performance Rust client for [ErrorBrain](https://github.com/errorbrain/errorbrain) - AI-powered debugging memory.

## 🚀 Features

- ✅ **Async/await** with Tokio runtime
- ✅ **Strongly typed** - Leverages Rust's type system
- ✅ **Automatic backtraces** - Built-in backtrace capture
- ✅ **Zero-copy** - Efficient memory handling
- ✅ **Error handling** - Comprehensive error types
- ✅ **Logging** - Integrated with tracing
- ✅ **Production-ready** - Optimized for performance

## 📦 Installation

Add to your `Cargo.toml`:

```toml
[dependencies]
errorbrain-sdk = { path = "sdk-rust" }
```

## 🔧 Quick Start

```rust
use errorbrain_sdk::{ErrorBrainClient, ErrorReport};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = ErrorBrainClient::new("http://localhost:8000".to_string());

    let report = ErrorReport::new("rust", "my-service", "Database connection failed")
        .with_tags(vec!["prod".to_string(), "database".to_string()]);

    let response = client.send_error(&report).await?;
    println!("Error ID: {}", response.id);
    println!("Explanation: {}", response.explanation);

    Ok(())
}
```

## 📖 Examples

Run examples:

```bash
cargo run --example basic
cargo run --example exception
cargo run --example metadata
```

## 🔌 API

### `ErrorBrainClient`

Main client for interacting with the ErrorBrain API.

#### Methods

- `new(base_url)` - Create new client
- `with_config(config)` - Create with custom configuration
- `health_check()` - Check API health
- `send_error(report)` - Send error report

### `ErrorReport`

Builder-style error report.

```rust
let report = ErrorReport::new("rust", "my-service", "Error message")
    .with_tags(vec!["prod".to_string()])
    .with_traceback("Stack trace".to_string())
    .with_metadata(metadata)
    .with_store_in_vault(true);
```

## 🧪 Testing

```bash
cargo test
cargo clippy
cargo fmt
```

## 📝 License

MIT

## 🔗 Links

- [ErrorBrain Repository](https://github.com/errorbrain/errorbrain)
- [Tokio Documentation](https://tokio.rs/)
- [Reqwest Documentation](https://docs.rs/reqwest/)
