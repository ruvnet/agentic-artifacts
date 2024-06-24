from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentic-artifacts",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for generating and managing CodeSandbox artifacts using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ruvnet/agentic-artifacts",
    packages=find_packages(include=["agentic_artifacts", "agentic_artifacts.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "litestar",
        "openai",
        "requests",
        "litellm",
        "python-dotenv",
        "uvicorn",
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "agentic-artifacts=main:main",
        ],
    },
)
