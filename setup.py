from setuptools import setup, find_packages

setup(
    name="sliver-tor-bridge",
    version="1.0.0",
    author="Otsmane Ahmed",
    author_email="your.email@example.com",
    description="Tor-based transport bridge for Sliver C2",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Otsmane-Ahmed/sliver-tor-bridge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.28.0",
        "pysocks>=1.7.1",
        "stem>=1.8.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "sliver-tor-bridge=sliver_tor_bridge.cli:cli",
        ],
    },
)
