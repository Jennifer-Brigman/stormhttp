from distutils.core import setup
from setuptools.command.test import test
from stormhttp import __version__


class PyTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        import sys
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name="stormhttp",
    packages=["stormhttp"],
    version=__version__,
    description="Performant asynchronous web application framework.",
    license="Apache 2",
    author="Seth Michael Larson",
    author_email="sethmichaellarson@protonmail.com",
    url="https://github.com/SethMichaelLarson/Stormsurge",
    download_url="https://github.com/SethMichaelLarson/Stormsurge/tarball/" + __version__,
    keywords=["web", "framework", "async"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP"
    ],
    install_requires=[
        "brotlipy==0.3.0",
        "cffi==1.7.0",
        "httptools==0.0.9",
        "pycparser==2.14"
    ],
    tests_require=[
        "pytest",
        "coverage",
        "coveralls"
    ],
    cmdclass={
        "test": PyTest
    }
)
