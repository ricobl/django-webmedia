#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

'''
class MyModelManager(models.Manager):
    pass

class MyModel(models.Model):
    """
    Sample model.
    """

    name = models.CharField('name', max_length=64)

    objects = MyModelManager()

    class Meta:
        verbose_name = 'my model'
        verbose_name_plural = 'my models'

    def __unicode__(self):
        return u'%s' % (self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('view_name', [self.pk])
'''
