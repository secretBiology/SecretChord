#  SecretBiology Copyright (c) 2021
#
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework
#

import setuptools

with open("PYPI.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SecretChord",
    version="0.0.1",
    author="Rohit Suratekar",
    author_email="rohitsuratekar@gmail.com",
    description="generate robust and beautiful Chord Diagrams",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/secretBiology/SecretChord",
    packages=setuptools.find_packages(),
    license='MIT License',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "numpy",
        "matplotlib",
        "SecretColors"
    ],
)
