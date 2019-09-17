==================
Core functionality
==================

This page details the core classes and functions that Fiesta uses.  These aren't
specific to one particular app, but are used throughout Fiesta's codebase.

Dynamic class loading
---------------------

The key to Fiesta's flexibility is dynamically loading classes.  This allows
projects to provide their own versions of classes that extend and override the
core functionality.  Dynamic loading classes is done via the dynamic loading
classes of Django-Oscar e-commerce framework 

.. automodule:: oscar.core.loading
    :members: get_classes, get_class
