# -*- coding: utf-8 -*-

import os
import re
import time

from django import template
from django.template import loader
from django.conf import settings
from django.utils.safestring import mark_safe, SafeUnicode

from ot.template.quick_tag import quick_tag
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
        # Retorna a data no formato "modified=[dia_ano][hora][minuto][segundo]"
        return time.strftime('modified=%j-%H%M%S', m_time)

    return ''

## TAGS

def get_filetype(ext):
    for filetype, types in app_settings.FILETYPES.items():
        if ext in types:
            return filetype
    return None

@register.tag
@quick_tag
def embed(context, src, **attrs):
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

    # Aplica processors configurados para o tipo de arquivo
    # (Ex. redimensionar imagem)
    processors = get_filetype_processors(filetype)
    for proc in processors:
        src, attrs = proc(src, attrs)

    # Expande atributos em chave="valor"
    str_attrs = ' '.join(['%s="%s"' % i for i in attrs.items()])

    # Contexto para o objeto a ser renderizado
    object_context = {'src': src, 'attrs': attrs,
                      'flat_attrs': mark_safe(str_attrs)}
    
    return loader.render_to_string('webmedia/embed/%s.html' % filetype, object_context)

