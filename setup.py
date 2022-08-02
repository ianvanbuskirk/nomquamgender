from setuptools import setup, find_packages

with open("README_p.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nomquamgender",
    version="0.1.4",
    author="Ian Van Buskirk",
    author_email="ian@colorado.edu",
    description="Data and code to support name-based gender classification in scientific research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ianvanbuskirk/nomquamgender",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['unidecode', 'numpy', 'pandas'],
    include_package_data=True
)