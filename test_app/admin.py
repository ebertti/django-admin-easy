# coding: utf-8
from django.contrib import admin
from easy.admin.field import LinkChangeListAdminField, ForeignKeyAdminField, BooleanAdminField
from test_app.models import Choice, Question, Poll


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

    poll_link = ForeignKeyAdminField('poll')
    bool_sample = BooleanAdminField(lambda x: x.id == 1, 'First')


class PollAdmin(admin.ModelAdmin):
    list_display = ('name', 'count_question')

    count_question = LinkChangeListAdminField('test_app', 'question', 'question_set.count', {'poll': 'id'}, 'Count')

admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)