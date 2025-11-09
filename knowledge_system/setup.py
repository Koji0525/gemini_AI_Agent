
from setuptools import setup, find_packages

setup(
    name="knowledge_system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "faiss-cpu",
        "sentence-transformers",
        "sqlite3",
    ],
)
