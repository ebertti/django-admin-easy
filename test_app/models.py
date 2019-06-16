# coding: utf-8
from django.db import models
from django.conf import settings

class Poll(models.Model):
    name = models.CharField(max_length=200)


class PollGroup(models.Model):
    """Add this model to test the ManyToManyAdminField."""

    name = models.CharField(max_length=200)
    polls = models.ManyToManyField(Poll, related_name='poll_groups')


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    image = models.ImageField(upload_to='media', blank=True, null=True)
    poll = models.ForeignKey(Poll, on_delete=models.PROTECT)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
