"""
The `compat` module provides support for backwards compatibility with older
versions of django/python, and compatibility wrappers around optional packages.
"""
# flake8: noqa


try:
    import defusedxml.lxml as detree
    
except ImportError:
    detree = None

try:
    from lxml import etree
except ImportError:
    etree = None
