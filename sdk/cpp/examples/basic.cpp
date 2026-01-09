/// \file
/// Basic ErrorBrain C++ SDK example

#include <errorbrain/errorbrain.h>
#include <iostream>
#include <map>

int main() {
    std::cout << "ErrorBrain C++ SDK - Basic Example" << std::endl;
    std::cout << "==================================" << std::endl << std::endl;

    try {
        ErrorBrain::ErrorBrainClient client("http://localhost:8000");

        // Health check
        std::cout << "Checking API health..." << std::endl;
        auto health = client.health_check();
        std::cout << "✅ API is healthy" << std::endl;
        std::cout << "   Status: " << health.status() << std::endl;
        std::cout << "   LLM Configured: " << (health.llm_configured() ? "yes" : "no")
                  << std::endl << std::endl;

        // Create error report
        std::map<std::string, std::string> metadata{
            {"user_id", "12345"},
            {"request_id", "abc-def"},
        };

        ErrorBrain::ErrorReport report("cpp", "billing-service",
                                       "Database connection timeout");
        report.with_traceback("thread panicked at 'connection timeout'\n   at "
                              "db/connection.cpp:42:10")
            .with_tags({"prod", "database"})
            .with_metadata(metadata);

        // Send error
        std::cout << "Sending error report..." << std::endl;
        auto response = client.send_error(report);
        std::cout << "✅ Error sent successfully" << std::endl;
        std::cout << "   ID: " << response.id() << std::endl;
        std::cout << "   Explanation: " << response.explanation() << std::endl;
        if (response.saved_path()) {
            std::cout << "   Saved to: " << *response.saved_path() << std::endl;
        }

    } catch (const ErrorBrain::ErrorBrainException& e) {
        std::cerr << "❌ Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
