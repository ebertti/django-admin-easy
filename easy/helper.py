# coding: utf-8
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)


class Nothing(object):
    def __str__(self):
        return 'Error'

    def __unicode__(self):
        return u'Error'


def deep_getattribute(obj, attr):
    attrs = attr.split(".")
    for i in attrs:
        obj = getattr(obj, i, Nothing())
    return obj


def call_or_get(obj, attr, default=None):
    ret = Nothing()
    if hasattr(attr, '__call__'):
        ret = attr(obj)
    if isinstance(ret, Nothing):
        value = deep_getattribute(obj, attr)
        if hasattr(value, '__call__'):
            ret = value()
        else:
            ret = value

    if (not ret or isinstance(ret, Nothing)) and default is not None:
        ret = default

    return ret