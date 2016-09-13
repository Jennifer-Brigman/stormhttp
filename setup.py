from distutils.core import setup
from setuptools.command.test import test
from setuptools import find_packages
import stormhttp


class PyTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        import sys
        sys.exit(pytest.main(self.test_args))

setup(
    name="stormhttp",
    packages=find_packages(exclude=["tests", "bench", "build"]),
    version=stormhttp.__version__,
    description="Lightning-fast asynchronous web framework for Python 3.5+",
    license="MIT",
    author="Seth Michael Larson",
    author_email="sethmichaellarson@protonmail.com",
    url="https://github.com/SethMichaelLarson/stormhttp",
    download_url="https://github.com/SethMichaelLarson/stormhttp/archive/" + stormhttp.__version__ + ".tar.gz",
    keywords=["web", "async", "framework"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP"
    ],
    install_requires=[
        "brotlipy>=0.5.1",
        "cchardet>=1.0.0",
        "cryptography>=1.5",
        "httptools>=0.0.9",
        "Jinja2>=2.8"
    ],
    tests_require=[
        "pytest",
        "coverage",
        "coveralls",
        "pytest-sugar"
    ],
    cmdclass={
        "test": PyTest
    }
)
