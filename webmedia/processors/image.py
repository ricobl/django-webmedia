#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageFile
from django.conf import settings
from webmedia import app_settings
import os

CROP = 'crop'
FIT = 'fit'

class Thumbnail(object):

    def __init__(self, src, **attrs):

        self.src = src

        self.method = attrs.pop('method', app_settings.IMAGE_RESIZE_METHOD)
        self.quality = attrs.pop('quality', app_settings.IMAGE_QUALITY)
        self.format = self.fix_format(attrs.pop('format', None))

        self.attrs = attrs

    def fix_format(self, format):
        """
        Fix thumbnail format to match PIL's specs and to convert
        BMPs to another formats.
        """
        if not format:
            format = os.path.splitext(self.src)[1][1:]
        format = format.upper()
        if format == 'JPEG':
            format = 'JPG'
        elif format == 'BMP' and app_settings.AUTO_CONVERT_BMPS:
            format = app_settings.AUTO_CONVERT_BMPS.upper()
        return format

    def get_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.src)

    def get_thumb_path(self):
        return os.path.join(app_settings.THUMBNAIL_ROOT, self.get_thumb_src())

    def get_thumb_src(self):
        # Get path, filename and extension
        path, filename = os.path.split(self.src)
        base, ext = os.path.splitext(filename)
        ext = ext[1:]

        flat_attrs = ''
        if self.attrs:
            filename = filename.replace('.', '_')
            # Flatten attributes to use in the filename
            flat_attrs = '_'
            # Flatten dimensions
            for att in ['width', 'height']:
                if self.attrs.get(att, False):
                    flat_attrs += '_%s%s' % (att[0], self.attrs[att])
            # Flatten resize method
            flat_attrs += '_%s%s' % ('m', self.method[0])

        if path:
            path += '/'

        return '%(path)s%(base)s_%(ext)s%(flat_attrs)s.%(ext)s' % {
            'path': path,
            'base': base,
            'flat_attrs': flat_attrs,
            'ext': self.format.lower(),
        }

    def _get_image(self):
        if not hasattr(self, '_image'):
            self._image = Image.open(self.get_path())
        return self._image

    def _set_image(self, obj):
        self._image = obj

    image = property(_get_image, _set_image)

    def generate(self):

        thumb_path = self.get_thumb_path()

        # Make sure directories exist
        path = os.path.dirname(thumb_path)
        if not os.path.isdir(path):
            os.makedirs(path)

        # Resize image
        if self.method == FIT:
            self.fit()
        elif self.method == CROP:
            self.crop()

        # Save thumbnail
        self.image.save(self.get_thumb_path(), quality=self.quality, optimize=(self.format != 'GIF'))

    def fit(self):
        img = self.image
        w, h = map(float, img.size)
        max_w, max_h = map(float, (self.attrs['width'] or w,
                                   self.attrs['height'] or h))
        self.image.thumbnail(map(int, (max_w, max_h)), Image.ANTIALIAS)

    def crop(self):

        img = self.image

        # Get dimensions
        w, h = map(float, img.size)
        max_w, max_h = map(float, (self.attrs['width'] or w,
                                   self.attrs['height'] or h))

        # Find the closest bigger proportion to the maximum size
        scale = max(max_w / w, max_h / h)

        # Image bigger than maximum size?
        if scale < 1:
            # Calculate proportions and resize
            img.thumbnail(map(int, (w * scale, h * scale)), Image.ANTIALIAS)
            # Update resized dimensions
            w, h = img.size
            
        # Avoid enlarging the image
        max_w = min(max_w, w)
        max_h = min(max_h, h)

        # Define the cropping box
        left = (w - max_w) / 2
        top = (h - max_h) / 2
        right = left + max_w
        bottom = top + max_h
        
        # Crop to fit the desired size
        self.image = img.crop(map(int, (left, top, right, bottom)))


def thumbnail(src, attrs):
    thumb = Thumbnail(src, **attrs)
    thumb.generate()
    return thumb.get_thumb_src(), thumb.attrs


