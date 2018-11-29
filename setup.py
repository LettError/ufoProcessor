#!/usr/bin/env python

import sys
from setuptools import setup, find_packages
from io import open


needs_wheel = {'bdist_wheel'}.intersection(sys.argv)
wheel = ['wheel'] if needs_wheel else []

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="ufoProcessor",
    use_scm_version={"write_to": "Lib/ufoProcessor/_version.py"},
    description="Read, write and generate UFOs with designspace data.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Erik van Blokland",
    author_email="erik@letterror.com",
    url="https://github.com/LettError/ufoProcessor",
    keywords='font development tools',
    license="MIT",
    packages=find_packages("Lib"),
    package_dir={"": "Lib"},
    python_requires='>=2.7',
    setup_requires=wheel + ["setuptools_scm"],
    install_requires=[
        "defcon[lxml]>=0.6.0",
        "fontMath>=0.4.9",
        "fontParts>=0.8.2",
        "fontTools[ufo,lxml]>=3.32.0",
        "mutatorMath>=2.1.2",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
