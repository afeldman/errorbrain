#ifndef ERRORBRAIN_CLIENT_H
#define ERRORBRAIN_CLIENT_H

#include "error.h"
#include "models.h"
#include <memory>
#include <string>

namespace ErrorBrain {

/// ErrorBrain API client
/// \brief Async HTTP client for ErrorBrain API
/// \example
/// ```cpp
/// ErrorBrainClient client("http://localhost:8000");
/// auto health = client.health_check();
/// std::cout << "Status: " << health.status() << std::endl;
///
/// ErrorReport report("cpp", "my-service", "Something went wrong");
/// auto response = client.send_error(report);
/// std::cout << "Error ID: " << response.id() << std::endl;
/// ```
class ErrorBrainClient {
public:
    /// Create a new ErrorBrain client
    /// \param base_url Base URL of the ErrorBrain API
    explicit ErrorBrainClient(const std::string& base_url);

    /// Create a new ErrorBrain client with custom configuration
    /// \param config Client configuration
    explicit ErrorBrainClient(const ClientConfig& config);

    /// Destructor
    ~ErrorBrainClient();

    /// Check if API is healthy
    /// \throws NetworkError if connection fails
    /// \throws RequestFailedError if API returns error
    /// \throws InvalidResponseError if response is invalid
    /// \return Health check response
    HealthResponse health_check() const;

    /// Send error report to ErrorBrain
    /// \param report Error report to send
    /// \throws NetworkError if connection fails
    /// \throws RequestFailedError if API returns error
    /// \throws SerializationError if response parsing fails
    /// \return Error response with ID and explanation
    ErrorResponse send_error(const ErrorReport& report) const;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace ErrorBrain

#endif // ERRORBRAIN_CLIENT_H
