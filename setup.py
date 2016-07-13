from distutils.core import setup
from stormsurge import __version__

setup(
    name="stormsurge",
    packages=["stormsurge"],
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
    ]
)
