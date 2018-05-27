#!/usr/bin/env python

from setuptools import setup

setup(name = "ufoProcessor",
      version = "1.0",
      description = "Read, write and generate UFOs with designspace data.",
      author = "Erik van Blokland",
      author_email = "erik@letterror.com",
      url = "https://github.com/LettError/ufoProcessor",
      keywords='font development tools',
      license = "MIT",
      packages = [
              "ufoProcessor",
      ],
      package_dir = {"":"Lib"},
      python_requires='>=2.7',
)
