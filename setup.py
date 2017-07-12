"""Credits https://pythonhosted.org/an_example_pypi_project/setuptools.html"""
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="falcon-stats",
    version="0.5",
    author="Dominik Muhs",
    author_email="dominik.muhs@outlook.com",
    description=("A simple middleware to gather request-response statistics "
                 "from the falcon REST framework"),
    license="MIT",
    keywords="falcon falconframework rest-api statistics middleware",
    url="https://github.com/dmuhs/falcon-stats",
    packages=['falconstats', 'tests'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "License :: OSI Approved :: MIT License"
    ],
)
