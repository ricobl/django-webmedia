#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
from django import template
from django.conf import settings
from django.test import TestCase
from webmedia import app_settings
from webmedia.processors.image import Thumbnail
import os
import shutil

def create_image(path, width=100, height=100):
    img = Image.new('RGB', (width, height))
    img.save(path)
    return img

class BaseEmbedTest(TestCase):

    def render_tag(self, tag, context={}):
        t = template.Template('{% load webmedia_tags %}' + tag)
        content = t.render(template.Context(context))
        return content

class EmbedTagTest(BaseEmbedTest):

    def setUp(self):
        self.settings_bkp = app_settings.PROCESSORS
        app_settings.PROCESSORS = {}

    def tearDown(self):
        app_settings.PROCESSORS = self.settings_bkp

    def test_simple_image(self):
        content = self.render_tag('{% embed "/media/logo.gif" %}')
        self.assertTrue('<img src="/media/logo.gif" ' in content)

    def test_relative_url(self):
        content = self.render_tag('{% embed "logo.gif" %}')
        self.assertTrue('<img src="/media/logo.gif" ' in content)

    def test_attributes(self):
        content = self.render_tag('{% embed "/media/logo.gif" width=100 height=200 %}')
        self.assertTrue(' src="/media/logo.gif"' in content, content)
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
            self.assertTrue(('file.%s' % ext) in content, content)

    def test_default_attribute(self):
        content = self.render_tag('{% embed "flash.swf" %}')
        self.assertTrue('<param name="wmode" value="opaque" />' in content)

        content = self.render_tag('{% embed "flash.swf" wmode="transparent" %}')
        self.assertTrue('<param name="wmode" value="transparent" />' in content)

class ProcessorTest(TestCase):

    def test_import(self):
        from webmedia.processors import get_filetype_processors
        from webmedia.processors.image import thumbnail
        image_processors = get_filetype_processors('image')
        self.assertEqual(image_processors, [thumbnail])


class ThumbnailTest(TestCase):

    def setUp(self):
        self.image_filename = 'imagetest.jpg'
        self.image_path = os.path.join(settings.MEDIA_ROOT, self.image_filename)
        create_image(self.image_path, width=100, height=100)

    def tearDown(self):
        os.remove(self.image_path)

    def test_relative_root(self):
        thumb = Thumbnail(self.image_filename)
        self.assertEquals(thumb.path, os.path.join(app_settings.THUMBNAIL_ROOT, 'imagetest_jpg.jpg'))
        self.assertEquals(thumb.url, app_settings.THUMBNAIL_URL + 'imagetest_jpg.jpg')

    def test_regeneration(self):

        def make_thumb():
            thumb = Thumbnail(self.image_filename, width=50, height=50, method=Thumbnail.CROP)
            thumb.generate()
            return thumb

        # Create first thumbnail
        thumb = make_thumb()
        # Go back in time and change file modification times
        # to allow comparison with new thumbnails
        mtime = os.path.getmtime(thumb.path) - 5
        os.utime(self.image_path, (mtime, mtime))
        os.utime(thumb.path, (mtime, mtime))

        # Create another, shouldn't generate a new thumb
        thumb = make_thumb()
        self.assertEquals(os.path.getmtime(thumb.path), mtime)

        # Recreate the source and regenerate the thumb, should create a new thumb
        create_image(self.image_path, width=100, height=100)
        thumb = make_thumb()
        self.assertNotEqual(os.path.getmtime(thumb.path), mtime)

    def test_original_fits(self):
        thumb = Thumbnail(self.image_filename)
        self.assertFalse(thumb.needs_resize())
        self.assertFalse(thumb.needs_generate())
        thumb.generate()
        self.assertFalse(os.path.isfile(thumb.path))

    def test_fit(self):
        thumb = Thumbnail(self.image_filename, width=50, height=40, method=Thumbnail.FIT)
        thumb.generate()
        thumb_path = os.path.join(app_settings.THUMBNAIL_ROOT, 'imagetest_jpg__w50_h40_mf.jpg')
        # Check if file exists
        self.assertTrue(os.path.isfile(thumb_path))
        # Check dimensions
        img = Image.open(thumb_path)
        self.assertEquals(img.size, (40, 40))

    def test_crop(self):
        thumb = Thumbnail(self.image_filename, width=50, height=40, method=Thumbnail.CROP)
        thumb.generate()
        thumb_path = os.path.join(app_settings.THUMBNAIL_ROOT, 'imagetest_jpg__w50_h40_mc.jpg')
        # Check if file exists
        self.assertTrue(os.path.isfile(thumb_path))
        # Check dimensions
        img = Image.open(thumb_path)
        self.assertEquals(img.size, (50, 40))


class EmbedResizeTest(BaseEmbedTest):

    def setUp(self):
        # Setup test dirs
        self.path = os.path.join(settings.MEDIA_ROOT, 'test_images')
        self.thumb_path = os.path.join(app_settings.THUMBNAIL_ROOT, 'test_images')
        for path in [self.path, self.thumb_path]:
            if not os.path.isdir(path):
                os.makedirs(path)
        # Create test image
        create_image(os.path.join(self.path, 'imagetest.jpg'))

    def tearDown(self):
        # Check and cleanup dirs
        for path in [self.path, self.thumb_path]:
            assert path
            shutil.rmtree(os.path.abspath(path))
        
    def test_thumbnail_crop(self):
        # Set paths
        orig = 'test_images/imagetest.jpg'
        thumb = 'test_images/imagetest_jpg__w50_h40_mc.jpg'
        thumb_path = os.path.join(app_settings.THUMBNAIL_ROOT, thumb)

        # Test crop
        content = self.render_tag('{% embed url width="50" height="40" method="crop" %}', {'url': orig})
        self.assertTrue(thumb in content, content)
        self.assertTrue(os.path.isfile(os.path.join(thumb_path)))
        self.assertTrue('method=' not in content)

    def test_thumbnail_fit(self):
        # Set paths
        orig = 'test_images/imagetest.jpg'
        thumb = 'test_images/imagetest_jpg__w50_h40_mf.jpg'
        thumb_path = os.path.join(app_settings.THUMBNAIL_ROOT, thumb)

        # Test fit
        content = self.render_tag('{% embed url width="50" height="40" method="fit" %}', {'url': orig})
        self.assertTrue(thumb in content)
        self.assertTrue(os.path.isfile(os.path.join(thumb_path)))
        self.assertTrue('method=' not in content)

