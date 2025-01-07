from setuptools import setup, find_packages

setup(
    name="testcontainers-demo-generator",
    version="0.1.0",
    description="A tool that generates production-quality demo applications showcasing Testcontainers integration testing patterns",
    author="Ganna Chernyshova",
    author_email="",  # Add author email if desired
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "crewai>=0.1.0",
        "crewai-tools>=0.0.4",
        "python-dotenv>=0.19.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "testcontainers-demo-generator=testcontainers_demo_generator.main:run",
        ],
    },
    python_requires=">=3.11",
    include_package_data=True,
    package_data={
        "testcontainers_demo_generator": ["config/*.yaml"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Code Generators",
    ],
)
