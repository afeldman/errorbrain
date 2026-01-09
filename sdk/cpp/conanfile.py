from conan import ConanFile
from conan.tools.cmake import cmake_layout
from conan.tools.cmake import CMake


class ErrorBrainConan(ConanFile):
    name = "errorbrain-sdk"
    version = "0.1.0"
    description = "ErrorBrain SDK for C++ - AI-powered debugging memory"
    author = "ErrorBrain Contributors"
    license = "MIT"
    homepage = "https://github.com/afeldman/errorbrain"
    url = "https://github.com/afeldman/errorbrain"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_examples": [True, False],
        "with_tests": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_examples": True,
        "with_tests": True,
    }

    requires = (
        "nlohmann_json/3.11.2",
        "openssl/3.2.0",
        "zlib/1.3",
        "curl/8.5.0",
        "boost/1.83.0",
    )

    build_requires = (
        "cmake/3.27.6",
        "gtest/1.14.0",
    )

    exports_sources = "src/*", "include/*", "examples/*", "tests/*", "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options["curl"].shared = True

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["errorbrain"]
