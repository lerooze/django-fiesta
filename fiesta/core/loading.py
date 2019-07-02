
from django.apps import apps
from fiesta.core.exceptions import ClassNotFoundError, AppNotFoundError
import sys
import traceback


def is_model_registered(app_label, model_name):
    """
    Checks whether a given model is registered. This is used to only
    register fiesta models if they aren't overridden by a forked app.
    """
    try:
        apps.get_registered_model(app_label, model_name)
    except LookupError:
        return False
    else:
        return True

def default_class_loader(module_label, classnames, module_prefix):
    """
    Dynamically import a list of classes from the given module.

    This works by looking up a matching app from the app registry,
    against the passed module label.  If the requested class can't be found in
    the matching module, then we attempt to import it from the corresponding
    core app.

    This is very similar to ``django.db.models.get_model`` function for
    dynamically loading models.  This function is more general though as it can
    load any class from the matching app, not just a model.

    Args:
        module_label (str): Module label comprising the app label and the
            module name, separated by a dot.  For example, 'catalogue.forms'.
        classname (str): Name of the class to be imported.

    Returns:
        The requested class object or ``None`` if it can't be found

    Examples:

        Load a single class:

        >>> get_class('codelist.dataclasses', 'CodelistDataclass')
        fiesta.apps.codelist.dataclasses.CodelistDataclass

        Load a list of classes:

        >>> get_classes('codelist.dataclasses',
        ...             ['CodelistDataclass', 'CodeDataclass'])
        [fiesta.apps.codelist.dataclasses.CodelistDataclass,
         fiesta.apps.codelist.dataclasses.CodeDataclass]

    Raises:

        AppNotFoundError: If no app is found in ``INSTALLED_APPS`` that matches
            the passed module label.

        ImportError: If the attempted import of a class raises an
            ``ImportError``, it is re-raised
    """

    if '.' not in module_label:
        # Importing from top-level modules is not supported, e.g.
        # get_class('shipping', 'Scale'). That should be easy to fix,
        # but @maikhoepfel had a stab and could not get it working reliably.
        # Overridable classes in a __init__.py might not be a good idea anyway.
        raise ValueError(
            "Importing from top-level modules is not supported")

    # import from Fiesta package (should succeed in most cases)
    # e.g. 'fiesta.apps.dashboard.catalogue.forms'
    fiesta_module_label = "%s.%s" % (module_prefix, module_label)
    fiesta_module = _import_module(fiesta_module_label, classnames)

    # returns e.g. 'fiesta.apps.dashboard.catalogue',
    # 'yourproject.apps.dashboard.catalogue' or 'dashboard.catalogue',
    # depending on what is set in INSTALLED_APPS
    app_name = _find_registered_app_name(module_label)
    if app_name.startswith('%s.' % module_prefix):
        # The entry is obviously an Fiesta one, we don't import again
        local_module = None
    else:
        # Attempt to import the classes from the local module
        # e.g. 'yourproject.dashboard.catalogue.forms'
        local_module_label = '.'.join(app_name.split('.') + module_label.split('.')[1:])
        local_module = _import_module(local_module_label, classnames)

    if fiesta_module is local_module is None:
        # This intentionally doesn't raise an ImportError, because ImportError
        # can get masked in complex circular import scenarios.
        raise ModuleNotFoundError(
            "The module with label '%s' could not be imported. This either"
            "means that it indeed does not exist, or you might have a problem"
            " with a circular import." % module_label
        )

    # return imported classes, giving preference to ones from the local package
    return _pluck_classes([local_module, fiesta_module], classnames)

def _import_module(module_label, classnames):
    """
    Imports the module with the given name.
    Returns None if the module doesn't exist, but propagates any import errors.
    """
    try:
        return __import__(module_label, fromlist=classnames)
    except ImportError:
        # There are 2 reasons why there could be an ImportError:
        #
        #  1. Module does not exist. In that case, we ignore the import and
        #     return None
        #  2. Module exists but another ImportError occurred when trying to
        #     import the module. In that case, it is important to propagate the
        #     error.
        #
        # ImportError does not provide easy way to distinguish those two cases.
        # Fortunately, the traceback of the ImportError starts at __import__
        # statement. If the traceback has more than one frame, it means that
        # application was found and ImportError originates within the local app
        __, __, exc_traceback = sys.exc_info()
        frames = traceback.extract_tb(exc_traceback)
        if len(frames) > 1:
            raise


def _pluck_classes(modules, classnames):
    """
    Gets a list of class names and a list of modules to pick from.
    For each class name, will return the class from the first module that has a
    matching class.
    """
    klasses = []
    for classname in classnames:
        klass = None
        for module in modules:
            if hasattr(module, classname):
                klass = getattr(module, classname)
                break
        if not klass:
            packages = [m.__name__ for m in modules if m is not None]
            raise ClassNotFoundError("No class '%s' found in %s" % (
                classname, ", ".join(packages)))
        klasses.append(klass)
    return klasses

def _find_registered_app_name(module_label):
    """
    Given a module label, finds the name of the matching Fiesta app from the
    Django app registry.
    """
    from fiesta.core.application import FiestaConfig

    app_label = module_label.split('.')[0]
    try:
        app_config = apps.get_app_config(app_label)
    except LookupError:
        raise AppNotFoundError(
            "Couldn't find an app to import %s from" % module_label)
    if not isinstance(app_config, FiestaConfig):
        raise AppNotFoundError(
            "Couldn't find an Fiesta app to import %s from" % module_label)
    return app_config.name
