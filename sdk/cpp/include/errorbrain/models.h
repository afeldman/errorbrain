#ifndef ERRORBRAIN_MODELS_H
#define ERRORBRAIN_MODELS_H

#include <chrono>
#include <map>
#include <nlohmann/json.hpp>
#include <optional>
#include <string>
#include <vector>

namespace ErrorBrain {

using json = nlohmann::json;

/// Configuration for ErrorBrain client
/// \brief Holds client settings like base URL and timeout
class ClientConfig {
public:
    /// Constructor
    /// \param base_url Base URL of the ErrorBrain API
    explicit ClientConfig(const std::string& base_url) : base_url_(base_url), timeout_ms_(30000) {}

    /// Get base URL
    [[nodiscard]] const std::string& base_url() const { return base_url_; }

    /// Get timeout in milliseconds
    [[nodiscard]] uint64_t timeout_ms() const { return timeout_ms_; }

    /// Set timeout in milliseconds
    ClientConfig& with_timeout(uint64_t timeout_ms) {
        timeout_ms_ = timeout_ms;
        return *this;
    }

    /// Get headers
    [[nodiscard]] const std::map<std::string, std::string>& headers() const { return headers_; }

    /// Add header
    ClientConfig& add_header(const std::string& key, const std::string& value) {
        headers_[key] = value;
        return *this;
    }

private:
    std::string base_url_;
    uint64_t timeout_ms_;
    std::map<std::string, std::string> headers_;
};

/// Error report to send to ErrorBrain API
/// \brief Builder-style error report
class ErrorReport {
public:
    /// Constructor
    /// \param language Programming language (e.g., "cpp", "rust", "python")
    /// \param project Project or service name
    /// \param message Error message
    ErrorReport(const std::string& language, const std::string& project,
                const std::string& message)
        : language_(language),
          project_(project),
          message_(message),
          traceback_(std::nullopt),
          store_in_vault_(true) {}

    /// Get language
    [[nodiscard]] const std::string& language() const { return language_; }

    /// Get project
    [[nodiscard]] const std::string& project() const { return project_; }

    /// Get message
    [[nodiscard]] const std::string& message() const { return message_; }

    /// Get traceback
    [[nodiscard]] const std::optional<std::string>& traceback() const { return traceback_; }

    /// Get tags
    [[nodiscard]] const std::vector<std::string>& tags() const { return tags_; }

    /// Get metadata
    [[nodiscard]] const std::optional<std::map<std::string, std::string>>& metadata() const {
        return metadata_;
    }

    /// Get store_in_vault
    [[nodiscard]] bool store_in_vault() const { return store_in_vault_; }

    /// Add tags
    ErrorReport& with_tags(const std::vector<std::string>& tags) {
        tags_ = tags;
        return *this;
    }

    /// Set traceback
    ErrorReport& with_traceback(const std::string& traceback) {
        traceback_ = traceback;
        return *this;
    }

    /// Add metadata
    ErrorReport& with_metadata(const std::map<std::string, std::string>& metadata) {
        metadata_ = metadata;
        return *this;
    }

    /// Set store_in_vault
    ErrorReport& with_store_in_vault(bool store) {
        store_in_vault_ = store;
        return *this;
    }

    /// Convert to JSON for API call
    [[nodiscard]] json to_json() const;

private:
    std::string language_;
    std::string project_;
    std::string message_;
    std::optional<std::string> traceback_;
    std::vector<std::string> tags_;
    std::optional<std::map<std::string, std::string>> metadata_;
    bool store_in_vault_;
};

/// Response from ErrorBrain API
/// \brief Contains error information and AI analysis
class ErrorResponse {
public:
    /// Constructor from JSON
    explicit ErrorResponse(const json& j);

    /// Get error ID
    [[nodiscard]] const std::string& id() const { return id_; }

    /// Get project
    [[nodiscard]] const std::string& project() const { return project_; }

    /// Get language
    [[nodiscard]] const std::string& language() const { return language_; }

    /// Get tags
    [[nodiscard]] const std::vector<std::string>& tags() const { return tags_; }

    /// Get created_at timestamp
    [[nodiscard]] const std::string& created_at() const { return created_at_; }

    /// Get explanation
    [[nodiscard]] const std::string& explanation() const { return explanation_; }

    /// Get saved path (if any)
    [[nodiscard]] const std::optional<std::string>& saved_path() const { return saved_path_; }

private:
    std::string id_;
    std::string project_;
    std::string language_;
    std::vector<std::string> tags_;
    std::string created_at_;
    std::string explanation_;
    std::optional<std::string> saved_path_;
};

/// Health check response
/// \brief Contains API status and configuration
class HealthResponse {
public:
    /// Constructor from JSON
    explicit HealthResponse(const json& j);

    /// Get status
    [[nodiscard]] const std::string& status() const { return status_; }

    /// Check if LLM is configured
    [[nodiscard]] bool llm_configured() const { return llm_configured_; }

    /// Check if vault is configured
    [[nodiscard]] bool vault_configured() const { return vault_configured_; }

    /// Get vault path (if configured)
    [[nodiscard]] const std::optional<std::string>& vault_path() const { return vault_path_; }

private:
    std::string status_;
    bool llm_configured_;
    bool vault_configured_;
    std::optional<std::string> vault_path_;
};

} // namespace ErrorBrain

#endif // ERRORBRAIN_MODELS_H
