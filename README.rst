django-admin-easy
=================

Collection of admin fields and decorators to help to create computed or custom fields more friendly and easy way

.. image:: https://pypip.in/v/django-admin-easy/badge.png?style=flat
 :target: http://pypi.python.org/pypi/django-admin-easy

.. image:: https://pypip.in/d/django-admin-easy/badge.png?style=flat
 :target: http://pypi.python.org/pypi/django-admin-easy

.. image:: https://travis-ci.org/ebertti/django-admin-easy.svg?branch=master&style=flat
 :target: https://travis-ci.org/ebertti/django-admin-easy

.. image:: https://coveralls.io/repos/ebertti/django-admin-easy/badge.png?branch=master&style=flat
 :target: https://coveralls.io/r/ebertti/django-admin-easy?branch=master

.. image:: https://landscape.io/github/ebertti/django-admin-easy/master/landscape.png?style=flat
   :target: https://landscape.io/github/ebertti/django-admin-easy/master

Installation
------------

1. ``pip install django-admin-easy``

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

        def is_true(self, obj)
            return obj.value > 0
        is_true.short_description = 'Positive'
        is_true.admin_order_field = 'value'
        is_true.boolean = True

It takes to much lines! =D

With **django-admin-easy** you can easy create this field with less lines:

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
        def is_true(self, obj)
            return obj.value > 0

More Examples
-------------

.. code-block:: python

    from django.contrib import admin
    import easy

    class YourAdmin(admin.ModelAdmin):
        list_fields = ('id', 'custom1', 'custom2', 'custom3' ... 'customN')

        actions = ('simples_action',)

        @easy.action('My Little Simple Magic Action')
        def simple_action(self, request, queryset)
            return queryset.update(magic=True)


        # render a value of field, method, property or your model or related model
        custom1 = easy.SimpleAdminField('model_field')
        custom1 = easy.SimpleAdminField('method_of_model')
        custom2 = easy.SimpleAdminField('related.attribute_or_method')
        custom4 = easy.SimpleAdminField('related_set.count', 'count')
        custom5 = easy.SimpleAdminField(lambda x: x.method(), 'show', 'order_by')

        # render boolean fields
        custom6 = easy.BooleanAdminField(lambda x: x.value > 10, 'high')

        # render foreignkey with link to change_form in admin
        custom7 = easy.ForeignKeyAdminField('related')

        # render foreignkey with link to change_form in admin and related_id content as text
        custom8 = easy.ForeignKeyAdminField('related', 'related_id')

        # render template
        custom9 = easy.TemplateAdminField('test.html', 'shorty description', 'order_field')

        # render to change_list of another model with a filter on query
        custom10 = easy.LinkChangeListAdminField('app_label', 'model_name', 'attribute_to_text', {'field_name':'field_to_query'})

        # display image of some model
        custom11 = easy.ImageAdminField('image', {'image_attrs':'attr_value'})

        @easy.smart(short_description='Field Description 12', admin_order_field='model_field')
        def custom12(self, obj):
            return obj.something_cool()

        @easy.short(desc='Field Description 13', order='model_field', tags=True)
        def custom13(self, obj):
            return '<b>' + obj.model_field + '</b>'

        @easy.short(desc='Field Description 14', order='model_field', bool=True)
        def custom14(self, obj):
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


Screenshot
----------

Using example of poll of django tutorial

.. image:: https://raw.githubusercontent.com/ebertti/django-admin-easy/master/screenshot/more.png

.. image:: https://raw.githubusercontent.com/ebertti/django-admin-easy/master/screenshot/related.png

Please help us
--------------
This project is still under development. Feedback and suggestions are very welcome and I encourage you to use the `Issues list <http://github.com/ebertti/django-admin-easy/issues>`_ on Github to provide that feedback.

Authors
-------
The django-admin-easy was original created by Ezequiel Bertti `@ebertti <https://github.com/ebertti>`_ October 2014.

Changelog
---------

* 0.2.1

  * Fix for Django 1.7 from `@kevgathuku <https://github.com/kevgathuku>`_
