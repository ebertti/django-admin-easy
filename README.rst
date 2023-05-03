django-admin-easy
=================

Collection of admin fields, decorators and mixin to help to create computed or custom fields more friendly and easy way


.. image:: https://img.shields.io/badge/django-1.8%201.9%201.10%201.11-brightgreen.svg
  :target: http://pypi.python.org/pypi/django-admin-easy

.. image:: https://img.shields.io/badge/django-2.0%202.1%202.2-brightgreen.svg
  :target: http://pypi.python.org/pypi/django-admin-easy

.. image:: https://img.shields.io/badge/django-3.0%203.1%203.2%204.0%204.1%204.2-brightgreen.svg
  :target: http://pypi.python.org/pypi/django-admin-easy

.. image:: https://img.shields.io/badge/django-4.0%204.1%204.2-brightgreen.svg
  :target: http://pypi.python.org/pypi/django-admin-easy

.. image:: https://img.shields.io/pypi/v/django-admin-easy.svg?style=flat
  :target: http://pypi.python.org/pypi/django-admin-easy

.. image:: https://img.shields.io/pypi/pyversions/django-admin-easy.svg?maxAge=2592000
  :target: http://pypi.python.org/pypi/django-admin-easy

.. image:: https://img.shields.io/pypi/format/django-admin-easy.svg?maxAge=2592000
  :target: http://pypi.python.org/pypi/django-admin-easy

.. image:: https://img.shields.io/pypi/status/django-admin-easy.svg?maxAge=2592000
  :target: http://pypi.python.org/pypi/django-admin-easy

.. image:: https://github.com/ebertti/django-admin-easy/actions/workflows/test.yml/badge.svg
  :target: https://github.com/ebertti/django-admin-easy/actions/workflows/test.yml

.. image:: https://img.shields.io/coveralls/ebertti/django-admin-easy/master.svg?maxAge=2592000
  :target: https://coveralls.io/r/ebertti/django-admin-easy?branch=master


Installation
------------

1. Requirements: **Django > 1.8** and **Python > 3.5**

2. ``pip install django-admin-easy==0.7.0``


* For **Django < 1.8** or **Python 2.x**

  ``pip install django-admin-easy==0.4.1``


How it Works
------------

When you want to display a field on Django Admin, and this field doesn't exist in your Model
or you need to compute some information, like a Image or Link, you will need to create a method on your ModelAdminClass like this:

.. code-block:: python

    from django.contrib import admin

    class YourAdmin(admin.ModelAdmin):
        fields = ('sum_method', 'some_img', 'is_true')

        def sum_method(self, obj):
            sum_result = obj.field1 + obj.field2 + obj.field3
            return '<b>%s</b>' % sum_result
        sum_method.short_description = 'Sum'
        sum_method.admin_order_field = 'field1'
        sum_method.allow_tags = True

        def some_img(self, obj):
            return '<img scr="%s">' % obj.image
        some_img.short_description = 'image'
        some_img.admin_order_field = 'id'
        some_img.allow_tags = True

        def is_true(self, obj):
            return obj.value > 0
        is_true.short_description = 'Positive'
        is_true.admin_order_field = 'value'
        is_true.boolean = True

It takes too much lines! =D

With **django-admin-easy** you can easily create this field with less lines:

.. code-block:: python

    from django.contrib import admin
    import easy

    class YourAdmin(admin.ModelAdmin):
        fields = ('sum_method', 'some_img', 'is_true')

        sum_method = easy.SimpleAdminField(lambda obj: '<b>%s</b>' % (obj.field1 + obj.field2 + obj.field3), 'Sum', 'field1', True)
        some_img = easy.ImageAdminField('image', 'id')
        is_true = easy.BooleanAdminField('Positive', 'value')

If you still prefer using a custom method, you can use our decorators, like this:

.. code-block:: python

    from django.contrib import admin
    import easy

    class YourAdmin(admin.ModelAdmin):
        fields = ('sum_method', 'some_img', 'is_true')

        @easy.smart(short_description='Sum', admin_order_field='field1', allow_tags=True )
        def sum_method(self, obj):
            sum_result = obj.field1 + obj.field2 + obj.field3
            return '<b>%s</b>' % sum_result

        @easy.short(desc='image', order='id', tags=True)
        def some_img(self, obj):
            return '<img scr="%s">' % obj.image

        @easy.short(desc='Positive', order='value', bool=True)
        def is_true(self, obj):
            return obj.value > 0

Another Decorators
------------------

In all of this extra decorators, you can use `short` or `smart` arguments to complement field information.

* **Allow HTML tags**

.. code-block:: python

    @easy.with_tags()
    def some_field_with_html(self, obj):
        return '<b>{}</b>'.format(obj.value)
    # output some as: mark_safe("<b>something</b>")


if value is `5`, will display:

**5** and not `<b>5</b>` on admin page.

* **Cached field**

If you, for some reason, need to cache a custom field on admin

.. code-block:: python

    @easy.cache(10)# in secondd, default is 60
    def some_field_with_html(self, obj):
        return obj.related.some_hard_word()

If you change something on your model, or some related object, you can clean this cache using this easy way:

.. code-block:: python

    import easy
    # wherever you want
    easy.cache_clear(my_model_instance)

    # or
    class MyModel(models.Model):
        # ... fields

        def save(*args, **kwargs):
            easy.cache_clear(self)
            super(MyModel, self).save(*args, **kwargs)


* **Django template filter**

Can be used with all template filters on your project.

.. code-block:: python

    # builtin template filter like {{ value|title }}
    @easy.filter('title')
    def some_field_with_html(self, obj):
        return 'ezequiel bertti'
    # output: "Ezequiel Bertti"

    # like {% load i10n %} and {{ value|localize }}
    @easy.filter('localize', 'l10n')
    def some_field_with_html(self, obj):
        return 10000
    # output: "10.000"

    # like {{ value|date:'y-m-d' }}
    @easy.filter('date', 'default', 'y-m-d')
    def some_field_with_html(self, obj):
        return datetime(2016, 06, 28)
    # output: "16-06-28"

* **Django utils functions**

Tested with:

.. code-block:: python

    @easy.utils('html.escape')
    @easy.utils('html.conditional_escape')
    @easy.utils('html.strip_tags')
    @easy.utils('safestring.mark_safe')
    @easy.utils('safestring.mark_for_escaping')
    @easy.utils('text.slugify')
    @easy.utils('translation.gettext')
    @easy.utils('translation.ugettext')
    @easy.utils('translation.gettext_lazy')
    @easy.utils('translation.ugettext_lazy')
    @easy.utils('translation.gettext_noop')
    @easy.utils('translation.ugettext_noop')
    def your_method(self, obj):
        return obj.value

More Examples
-------------

.. code-block:: python

    from django.contrib import admin
    import easy

    class YourAdmin(admin.ModelAdmin):
        list_fields = ('id', 'custom1', 'custom2', 'custom3' ... 'customN')

        actions = ('simples_action',)

        @easy.action('My Little Simple Magic Action')
        def simple_action(self, request, queryset):
            return queryset.update(magic=True)

        # actoin only for user that has change permission on this model
        @easy.action('Another Simple Magic Action', 'change')
        def simple_action(self, request, queryset):
            return queryset.update(magic=True)


        # render a value of field, method, property or your model or related model
        simple1 = easy.SimpleAdminField('model_field')
        simple2 = easy.SimpleAdminField('method_of_model')
        simple3 = easy.SimpleAdminField('related.attribute_or_method')
        simple4 = easy.SimpleAdminField('related_set.count', 'count')
        simple5 = easy.SimpleAdminField(lambda x: x.method(), 'show', 'order_by')

        # render boolean fields
        bool1 = easy.BooleanAdminField(lambda x: x.value > 10, 'high')

        # render with string format fields
        format1 = easy.FormatAdminField('{o.model_field} - {o.date_field:Y%-%m}', 'column name')

        # render foreignkey with link to change_form in admin
        fk1 = easy.ForeignKeyAdminField('related')

        # render foreignkey with link to change_form in admin and related_id content as text
        fk2 = easy.ForeignKeyAdminField('related', 'related_id')

        # render foreignkey_id, like raw_id_fields, with link to change_form in admin and related_id content as text
        # without extra queries or select_related to prevent extra n-1 queries
        raw1 = easy.RawIdAdminField('related')

        # render template
        template1 = easy.TemplateAdminField('test.html', 'shorty description', 'order_field')

        # render to change_list of another model with a filter on query
        link1 = easy.LinkChangeListAdminField('app_label', 'model_name', 'attribute_to_text',
                                              {'field_name':'dynamic_value_model'})

        link2 = easy.LinkChangeListAdminField('app_label', 'model_name', 'attribute_to_text',
                                              {'field_name':'dynamic_value_model'},
                                              {'another_field': 'static_value'})

        # display image of some model
        image1 = easy.ImageAdminField('image', {'image_attrs':'attr_value'})

        # use django template filter on a field
        filter1 = easy.FilterAdminField('model_field', 'upper')
        filter2 = easy.FilterAdminField('date_field', 'date', 'django', 'y-m-d')
        filter3 = easy.FilterAdminField('float_field', 'localize', 'l18n')

        @easy.smart(short_description='Field Description 12', admin_order_field='model_field')
        def custom12(self, obj):
            return obj.something_cool()

        @easy.short(desc='Field Description 1', order='model_field', tags=True)
        def decorator1(self, obj):
            return '<b>' + obj.model_field + '</b>'

        @easy.short(desc='Field Description 2', order='model_field', bool=True)
        def decorator2(self, obj):
            return obj.model_field > 10


If you want to use on admin form to show some information,
don't forget to add your custom field on ``readonly_fields`` attribute of your admin class

.. code-block:: python

    from django.contrib import admin
    import easy

    class YourAdmin(admin.ModelAdmin):
        fields = ('custom1', 'custom2', 'custom3' ... 'customN')
        readonly_fields = ('custom1', 'custom2', 'custom3' ... 'customN')

        custom1 = easy.ForeignKeyAdminField('related')
        # ...

Another way to use is directly on ``list_fields`` declaration:

.. code-block:: python

    from django.contrib import admin
    import easy

    class YourAdmin(admin.ModelAdmin):
        list_fields = (
            easy.TemplateAdminField('test.html', 'shorty description', 'order_field'),
            easy.ImageAdminField('image', {'image_attrs':'attr_value'}),
            # ...
        )

        # ...

Mixin
-----

To help you to create a custom view on django admin, we create the MixinEasyViews for your Admin Classes

.. code-block:: python

    from django.contrib import admin
    import easy

    class MyModelAdmin(easy.MixinEasyViews, admin.ModelAdmin):
        # ...

        def easy_view_jump(self, request, pk=None):
            # do something here
            return HttpResponse('something')

To call this view, you can use this reverse:

.. code-block:: python

    from django.core.urlresolvers import reverse

    # to do something with one object of a model
    reverse('admin:myapp_mymodel_easy', args=(obj.pk, 'jump'))

    # or to do something with a model
    reverse('admin:myapp_mymodel_easy', args=('jump',))

Or one HTML template

.. code-block:: html

    #<!-- to do something with one object of a model -->
    {% url 'admin:myapp_mymodel_easy' obj.pk 'jump' %}

    #<!-- or to do something with a model -->
    {% url 'admin:myapp_mymodel_easy' 'jump' %}

Utilities
---------

* Response for admin actions

  Return for the change list and show some message for the user keeping or not the filters.

.. code-block:: python

    from django.contrib import admin
    from django.contrib import messages
    import easy

    class YourAdmin(admin.ModelAdmin):
        # ...
        actions = ('simples_action',)

        def simples_action(self, request, queryset):

            success = queryset.do_something()
            if success:
                return easy.action_response(request, 'Some success message for user', keep_querystring=False)
            else:
                return easy.action_response(request, 'Some error for user', messages.ERROR)

            # or just redirect to changelist with filters
            return easy.action_response()

So easy, no?

Screenshot
----------

Using example of poll of django tutorial

.. image:: https://raw.githubusercontent.com/ebertti/django-admin-easy/master/screenshot/more.png

.. image:: https://raw.githubusercontent.com/ebertti/django-admin-easy/master/screenshot/related.png

Please help us
--------------
This project is still under development. Feedback and suggestions are very welcome and I encourage you to use the `Issues list <http://github.com/ebertti/django-admin-easy/issues>`_ on Github to provide that feedback.

.. image:: https://img.shields.io/github/issues/ebertti/django-admin-easy.svg
   :target: https://github.com/ebertti/django-admin-easy/issues

.. image:: https://img.shields.io/waffle/label/ebertti/django-admin-easy/in%20progress.svg?maxAge=2592000
   :target: https://waffle.io/ebertti/django-admin-easy

.. image:: https://img.shields.io/github/forks/ebertti/django-admin-easy.svg
   :target: https://github.com/ebertti/django-admin-easy/network

.. image:: https://img.shields.io/github/stars/ebertti/django-admin-easy.svg
   :target: https://github.com/ebertti/django-admin-easy/stargazers

Authors
-------
The django-admin-easy was originally created by Ezequiel Bertti `@ebertti <https://github.com/ebertti>`_ October 2014.

Changelog
---------
* 0.7.0

   Add support for Django 4.0, 4.1 and 4.2
   Add support for Python 3.10 and 3.11
   Add Github Actions for testing
   Add job to realease on pypi
   Thanks @Lex98

* 0.6.1

   Add support for Django 3.2 and Python 3.9

* 0.6

   Add RawIdAdminField

* 0.5.1

   Add permission on action decorator

* 0.4.1

   Django 2.0

* 0.4

   Django 1.11
   Create module utils with action_response

* 0.3.2

   Add params_static to LinkChangeListAdminField

* 0.3.1

   Add FormatAdminField

* 0.3

   Add import from `__future__` on all files
   Django 1.10
   More decorators
   More admin fields

* 0.2.2

   Add MixinEasyViews

* 0.2.1

   Fix for Django 1.7 from `@kevgathuku <https://github.com/kevgathuku>`_
