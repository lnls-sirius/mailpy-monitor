#!/usr/bin/env python3
import os
import pathlib
import sys

from setuptools import find_packages, setup

from src.mailpy import __author__, __author_email__, __source_url__, __version__

assert sys.version_info >= (3, 8, 5), "Project requires 3.8.5+"


CURRENT_DIR = pathlib.Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))  # for setuptools.build_meta


def get_abs_path(relative) -> str:
    return os.path.join(CURRENT_DIR, relative)


def _load_text(name: str) -> str:
    _path = get_abs_path(name)
    if not os.path.exists(_path):
        return ""

    with open(_path, "r") as f:
        return f.read().strip()


def get_long_description() -> str:

    desc = _load_text("README.md")

    desc += "\n\n"

    desc += _load_text("CHANGES.md")

    return desc


long_description = get_long_description()
requirements = _load_text("requirements.txt")


setup(
    name="mailpy",
    author=__author__,
    author_email=__author_email__,
    entry_points={
        "console_scripts": [
            "mailpy=mailpy_run:start_alarm_server",
            "mailpy-db=mailpy_run:start_test_database",
        ],
    },
    classifiers=[
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: EPICS",
    ],
    description="EPICS Alarm Server for Sirius",
    download_url=__source_url__,
    license="GNU GPLv3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__source_url__,
    project_urls={
        "Changelog": __source_url__,
    },
    version=__version__,
    install_requires=requirements,
    include_package_data=True,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"mailpy": ["resources/*"]},
    python_requires=">=3.8",
    scripts=[],
    test_suite="tests",
    zip_safe=False,
)
