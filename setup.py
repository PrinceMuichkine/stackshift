from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stackshift",
    version="0.1.0",
    author="princemuichkine",
    author_email="dev@psychoroid.com",
    description="A CLI tool to migrate Vite projects to Next.js",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/princemuichkine/stackshift",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "anthropic>=0.18.0",
        "rich>=10.0.0",
        "prompt_toolkit>=3.0.0",
        "aiofiles>=0.8.0",
    ],
    entry_points={
        "console_scripts": [
            "stackshift=stackshift.cli:app",
        ],
    },
) 