from __future__ import annotations

from dataclasses import asdict
from functools import wraps
from typing import Optional, Callable, Union, List

from django import utils as django_utils
from django.core.cache import cache as django_cache
from django.utils.safestring import mark_safe

from easy import helper

Model: "django.db.models.Model"

def smart(**kwargs):
    """
    Simple decorator to get custom fields on admin class, using this you will use less line codes

    :param short_description: description of custom field (Optional[str])
    :type short_description: str
    :param admin_order_field: field to order on click (Optional[str])
    :type admin_order_field: str
    :param allow_tags: allow html tags (Optional[bool])
    :type allow_tags: bool
    :param boolean: if field boolean (Optional[bool])
    :type boolean: bool
    :param empty_value_display: Default value when field is null (Optional[str])
    :type empty_value_display: str

    :return: method decorated (Callable)
    """

    def decorator(func):
        for key, value in kwargs.items():
            setattr(func, key, value)
        return func

    return decorator

FUNCTION_MAP = {
    'desc': 'short_description',
    'order': 'admin_order_field',
    'bool': 'boolean',
    'tags': 'allow_tags',
    'empty': 'empty_value_display'
}


def short(**kwargs: Union[str, bool]) -> Callable:
    """
    Short decorator to set some attrs on admin method.

    :param kwargs: key-value pairs to set on method.
    :return: method decorated (Callable)
    """

    def decorator(func: Callable) :
        for key, value in kwargs.items():
            if key in FUNCTION_MAP:
                setattr(func, FUNCTION_MAP[key], value)
            else:
                setattr(func, key, value)

        if getattr(func, 'allow_tags', False):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return mark_safe(func(*args, **kwargs))
            return wrapper
        return func

    return decorator


def action(short_description: str, permission: Optional[Union[str, List[str]]] = None) -> Callable:
    """
    Action decorator to set some attrs on admin method.

    :param short_description: description of custom field (str)
    :param permission: permission to use. (Optional[Union[str, List[str]]])
    :return: method decorated (Callable)
    """

    def decorator(func: Callable) -> Callable:
        func.short_description = short_description
        if permission:
            if isinstance(permission, str):
                func.allowed_permissions = (permission,)
            else:
                func.allowed_permissions = permission
        return func

    return decorator


def utils(django_utils_function: str) -> Callable[[Callable], Callable]:
    """
    Util decorator to apply a django.utils function on the method result.

    :param django_utils_function: name of the function to apply (str)
    :return: function decorated (Callable[[Callable], Callable])
    """

    def decorator(func: Callable):
        util_function = helper.deep_getattribute(django_utils, django_utils_function)
        if isinstance(util_function, helper.Nothing):
            raise Exception('Function {} not exist on django.utils module.'.format(django_utils_function))

        @wraps(func)
        def wrapper(*args, **kwargs):
            return util_function(func(*args, **kwargs))

        return wrapper

    return decorator


def filter(django_builtin_filter: str, load: Optional[str] = None, *extra: Union[str, List[str]]) -> Callable[[Callable], Callable]:
    """
    Filter decorator to apply a django builtin filter on the method result.

    :param django_builtin_filter: name of the filter to apply (str)
    :param load: library to be loaded like load in templatetag. (Optional[str])
    :param extra: extra arguments to pass to the filter. (Union[str, List[str]])
    :return: method decorated (Callable[[Callable], Callable])
    """

    def decorator(func: Callable) -> Callable:
        filter_method = helper.get_django_filter(django_builtin_filter, load)

        @wraps(func)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            return filter_method(value, *extra)

        return wrapper
    return decorator


def with_tags():
    """
    Decorator to mark result of method as safe and allow tags.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return mark_safe(func(*args, **kwargs))
        return wrapper
    return decorator


def cache(seconds: int = 60):
    """
    Cache decorator to cache the result of a method.

    :param seconds: The cache time in seconds. (int)
    :return: The cached method
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(admin, model):
            cache_method_key = helper.cache_method_key(model, func.__name__)
            value = django_cache.get(cache_method_key)
            if not value:
                value = func(admin, model)
                cache_object_key = helper.cache_object_key(model)
                obj_methods_caches = django_cache.get(cache_object_key) or ''
                django_cache.set_many({
                    cache_method_key: value,
                    cache_object_key: obj_methods_caches + '|' + cache_method_key
                }, seconds)
            return value

        return wrapper
    return decorator


def clear_cache(model: Model) -> None:
    """
    Clear cache for specific model.

    :param model: The model to clear cache for.
    :type model: django.db.models.Model
    """
    cache_object_key = helper.cache_object_key(model)
    obj_methods_caches = django_cache.get(cache_object_key)
    methods_key = obj_methods_caches.split('|') if obj_methods_caches else []
    django_cache.delete_many(methods_key)
