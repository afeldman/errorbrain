//! Error types for ErrorBrain SDK.

use std::fmt;

/// Result type for ErrorBrain operations.
pub type Result<T> = std::result::Result<T, ErrorBrainError>;

/// Error types for ErrorBrain SDK.
///
/// # Examples
///
/// ```rust
/// use errorbrain_sdk::{ErrorBrainError, Result};
///
/// fn main() -> Result<()> {
///     let result: Result<()> = Err(ErrorBrainError::RequestFailed(500, "oops".into()));
///
///     match result {
///         Err(ErrorBrainError::RequestFailed(status, msg)) => {
///             println!("Request failed {}: {}", status, msg)
///         }
///         Err(ErrorBrainError::InvalidResponse) => println!("Invalid response"),
///         Ok(_) => println!("Success"),
///         _ => println!("Other error"),
///     }
///
///     Ok(())
/// }
/// ```
#[derive(Debug)]
pub enum ErrorBrainError {
    /// Request failed with status code and message
    RequestFailed(u16, String),
    /// Invalid response from server
    InvalidResponse,
    /// Request timeout
    Timeout,
    /// Network error
    NetworkError(String),
    /// Serialization/deserialization error
    SerializationError(String),
    /// Configuration error
    ConfigError(String),
}

impl fmt::Display for ErrorBrainError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ErrorBrainError::RequestFailed(code, msg) => {
                write!(f, "Request failed with status {}: {}", code, msg)
            }
            ErrorBrainError::InvalidResponse => write!(f, "Invalid response from server"),
            ErrorBrainError::Timeout => write!(f, "Request timeout"),
            ErrorBrainError::NetworkError(msg) => write!(f, "Network error: {}", msg),
            ErrorBrainError::SerializationError(msg) => write!(f, "Serialization error: {}", msg),
            ErrorBrainError::ConfigError(msg) => write!(f, "Configuration error: {}", msg),
        }
    }
}

impl std::error::Error for ErrorBrainError {}
