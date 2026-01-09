#include "errorbrain/error.h"
#include "errorbrain/errorbrain.h"
#include "errorbrain/models.h"

#include <gtest/gtest.h>
#include <future>
#include <type_traits>
#include <utility>

using ErrorBrain::ClientConfig;
using ErrorBrain::ErrorBrainClient;
using ErrorBrain::ErrorReport;
using ErrorBrain::NetworkError;
using ErrorBrain::RequestFailedError;
using ErrorBrain::SerializationError;

static_assert(std::is_same_v<decltype(std::declval<ErrorBrainClient>().health_check_async()),
                                 std::future<ErrorBrain::HealthResponse>>,
              "health_check_async should return std::future<HealthResponse>");
static_assert(std::is_same_v<decltype(std::declval<ErrorBrainClient>().send_error_async(
                                   std::declval<ErrorReport>())),
                                 std::future<ErrorBrain::ErrorResponse>>,
              "send_error_async should return std::future<ErrorResponse>");
static_assert(std::is_default_constructible_v<ErrorBrainClient>,
                            "ErrorBrainClient should be default constructible using env or fallback");

TEST(ClientConfigTest, AppliesTimeoutAndHeaders) {
    ClientConfig config("http://localhost:8000");
    config.with_timeout(5000).add_header("X-Test", "1");

    EXPECT_EQ(config.base_url(), "http://localhost:8000");
    EXPECT_EQ(config.timeout_ms(), 5000);
    ASSERT_EQ(config.headers().size(), 1u);
    EXPECT_EQ(config.headers().at("X-Test"), "1");
}

TEST(ErrorTypesTest, RequestFailedCarriesStatus) {
    RequestFailedError err(503, "maintenance");
    EXPECT_EQ(err.status_code(), 503);
    EXPECT_NE(std::string(err.what()).find("503"), std::string::npos);
    EXPECT_NE(std::string(err.what()).find("maintenance"), std::string::npos);
}

TEST(ErrorTypesTest, SerializationErrorHasMessage) {
    SerializationError err("bad json");
    EXPECT_NE(std::string(err.what()).find("Serialization error"), std::string::npos);
    EXPECT_NE(std::string(err.what()).find("bad json"), std::string::npos);
}

TEST(ErrorBrainClientTest, ConstructsWithBaseUrl) {
    EXPECT_NO_THROW({ ErrorBrainClient client("http://localhost:8000"); });
}

TEST(ErrorBrainClientTest, ConstructsWithConfig) {
    ClientConfig config("http://localhost:8000");
    config.with_timeout(1000);
    EXPECT_NO_THROW({ ErrorBrainClient client(config); });
}
