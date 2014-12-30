# coding: utf-8
from django.utils.six.moves.urllib.parse import urlencode
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse
from django.db.models import Model, ImageField as ModelImageField
from django.conf import settings
from django.template.loader import render_to_string

try:
    from django.forms.utils import flatatt
except ImportError:
    from django.forms.util import flatatt

from easy import helper


class BaseAdminField(object):

    def __init__(self, short_description, admin_order_field=None, allow_tags=False):
        self.short_description = short_description
        if admin_order_field:
            self.admin_order_field = admin_order_field
        if allow_tags:
            self.allow_tags = allow_tags

    def render(self, obj):
        raise NotImplementedError()

    def __call__(self, obj):
        return self.render(obj)


class SimpleAdminField(BaseAdminField):

    def __init__(self, attr, short_description=None, admin_order_field=None, allow_tags=False, default=None):
        self.attr = attr
        self.default = default

        if hasattr(attr, '__call__'):
            assert short_description
        else:
            admin_order_field = admin_order_field or attr.replace('.', '__')

        short_description = short_description or attr.split('.')[-1]

        super(SimpleAdminField, self).__init__(short_description, admin_order_field, allow_tags)

    def render(self, obj):
        return helper.call_or_get(obj, self.attr, self.default)


class BooleanAdminField(SimpleAdminField):

    def __init__(self, attr, short_description=None, admin_order_field=None):
        self.boolean = True
        super(BooleanAdminField, self).__init__(attr, short_description, admin_order_field, False, False)

    def render(self, obj):
        return bool(super(BooleanAdminField, self).render(obj))


class ForeignKeyAdminField(SimpleAdminField):

    def __init__(self, attr, display=None, short_description=None, admin_order_field=None, default=None):
        self.display = display
        super(ForeignKeyAdminField, self).__init__(attr, short_description, admin_order_field, True, default)

    def render(self, obj):
        ref = helper.call_or_get(obj, self.attr, self.default)
        display = None
        if self.display:
            display = helper.call_or_get(obj, self.display, self.default)

        if isinstance(ref, Model):
            return '<a href="%s">%s</a>' % (
                reverse(
                    admin_urlname(ref._meta, 'change'),
                    args=(ref.pk,)
                ),
                display or ref
            )

        return self.default


class LinkChangeListAdminField(BaseAdminField):

    def __init__(self, app, model, attr, params=None, short_description=None, admin_order_field=None):
        self.app = app
        self.model = model
        self.attr = attr
        self.params = params or {}
        super(LinkChangeListAdminField, self).__init__(short_description or model, admin_order_field, True)

    def render(self, obj):
        text = helper.call_or_get(obj, self.attr)
        p_params = {}
        for key in self.params.keys():
            p_params[key] = helper.call_or_get(obj, self.params[key])

        return '<a href="%s">%s</a>' % (
            reverse('admin:%s_%s_changelist' % (self.app, self.model)) + '?' + urlencode(p_params),
            text
        )


class ExternalLinkAdminField(BaseAdminField):
    # todo : test with this one

    def __init__(self, attr, text, link, args, short_description, **kwargs):
        self.text = text
        self.attr = attr
        self.link = link
        if args:
            self.args = args if isinstance(args, (list, tuple)) else (args,)
        else:
            self.args = None
        super(ExternalLinkAdminField, self).__init__(short_description, kwargs.get('admin_order_field'), True)

    def render(self, obj):
        if self.attr == 'self':
            if not self.link:
                return obj.get_absolute_url()
            else:
                assert self.link
                if self.args:
                    p_args = [helper.deep_getattribute(obj, arg) for arg in self.args]
                else:
                    p_args = None
                return reverse(self.link, args=p_args)

        if not self.link:
            return helper.deep_getattribute(obj, self.attr).get_absolute_url()

        assert self.link
        ref = helper.deep_getattribute(obj, self.attr)

        if self.args:
            p_args = [helper.deep_getattribute(ref, arg) for arg in self.args]
        else:
            p_args = None

        return '<a href=%s>%s</a>' % (reverse(self.link, args=p_args), self.text)


class TemplateAdminField(BaseAdminField):

    def __init__(self, template, context=None, short_description='without_name', admin_order_field=None):
        self.context = context or {}
        self.template = template
        super(TemplateAdminField, self).__init__(short_description, admin_order_field, True)

    def render(self, obj):
        context = self.context.copy()
        context.update({'obj': obj})
        return render_to_string(self.template, context)


class ImageAdminField(BaseAdminField):

    def __init__(self, attr, params=None, short_description=None, admin_order_field=None):
        self.attr = attr
        self.params = params
        super(ImageAdminField, self).__init__(short_description or attr, admin_order_field, True)

    def render(self, obj):
        src = helper.call_or_get(obj, self.attr)

        if isinstance(src, ModelImageField):
            src = settings.MEDIA_URL + src

        p_params = {}
        for key in self.params.keys():
            p_params[key] = helper.call_or_get(obj, self.params[key])

        p_params['src'] = src

        return '<img%s/>' % (
            flatatt(p_params)
        )





