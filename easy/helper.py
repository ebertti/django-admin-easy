from __future__ import annotations
from typing import Callable, Union, Any

import django

EASY_CACHE_TEMPLATE_METHOD = 'easy.{}.{}.{}'
EASY_CACHE_TEMPLATE_OBJ = 'easy.{}.{}'


Model: django.db.models.Model

class Nothing(object):
    def __str__(self):
        return 'Error'

    def __unicode__(self):
        return u'Error'


def deep_getattribute(obj: object, attr: str) -> object:
    """
    Retrieves the value of a nested attribute from an object.

    Args:
        obj (object): The object to retrieve the attribute from.
        attr (str): The attribute to retrieve, in the form of a dot-separated string.

    Returns:
        object: The value of the attribute, or a Nothing instance if the attribute does not exist.
    """
    attrs = attr.split(".")
    for i in attrs:
        obj = getattr(obj, i, Nothing())
    return obj

def get_django_filter(django_filter: str, load: str = 'django') -> Callable:
    """
    Retrieves a Django filter method from the specified templatetag library.

    Args:
        django_filter (str): The name of the Django filter method.
        load (str, optional): The name of the templatetag library to load. Defaults to 'django'.

    Returns:
        Callable: The Django filter method.

    Raises:
        Exception: If the specified Django filter or templatetag library does not exist.
    """
    if django.VERSION < (1, 9):
        from django.template.base import get_library
        if load and load != 'django':
            library = get_library(load)
        else:
            library_path = 'django.template.defaultfilters'
            if django.VERSION > (1, 8):
                from django.template.base import import_library
                library = import_library(library_path)
            else:
                from django.template import import_library
                library = import_library(library_path)

    else:
        from django.template.backends.django import get_installed_libraries
        from django.template.library import import_library
        libraries = get_installed_libraries()
        if load and load != 'django':
            library_path = libraries.get(load)
            if not library_path:
                raise Exception(f'templatetag "{load}" is not registered')
        else:
            library_path = 'django.template.defaultfilters'

        library = import_library(library_path)
    filter_method = library.filters.get(django_filter)
    if not filter_method:
        raise Exception(f'filter "{django_filter}" not exist on {load} templatetag package')

    return filter_method


def call_or_get(obj: object, attr: Union[str, Callable[[object], Any]], default: Any = None) -> Any:
    """
    Calls the given attribute if it is a callable, otherwise retrieves its value.

    Args:
        obj (object): The object to call the attribute on.
        attr (Union[str, Callable[[object], Any]]): The attribute to call or retrieve.
        default (Any, optional): The default value to return if the attribute's value is None or an instance of Nothing.

    Returns:
        Any: The result of calling the attribute if it is a callable, otherwise its value. If the attribute's value is None or an instance of Nothing, returns the default value if it is provided, otherwise returns None.
    """
    ret = Nothing()

    if callable(attr):
        ret = attr(obj)

    if isinstance(ret, Nothing):
        value = deep_getattribute(obj, attr)
        if callable(value):
            ret = value()
        else:
            ret = value

    if (not ret or isinstance(ret, Nothing)) and default is not None:
        ret = default

    return ret


def get_model_name(model: Model) -> str:
    """
    Retrieves the name of a Django model.

    Args:
        model (Model): The Django model object.

    Returns:
        str: The name of the model.
    """
    if django.VERSION < (1, 6):
        return model._meta.module_name
    else:
        return model._meta.model_name


def cache_method_key(model: Model, method_name: str) -> str:
    """
    Generates a cache key for a method of a model instance.

    Args:
        model (Model): The model instance.
        method_name (str): The name of the method.

    Returns:
        str: The cache key.
    """
    return EASY_CACHE_TEMPLATE_METHOD.format(
        model._meta.app_label,
        get_model_name(model),
        method_name,
        model.pk
    )


def cache_object_key(model: Model) -> str:
    """
    Generates a cache key for a model instance.

    Args:
        model (Model): The model instance.

    Returns:
        str: The cache key.
    """
    return EASY_CACHE_TEMPLATE_OBJ.format(
        model._meta.app_label,
        get_model_name(model),
        model.pk
    )
