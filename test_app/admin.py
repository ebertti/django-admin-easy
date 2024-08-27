# coding: utf-8
from django.contrib import admin
from django.http.response import HttpResponse
import easy
from test_app.models import Choice, Question, Poll, Tag


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'poll_link', 'bool_sample', 'question_text', 'pub_date',)
    list_filter = ('pub_date',)
    search_fields = ('question_text',)
    fieldsets = (
        (None, {
            'fields': ('poll', 'question_text',)
        }),(
            'Date information',
            {'classes': ('collapse',),
            'fields': ('pub_date',),
            }
        ),
    )
    inlines = (ChoiceInline,)

    poll_link = easy.ForeignKeyAdminField('poll')
    bool_sample = easy.BooleanAdminField(lambda x: x.id == 1, 'First')


class PollAdmin(easy.MixinEasyViews, admin.ModelAdmin):
    list_display = ('name', 'count_question')

    count_question = easy.LinkChangeListAdminField('test_app', 'question', 'question_set.count', {'poll': 'id'}, 'Count')

    def easy_view_test(self, request, *args):

        return HttpResponse('test is ok with %s' % (args or 'list'))

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_link')

    generic_link = easy.GenericForeignKeyAdminField('generic', cache_content_type=True)

admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
