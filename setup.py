from setuptools import setup, find_packages


setup(
    name="classy-mermaid",
    version="0.1.0",
    description="A MkDocs plugin to create class diagrams with mermaid",
    long_description="",
    keywords="mkdocs, mermaid",
    url="",
    author="Elizabeth Sall",
    author_email="elizabeth@urbanlabs.io",
    license="Apache 2.0",
    python_requires=">=3.7",
    install_requires=["mkdocs>=1.0.4"],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
)
