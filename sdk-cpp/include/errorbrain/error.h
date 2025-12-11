#ifndef ERRORBRAIN_ERROR_H
#define ERRORBRAIN_ERROR_H

#include <exception>
#include <iostream>
#include <string>

namespace ErrorBrain {

/// Error types for ErrorBrain SDK.
///
/// Usage:
/// ```cpp
/// try {
///     client.health_check();
/// } catch (const ErrorBrainException& e) {
///     std::cerr << "Error: " << e.what() << std::endl;
/// }
/// ```
class ErrorBrainException : public std::exception {
public:
    /// Construct exception with message
    explicit ErrorBrainException(const std::string& message) : message_(message) {}

    /// Get error message
    const char* what() const noexcept override { return message_.c_str(); }

private:
    std::string message_;
};

/// Network error exception
class NetworkError : public ErrorBrainException {
public:
    explicit NetworkError(const std::string& message) : ErrorBrainException(message) {}
};

/// Request failed exception
class RequestFailedError : public ErrorBrainException {
public:
    RequestFailedError(int status_code, const std::string& message)
        : ErrorBrainException("Request failed with status " + std::to_string(status_code) +
                              ": " + message),
          status_code_(status_code) {}

    int status_code() const { return status_code_; }

private:
    int status_code_;
};

/// Invalid response exception
class InvalidResponseError : public ErrorBrainException {
public:
    InvalidResponseError() : ErrorBrainException("Invalid response from server") {}
};

/// Serialization error exception
class SerializationError : public ErrorBrainException {
public:
    explicit SerializationError(const std::string& message)
        : ErrorBrainException("Serialization error: " + message) {}
};

/// Configuration error exception
class ConfigError : public ErrorBrainException {
public:
    explicit ConfigError(const std::string& message)
        : ErrorBrainException("Configuration error: " + message) {}
};

} // namespace ErrorBrain

#endif // ERRORBRAIN_ERROR_H
