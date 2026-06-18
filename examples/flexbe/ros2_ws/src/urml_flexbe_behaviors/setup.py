"""ament_python setup for urml_flexbe_behaviors."""

from glob import glob

from setuptools import find_packages, setup

package_name = "urml_flexbe_behaviors"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="URML Maintainers",
    maintainer_email="greenvh@gmail.com",
    description="FlexBE behaviors for URML (URML Turtle Patrol; URML UR-3e Pick-Place).",
    license="Apache-2.0",
    tests_require=["pytest"],
)
