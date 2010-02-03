# -*- coding: utf-8 -*-

import os
import re
import time

from django import template
from django.template import loader
from django.conf import settings
from django.utils.safestring import mark_safe, SafeUnicode

from ot.template.quicktag import quicktag
from webmedia import app_settings
from webmedia.processors import get_filetype_processors

register = template.Library()

## HELPERS

def url_to_root(path):
    """
    Recebe uma URL local e retorna o caminho no sistema de arquivos.
    """
    # Verifica se foi passado um caminho
    if not path:
        return path

    # Remove a MEDIA_URL do início do caminho
    if path.startswith(settings.MEDIA_URL):
        path = path.replace(settings.MEDIA_URL, '', 1)

    # Prefixa o caminho com o caminho local para os arquivos estáticos
    newpath = os.path.join(settings.MEDIA_ROOT, path)
    return newpath

def nocache(path):
    """
    Recebe o caminho de um arquivo.
    Retorna um string baseado na data de modificação do arquivo.

    Útil para evitar o cache de arquivos estáticos por parte do browser.
    """

    # Verifica se foi passado um caminho
    if not path:
        return ''

    # Converte a URL em caminho para o sistema de arquivos
    full_path = url_to_root(path)

    # Verifica se o arquivo existe
    if os.path.isfile(full_path):
        # Lê a data de modificação do arquivo
        m_time = time.localtime(os.path.getmtime(full_path))
        # Retorna a data no formato "[dia_ano][hora][minuto][segundo]"
        return time.strftime('%j-%H%M%S', m_time)

    return ''


def get_filetype(ext):
    for filetype, types in app_settings.FILETYPES.items():
        if ext in types:
            return filetype
    return None

def apply_processors(src, attrs):
    return src, attrs

def get_relative_url(src):
    """
    Fixes URL source by prepending with MEDIA_URL when appropriate.
    """
    # Normalizes the src by removing MEDIA_URL from the beginning
    if src.startswith(settings.MEDIA_URL):
        src = src[len(settings.MEDIA_URL):]
    # Skip external and absolute URLs
    if not src.startswith('http://') and not src.startswith('/'):
        return settings.MEDIA_URL + src
    return src

def process_file(src, **attrs):
    # Fail silently if there's no path or extension
    src_no_ext, ext = os.path.splitext(src)
    if not src or not ext:
        return None, None, None

    # Removes the "." from the extension and get the filetype
    ext = ext[1:]
    filetype = get_filetype(ext)

    # Extends default attributes for the filetype
    default_attrs = app_settings.FILETYPES_ATTRIBUTES.get(filetype, {})
    attrs = dict(default_attrs, **attrs)

    # Convert the src to a URL relative to the MEDIA_URL or absolute
    src = get_relative_url(src)

    # Apply processors (image resize or others)
    processors = get_filetype_processors(filetype)
    for proc in processors:
        src, attrs = proc(src, attrs)

    # Add anti-cache query string
    anti_cache = nocache(src)
    if anti_cache:
        src += '?' + anti_cache

    # Return the (possibly) modified src and attributes
    return src, filetype, attrs


## FILTERS

@register.filter
def process(src, args):
    """ Apply processors to a file and return the modified source. """
    # Create a dict from "key=value,other_key=other_value" string
    attrs = dict((pair.split('=') for pair in str(args).split(',')))
    new_src, filetype, attrs = process_file(src, **attrs)
    if not new_src:
        return src
    return new_src


## TAGS

@register.tag
@quicktag
def embed(src, **attrs):
    """ Apply processor to a file and return the appropriate HTML tag. """
    src, filetype, attrs = process_file(src, **attrs)
    if not src:
        return ''

    # Flatten attributes
    str_attrs = ' '.join(['%s="%s"' % i for i in attrs.items()])
    # Return the rendered template for the filetype
    context = {'src': src, 'attrs': attrs,
               'flat_attrs': mark_safe(str_attrs)}
    return loader.render_to_string('webmedia/embed/%s.html' % filetype, context)

