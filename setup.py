from setuptools import setup, find_packages

setup(
    name="stackshift",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer[all]>=0.9.0,<0.10.0",
        "rich>=13.7.0,<14.0.0",
        "anthropic>=0.42.0,<0.43.0",
        "python-dotenv>=1.0.1,<2.0.0",
        "aiofiles>=23.2.1,<24.0.0",
        "prompt_toolkit>=3.0.43,<4.0.0",
        "pydantic>=2.5.0,<3.0.0",
        "jinja2>=3.1.2,<4.0.0",
        "ast-comments>=1.0.1,<2.0.0"
    ],
    entry_points={
        "console_scripts": [
            "stackshift=cli:app",
        ],
    },
    python_requires=">=3.8",
    author="Stackshift Team",
    description="A tool for migrating Vite projects to Next.js",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/stackshift/stackshift",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 