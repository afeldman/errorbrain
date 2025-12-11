/// \file
/// Metadata ErrorBrain C++ SDK example

#include <errorbrain/errorbrain.h>
#include <iostream>
#include <map>

int main() {
    std::cout << "ErrorBrain C++ SDK - Metadata Example" << std::endl;
    std::cout << "====================================" << std::endl << std::endl;

    try {
        ErrorBrain::ErrorBrainClient client;

        // Create comprehensive metadata
        std::map<std::string, std::string> metadata{
            {"endpoint", "/api/v1/users"},
            {"method", "POST"},
            {"client_ip", "203.0.113.42"},
            {"requests_per_minute", "1200"},
            {"limit", "1000"},
            {"user_id", "user_12345"},
        };

        ErrorBrain::ErrorReport report("cpp", "api-gateway", "Rate limit exceeded");
        report.with_tags({"api", "rate-limit", "production"})
            .with_metadata(metadata)
            .with_store_in_vault(true);

        auto response = client.send_error(report);
        std::cout << "✅ Error with metadata sent" << std::endl;
        std::cout << "   ID: " << response.id() << std::endl;
        std::cout << "   Tags: ";
        for (size_t i = 0; i < response.tags().size(); ++i) {
            if (i > 0) std::cout << ", ";
            std::cout << response.tags()[i];
        }
        std::cout << std::endl;
        std::cout << "   Analysis: " << response.explanation() << std::endl;

    } catch (const ErrorBrain::ErrorBrainException& e) {
        std::cerr << "❌ Failed to send error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
