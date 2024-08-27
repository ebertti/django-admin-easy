# coding: utf-8
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Poll(models.Model):
    name = models.CharField(max_length=200)


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    image = models.ImageField(upload_to='media', blank=True, null=True)
    poll = models.ForeignKey(Poll, on_delete=models.PROTECT)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

class Tag(models.Model):
    name = models.CharField(max_length=50)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    generic = GenericForeignKey('content_type', 'object_id')