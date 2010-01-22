#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from webmedia import app_settings

def player(src, attrs):
    attrs['FlashVars'] = 'soundFile=%s&titles=%s' % (src, attrs.pop('title', ''))
    attrs['width'] = '240'
    attrs['height'] = '30'
    return app_settings.SOUND_PLAYER_URL, attrs

