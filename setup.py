try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import find_packages, setup

with open("README.rst") as f:
    long_description = f.read()

setup(
    name="redo",
    version="3.0.0",
    description="Utilities to retry Python callables.",
    long_description=long_description,
    author="Ben Hearsum",
    author_email="ben@hearsum.ca",
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["retry = redo.cmd:main"]},
    url="https://github.com/mozilla-releng/redo",
    license="MPL-2.0",
    classifiers=[
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
