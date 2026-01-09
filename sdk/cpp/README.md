# ErrorBrain C++ SDK

Modern C++ client for [ErrorBrain](https://github.com/errorbrain/errorbrain) - AI-powered debugging memory.

## 🚀 Features

- ✅ **C++17** - Modern C++ standard
- ✅ **Header-only option** - Easy integration
- ✅ **Type-safe** - Strong type system
- ✅ **Exception-based** - C++ idiomatic error handling
- ✅ **Zero-overhead** - Optimized performance
- ✅ **Doxygen docs** - Full API documentation
- ✅ **CMake** - Easy build and integration

## 📦 Installation

### Using Conan

```toml
[requires]
errorbrain-sdk/0.1.0

[generators]
CMakeDeps
CMakeToolchain
```

Then build with:

```bash
conan install . && cmake -B build && cmake --build build
```

### Manual Installation

1. Clone ErrorBrain repository
2. Add sdk-cpp to your project
3. Link against the library

## 🔧 Quick Start

```cpp
#include <errorbrain/errorbrain.h>
#include <iostream>

int main() {
    ErrorBrain::ErrorBrainClient client("http://localhost:8000");

    // Health check
    auto health = client.health_check();
    std::cout << "Status: " << health.status() << std::endl;

    // Send error
    ErrorBrain::ErrorReport report("cpp", "my-service", "Something went wrong");
    auto response = client.send_error(report);
    std::cout << "Error ID: " << response.id() << std::endl;
    std::cout << "Explanation: " << response.explanation() << std::endl;

    return 0;
}
```

## 📖 Examples

Build and run examples:

```bash
conan install . --build=missing
cmake -B build -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake
cmake --build build

./build/bin/example_basic
./build/bin/example_exception
./build/bin/example_metadata
```

## 🔌 API Reference

### ErrorBrainClient

Main client class for ErrorBrain API.

#### Methods

- `ErrorBrainClient(base_url)` - Create with URL
- `ErrorBrainClient(config)` - Create with configuration
- `health_check()` - Check API health and configuration
- `send_error(report)` - Send error report

#### Exceptions

- `NetworkError` - Network/connection failure
- `RequestFailedError` - API returned error
- `InvalidResponseError` - Response parsing failed
- `SerializationError` - JSON serialization error

### ErrorReport

Builder-style error report class.

```cpp
ErrorBrain::ErrorReport report("cpp", "my-service", "Error message");
report.with_tags({"prod", "db"})
      .with_traceback("stack trace")
      .with_metadata({{"key", "value"}})
      .with_store_in_vault(true);
```

## 🧪 Testing

```bash
conan install . --build=missing -o errorbrain-sdk/*:with_tests=True
cmake -B build && cmake --build build
ctest --output-on-failure
```

## 🏗️ Build Options

- `with_examples=True/False` - Build examples
- `with_tests=True/False` - Build unit tests
- `shared=True/False` - Build shared or static library

## 📝 Documentation

Generate Doxygen documentation:

```bash
doxygen Doxyfile
# Open build/docs/html/index.html
```

## 📝 License

MIT

## 🔗 Links

- [ErrorBrain Repository](https://github.com/errorbrain/errorbrain)
- [C++17 Standard](https://en.cppreference.com/)
- [CMake Documentation](https://cmake.org/documentation/)
