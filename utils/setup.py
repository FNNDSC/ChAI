from setuptools import setup

setup(
    name="docling-batch",
    version="0.1.0",
    py_modules=["docling_batch_convert"],
    install_requires=[
        "docling",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "docling-batch=docling_batch_convert:main",
        ],
    },
    author="Your Name",
    description="Batch converter using Docling for Markdown, text, and structured formats from many source types.",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
