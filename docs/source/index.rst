.. Fiesta documentation master file, created by
   sphinx-quickstart on Tue Sep 17 14:23:55 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

======
Fiesta
======

---------------------------------------
An integrated SDMX framework for Django
---------------------------------------

Fiesta aims to be an integrated SDMX framework that performs all processes
during the production and dissemination cycle.

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

First steps
===========
.. toctree::
   :maxdepth: 1

   internals/sandbox

Using Fiesta 
============

All you need to start developing a Fiesta project.

.. toctree::
   :maxdepth: 1

   topics/customisation
   topics/class_loading_explained
   topics/deploying
   topics/translation
   topics/upgrading
   topics/fork_app

Reference
=========

.. toctree::
   :maxdepth: 1

   .. Core functionality </ref/core>
   .. Fiesta's apps </ref/apps/index>
   .. howto/index
   .. ref/settings

The Oscar open-source project
=============================

Learn about the ideas behind Oscar and how you can contribute.

.. toctree::
   :maxdepth: 1

   internals/design-decisions
   releases/index
   internals/contributing/index

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
