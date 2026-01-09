#include "errorbrain/models.h"

#include <gtest/gtest.h>
#include <map>
#include <nlohmann/json.hpp>
#include <string>
#include <vector>

using ErrorBrain::ErrorReport;
using ErrorBrain::ErrorResponse;
using ErrorBrain::HealthResponse;
using json = nlohmann::json;

TEST(ErrorReportTest, ToJsonIncludesFields) {
    ErrorReport report("cpp", "service", "Boom");
    report.with_traceback("trace").with_tags({"prod", "api"}).with_metadata({{"key", "value"}});

    json payload = report.to_json();

    EXPECT_EQ(payload.at("language"), "cpp");
    EXPECT_EQ(payload.at("project"), "service");
    EXPECT_EQ(payload.at("message"), "Boom");
    EXPECT_EQ(payload.at("traceback"), "trace");
    ASSERT_TRUE(payload.contains("tags"));
    EXPECT_EQ(payload.at("tags").size(), 2);
    ASSERT_TRUE(payload.contains("metadata"));
    EXPECT_EQ(payload.at("metadata").at("key"), "value");
    EXPECT_TRUE(payload.at("store_in_vault").get<bool>());
}

TEST(ErrorResponseTest, ParsesSavedPathWhenPresent) {
    json payload = {
        {"id", "abc-123"},
        {"project", "svc"},
        {"language", "cpp"},
        {"tags", std::vector<std::string>{"prod"}},
        {"created_at", "2024-01-01T00:00:00Z"},
        {"explanation", "details"},
        {"saved_path", "/tmp/out"}
    };

    ErrorResponse response(payload);

    EXPECT_EQ(response.id(), "abc-123");
    EXPECT_EQ(response.project(), "svc");
    EXPECT_EQ(response.language(), "cpp");
    ASSERT_TRUE(response.saved_path().has_value());
    EXPECT_EQ(response.saved_path().value(), "/tmp/out");
}

TEST(ErrorResponseTest, HandlesMissingSavedPath) {
    json payload = {
        {"id", "abc-123"},
        {"project", "svc"},
        {"language", "cpp"},
        {"tags", std::vector<std::string>{"prod"}},
        {"created_at", "2024-01-01T00:00:00Z"},
        {"explanation", "details"},
        {"saved_path", nullptr}
    };

    ErrorResponse response(payload);

    EXPECT_FALSE(response.saved_path().has_value());
}

TEST(HealthResponseTest, ParsesConfigurationFlags) {
    json payload = {
        {"status", "ok"},
        {"llm_configured", true},
        {"vault_configured", false},
        {"vault_path", nullptr}
    };

    HealthResponse response(payload);

    EXPECT_EQ(response.status(), "ok");
    EXPECT_TRUE(response.llm_configured());
    EXPECT_FALSE(response.vault_configured());
    EXPECT_FALSE(response.vault_path().has_value());
}
