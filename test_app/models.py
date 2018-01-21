# coding: utf-8
from django.db import models
from django.conf import settings

class Poll(models.Model):
    name = models.CharField(max_length=200)


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    image = models.ImageField(upload_to=settings.STATIC_PATH + '/media', blank=True, null=True)
    poll = models.ForeignKey(Poll, on_delete=models.PROTECT)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
