======================
Sample Fiesta projects
======================

Fiesta ships with one sample project: a 'sandbox' site, which is a vanilla
install of Fiesta using the default settings.

The sandbox site
----------------

The sandbox site is a minimal implementation of Fiesta where everything is left
in its default state.  It is useful for exploring Fiesta's functionality
and developing new features.

The sandbox is, in effect, the blank canvas upon which you can build your site.

.. Browse the external sandbox site
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
..
.. An instance of the sandbox site is built hourly from master branch and made
.. available at http://latest.oscarcommerce.com 
..
.. .. warning::
..     
..     It is possible for users to access the dashboard and edit the site content.
..     Hence, the data can get quite messy.  It is periodically cleaned up.


Run the sandbox locally
~~~~~~~~~~~~~~~~~~~~~~~

It's pretty straightforward to get the sandbox site running locally so you can
play around with Fiesta.

.. .. warning::
..     
..     While installing Oscar is straightforward, some of Oscar's dependencies
..     don't support Windows and are tricky to be properly installed, and therefore
..     you might encounter some errors that prevent a successful installation.

.. In order to compile uWSGI, which is a dependency of the sandbox, you will
.. first need to install the Python development headers with:::
..
..     $ sudo apt-get install python3-dev

Install Oscar and its dependencies within a virtualenv:

.. code-block:: bash

    $ git clone https://github.com/lerooze/django-fiesta.git
    $ cd django-fiesta
    $ make sandbox
    (django-fiesta) $ sandbox/manage.py runserver


The sandbox site (initialised with a sample set of products) will be available
at: http://localhost:8000.  A sample superuser is installed with credentials::

    username: superuser
    email: superuser@fiesta_sdmx.org
    password: testing
