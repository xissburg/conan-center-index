from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"

class EdynConan(ConanFile):
    name = "edyn"
    version = "1.2.0"
    description = "Edyn is a real-time physics engine organized as an ECS"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xissburg/edyn"
    topics = ("physics", "game-development", "ecs")
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "floating_type": ["float", "double"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "floating_type": "float",
    }
    generators = "cmake", "cmake_find_package_multi"

    def requirements(self):
        self.requires("entt/3.10.1")

    @property
    def _compiler_required(self):
        return {
            "gcc": "9.3", # GCC 9.3 started supporting attributes in constructor arguments
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)
        try:
            minimum_required_compiler_version = self._compiler_required[str(self.settings.compiler)]
            if tools.Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration("This package requires C++17 support. The current compiler does not support it.")
        except KeyError:
            self.output.warn("This recipe has no support for the current compiler. Please consider adding it.")

    def source(self):
        self.run("git clone https://github.com/xissburg/edyn.git")
        self.run("cd edyn && git checkout v" + self.version)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["EDYN_INSTALL"] = True
        cmake.configure(source_folder="edyn")
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src="edyn")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "Edyn")
        self.cpp_info.set_property("cmake_file_name", "Edyn")
        self.cpp_info.set_property("cmake_target_name", "Edyn::Edyn")
        self.cpp_info.set_property("pkg_config_name", "Edyn")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs += ["m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winmm"]

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Edyn"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Edyn"
        self.cpp_info.names["cmake_find_package"] = "Edyn"
        self.cpp_info.names["cmake_find_package_multi"] = "Edyn"
