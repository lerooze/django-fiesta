#!/usr/bin/env python
"""
Installation script:

To release a new version to PyPi:
- Ensure the version is correctly set in fiesta.__version__.py
- Run: make release
"""
import os
import re
import sys

from codecs import open

from setuptools import find_packages, setup


local_here = os.path.dirname(__file__)
abs_here = os.path.abspath(local_here)
sys.path.append(os.path.join(local_here, 'src'))

install_requires = [
    'django',
    # for REST web services
    'djangorestframework',
    # for hierarchical models
    'django-treebeard',
    # for localization
    'django-modeltranslation',
    # for version field
    'django-versionfield2',
    # for multi email field
    'django-multi-email-field',
    # for serializers 
    'pydantic',
    # lxml for xml parsing, schema validation and xml generation
    'lxml',
    # for manipulating strings
    'inflection',
    # for manipulating dates
    'python-dateutil',
    # for external sdmx requests
    'requests',
    # for manipulating time deltas
    'isodate',
]

docs_requires = [
    'Sphinx==2.0.1',
    'sphinxcontrib-napoleon==0.7',
    'sphinx_rtd_theme==0.4.3',
    'sphinx-issues==1.2.0',
]

# sorl_thumbnail_version = 'sorl-thumbnail>=12.4.1,<12.5'
# easy_thumbnails_version = 'easy-thumbnails==2.5'

test_requires = [
    # 'WebTest>=2.0,<2.1',

    # 'coverage>=4.5,<4.6',
    'coverage>=4.5',

    # 'django-webtest==1.9.4',
    # 'psycopg2>=2.7,<2.8',

    # 'pytest>=4.0,<4.5',
    'pytest>=4.0',
    'pytest-cov==2.6.1',
    'pytest-django==3.4.8',
    'pytest-spec',
    'pdbpp',

    #'pytest-xdist>=1.25,<1.28',
    'pytest-xdist>=1.25',

    #'tox>=3.0,<3.9',
    'tox>=3.0',


    # sorl_thumbnail_version,
    # easy_thumbnails_version,
]

about = {}
with open(os.path.join(abs_here, 'src', 'fiesta', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

with open(os.path.join(abs_here, 'README.rst')) as fh:
    readme = re.sub(
        '^.. start-no-pypi.*^.. end-no-pypi', '', fh.read(), flags=re.M | re.S)

# with open('README.md', 'r', 'utf-8') as f:
#     readme = f.read()
# with open('HISTORY.md', 'r', 'utf-8') as f:

    # history = f.read()
setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'docs': docs_requires,
        'test': test_requires,
        # 'sorl-thumbnail': [sorl_thumbnail_version],
        # 'easy-thumbnails': [easy_thumbnails_version],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
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
