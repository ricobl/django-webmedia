# -*- coding: utf-8 -*-

from django.conf import settings
import os

FILETYPES = getattr(settings, 'WEBMEDIA_FILETYPES', {
    'image': ('gif', 'jpg', 'jpeg', 'bmp', 'png'),
    'stylesheet': ('css',), 
    'javascript':('js',),
    'flash': ('swf',),
    'sound': ('mp3',),
})

FILETYPES_ATTRIBUTES = getattr(settings, 'WEBMEDIA_FILETYPES_ATTRIBUTES', {
    'flash': {'wmode': 'opaque'},
})

THUMBNAIL_ROOT = getattr(settings, 'WEBMEDIA_THUMBNAIL_ROOT', os.path.join(settings.MEDIA_ROOT, 'thumbs'))
THUMBNAIL_URL = getattr(settings, 'WEBMEDIA_THUMBNAIL_URL', settings.MEDIA_URL + 'thumbs/')

PROCESSORS = getattr(settings, 'WEBMEDIA_PROCESSORS', {
    'image': ('webmedia.processors.image.thumbnail',),
})

IMAGE_RESIZE_METHOD = getattr(settings, 'WEBMEDIA_IMAGE_RESIZE_METHOD', 'crop')
IMAGE_QUALITY = getattr(settings, 'WEBMEDIA_IMAGE_QUALITY', 80)
AUTO_CONVERT_BMPS = getattr(settings, 'WEBMEDIA_AUTO_CONVERT_BMPS', 'GIF')
