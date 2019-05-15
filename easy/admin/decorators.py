from collections.abc import Iterable
from functools import wraps
from django import utils as django_utils
from django.core.cache import cache as django_cache
from django.utils.safestring import mark_safe

from easy import helper


def smart(**kwargs):
    """
    Simple decorator to get custom fields on admin class, using this you will use less line codes

    :param short_description: description of custom field
    :type str:

    :param admin_order_field: field to order on click
    :type str:

    :param allow_tags: allow html tags
    :type bool:

    :param boolean: if field is True, False or None
    :type bool:

    :param empty_value_display: Default value when field is null
    :type str:

    :return: method decorated
    :rtype: method
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


def short(**kwargs):
    def decorator(func):
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


def action(short_description, permission=None):
    def decorator(func):
        func.short_description = short_description
        if permission:
            if isinstance(permission, str):
                func.allowed_permissions = (permission,)
            else:
                func.allowed_permissions = permission
        return func

    return decorator


def utils(django_utils_function):
    def decorator(func):
        util_function = helper.deep_getattribute(django_utils, django_utils_function)
        if isinstance(util_function, helper.Nothing):
            raise Exception('Function {} not exist on django.utils module.'.format(django_utils_function))

        @wraps(func)
        def wrapper(*args, **kwargs):
            return util_function(func(*args, **kwargs))

        return wrapper

    return decorator


def filter(django_builtin_filter, load=None, *extra):  # noqa

    def decorator(func):
        filter_method = helper.get_django_filter(django_builtin_filter, load)

        @wraps(func)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            return filter_method(value, *extra)

        return wrapper
    return decorator


def with_tags():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return mark_safe(func(*args, **kwargs))
        return wrapper
    return decorator


def cache(seconds=60):
    def decorator(func):
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


def clear_cache(model):
    cache_object_key = helper.cache_object_key(model)
    obj_methods_caches = django_cache.get(cache_object_key)
    methods_key = obj_methods_caches.split('|')
    django_cache.delete_many(methods_key)
