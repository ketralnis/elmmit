from setuptools import find_packages
from distutils.core import setup


setup(
    name='elmmit',
    packages=find_packages(),
    install_requires=[
        "flask",
    ]
)
