# coding: utf-8
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

def smart(**kwargs):
    """
    Simple decorator to get custom fields on admin class, using this you will use less line codes

    :param short_description: description of custom field
    :type str:

    :param admin_order_field: field to order on click
    :type str :

    :param allow_tags: allow html tags
    :type bool:

    :param boolean: if field is True, False or None
    :type bool:

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
}


def short(**kwargs):
    def decorator(func):
        for key, value in kwargs.items():
            if key in FUNCTION_MAP:
                setattr(func, FUNCTION_MAP[key], value)
        return func

    return decorator


def action(short_description):
    def decorator(func):
        func.short_description = short_description
        return func

    return decorator