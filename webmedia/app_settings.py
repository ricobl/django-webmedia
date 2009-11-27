# -*- coding: utf-8 -*-

from django.conf import settings

FILETYPES = getattr(settings, 'WEBMEDIA_FILETYPES', {
    'image': ('gif', 'jpg', 'jpeg', 'bmp', 'png'),
    'stylesheet': ('css',), 
    'javascript':('js',),
    'flash': ('swf',),
})

FILETYPES_ATTRIBUTES = getattr(settings, 'WEBMEDIA_FILETYPES_ATTRIBUTES', {
    'flash': {'wmode': 'opaque'},
})

