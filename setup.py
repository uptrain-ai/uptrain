"""
A setuptools based setup module.
"""
#!/usr/bin/env python

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# sentence-tranformers deps (it installs torch-gpu by default)
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

setup(
    name="uptrain",
    version="0.3.1",
    description="UpTrain - ML Observability and Retraining Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # The project's main homepage.
    url="https://github.com/uptrain-ai/uptrain",
    # Author details
    maintainer="UpTrain AI Team",
    maintainer_email="uptrain.ai@gmail.com",
    # Choose your license
    license="Apache License 2.0",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: Apache Software License",
        # Specify the Python versions you support here. In particular, ensure
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="uptrain ai retraining ML observability",
    packages=find_packages(),
    package_data={"": ["*.pyi"]},
    install_requires=[
        # utilities
        "tqdm>=4.0",
        "pydantic<1.10.10",
        "aiolimiter>=1.1",
        "loguru",
        "lazy_loader",
        "networkx",
        # datasets and transforms
        "polars>=0.18",
        "deltalake>=0.9",
        "numpy>=1.23.0",
        "pyarrow>=10.0.0",
        # visualization
        "plotly>=5.0.0",
        "streamlit>=1.23",
        # llm related
        "openai>=0.27",
        "evals==1.0.3.post1",
        # "evals @ git+https://github.com/openai/evals.git@main",
        # access to remote execution
        "httpx>=0.24.1",
    ],
    extras_require={
        "v0": [
            "pandas>=1.0.0",
            "river",
            "scikit_learn>=1.0.0",
            "umap-learn",
            "json-fix>=0.5.0",
            "xgboost",
        ],
        "full": [
            "river<0.18",
            "scikit_learn>=1.0.0",
            "umap-learn",
            "rouge-score",
            "sentence-transformers",
            "InstructorEmbedding",
        ],
    },  # Optional
    tests_require=["pytest>=7.0"],
)
