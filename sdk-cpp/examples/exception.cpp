/// \file
/// Exception handling ErrorBrain C++ SDK example

#include <errorbrain/errorbrain.h>
#include <iostream>

void risky_operation() {
    int values[] = {1, 2, 3};
    int size = 3;
    int index = 10;

    if (index >= size) {
        throw std::out_of_range("Array index out of bounds");
    }

    std::cout << values[index] << std::endl;
}

int main() {
    std::cout << "ErrorBrain C++ SDK - Exception Example" << std::endl;
    std::cout << "======================================" << std::endl << std::endl;

    try {
        risky_operation();
    } catch (const std::out_of_range& e) {
        std::cout << "Caught error: " << e.what() << std::endl << std::endl;

        try {
            ErrorBrain::ErrorBrainClient client;

            ErrorBrain::ErrorReport report("cpp", "data-pipeline",
                                           std::string("Error: ") + e.what());
            report.with_tags({"cron", "prod"});

            auto response = client.send_error(report);
            std::cout << "✅ Error logged" << std::endl;
            std::cout << "   ID: " << response.id() << std::endl;
            std::cout << "   Analysis: " << response.explanation() << std::endl;

        } catch (const ErrorBrain::ErrorBrainException& eb) {
            std::cerr << "❌ Failed to log error: " << eb.what() << std::endl;
            return 2;
        }
    }

    return 0;
}
