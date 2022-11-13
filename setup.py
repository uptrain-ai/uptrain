"""A setuptools based setup module.
"""
#!/usr/bin/env python

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name="oodles",
    version="0.1.dev",
    description="An Oodles.ai retaining framework",
    long_description="Smart and Automated Model Refinement",
    # The project's main homepage.
    url="https://github.com/Oodles-ai/oodles",
    # Author details
    maintainer="Oodles AI Team",
    maintainer_email="vipul@oodles.ai",
    # Choose your license
    license="Apache 2.0",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: Apache 2.0 License",
        # Specify the Python versions you support here. In particular, ensure
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="oodles ai retraining ML",
    packages=find_packages(),
    install_requires=[],
)
