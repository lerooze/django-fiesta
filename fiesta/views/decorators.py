import collections
from functools import wraps

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import reverse_lazy


def check_permissions(user, permissions):
    """
    Permissions can be a list or a tuple of lists. If it is a tuple,
    every permission list will be evaluated and the outcome will be checked
    for truthiness.
    Each item of the list(s) must be either a valid Django permission name
    (model.codename) or a property or method on the User model
    (e.g. 'is_active', 'is_superuser').

    Example usage:
    - permissions_required(['is_anonymous', ])
      would replace login_forbidden
    """
    def _check_one_permission_list(perms):
        regular_permissions = [perm for perm in perms if '.' in perm]
        conditions = [perm for perm in perms if '.' not in perm]
        # always check for is_active if not checking for is_anonymous
        if (conditions
                and 'is_anonymous' not in conditions
                and 'is_active' not in conditions):
            conditions.append('is_active')
        attributes = [getattr(user, perm) for perm in conditions]
        # evaluates methods, explicitly casts properties to booleans
        passes_conditions = all([
            attr() if isinstance(attr, collections.Callable) else bool(attr) for attr in attributes])
        return passes_conditions and user.has_perms(regular_permissions)

    if not permissions:
        return True
    elif isinstance(permissions, list):
        return _check_one_permission_list(permissions)
    else:
        return any(_check_one_permission_list(perm) for perm in permissions)
