import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nova-pid-viz",
    version="0.0.1",
    author="Leigh Oliver",
    author_email="leighcharlesoliver@gmail.com",
    description="Package under development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leighleighleigh/nova_pid_viz",
    project_urls={
        "Bug Tracker": "https://github.com/leighleighleigh/nova_pid_viz/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)