from typing import Optional, Union, List, Any, Dict

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models import Model, ImageField as ModelImageField, ForeignKey
from django.conf import settings
from django.forms.utils import flatatt
from django.urls import reverse
from django.utils.html import conditional_escape
from django.template.loader import render_to_string
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from .decorators import django_cache

from easy import helper


class BaseAdminField(object):

    def __init__(
        self,
        short_description: str,
        admin_order_field: Optional[str] = None,
        allow_tags: bool = False
    ) -> None:
        """
            Base Admin Field to be extended
        Args:
            short_description (str): The short description of the admin field.
            admin_order_field (Optional[str]): The field to order by when clicked in the admin.
            allow_tags (bool): Whether to allow HTML tags in the rendered field.
        """
        self.short_description = short_description
        if admin_order_field:
            self.admin_order_field = admin_order_field
        if allow_tags:
            self.allow_tags = allow_tags

    def render(self, obj):
        raise NotImplementedError()

    def __call__(self, obj):
        if getattr(self, 'allow_tags', False):
            return mark_safe(self.render(obj))
        return self.render(obj)


class SimpleAdminField(BaseAdminField):

    def __init__(
        self,
        attr: str,
        short_description: Optional[str] = None,
        admin_order_field: Optional[str] = None,
        allow_tags: bool = False,
        default: Optional[str] = None
    ) -> None:
        """
        Admin field that renders the value of the specified attribute.

        Args:
            attr (str): The attribute to render. If a callable, the callable will be
                called with the object as the only argument and its return value will be rendered.
            short_description (Optional[str]): The short description of the field.
            admin_order_field (Optional[str]): The field to order by when clicked in the admin. If not specified, the
                attribute name will be used.
            allow_tags (bool): Whether to allow HTML tags in the rendered field.
            default (Optional[str]): The default value to render if the attribute is None.
                If a callable, the callable will be called with no arguments and its return value will be rendered.
        """
        self.attr = attr
        self.default = default

        if callable(attr):
            assert short_description
        else:
            admin_order_field = admin_order_field or attr.replace('.', '__')

        short_description = short_description or attr.split('.')[-1]

        super(SimpleAdminField, self).__init__(short_description, admin_order_field, allow_tags)

    def render(self, obj):
        return helper.call_or_get(obj, self.attr, self.default)


class BooleanAdminField(SimpleAdminField):

    def __init__(
        self,
        attr: str,
        short_description: Optional[str] = None,
        admin_order_field: Optional[str] = None
    ) -> None:
        """
        Admin field that renders a boolean icon for the value.

        Args:
            attr (str): The attribute to render.
            short_description (Optional[str]): The short description of the field.
            admin_order_field (Optional[str]): The field to order by when clicked in the admin.
        """
        self.boolean = True
        super(BooleanAdminField, self).__init__(attr, short_description, admin_order_field, False, False)

    def render(self, obj):
        return bool(super(BooleanAdminField, self).render(obj))


class ForeignKeyAdminField(SimpleAdminField):

    def __init__(
        self,
        attr: str,
        display: Optional[str] = None,
        short_description: Optional[str] = None,
        admin_order_field: Optional[str] = None,
        default: Optional[str] = None,
    ) -> None:
        """
        Admin field for displaying foreign key with link to change related object.

        Args:
            attr (str): The foreign key attribute to display.
            display (Optional[str]): The attribute to display instead of the foreign key
                attribute. Defaults to None.
            short_description (Optional[str]): The short description of the field.
            admin_order_field (Optional[str]): The field to order by when clicked in the admin.
            default (Optional[str]): The default value to display if the foreign key attribute
                is None. Defaults to None.
        """
        self.display = display
        super().__init__(attr, short_description, admin_order_field, True, default)

    def render(self, obj):
        ref = helper.call_or_get(obj, self.attr, self.default)
        display = None
        if self.display:
            display = helper.call_or_get(obj, self.display, self.default)

        display = display or ref
        if isinstance(ref, Model):
            return '<a href="%s">%s</a>' % (
                reverse(
                    admin_urlname(ref._meta, 'change'),
                    args=(ref.pk,)
                ),
                conditional_escape(display or ref)
            )

        return self.default


class RawIdAdminField(SimpleAdminField):

    def __init__(
        self,
        attr: str,
        short_description: Optional[str] = None,
        admin_order_field: Optional[str] = None,
        default: Optional[str] = None,
    ) -> None:
        """
        Admin field for displaying raw id of foreign key.

        Args:
            attr (str): The foreign key attribute to display.
            short_description (Optional[str]): The short description of the field.
            admin_order_field (Optional[str]): The field to order by when clicked in the admin.
            default (Optional[str]): The default value to display if the foreign key attribute
                is None. Defaults to None.
        """
        super(RawIdAdminField, self).__init__(attr, short_description, admin_order_field, True, default)

    def render(self, obj):
        field = obj._meta.get_field(self.attr)

        if isinstance(field, ForeignKey):
            meta = field.related_model._meta
            id = getattr(obj, field.attname)
            return '<a href="%s">%s</a>' % (
                reverse(
                    admin_urlname(meta, 'change'),
                    args=(id,)
                ),
                conditional_escape(id)
            )

        return self.default

class GenericForeignKeyAdminField(SimpleAdminField):

    def __init__(
        self,
        attr: str,
        short_description: Optional[str] = None,
        admin_order_field: Optional[str] = None,
        default: Optional[str] = None,
        cache_content_type: bool = False,
        related_attr: Optional[str] = None
    ) -> None:
        """
        Admin field for displaying generic foreign key with link to change related object.

        Args:
            attr (str): The foreign key attribute to display.
            short_description (Optional[str]): The short description of the field.
            admin_order_field (Optional[str]): The field to order by when clicked in the admin.
            default (Optional[str]): The default value to display if the foreign key attribute
                is None. Defaults to None.
            cache_content_type (bool): Whether to cache the content type. Defaults to False.
            related_attr (Optional[str]): The attribute to display instead of the foreign key
                attribute of related object. Defaults to None.
        """
        self.cache_content_type = cache_content_type
        self.related_attr = related_attr
        super(GenericForeignKeyAdminField, self).__init__(
            attr,
            short_description,
            admin_order_field,
            True,
            default
        )

    def render(self, obj):
        from django.contrib.contenttypes.fields import GenericForeignKey
        ct = None
        field = obj._meta.get_field(self.attr)

        if not isinstance(field, GenericForeignKey):
            return self.default

        pk = getattr(obj, field.fk_field)
        if not pk:
            return self.default

        if self.cache_content_type:
            key = helper.EASY_CACHE_TEMPLATE_OBJ.format(
                'content-type',
                getattr(obj, f"{field.ct_field}_id")
            )
            ct = django_cache.get(key)
            if not ct:
                ct = getattr(obj, field.ct_field)
                django_cache.set(key, ct)

        if self.related_attr:
            if self.cache_content_type:
                related = ct.get_object_for_this_type(pk=pk)
            else:
                related = getattr(obj, self.attr)
            display = helper.call_or_get(related, self.related_attr, self.default)
        else:
            display = pk

        if not ct:
            ct = getattr(obj, field.ct_field)
        return '<a href="%s">%s</a>' % (
            reverse(
                'admin:%s_%s_change' % (ct.app_label, ct.model),
                args=(pk,)
            ),
            "%s | %s" % (display, ct.name)
        )


class LinkChangeListAdminField(BaseAdminField):

    def __init__(
        self,
        app: str,
        model: str,
        attr: str,
        params: Optional[Dict[str, str]] = None,
        params_static: Optional[Dict[str, str]] = None,
        short_description: Optional[str] = None,
        admin_order_field: Optional[str] = None,
    ) -> None:
        """
        Admin field for displaying link to change list filtered by some parameters in the URL.

        Args:
            app (str): The Django app label.
            model (str): The Django model name.
            attr (str): The attribute to display.
            params (Optional[Dict[str, str]]): The parameters to include in the URL.
            params_static (Optional[Dict[str, str]]): The static parameters to include in the URL.
            short_description (Optional[str]): The short description of the field.
            admin_order_field (Optional[str]): The field to order by when clicked in the admin.
        """
        self.app = app
        self.model = model
        self.attr = attr
        self.params = params or {}
        self.params_static = params_static or {}
        super(LinkChangeListAdminField, self).__init__(short_description or model, admin_order_field, True)

    def render(self, obj):
        text = helper.call_or_get(obj, self.attr)
        p_params = {}
        for key in self.params.keys():
            p_params[key] = helper.call_or_get(obj, self.params[key])

        p_params.update(self.params_static)

        return '<a href="%s">%s</a>' % (
            reverse('admin:%s_%s_changelist' % (self.app, self.model)) + '?' + urlencode(p_params),
            conditional_escape(text)
        )


class ExternalLinkAdminField(BaseAdminField):
    # todo : test with this one

    def __init__(self, attr, text, link, args, short_description, **kwargs):
        self.text = conditional_escape(text)
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

    def __init__(
        self,
        template: str,
        context: Optional[Dict[str, Any]] = None,
        short_description: Optional[str] = 'without_name',
        admin_order_field: Optional[str] = None,
    ) -> None:
        """
        Admin field for rendering a template.

        Args:
            template (str): The name of the template to render.
            context (Optional[Dict[str, Any]]): The context to pass to the template. Defaults to None.
            short_description (Optional[str]): The short description of the field. Defaults to 'without_name'.
            admin_order_field (Optional[str]): The field to order by when clicked in the admin.
        """
        self.context = context or {}
        self.template = template
        super(TemplateAdminField, self).__init__(short_description, admin_order_field, True)

    def render(self, obj):
        context = self.context.copy()
        context.update({'obj': obj})
        return render_to_string(self.template, context)


class ImageAdminField(BaseAdminField):

    def __init__(
        self,
        attr: str,
        params: Optional[Dict[str, str]] = None,
        short_description: Optional[str] = None,
        admin_order_field: Optional[str] = None
    ) -> None:
        """
        Admin field for rendering an image.

        Args:
            attr (str): The attribute containing the image path.
            params (Optional[Dict[str, str]]): The additional parameters to include in the image tag. Defaults to None.
            short_description (Optional[str]): The short description of the field. Defaults to None.
            admin_order_field (Optional[str]): The field to order by when clicked in the admin. Defaults to None.
        """
        self.attr = attr
        self.params = params or {}
        super().__init__(short_description or attr, admin_order_field, True)

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


class FilterAdminField(SimpleAdminField):

    def __init__(
        self,
        attr: str,
        django_filter: str,
        load: Optional[str] = None,
        extra: Optional[Union[str, List[str]]] = None,
        short_description: Optional[str] = None,
        admin_order_field: Optional[str] = None,
        allow_tags: bool = False,
        default: Optional[str] = None,
    ) -> None:
        """
        Admin field that applies a Django filter to the field's value.

        Args:
            attr (str): The attribute to render.
            django_filter (str): The Django template filter to apply.
            load (Optional[str]): library to be loaded like load in templatetag.
            extra (Optional[Union[str, List[str]]]): The extra arguments to pass to the filter.
            short_description (Optional[str]): The short description to use.
            admin_order_field (Optional[str]): The field to order by when clicked in the admin.
            allow_tags (bool): Whether to allow HTML tags in the rendered field.
            default (Optional[str]): The default value to use.
        """
        self.filter = django_filter
        self.load = load
        self.extra = extra
        super().__init__(attr, short_description, admin_order_field, allow_tags, default)

    def render(self, obj):
        value = super(FilterAdminField, self).render(obj)
        filter_method = helper.get_django_filter(self.filter, self.load)
        args = (self.extra) if self.extra else []
        return filter_method(value, *args)


class CacheAdminField(SimpleAdminField):

    def __init__(
        self,
        attr: str,
        django_filter: str,
        load: Optional[str] = None,
        extra: Optional[Union[str, List[str]]] = None,
        short_description: Optional[str] = None,
        admin_order_field: Optional[str] = None,
        allow_tags: bool = False,
        default: Optional[str] = None,
    ) -> None:
        """
        Admin field that formats the value using a string format.
        Args:
            attr (str): The attribute to render.
            django_filter (str): The Django filter to use.
            load (Optional[str]): The load method to use.
            extra (Optional[Union[str, List[str]]]): The extra arguments to use.
            short_description (Optional[str]): The short description to use.
            admin_order_field (Optional[str]): The admin order field to use.
            allow_tags (bool): Whether to allow HTML tags in the rendered field.
            default (Optional[str]): The default value to use.
        """
        self.filter = django_filter
        self.load = load
        self.extra = extra
        super().__init__(attr, short_description, admin_order_field, allow_tags, default)

    def render(self, obj):
        value = super(CacheAdminField, self).render(obj)
        filter_method = helper.get_django_filter(self.filter, self.load)
        args = (self.extra) if self.extra else []
        return filter_method(value, *args)


class FormatAdminField(BaseAdminField):

    def __init__(
        self,
        format_string: str,
        short_description: str,
        admin_order_field: Optional[str] = None,
        allow_tags: bool = False,
    ) -> None:
        """
        Admin field that formats the value using a string format.
        Args:
            format_string (str): The string format to use when rendering the field.
            short_description (str): The short description of the field.
            admin_order_field (str, optional): The field to order by when clicked in the admin.
            allow_tags (bool, optional): Whether to allow HTML tags in the rendered field.
        """
        self.format_string = format_string
        super().__init__(short_description, admin_order_field, allow_tags)

    def render(self, obj):

        return self.format_string.format(o=obj)
