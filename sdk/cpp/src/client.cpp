#include "errorbrain/errorbrain.h"
#include "errorbrain/error.h"
#include <curl/curl.h>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <utility>

namespace ErrorBrain {

// CURL callback for response body
static size_t write_callback(void* contents, size_t size, size_t nmemb, std::string* response) {
    response->append((char*)contents, size * nmemb);
    return size * nmemb;
}

// CURL callback for response headers
static size_t header_callback(char* buffer, size_t size, size_t nmemb, void* userp) {
    return size * nmemb;
}

class ErrorBrainClient::Impl {
public:
    explicit Impl(const ClientConfig& config) : config_(config) {}

    const ClientConfig& config() const { return config_; }

private:
    ClientConfig config_;
};

ErrorBrainClient::ErrorBrainClient(const std::string& base_url)
    : impl_(std::make_unique<Impl>(ClientConfig(base_url))) {}

ErrorBrainClient::ErrorBrainClient(const ClientConfig& config)
    : impl_(std::make_unique<Impl>(config)) {}

ErrorBrainClient::ErrorBrainClient()
    : ErrorBrainClient([] {
          const char* env = std::getenv("ERRORBRAIN_API_URL");
          return env != nullptr ? std::string(env) : std::string("http://localhost:8000");
      }()) {}

ErrorBrainClient::~ErrorBrainClient() = default;

HealthResponse ErrorBrainClient::health_check() const {
    CURL* curl = curl_easy_init();
    if (!curl) {
        throw NetworkError("Failed to initialize CURL");
    }

    std::string response_body;
    std::string url = impl_->config().base_url() + "/healthz";
    long response_code = 0;

    try {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, impl_->config().timeout_ms());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_body);
        curl_easy_setopt(curl, CURLOPT_HEADERFUNCTION, header_callback);

        CURLcode res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            throw NetworkError(std::string("Health check failed: ") +
                               curl_easy_strerror(res));
        }

        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);

        if (response_code != 200) {
            throw RequestFailedError(response_code, "Health check failed");
        }

        curl_easy_cleanup(curl);

        try {
            json response_json = json::parse(response_body);
            return HealthResponse(response_json);
        } catch (const std::exception& e) {
            throw InvalidResponseError();
        }
    } catch (...) {
        curl_easy_cleanup(curl);
        throw;
    }
}

ErrorResponse ErrorBrainClient::send_error(const ErrorReport& report) const {
    CURL* curl = curl_easy_init();
    if (!curl) {
        throw NetworkError("Failed to initialize CURL");
    }

    std::string response_body;
    std::string url = impl_->config().base_url() + "/v1/errors";
    long response_code = 0;
    json report_json = report.to_json();
    std::string report_str = report_json.dump();

    try {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, impl_->config().timeout_ms());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_body);
        curl_easy_setopt(curl, CURLOPT_HEADERFUNCTION, header_callback);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, report_str.c_str());

        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        CURLcode res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            curl_slist_free_all(headers);
            throw NetworkError(std::string("Error send failed: ") +
                               curl_easy_strerror(res));
        }

        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
        curl_slist_free_all(headers);

        if (response_code != 200) {
            throw RequestFailedError(response_code, response_body);
        }

        curl_easy_cleanup(curl);

        try {
            json response_json = json::parse(response_body);
            return ErrorResponse(response_json);
        } catch (const std::exception& e) {
            throw SerializationError(e.what());
        }
    } catch (...) {
        curl_easy_cleanup(curl);
        throw;
    }
}

std::future<HealthResponse> ErrorBrainClient::health_check_async() const {
    return std::async(std::launch::async, [this]() { return this->health_check(); });
}

std::future<ErrorResponse> ErrorBrainClient::send_error_async(ErrorReport report) const {
    return std::async(std::launch::async, [this, report = std::move(report)]() {
        return this->send_error(report);
    });
}

} // namespace ErrorBrain
