import uuid
import django

from django.contrib.admin import AdminSite
from django.contrib.sessions.backends.db import SessionStore
from django.http.request import HttpRequest, QueryDict
from django import test
from django.utils.datetime_safe import datetime, time
from django.utils.safestring import SafeData
from easy.six import urlencode
from model_mommy import mommy

import easy
from easy.helper import Nothing
from test_app.admin import PollAdmin
from test_app.models import Question, Poll


class TestSimpleAdminField(test.TestCase):

    def test_simple(self):
        question = mommy.make(
            Question
        )

        custom_field = easy.SimpleAdminField('poll')
        ret = custom_field(question)

        self.assertEqual(ret, question.poll)
        self.assertEqual(custom_field.admin_order_field, 'poll')
        self.assertEqual(custom_field.short_description, 'poll')

    def test_simple_lambda(self):
        question = mommy.make(
            Question
        )

        custom_field = easy.SimpleAdminField(lambda obj: obj.poll, 'shorty')
        ret = custom_field(question)

        self.assertEqual(ret, question.poll)
        self.assertFalse(hasattr(custom_field, 'admin_order_field'))
        self.assertEqual(custom_field.short_description, 'shorty')

    def test_simple_default(self):
        question = mommy.make(
            Question
        )

        custom_field = easy.SimpleAdminField('not', default='default')
        ret = custom_field(question)

        self.assertEqual(ret, 'default')
        self.assertEqual(custom_field.short_description, 'not')


class TestBooleanAdminField(test.TestCase):
    def test_boolean(self):
        question = mommy.make(
            Question,
            question_text='Eba!'
        )

        custom_field = easy.BooleanAdminField(lambda x: x.question_text == "Eba!", 'Eba?')
        ret = custom_field(question)

        self.assertEqual(ret, True)
        self.assertTrue(custom_field.boolean)


class TestForeignKeyAdminField(test.TestCase):
    def test_foreignkey(self):
        question = mommy.make(
            Question,
            question_text='Eba!'
        )

        custom_field = easy.ForeignKeyAdminField('poll')
        ret = custom_field(question)
        if django.VERSION < (1, 9):
            expected = u'<a href="/admin/test_app/poll/1/">Poll object</a>'
        elif django.VERSION < (2, 0):
            expected = u'<a href="/admin/test_app/poll/1/change/">Poll object</a>'
        else:
            expected = u'<a href="/admin/test_app/poll/1/change/">Poll object (1)</a>'

        self.assertEqual(expected, ret)
        self.assertTrue(custom_field.allow_tags)

    def test_foreignkey_display(self):
        question = mommy.make(
            Question,
            question_text='Eba!'
        )

        custom_field = easy.ForeignKeyAdminField('poll', 'poll_id')
        ret = custom_field(question)
        if django.VERSION < (1, 9):
            expected = u'<a href="/admin/test_app/poll/1/">1</a>'
        else:
            expected = u'<a href="/admin/test_app/poll/1/change/">1</a>'

        self.assertEqual(expected, ret)
        self.assertTrue(custom_field.allow_tags)

    def test_foreignkey_display_sub_property(self):
        question = mommy.make(
            Question,
            question_text='Eba!'
        )

        custom_field = easy.ForeignKeyAdminField('poll', 'poll.id')
        ret = custom_field(question)

        if django.VERSION < (1, 9):
            expected = u'<a href="/admin/test_app/poll/1/">1</a>'
        else:
            expected = u'<a href="/admin/test_app/poll/1/change/">1</a>'

        self.assertEqual(expected, ret)
        self.assertTrue(custom_field.allow_tags)


class TestTemplateAdminField(test.TestCase):

    def test_template(self):
        question = mommy.make(
            Question,
            question_text='Eba!'
        )

        custom_field = easy.TemplateAdminField('test.html', {'a': '1'})
        ret = custom_field(question)

        expected = u'<div>Eba! - 1</div>'

        self.assertEqual(expected, ret)
        self.assertTrue(custom_field.allow_tags)


class TestLinkChangeListAdminField(test.TestCase):

    def test_link(self):
        poll = mommy.make(
            Poll,
        )

        custom_field = easy.LinkChangeListAdminField('test_app', 'question', 'question_set.count',
                                                     {'pool': 'id'}, {'static': 1})
        ret = custom_field(poll)

        q = urlencode({'pool': poll.id, 'static': 1})

        expected = u'<a href="/admin/test_app/question/?' + q +'">0</a>'

        self.assertEqual(expected, ret)
        self.assertTrue(custom_field.allow_tags)


class TestImageField(test.TestCase):

    def test_image_field(self):
        question = mommy.make(
            Question,
            image='asd.jpg',
            question_text='bla'
        )

        custom_field = easy.ImageAdminField('image', {'title': 'question_text'})
        ret = custom_field(question)

        expected = u'<img src="asd.jpg" title="bla"/>'

        self.assertEqual(expected, ret)
        self.assertTrue(custom_field.allow_tags)

class TestFilterField(test.TestCase):

    def test_image_field(self):
        question = mommy.make(
            Question,
            question_text='Django admin easy is helpful?'
        )

        custom_field = easy.FilterAdminField('question_text', 'upper')
        ret = custom_field(question)

        self.assertEqual(ret, 'DJANGO ADMIN EASY IS HELPFUL?')


class TestFormatField(test.TestCase):
    def test_format_field(self):
        question = mommy.make(
            Question,
            pub_date=datetime(2016, 11, 22),
            question_text='Django admin easy is helpful?',
        )

        custom_field = easy.FormatAdminField('{o.question_text} | {o.pub_date:%Y-%m-%d}', 'column')
        ret = custom_field(question)

        self.assertEqual(ret, 'Django admin easy is helpful? | 2016-11-22')


class TestNothing(test.TestCase):

    def test_nothing(self):
        nothing = Nothing()

        self.assertEqual(nothing.__str__(), 'Error')
        self.assertEqual(nothing.__unicode__(), u'Error')


class TestSmartDecorator(test.TestCase):

    def test_decorator(self):

        @easy.smart(short_description='test', admin_order_field='test_field', allow_tags=True, boolean=True)
        def field(self, obj):
            return obj

        self.assertEqual(field.short_description, 'test')
        self.assertEqual(field.admin_order_field, 'test_field')
        self.assertEqual(field.allow_tags, True)
        self.assertEqual(field.boolean, True)
        self.assertEqual(field(object(), 1), 1)


class TestShortDecorator(test.TestCase):

    def test_decorator(self):

        @easy.short(desc='test', order='test_field', tags=True, bool=True, empty='-')
        def field(self, obj):
            return obj

        self.assertEqual(field.short_description, 'test')
        self.assertEqual(field.admin_order_field, 'test_field')
        self.assertEqual(field.allow_tags, True)
        self.assertEqual(field.boolean, True)
        self.assertEqual(field.empty_value_display, '-')
        self.assertEqual(field(object(), 1), '1')

    def test_with_no_default_keys(self):
        @easy.short(asd='test', ds='test_field')
        def field(self, obj):
            return obj

        self.assertEqual(field.asd, 'test')
        self.assertEqual(field.ds, 'test_field')

class TestWithTagDecorator(test.TestCase):

    def test_decorator_empty(self):

        @easy.with_tags()
        def field(self, obj):
            return obj

        r = field(self, 'asd')
        self.assertIsInstance(field(object(), 'asd'), SafeData)


class TestDjangoUtilsDecorator(test.TestCase):

    def test_decorators(self):

        @easy.utils('html.escape')
        @easy.utils('html.conditional_escape')
        @easy.utils('html.strip_tags')
        @easy.utils('text.slugify')
        @easy.utils('translation.gettext')
        @easy.utils('translation.ugettext')
        @easy.utils('translation.gettext_noop')
        @easy.utils('translation.ugettext_noop')
        def field(self, obj):
            return obj

        self.assertEquals(field(object(), 'asd'), 'asd')

    def test_function_not_exist(self):

        with self.assertRaises(Exception):
            @easy.utils('anything')
            def field(self, obj):
                return obj

class TestDjangoFilterDecorator(test.TestCase):

    def test_decorators(self):

        @easy.filter('localize', 'l10n')
        def field(self, obj):
            return 10

        self.assertEquals(field(object(), 'asd'), '10')

    def test_decorators_from_detaultags(self):

        @easy.filter('capfirst')
        def field(self, obj):
            return 'ezequiel bertti'

        self.assertEquals(field(object(), 'asd'), 'Ezequiel bertti')

    def test_decorators_with_args(self):

        @easy.filter('date', 'django', 'y-m-d')
        def field(self, obj):
            return datetime(2016, 6, 25)

        self.assertEquals(field(object(), 'asd'), '16-06-25')

    def test_templatetag_not_exist(self):

        with self.assertRaises(Exception):
            @easy.filter('asd')
            def field(self, obj):
                return obj

    def test_filter_not_exist(self):
        with self.assertRaises(Exception):
            @easy.filter('asd', 'localize')
            def field(self, obj):
                return obj


class TestCacheDecorator(test.TestCase):

    @easy.cache(10)
    def field(self, obj):
        return uuid.uuid1()

    @easy.cache(10)
    def field2(self, obj):
        return uuid.uuid1()

    def setUp(self):
        self.pool = mommy.make(
            Poll,
        )

        self.value = self.field(self.pool)

    def test_decorators(self):
        value2 = self.field(self.pool)

        self.assertEquals(self.value, value2)

    def test_delete_cache(self):
        easy.clear_cache(self.pool)
        value2 = self.field(self.pool)

        self.assertNotEquals(self.value, value2)

    def test_another_field(self):

        value1 = self.field(self.pool)
        value2 = self.field2(self.pool)

        self.assertNotEquals(value1, value2)


class TestMultiDecorator(test.TestCase):

    def test_multidecorator(self):

        @easy.utils('safestring.mark_safe')
        @easy.filter('date', 'django', 'y-m-d')
        def field(self, obj):
            return datetime(2016, 6, 25)

        v = field(1, 1)
        self.assertEquals(v, '16-06-25')
        self.assertIsInstance(v, SafeData)


class TestActionDecorator(test.TestCase):

    def test_decorator(self):
        @easy.action('description')
        def field(self, obj):
            return obj

        self.assertEqual(field(self, 1), 1)
        self.assertEqual(field.short_description, 'description')

    def test_decorator_permission(self):
        @easy.action('description', 'change')
        def field(self, obj):
            return obj

        self.assertEqual(field(self, 1), 1)
        self.assertEqual(field.short_description, 'description')
        self.assertEqual(field.allowed_permissions, ('change',))


    def test_decorator_permission_array(self):
        @easy.action('description', ['change'])
        def field(self, obj):
            return obj

        self.assertEqual(field(self, 1), 1)
        self.assertEqual(field.short_description, 'description')
        self.assertEqual(field.allowed_permissions, ['change',])


class TestEasyView(test.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.admin = PollAdmin(Poll, AdminSite())
        super(TestEasyView, cls).setUpClass()

    def test_register_view(self):
        views = self.admin.get_urls()
        if django.VERSION < (1, 9):
            self.assertEqual(len(views), 7)
        elif django.VERSION < (2, 0):
            self.assertEqual(len(views), 8)
        else:
            self.assertEqual(len(views), 9)

    def test_exist_view(self):
        request = HttpRequest()
        response1 = self.admin.easy_list_view(request, 'test')
        response2 = self.admin.easy_object_view(request, 1, 'test')

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

    def test_not_exist_view(self):
        from django.contrib.messages.storage import default_storage

        request = HttpRequest()
        request.session = SessionStore('asd')
        request._messages = default_storage(request)

        response1 = self.admin.easy_list_view(request, 'not')
        response2 = self.admin.easy_object_view(request, 1, 'not')

        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(len(request._messages._queued_messages), 2)


class TestUtilActionRedirect(test.TestCase):

    def test_response_normal(self):
        from django.contrib.messages.storage import default_storage

        request = HttpRequest()
        request.GET = QueryDict('test=asd')
        request.session = SessionStore('asd')
        request._messages = default_storage(request)

        response = easy.action_response(request, 'Some message')

        self.assertEqual(len(request._messages._queued_messages), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], './?test=asd')

    def test_response_without_querystring(self):
        from django.contrib.messages.storage import default_storage

        request = HttpRequest()
        request.GET = QueryDict('test=asd')
        request.session = SessionStore('asd')
        request._messages = default_storage(request)

        response = easy.action_response(request, 'Some message', keep_querystring=False)

        self.assertEqual(len(request._messages._queued_messages), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '.')

    def test_response_whitout_message(self):
        from django.contrib.messages.storage import default_storage

        request = HttpRequest()
        request.GET = QueryDict('test=asd')
        request.session = SessionStore('asd')
        request._messages = default_storage(request)

        response = easy.action_response(request)
        self.assertEqual(len(request._messages._queued_messages), 0)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], './?test=asd')

    def test_response_whitout_message_and_querystring(self):
        from django.contrib.messages.storage import default_storage

        request = HttpRequest()
        request.GET = QueryDict('test=asd')
        request.session = SessionStore('asd')
        request._messages = default_storage(request)

        response = easy.action_response(request, keep_querystring=False)

        self.assertEqual(len(request._messages._queued_messages), 0)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '.')

    def test_response_whitout_GET(self):
        from django.contrib.messages.storage import default_storage

        request = HttpRequest()
        request.session = SessionStore('asd')
        request._messages = default_storage(request)

        response = easy.action_response(request)

        self.assertEqual(len(request._messages._queued_messages), 0)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '.')
