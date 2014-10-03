# coding: utf-8
from django.contrib import admin
from easy.admin.field import LinkChangeListAdminField, ForeignKeyAdminField
from test_app.models import Choice, Question, Poll


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('poll_link', 'question_text', 'pub_date',)
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


class PollAdmin(admin.ModelAdmin):
    list_display = ('name', 'count_question')

    count_question = LinkChangeListAdminField('test_app', 'question', 'question_set.count', {'poll': 'id'}, 'Count')

admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)