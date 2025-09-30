from setuptools import setup, find_packages


setup(
    name="zyra-tool",
    version="1.0.8",
    author="Karthik Rishinarada",
    author_email="karthikdmy11135@gmail.com",
    description="zyra: A version control system that is built from scratch in python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/karthik11135/zyra",
    packages=find_packages(),
    py_modules=["zyra", "argparsing", "main"],
    include_package_data=True,
    install_requires=[
        "termcolor>=2.2.0",
    ],
    entry_points={
        "console_scripts": [
            "zyra=zyra:main",
        ],
    },
    python_requires=">=3.10",
)
