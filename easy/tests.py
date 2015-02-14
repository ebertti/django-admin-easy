# coding: utf-8
from django.contrib.admin import AdminSite
from django.contrib.sessions.backends.db import SessionStore
from django.http.request import HttpRequest
from django import test
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

        expected = u'<a href="/admin/test_app/poll/1/">Poll object</a>'

        self.assertEqual(expected, ret)
        self.assertTrue(custom_field.allow_tags)

    def test_foreignkey_display(self):
        question = mommy.make(
            Question,
            question_text='Eba!'
        )

        custom_field = easy.ForeignKeyAdminField('poll', 'poll_id')
        ret = custom_field(question)

        expected = u'<a href="/admin/test_app/poll/1/">1</a>'

        self.assertEqual(expected, ret)
        self.assertTrue(custom_field.allow_tags)

    def test_foreignkey_display_sub_property(self):
        question = mommy.make(
            Question,
            question_text='Eba!'
        )

        custom_field = easy.ForeignKeyAdminField('poll', 'poll.id')
        ret = custom_field(question)

        expected = u'<a href="/admin/test_app/poll/1/">1</a>'

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

        custom_field = easy.LinkChangeListAdminField('test_app', 'question', 'question_set.count', {'pool': 'id'})
        ret = custom_field(poll)

        expected = u'<a href="/admin/test_app/question/?pool=1">0</a>'

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

        @easy.short(desc='test', order='test_field', tags=True, bool=True)
        def field(self, obj):
            return obj

        self.assertEqual(field.short_description, 'test')
        self.assertEqual(field.admin_order_field, 'test_field')
        self.assertEqual(field.allow_tags, True)
        self.assertEqual(field.boolean, True)
        self.assertEqual(field(object(), 1), 1)


class TestActionDecorator(test.TestCase):

    def test_decorator(self):
        @easy.action('description')
        def field(self, obj):
            return obj

        self.assertEqual(field(self, 1), 1)
        self.assertEqual(field.short_description, 'description')


class TestEasyView(test.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.admin = PollAdmin(Poll, AdminSite())
        super(TestEasyView, cls).setUpClass()

    def test_register_view(self):
        views = self.admin.get_urls()
        self.assertEqual(len(views), 7)

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









