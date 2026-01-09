//! Data models for ErrorBrain SDK.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

/// Configuration for ErrorBrain client.
///
/// # Examples
///
/// ```rust
/// use errorbrain_sdk::ClientConfig;
///
/// let config = ClientConfig::new("http://localhost:8000")
///     .with_timeout(30000);
/// ```
#[derive(Debug, Clone)]
pub struct ClientConfig {
    /// Base URL of the ErrorBrain API
    pub base_url: String,
    /// Request timeout in milliseconds
    pub timeout_ms: u64,
    /// Additional headers
    pub headers: HashMap<String, String>,
}

impl ClientConfig {
    /// Create a new client configuration.
    ///
    /// # Arguments
    ///
    /// * `base_url` - Base URL of the ErrorBrain API
    pub fn new(base_url: impl Into<String>) -> Self {
        Self {
            base_url: base_url.into(),
            timeout_ms: 30000,
            headers: HashMap::new(),
        }
    }

    /// Set request timeout in milliseconds.
    pub fn with_timeout(mut self, timeout_ms: u64) -> Self {
        self.timeout_ms = timeout_ms;
        self
    }

    /// Add a custom header.
    pub fn with_header(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.headers.insert(key.into(), value.into());
        self
    }
}

/// Error report to send to ErrorBrain API.
///
/// # Examples
///
/// ```rust
/// use errorbrain_sdk::ErrorReport;
/// use std::collections::HashMap;
///
/// let mut metadata = HashMap::new();
/// metadata.insert("user_id".to_string(), "12345".to_string());
///
/// let report = ErrorReport {
///     language: "rust".to_string(),
///     project: "my-service".to_string(),
///     message: "Database connection failed".to_string(),
///     traceback: None,
///     tags: vec!["prod".to_string(), "database".to_string()],
///     metadata: Some(metadata),
///     store_in_vault: true,
/// };
/// ```
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorReport {
    /// Programming language (e.g., "rust", "python", "go")
    pub language: String,
    /// Project or service name
    pub project: String,
    /// Error message
    pub message: String,
    /// Optional stack trace
    pub traceback: Option<String>,
    /// Tags for categorization
    pub tags: Vec<String>,
    /// Additional metadata
    pub metadata: Option<HashMap<String, String>>,
    /// Whether to save in Obsidian vault
    pub store_in_vault: bool,
}

impl ErrorReport {
    /// Create a new error report.
    ///
    /// # Arguments
    ///
    /// * `language` - Programming language
    /// * `project` - Project name
    /// * `message` - Error message
    pub fn new(
        language: impl Into<String>,
        project: impl Into<String>,
        message: impl Into<String>,
    ) -> Self {
        Self {
            language: language.into(),
            project: project.into(),
            message: message.into(),
            traceback: None,
            tags: Vec::new(),
            metadata: None,
            store_in_vault: true,
        }
    }

    /// Add tags to the report.
    pub fn with_tags(mut self, tags: Vec<String>) -> Self {
        self.tags = tags;
        self
    }

    /// Add metadata to the report.
    pub fn with_metadata(mut self, metadata: HashMap<String, String>) -> Self {
        self.metadata = Some(metadata);
        self
    }

    /// Set traceback.
    pub fn with_traceback(mut self, traceback: String) -> Self {
        self.traceback = Some(traceback);
        self
    }

    /// Set whether to store in vault.
    pub fn with_store_in_vault(mut self, store: bool) -> Self {
        self.store_in_vault = store;
        self
    }
}

/// Response from ErrorBrain API.
///
/// # Examples
///
/// ```rust,no_run
/// use errorbrain_sdk::ErrorBrainClient;
///
/// # #[tokio::main]
/// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
/// let client = ErrorBrainClient::new("http://localhost:8000".to_string());
/// let response = client.health_check().await?;
/// println!("Status: {}", response.status);
/// # Ok(())
/// # }
/// ```
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorResponse {
    /// Unique error identifier
    pub id: String,
    /// Project name
    pub project: String,
    /// Programming language
    pub language: String,
    /// Tags
    pub tags: Vec<String>,
    /// Timestamp
    pub created_at: DateTime<Utc>,
    /// AI-generated explanation
    pub explanation: String,
    /// Path where error was saved
    pub saved_path: Option<String>,
}

/// Health check response.
///
/// Contains API status and configuration information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthResponse {
    /// API status
    pub status: String,
    /// Whether LLM is configured
    pub llm_configured: bool,
    /// Whether Obsidian vault is configured
    pub vault_configured: bool,
    /// Vault path (if configured)
    pub vault_path: Option<String>,
}
