from setuptools import setup

setup(
    name="retry",
    version="1.0",
    description="Utilities to retry Python callables.",
    author="Mozilla Release Engineering",
    author_email="release+pypi@mozilla.com",
    packages=["retry"],
    entry_points={
        "console_scripts": ["retry = retry.cmd:main"],
    },
)
