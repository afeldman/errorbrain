//! HTTP client for ErrorBrain API.

use crate::error::{ErrorBrainError, Result};
use crate::models::{ClientConfig, ErrorReport, ErrorResponse, HealthResponse};
use reqwest::Client;
use std::env;
use tracing::{debug, error, info};

/// ErrorBrain API client.
///
/// Provides async methods for interacting with the ErrorBrain API.
///
/// # Examples
///
/// ```rust,no_run
/// use errorbrain_sdk::{ErrorBrainClient, ErrorReport};
///
/// #[tokio::main]
/// async fn main() -> Result<(), Box<dyn std::error::Error>> {
///     let client = ErrorBrainClient::new("http://localhost:8000".to_string());
///
///     // Health check
///     let health = client.health_check().await?;
///     println!("API Status: {}", health.status);
///
///     // Send error
///     let report = ErrorReport::new("rust", "my-service", "Something went wrong");
///     let response = client.send_error(&report).await?;
///     println!("Error ID: {}", response.id);
///
///     Ok(())
/// }
/// ```
pub struct ErrorBrainClient {
    config: ClientConfig,
    client: Client,
}

impl ErrorBrainClient {
    /// Create a new ErrorBrain client.
    ///
    /// # Arguments
    ///
    /// * `base_url` - Base URL of the ErrorBrain API
    ///
    /// Uses `ERRORBRAIN_API_URL` environment variable if not provided.
    pub fn new(base_url: impl Into<String>) -> Self {
        let base_url = base_url.into();
        let config = ClientConfig::new(base_url);
        let client = Client::new();

        Self { config, client }
    }

    /// Create a new ErrorBrain client with custom configuration.
    pub fn with_config(config: ClientConfig) -> Self {
        let client = Client::new();
        Self { config, client }
    }

    /// Check if API is healthy.
    ///
    /// # Errors
    ///
    /// Returns `ErrorBrainError` if request fails.
    ///
    /// # Examples
    ///
    /// ```rust,no_run
    /// # use errorbrain_sdk::ErrorBrainClient;
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// let client = ErrorBrainClient::new("http://localhost:8000".to_string());
    /// let health = client.health_check().await?;
    /// println!("LLM Configured: {}", health.llm_configured);
    /// # Ok(())
    /// # }
    /// ```
    pub async fn health_check(&self) -> Result<HealthResponse> {
        debug!("Checking API health");

        let url = format!("{}/healthz", self.config.base_url);
        let response = self
            .client
            .get(&url)
            .timeout(std::time::Duration::from_millis(self.config.timeout_ms))
            .send()
            .await
            .map_err(|e| {
                error!("Health check failed: {}", e);
                ErrorBrainError::NetworkError(e.to_string())
            })?;

        if !response.status().is_success() {
            error!("Health check returned {}", response.status());
            return Err(ErrorBrainError::RequestFailed(
                response.status().as_u16(),
                "Health check failed".to_string(),
            ));
        }

        let health = response.json::<HealthResponse>().await.map_err(|e| {
            error!("Failed to parse health response: {}", e);
            ErrorBrainError::SerializationError(e.to_string())
        })?;

        info!("API health check successful");
        Ok(health)
    }

    /// Send an error report to ErrorBrain.
    ///
    /// # Arguments
    ///
    /// * `report` - Error report to send
    ///
    /// # Errors
    ///
    /// Returns `ErrorBrainError` if request fails.
    ///
    /// # Examples
    ///
    /// ```rust,no_run
    /// # use errorbrain_sdk::{ErrorBrainClient, ErrorReport};
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// let client = ErrorBrainClient::new("http://localhost:8000".to_string());
    /// let report = ErrorReport::new("rust", "my-service", "Error message");
    /// let response = client.send_error(&report).await?;
    /// println!("Explanation: {}", response.explanation);
    /// # Ok(())
    /// # }
    /// ```
    pub async fn send_error(&self, report: &ErrorReport) -> Result<ErrorResponse> {
        debug!("Sending error report for project: {}", report.project);

        let url = format!("{}/v1/errors", self.config.base_url);
        let response = self
            .client
            .post(&url)
            .json(report)
            .timeout(std::time::Duration::from_millis(self.config.timeout_ms))
            .send()
            .await
            .map_err(|e| {
                error!("Failed to send error: {}", e);
                ErrorBrainError::NetworkError(e.to_string())
            })?;

        if !response.status().is_success() {
            let status = response.status().as_u16();
            let text = response.text().await.unwrap_or_default();
            error!("Error API returned {}: {}", status, text);
            return Err(ErrorBrainError::RequestFailed(
                status,
                text,
            ));
        }

        let error_response = response.json::<ErrorResponse>().await.map_err(|e| {
            error!("Failed to parse error response: {}", e);
            ErrorBrainError::SerializationError(e.to_string())
        })?;

        info!("Error report sent successfully: {}", error_response.id);
        Ok(error_response)
    }
}

impl Default for ErrorBrainClient {
    fn default() -> Self {
        let base_url = env::var("ERRORBRAIN_API_URL")
            .unwrap_or_else(|_| "http://localhost:8000".to_string());
        Self::new(base_url)
    }
}
