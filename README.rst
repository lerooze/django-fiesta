Django-fiesta: A Django SDMX web framework 
==========================================

Fiesta aims to becoma a SDMX_  web framework for Django.  It is still under
active development and thus should not yet be used.

Current Features 
----------------

- Generation of django database models that reflect the SDMX information model 
  - Currently models for the following maintainable artefacts are implemented:
    - OrganisationSchemes, Codelists, ConceptSchemes
- Generation of django database models that reflect the SDMX registry interface model
  - Currently supports StructureSubmissions for the above listed maintainable artefacts 
- Loads external SDMX messages into pythonic dataclass objects
- Partial implementation of RegistryInterface services
- Partial implementation of SDMX RESTful API


.. _SDMX: https://sdmx.org
