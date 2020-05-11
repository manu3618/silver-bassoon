#!/usr/bin/env python

from distutils.core import setup

REQUIREMENTS_FILENAMES = ["requirements.txt", "dev-requirements.txt"]


def requirements_from_file(filename):
    with open(filename) as fd:
        return fd.read().splitlines()


def get_requirements(filenames):
    req = []
    for filename in filenames:
        req.extend(requirements_from_file(filename))
    return req


setup(
    name="Silver-basson",
    version="0.0",
    description="No description available for now",
    author="manu",
    author_email="manu+gthub@hbrt.eu",
    url="https://github.com/manu3618/silver-bassoon.git",
    package_dir={"": "src"},
    packages=["bassoon"],
    install_requires=get_requirements(REQUIREMENTS_FILENAMES),
)
