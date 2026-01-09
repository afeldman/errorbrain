#include "errorbrain/error.h"

#include <string>
#include <utility>

namespace ErrorBrain {

ErrorBrainException::ErrorBrainException(std::string message)
	: message_(std::move(message)) {}

const char* ErrorBrainException::what() const noexcept { return message_.c_str(); }

NetworkError::NetworkError(std::string message)
	: ErrorBrainException(std::move(message)) {}

RequestFailedError::RequestFailedError(int status_code, std::string message)
	: ErrorBrainException("Request failed with status " + std::to_string(status_code) +
						  ": " + message),
	  status_code_(status_code) {}

int RequestFailedError::status_code() const { return status_code_; }

InvalidResponseError::InvalidResponseError()
	: ErrorBrainException("Invalid response from server") {}

SerializationError::SerializationError(std::string message)
	: ErrorBrainException("Serialization error: " + std::move(message)) {}

ConfigError::ConfigError(std::string message)
	: ErrorBrainException("Configuration error: " + std::move(message)) {}

} // namespace ErrorBrain
