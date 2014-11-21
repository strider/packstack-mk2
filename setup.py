#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys

from setuptools import setup, find_packages, Command


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read_readme(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as readme:
        data = readme.read()
    return data

def read_requirements(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as reqs:
        data = [
            i.strip().split('=', 1)[0].strip('<> \t')
            for i in reqs
        ]
    return data


setup(
    name='packstack',
    version='mk2',
    author='Martin Magr',
    author_email='mmagr@redhat.com',
    description='Command line OpenStack installer',
    license='ASL 2.0',
    keywords='openstack,installer',
    url='https://github.com/stackforge/packstack',
    packages=find_packages('.'),
    include_package_data=True,
    long_description=read('README'),
    zip_safe=False,
    install_requires=read_requirements('requirements.txt'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ],
    scripts=['bin/packstack'],
)
