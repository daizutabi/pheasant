import os
import re

from setuptools import find_packages, setup


def get_version(package):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        package, '__init__.py')
    with open(path, 'r') as file:
        source = file.read()
    m = re.search(r'__version__ = ["\'](.+)["\']', source)
    if m:
        return m.group(1)
    else:
        return '0.0.0'


long_description = (
    "Pheasant is a Markdown converter which is designed to be used "
    "as a plugin for static site generators such as MkDocs or Pelican. "
    "The Pheasant main feature is auto generation of outputs for a fenced "
    "code block in Markdown source using Jupyter client. In addition, "
    "Pheasant can automatically number headers, figures, and tables."
)

setup(
    name='pheasant',
    version=get_version('pheasant'),
    description='Documentation tool for Pelican and MkDocs.',
    long_description=long_description,
    url='https://pheasant.daizutabi.net',
    author='daizutabi',
    author_email='daizutabi@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests', 'docs']),
    include_package_data=True,
    install_requires=['click', 'jupyter', 'markdown', 'pillow'],
    entry_points={
        'console_scripts': [
           'pheasant = pheasant.main:cli',
        ],
        'mkdocs.plugins': [
            'pheasant = pheasant.plugins.mkdocs:PheasantPlugin',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Documentation',
    ],
)

# https://pypi.python.org/pypi?%3Aaction=list_classifiers
