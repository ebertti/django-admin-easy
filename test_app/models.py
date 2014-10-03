# coding: utf-8
from django.db import models


class Poll(models.Model):
    name = models.CharField(max_length=200)


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    poll = models.ForeignKey(Poll)


class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)