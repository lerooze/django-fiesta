# Django-fiesta

**Implementation of SDMX information model made easy**

Fiesta is a project that facilitates when comlete a quick deployment of
the SDMX information model using the Django web framework.

Full documentation for the project will be available at .

---

# Features 

* Generates database schema to store SDMX structure data (partial)
* Deployable to many different database servers
* Customizable 
* Loading external SDMX messages into pythonic dataclass objects.
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

# Requirements

* Python (3.7)
* Django (2
* defusedxml(0.6)
* djangorestframework(3.9)
* django-treebeard(4.3)
* inflection(0.3)
* isodate(0.6)
* lxml(4.3)
* python-dateutil(2.8)
* requests(2.21)
* PyYAML(5.1)


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
