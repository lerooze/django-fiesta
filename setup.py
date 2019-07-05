#!/usr/bin/env python
"""
Installation script:

To release a new version to PyPi:
- Ensure the version is correctly set in fiesta.__init__.py
- Run: make release
"""
import os
import re
import sys

from setuptools import find_packages, setup

PROJECT_DIR = os.path.dirname(__file__)

sys.path.append(os.path.join(PROJECT_DIR, 'src'))
from fiesta import get_version  # noqa isort:skip

install_requires = [
    'django>=2.2,<2.3',
    'djangorestframework>=3.9',
    # lxml for xml parsing, schema validation and xml generation
    'lxml',
    # for manipulating strings
    'inflection',
    # for hierarchical models
    'django-treebeard',
    # for manipulating dates
    'python-dateutil',
    # for external sdmx requests
    'requests',
    # for manipulating time deltas
    'isodate'
]

docs_requires = [
    # 'Sphinx==2.0.1',
    # 'sphinxcontrib-napoleon==0.7',
    # 'sphinx_rtd_theme==0.4.3',
    # 'sphinx-issues==1.2.0',
]

# sorl_thumbnail_version = 'sorl-thumbnail>=12.4.1,<12.5'
# easy_thumbnails_version = 'easy-thumbnails==2.5'

test_requires = [
    # 'WebTest>=2.0,<2.1',
    # 'coverage>=4.5,<4.6',
    # 'django-webtest==1.9.4',
    # 'py>=1.4.31',
    # 'psycopg2>=2.7,<2.8',
    # 'pytest>=4.0,<4.5',
    # 'pytest-cov==2.6.1',
    # 'pytest-django==3.4.8',
    # 'pytest-xdist>=1.25,<1.28',
    # 'tox>=3.0,<3.9',
    # sorl_thumbnail_version,
    # easy_thumbnails_version,
]

with open(os.path.join(PROJECT_DIR, 'README.rst')) as fh:
    long_description = re.sub(
        '^.. start-no-pypi.*^.. end-no-pypi', '', fh.read(), flags=re.M | re.S)

setup(
    name='django-fiesta',
    version=get_version(),
    url='https://github.com/lerooze/django-fiesta',
    author="Antonios Loumiotis",
    author_email="al459@columbia",
    description="A SDMX framework for Django",
    long_description=long_description,
    keywords="SDMX, Django",
    license='BSD',
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

# # Show contributing instructions if being installed in 'develop' mode
# if len(sys.argv) > 1 and sys.argv[1] == 'develop':
#     docs_url = 'https://django-fiesta.readthedocs.io/en/latest/internals/contributing/index.html'
#     mailing_list = 'django-fiesta@googlegroups.com'
#     mailing_list_url = 'https://groups.google.com/forum/?fromgroups#!forum/django-fiesta'
#     twitter_url = 'https://twitter.com/django_fiesta'
#     msg = (
#         "You're installing Fiesta in 'develop' mode so I presume you're thinking\n"
#         "of contributing:\n\n"
#         "(a) That's brilliant - thank you for your time\n"
#         "(b) If you have any questions, please use the mailing list:\n    %s\n"
#         "    %s\n"
#         "(c) There are more detailed contributing guidelines that you should "
#         "have a look at:\n    %s\n"
#         "(d) Consider following @django_fiesta on Twitter to stay up-to-date\n"
#         "    %s\n\nHappy hacking!") % (mailing_list, mailing_list_url,
#                                        docs_url, twitter_url)
#     line = '=' * 82
#     print(("\n%s\n%s\n%s" % (line, msg, line)))
