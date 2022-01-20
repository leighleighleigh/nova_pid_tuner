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
    install_requires=[
        'aenum==3.1.5',
        'numpy==1.22.0',
        'PyQt5==5.15.6',
        'PyQt5-Qt5==5.15.2',
        'PyQt5-sip==12.9.0',
        'pyqtgraph==0.12.3',
        'python-can==3.3.4',
        'wrapt==1.13.3'
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)