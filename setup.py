try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import find_packages, setup


setup(
    name="redo",
    version="2.0.3",
    description="Utilities to retry Python callables.",
    author="Ben Hearsum",
    author_email="ben@hearsum.ca",
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["retry = redo.cmd:main"]},
    url="https://github.com/mozilla-releng/redo",
)
