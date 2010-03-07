#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.utils.importlib import import_module
from webmedia import app_settings

def get_filetype_processors(filetype):
    """
    Get a list of callable processors for a given filetype.
    """
    processors = []
    for path in app_settings.PROCESSORS.get(filetype, []):
        module_path, processor_name = path.rsplit('.', 1)
        module = import_module(module_path)
        processors.append(getattr(module, processor_name))

    return processors
