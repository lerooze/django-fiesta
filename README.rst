===========================
A Django SDMX web framework 
===========================

Fiesta aims to be an integrated `SDMX` framework that performs all steps during
the production and dissemination cycle of SDMX data.  Fiesta is still in active
development and its first release is expected by the end of 2019.

Developing features:

* Generation of database classes to store SDMX metadata artefacts in almost any
  database server

* Abstract database classes that can be inherited to build database classed to
  store SDMX domain specific data

* Parser classes to parse SDMX data and metadata

* Renderer classes to render SDMX dataset objects into SDMX data formats

* Utilities to convert SDMX data to different formats

* Structure specific schema generation based on data structure definitions

* RESTful API to disseminate SDMX data as well as registry interface services

* Abstract framework to develop domain-specific SDMX applications 

Further reading:

* `Documentation`_ on the excellent `readthedocs.org`_

License
-------

Fiesta is released under the permissive `New BSD license`_ (see summary_).

.. _summary: https://tldrlegal.com/license/bsd-3-clause-license-(revised)

.. _`New BSD license`: https://github.com/lerooze/django-fiesta/blob/master/LICENSE

.. _SDMX: https://sdmx.org

.. _`Documentation`: https://django-fiesta.readthedocs.io/en/latest/

.. _`readthedocs.org`: http://readthedocs.org
