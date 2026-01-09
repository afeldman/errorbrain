// Disable all warnings for now - will be configured in CI
#![allow(warnings)]

//! ErrorBrain Rust SDK
//!
//! A Rust client for the ErrorBrain API - AI-powered debugging memory.
//!
//! # Features
//!
//! - Async/await support with Tokio
//! - Strongly typed with Rust's type system
//! - Automatic error backtrace capture
//! - Metadata and tagging support
//! - Health check integration
//!
//! # Example
//!
//! ```rust,no_run
//! use errorbrain_sdk::{ErrorBrainClient, ErrorReport};
//!
//! #[tokio::main]
//! async fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     let client = ErrorBrainClient::new("http://localhost:8000".to_string());
//!
//!     let report = ErrorReport {
//!         language: "rust".to_string(),
//!         project: "my-service".to_string(),
//!         message: "Connection timeout".to_string(),
//!         traceback: None,
//!         tags: vec!["prod".to_string()],
//!         metadata: None,
//!         store_in_vault: true,
//!     };
//!
//!     let response = client.send_error(&report).await?;
//!     println!("Error ID: {}", response.id);
//!     println!("Explanation: {}", response.explanation);
//!
//!     Ok(())
//! }
//! ```

pub mod client;
pub mod error;
pub mod models;

pub use client::ErrorBrainClient;
pub use error::{ErrorBrainError, Result};
pub use models::{ClientConfig, ErrorReport, ErrorResponse, HealthResponse};
