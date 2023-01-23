"""A setuptools based setup module.
"""
#!/usr/bin/env python

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name="uptrain",
    version="0.1.dev0",
    description="UpTrain - ML Observability and Retraining Framework",
    long_description="Smart and Automated Model Refinement",
    # The project's main homepage.
    url="https://github.com/uptrain-ai/uptrain",
    # Author details
    maintainer="UpTrain AI Team",
    maintainer_email="uptrain.ai@gmail.com",
    # Choose your license
    license="Apache License 2.0",
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
        "License :: OSI Approved :: Apache Software License",
        # Specify the Python versions you support here. In particular, ensure
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="uptrain ai retraining ML observability",
    packages=find_packages(),
    install_requires=[
        "imgaug==0.4.0",
        "numpy==1.24.1",
        "pandas==1.5.2",
        "plotly==5.11.0",
        "pydantic==1.10.4",
        "scikit_learn==1.2.0",
        "scipy==1.10.0",
        "seaborn==0.12.2",
        "setuptools==65.6.3",
        "streamlit==1.16.0",
        "tensorboardX==2.5.1",
        "torch==1.13.1",
        "xgboost==1.7.3",
        "joblib==1.2.0",
        "tensorboard==2.11.0",
        "jupyterlab==3.5.2",
    ],
)
