#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageFile
from django.conf import settings
from webmedia import app_settings
import os

class Thumbnail(object):

    CROP = 'crop'
    FIT = 'fit'

    def __init__(self, original_src, **attrs):

        # Make absolute paths relative
        if original_src.startswith(settings.MEDIA_ROOT):
            original_src = original_src[len(settings.MEDIA_ROOT):]

        self.original_src = original_src

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
            format = os.path.splitext(self.original_src)[1][1:]
        format = format.upper()
        if format == 'JPEG':
            format = 'JPG'
        elif format == 'BMP' and app_settings.AUTO_CONVERT_BMPS:
            format = app_settings.AUTO_CONVERT_BMPS.upper()
        return format

    @property
    def src(self):
        # Get path, filename and extension
        path, filename = os.path.split(self.original_src)
        base, ext = os.path.splitext(filename)
        ext = ext[1:]

        # Fix paths to end with '/'
        if path:
            path += '/'

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

        return '%(path)s%(base)s_%(ext)s%(flat_attrs)s.%(ext)s' % {
            'path': path,
            'base': base,
            'flat_attrs': flat_attrs,
            'ext': self.format.lower(),
        }

    @property
    def path(self):
        return os.path.join(app_settings.THUMBNAIL_ROOT, self.src)

    @property
    def url(self):
        return app_settings.THUMBNAIL_URL + self.src

    @property
    def original_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.original_src)

    def _get_image(self):
        if not hasattr(self, '_image'):
            self._image = Image.open(self.original_path)
        return self._image

    def _set_image(self, obj):
        self._image = obj

    image = property(_get_image, _set_image)

    def original_changed(self):
        if not os.path.isfile(self.path):
            return True
        return os.path.getmtime(self.original_path) > os.path.getmtime(self.path)

    def needs_resize(self):
        return 'width' in self.attrs or 'height' in self.attrs

    def needs_generate(self):
        """
        Checks if the thumbnail needs to be generated/resized and if
        the original file has changed.
        """
        return self.needs_resize() and self.original_changed()

    def generate(self):

        # Check if the thumbnail must be generated
        if not self.needs_generate():
            return

        # Make sure directories exist
        dirname = os.path.dirname(self.path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        # Resize image
        if self.method == Thumbnail.FIT:
            self.fit()
        elif self.method == Thumbnail.CROP:
            self.crop()

        # Save thumbnail
        self.image.save(self.path, quality=self.quality, optimize=(self.format != 'GIF'))

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
    # Skip external URLs
    if src.startswith('http://'):
        return src, attrs

    # Skip absolute files outside the MEDIA_URL
    if not src.startswith(settings.MEDIA_URL):
        return src, attrs

    # Create thumbnail instance
    path = src.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
    thumb = Thumbnail(path, **attrs)

    # Return original if doesn't need a thumbnail
    if not thumb.needs_resize():
        return src, thumb.attrs

    # Generate thumb and return URL + attrs
    thumb.generate()
    return thumb.url, thumb.attrs

