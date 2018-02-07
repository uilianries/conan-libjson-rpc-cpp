from conans import ConanFile
from conans.tools import download, unzip, check_with_algorithm_sum, cpu_count
import os
import glob

class JsonRPCCPPConan(ConanFile):
    name = "jsonrpc-cpp"
    version = "0.4"
    checksums = {
        "md5": "b01e0a9c54d5e511e33d4d5ba28bf958",
        "sha1": "2c83097708614f08dbb13be7c0a968e5d4d6e579",
        "sha256": "b6fd22acff6f4bcac70e2801b0f997d8a5dfcf39bb11901274e19fb8c9b1b39c"
    }
    khomp_src = "{}-{}.tar.bz2".format(name, version)
    khomp_src_folder = "{}-{}".format(name, version)
    khomp_conanfile_folder = os.path.dirname(__file__)
    description = "JsonRpc-Cpp is an OpenSource implementation of JSON-RPC protocol in C++. JSON-RPC is a lightweight remote procedure call protocol similar to XML-RPC."
    homepage = "https://sourceforge.net/projects/jsonrpc-cpp/"
    url = "https://downloads.sourceforge.net/project/jsonrpc-cpp/jsonrpc-cpp/{}?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fjsonrpc-cpp%2Ffiles%2Fjsonrpc-cpp%2F{}%2Fdownload&ts=1517403885".format(khomp_src, khomp_src)
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "txt"
    options = {
        "shared": [True, False, "Both"]
    }
    default_options = "shared=True"
    exports = "patches/*"
    requires = "jsoncpp/0.5.0@khomp/stable"

    def checksum(self):
        for (algorithm, result) in self.checksums.items():
            check_with_algorithm_sum(algorithm, self.khomp_src, result)

    def patch(self):
        khomp_patches_file = "{}/khomp-patches-applied".format(self.khomp_src_folder)
        if not os.path.isfile(khomp_patches_file):
            patches = glob.glob("{}/patches/*.patch".format(self.khomp_conanfile_folder))
            patches.sort()
            # apply patches
            for patch_file in patches:
                print("{}: patch source with {}".format(self.name, patch_file))
                self.run("cd {} && patch -p0 < {}".format(self.khomp_src_folder, patch_file))

            open(khomp_patches_file, "w").write("done")

    def source(self):
        if os.path.exists(self.khomp_src):
            try:
                self.checksum()
            except:
                os.unlink(self.khomp_src)
                self.source()
        else:
            download(self.url, self.khomp_src)
            self.checksum()

        if not os.path.exists(self.khomp_src_folder):
            # NOTE: conan unzip does not support xz
            # unzip(self.khomp_src)
            self.run("bzcat {} | tar x".format(self.khomp_src))

    def build(self):
        if self.settings.os == "Linux":
            self.source()
            self.patch()

            cpppath = ""
            libpath = ""

            cpppath += ":".join(self.deps_cpp_info["jsoncpp"].include_paths)
            libpath += ":".join(self.deps_cpp_info["jsoncpp"].lib_paths)

            self.run("cd {} && scons platform=linux-gcc cpppath={} libpath={} -j{}".format(self.khomp_src_folder, cpppath, libpath, cpu_count()))

    def package(self):
        self.copy("*.h", dst="include/", src="{}/src".format(self.khomp_src_folder), keep_path=False, excludes=("jsonrpc_httpclient.h", ))
        if self.options.shared in (True, "Both"):
            self.copy("libjsonrpc.so", dst="lib", src=self.khomp_src_folder, keep_path=False, symlinks=False)
        if self.options.shared in (False, "Both"):
            self.copy("libjsonrpc.a", dst="lib", src=self.khomp_src_folder, keep_path=False, symlinks=False)

    def package_info(self):
        self.cpp_info.libs = ["jsonrpc"]
