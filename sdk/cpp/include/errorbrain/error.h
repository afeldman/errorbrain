#ifndef ERRORBRAIN_ERROR_H
#define ERRORBRAIN_ERROR_H

#include <exception>
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
    explicit ErrorBrainException(std::string message);

    /// Get error message
    const char* what() const noexcept override;

protected:
    std::string message_;
};

/// Network error exception
class NetworkError : public ErrorBrainException {
public:
    explicit NetworkError(std::string message);
};

/// Request failed exception
class RequestFailedError : public ErrorBrainException {
public:
    RequestFailedError(int status_code, std::string message);

    int status_code() const;

private:
    int status_code_;
};

/// Invalid response exception
class InvalidResponseError : public ErrorBrainException {
public:
    InvalidResponseError();
};

/// Serialization error exception
class SerializationError : public ErrorBrainException {
public:
    explicit SerializationError(std::string message);
};

/// Configuration error exception
class ConfigError : public ErrorBrainException {
public:
    explicit ConfigError(std::string message);
};

} // namespace ErrorBrain

#endif // ERRORBRAIN_ERROR_H
