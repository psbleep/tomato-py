#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import io
from setuptools import setup

setup(
    name="tomato-py",
    version="0.0.1",
    description="Pomodoro timer for the terminal",
    keywords="pomodoro,timer,time",
    author="Patrick Schneeweis",
    author_email="psbleep@protonmail.com",
    url="https://github.com/psbleep/tomato_py",
    license="GPLv3",
    long_description=io.open("README.md", "r", encoding="utf-8").read(),
    platforms="any",
    zip_safe=False,
    include_package_data=True,
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["tomato_py"],
    install_requires=["click==7.1.2"],
    entry_points={
        "console_scripts": [
            "tomato = tomato_py.__main__:cli",
        ]
    },
)
