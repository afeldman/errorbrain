use errorbrain_sdk::{ErrorBrainClient, ErrorBrainError, ErrorReport};
use mockito::{Matcher, Server};
use serde_json::json;

#[tokio::test]
async fn health_check_success() {
    let mut server = Server::new_async().await;
    let _m = server
        .mock("GET", "/healthz")
        .with_status(200)
        .with_header("content-type", "application/json")
        .with_body(r#"{"status":"ok","llm_configured":true,"vault_configured":false,"vault_path":null}"#)
        .create_async()
        .await;

    let client = ErrorBrainClient::new(server.url());
    let health = client.health_check().await.expect("health check should succeed");

    assert_eq!(health.status, "ok");
    assert!(health.llm_configured);
    assert!(!health.vault_configured);
}

#[tokio::test]
async fn send_error_success() {
    let mut server = Server::new_async().await;
    let _m = server
        .mock("POST", "/v1/errors")
        .match_header("content-type", "application/json")
        .match_body(Matcher::PartialJson(json!({
            "language": "rust",
            "project": "svc",
            "message": "boom"
        })))
        .with_status(200)
        .with_header("content-type", "application/json")
        .with_body(r#"{"id":"abc-123","project":"svc","language":"rust","tags":[],"created_at":"2024-01-01T00:00:00Z","explanation":"ok","saved_path":null}"#)
        .create_async()
        .await;

    let client = ErrorBrainClient::new(server.url());
    let report = ErrorReport::new("rust", "svc", "boom");

    let response = client.send_error(&report).await.expect("request should succeed");

    assert_eq!(response.id, "abc-123");
    assert_eq!(response.project, "svc");
    assert_eq!(response.language, "rust");
}

#[tokio::test]
async fn send_error_handles_failure() {
    let mut server = Server::new_async().await;
    let _m = server
        .mock("POST", "/v1/errors")
        .with_status(500)
        .with_body("internal error")
        .create_async()
        .await;

    let client = ErrorBrainClient::new(server.url());
    let report = ErrorReport::new("rust", "svc", "boom");

    let result = client.send_error(&report).await;

    match result {
        Err(ErrorBrainError::RequestFailed(status, msg)) => {
            assert_eq!(status, 500);
            assert!(msg.contains("internal error") || msg.is_empty());
        }
        other => panic!("unexpected result: {:?}", other),
    }
}

#[tokio::test]
async fn send_error_handles_invalid_json() {
    let mut server = Server::new_async().await;
    let _m = server
        .mock("POST", "/v1/errors")
        .with_status(200)
        .with_header("content-type", "application/json")
        .with_body("not-json")
        .create_async()
        .await;

    let client = ErrorBrainClient::new(server.url());
    let report = ErrorReport::new("rust", "svc", "boom");

    let result = client.send_error(&report).await;

    match result {
        Err(ErrorBrainError::SerializationError(msg)) => {
            assert!(msg.contains("json") || !msg.is_empty());
        }
        other => panic!("expected serialization error, got {:?}", other),
    }
}
