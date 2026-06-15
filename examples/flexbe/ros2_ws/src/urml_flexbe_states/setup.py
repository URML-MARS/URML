"""ament_python setup for urml_flexbe_states."""

from setuptools import find_packages, setup

package_name = "urml_flexbe_states"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="URML Maintainers",
    maintainer_email="greenvh@gmail.com",
    description="FlexBE states for URML (ExecuteUrmlState).",
    license="Apache-2.0",
    tests_require=["pytest"],
)
