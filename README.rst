django-admin-easy
=================

Collection of admin fields and decorators to help to create computed or custom fields more friendly and easy way

.. image:: https://pypip.in/v/django-admin-easy/badge.png
 :target: http://pypi.python.org/pypi/requery

.. image:: https://pypip.in/d/django-admin-easy/badge.png
 :target: http://pypi.python.org/pypi/requery

.. image:: https://travis-ci.org/ebertti/django-admin-easy.svg?branch=master
 :target: https://travis-ci.org/ebertti/django-admin-easy

.. image:: https://coveralls.io/repos/ebertti/django-admin-easy/badge.png?branch=master
 :target: https://coveralls.io/r/ebertti/django-admin-easy?branch=master

.. image:: https://landscape.io/github/ebertti/django-admin-easy/master/landscape.png
   :target: https://landscape.io/github/ebertti/django-admin-easy/master

Installation
------------

1. ``pip install django-admin-easy``

Usage
-----

in your admin file

.. code-block:: python

    from django.contrib import admin
    import easy

    class YourAdmin(admin.ModelAdmin):
        list_fields = ('id', 'custom1', 'custom2', 'custom3' ... 'customN')

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

        # render template
        custom8 = easy.TemplateAdminField('test.html', 'shorty description', 'order_field')

        # render to change_list of another model with a filter on query
        custom9 = easy.LinkChangeListAdminField('app_label', 'model_name', 'attribute_to_text', {'field_name':'field_to_query'})

        @easy.smart(short_description='Field Description 10', admin_order_field='model_field')
        def custom10(self, obj):
            return obj.something_cool()

        @easy.smart(short_description='Field Description 11', admin_order_field='model_field', allow_tags=True)
        def custom11(self, obj):
            return '<b>' + obj.model_field + '</b>'

        @easy.smart(short_description='Field Description 12', admin_order_field='model_field', boolean=True)
        def custom12(self, obj):
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