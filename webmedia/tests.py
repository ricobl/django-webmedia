#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django import template
from django.template import mark_safe

class EmbedTagTest(TestCase):

    def render_tag(self, tag, context={}):
        t = template.Template('{% load webmedia_tags %}' + tag)
        content = t.render(template.Context(context))
        return content

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

