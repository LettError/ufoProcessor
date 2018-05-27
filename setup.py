#!/usr/bin/env python

from setuptools import setup

setup(name = "ufoProcessor",
      version = "0.3",
      description = "Python object to read, write and generate designspace data.",
      author = "Erik van Blokland",
      author_email = "erik@letterror.com",
      url = "https://github.com/LettError/ufoProcessor",
      license = "MIT",
      packages = [
              "ufoProcessor",
      ],
      package_dir = {"":"Lib"},
)
