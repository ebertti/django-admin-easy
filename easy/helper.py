import django

EASY_CACHE_TEMPLATE_METHOD = 'easy.{}.{}.{}'
EASY_CACHE_TEMPLATE_OBJ = 'easy.{}.{}'


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

def get_django_filter(django_filter, load='django'):

    if django.VERSION < (1, 9):
        from django.template.base import get_library
        if load and not load == 'django':
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
        if load and not load == 'django':
            library_path = libraries.get(load)
            if not library_path:
                raise Exception('templatetag "{}" is not registered'.format(load))
        else:
            library_path = 'django.template.defaultfilters'

        library = import_library(library_path)
    filter_method = library.filters.get(django_filter)
    if not filter_method:
        raise Exception('filter "{}" not exist on {} templatetag package'.format(
            django_filter, load
        ))

    return filter_method


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


def get_model_name(model):
    if django.VERSION < (1, 6):
        return model._meta.module_name
    else:
        return model._meta.model_name


def cache_method_key(model, method_name):
    return EASY_CACHE_TEMPLATE_METHOD.format(
        model._meta.app_label,
        get_model_name(model),
        method_name,
        model.pk
    )


def cache_object_key(model):
    return EASY_CACHE_TEMPLATE_OBJ.format(
        model._meta.app_label,
        get_model_name(model),
        model.pk
    )
