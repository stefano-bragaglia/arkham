from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("python.pycharm")


name = "arkham"
version = "0.0.1"
summary = "Arkham Horror LCG"
description = "Experiments with Arkham Horror LCG"
author = "Stefano Bragaglia"
license = "Later"
url = "Later"
default_task = ["clean", "analyze", "publish", "install"]


@init
def set_properties(project):
    project.set_property("flake8_break_build", True)  # default is False
    project.set_property("flake8_verbose_output", True)  # default is False
    project.set_property("flake8_radon_max", 10)  # default is None
    project.set_property_if_unset("flake8_max_complexity", 10)  # default is None
    # Complexity: <= 10 is easy, <= 20 is complex, <= 50 great difficulty, > 50 unmaintainable

    project.set_property("coverage_break_build", True)  # default is False
    project.set_property("coverage_verbose_output", True)  # default is False
    project.set_property("coverage_allow_non_imported_modules", False)  # default is True
    project.set_property("coverage_exceptions", [
        "__init__",
        "arkham",
        "arkham.basic",
        "arkham.phases",
        "arkham.newer",
        "arkham.investigators",
    ])
    
    project.set_property("coverage_threshold_warn", 35)  # default is 70
    project.set_property("coverage_branch_threshold_warn", 35)  # default is 0
    project.set_property("coverage_branch_partial_threshold_warn", 35)  # default is 0

    project.set_property("dir_source_unittest_python", "src/test/python")
    project.set_property("unittest_module_glob", "tests_*")

    project.depends_on("assertpy")
    project.depends_on_requirements("requirements.txt")
