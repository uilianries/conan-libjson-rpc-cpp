#!/usr/bin/python
# -*- coding: utf-8 -*-
from conans import ConanFile, tools, CMake
import os

class LibJsonRPCCPPConan(ConanFile):
    name = "libjson-rpc-cpp"
    version = "1.1.1"
    description = "C++ framework for json-rpc (json remote procedure call) "
    homepage = "https://github.com/cinemast/libjson-rpc-cpp"
    url = "http://gitlab.khomp.corp/conan/conan-libjson-rpc-cpp"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = "shared=True", "fPIC=True"
    exports_sources = ["CMakeLists.txt", "cmake.patch"]
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    requires = "jsoncpp/1.8.4@khomp/stable"
    patch_once = False

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        source_url = "https://github.com/cinemast/libjson-rpc-cpp"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)
        tools.patch(base_path=self.source_subfolder, patch_file="cmake.patch")
        tools.replace_in_file(os.path.join(self.source_subfolder, "CMakeLists.txt"), 'set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/lib")', "")
        tools.replace_in_file(os.path.join(self.source_subfolder, "CMakeLists.txt"), 'set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/bin")', "")
        tools.replace_in_file(os.path.join(self.source_subfolder, "CMakeLists.txt"), 'set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/lib")', "")

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        cmake.definitions["COMPILE_EXAMPLES"] = False
        cmake.definitions["COMPILE_TESTS"] = False
        cmake.definitions["COMPILE_STUBGEN"] = False
        cmake.definitions["REDIS_SERVER"] = False
        cmake.definitions["REDIS_CLIENT"] = False
        cmake.definitions["HTTP_SERVER"] = False
        cmake.definitions["HTTP_CLIENT"] = False
        cmake.definitions["TCP_SOCKET_SERVER"] = True
        cmake.definitions["WITH_COVERAGE"] = False
        cmake.configure()
        tools.replace_in_file(os.path.join("gen", "jsonrpccpp", "common", "jsonparser.h"), "#include <jsoncpp/json/json.h>", "#include <json/json.h>")
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", keep_path=False)
        self.copy("*.h", src=os.path.join("source_subfolder", "src", "jsonrpccpp"), dst=os.path.join("include", "jsonrpccpp"))
        self.copy("*.h", src=os.path.join("gen"), dst=os.path.join("include"))
        self.copy("*.so*", dst="lib", src="lib")
        self.copy("*.a", dst="lib", src="lib")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.append("pthread")
