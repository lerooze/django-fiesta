#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import shutil
import sys
from io import open

from setuptools import find_packages, setup


def read(f):
    return open(f, 'r', encoding='utf-8').read()


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('fiesta')


if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('django-sdmx.egg-info')
    sys.exit()


setup(
    name='django-fiesta',
    version=version,
    #url='https://www.django-rest-framework.org/',
    license='BSD',
    description='SDMX implementation made easy',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Antonios Loumiotis',
    author_email='al459@columbia.edu',
    packages=find_packages(exclude=['tests*', 'django-fiesta*']),
    include_package_data=True,
    install_requires=[
        'django>=2.1',
        'lxml',
        'djangorestframework',
        'inflection',
        'django-treebeard',
        'python-dateutil',
        'pyyaml',
        'requests',
        'isodate'
    ],
    python_requires=">=3.7",
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis'
    ]
)
