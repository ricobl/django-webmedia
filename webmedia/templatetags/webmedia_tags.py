# -*- coding: utf-8 -*-

import os
import re
import time

from django import template
from django.template import loader
from django.conf import settings
from django.utils.safestring import mark_safe, SafeUnicode

from qucktag.template.quicktag import quicktag
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

## TAGS

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

@register.tag
@quicktag
def embed(src, **attrs):
    # Falha silenciosamente se não houver um caminho
    # ou extensão
    src_no_ext, ext = os.path.splitext(src)
    if not src or not ext:
        return ''

    # Remove o "." da extensão e encontra o tipo de arquivo
    ext = ext[1:]
    filetype = get_filetype(ext)

    # Extende os atributos padrão para o tipo de arquivo
    default_attrs = app_settings.FILETYPES_ATTRIBUTES.get(filetype, {})
    attrs = dict(default_attrs, **attrs)

    # Ajusta o src para URL relativa ao MEDIA_URL ou absoluta
    src = get_relative_url(src)

    # Aplica processors configurados para o tipo de arquivo
    # (Ex. redimensionar imagem)
    processors = get_filetype_processors(filetype)
    for proc in processors:
        src, attrs = proc(src, attrs)

    # Expande atributos em chave="valor"
    str_attrs = ' '.join(['%s="%s"' % i for i in attrs.items()])

    # Anexa código da data de modificação para evitar cache
    anti_cache = nocache(src)
    if anti_cache:
        src += '?' + anti_cache

    # Contexto para o objeto a ser renderizado
    context = {'src': src, 'attrs': attrs,
               'flat_attrs': mark_safe(str_attrs)}
    
    return loader.render_to_string('webmedia/embed/%s.html' % filetype, context)

