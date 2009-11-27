#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.template import mark_safe
from django.test import TestCase
from PIL import Image
import os
import shutil

class BaseEmbedTest(TestCase):

    def render_tag(self, tag, context={}):
        t = template.Template('{% load webmedia_tags %}' + tag)
        content = t.render(template.Context(context))
        return content

class EmbedTagTest(BaseEmbedTest):

    def test_simple_image(self):
        content = self.render_tag('{% embed "/media/logo.gif" %}')
        self.assertTrue('<img src="/media/logo.gif" ' in content)

    def test_attributes(self):
        content = self.render_tag('{% embed "/media/logo.gif" width=100 height=200 %}')
        self.assertTrue(' src="/media/logo.gif"' in content)
        self.assertTrue(' width="100"' in content)
        self.assertTrue(' height="200"' in content)

    def test_extensions(self):
        extension_list = [
            'gif', 'jpg', 'jpeg', 'bmp', 'png',
            'css', 'js',
            'swf',
        ]
        tag = '{% embed src width=100 height=200 %}'
        for ext in extension_list:
            content = self.render_tag(tag, {'src': "file.%s" % ext})
            self.assertTrue(('file.%s' % ext) in content)

    def test_default_attribute(self):
        content = self.render_tag('{% embed "flash.swf" %}')
        self.assertTrue('<param name="wmode" value="opaque" />' in content)

        content = self.render_tag('{% embed "flash.swf" wmode="transparent" %}')
        self.assertTrue('<param name="wmode" value="transparent" />' in content)

class EmbedResizeTest(BaseEmbedTest):

    def setUp(self):
        self.path = os.path.join(settings.MEDIA_ROOT, 'test_images')
        os.makedirs(self.path)
        img = Image.new('RGB', (100,100))
        img.save(os.path.join(self.path, 'imagetest.jpg'))

    def tearDown(self):
        # Safety check
        assert self.path.replace(settings.MEDIA_ROOT, '') != ''
        assert self.path.replace(settings.MEDIA_ROOT, '') != '/'
        assert self.path.replace(settings.MEDIA_ROOT, '') != './'
        shutil.rmtree(self.path)
        
    def test_image_resize(self):
        content = self.render_tag('{% embed "test_images/imagetest.jpg" width="200" height="200" %}')
        self.assertTrue(os.path.isfile(os.path.join(settings.MEDIA_ROOT,'imagetest_jpg_200x200.jpg')))

