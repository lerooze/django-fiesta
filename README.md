# Django-fiesta

**An implementation of the SDMX information model using Django**

Fiesta is a developing project that aims when complete to fully implement 
the SDMX information model using the Django web framework.

Full documentation for the project will be available at ... 

---

# Features 

* Generates database schema to store SDMX structure data
  * Currently supports OrganisationSchemes, Codelists, ConceptSchemes
* Deployable to many different type of database servers
* Customizable 
* Loads external SDMX messages into pythonic dataclass objects.
* Implementation of RegistryInterface services (partial).
* Implementation of SDMX RESTful API (partial).

----

# Still to do

* Complete database schema to store SDMX structure data and create abstract model classes than can be used in new apps to store SDMX data and metadata
* Complete Registry Interface services
* Complete SDMX RESTful API
* Create SDMX SOAP API
* Create schemas for structure specific data and metadata

----

# Quick Examples

----


# Quick start 

1. Add "fiesta" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'fiesta',
    )

2. Include the sdmx URLconf in your project urls.py like this::

    `path('fiesta', include('fiesta.urls'))`

3. Run `python manage.py migrate` to create the sdmx models.

4. Run the initialization database model script that creates two initial
   organisations and two corresponding users

5. Start the development server and make registry interface requests using
   http://127.0.0.1:8000/fiesta/wsreg/ entry point and RESTful SDMX requests
   using http://127.0.0.1:8000/fiesta/wsrest/ entry point.  

   For example to make a structure submission post request use the following
   URI should be used: http://127.0.0.1:8000/fiesta/wsreg/StructureSubmission/
