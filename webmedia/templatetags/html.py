# -*- coding: utf-8 -*-

import os
import re
import time

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe, SafeUnicode

from ot.template import quick_tag

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

@register.tag
@quick_tag
def embed(context, src, **kwargs):
    # Falha silenciosamente se não houver um caminho
    if not src:
        return ''

    # Quebra o caminho e a extensão
    src_no_ext, ext = os.path.splitext(src)
    
    # Contexto para o objeto a ser renderizado
    object_context = kwargs.copy()
    object_context.update({
        'src': src,
        'ext': ext,
        # Acrescenta o caminho sem extensão
        # para o script de ativação de activex para o IE
        'src_no_ext': src_no_ext,
        'get': get,
    })
    
    # Argumentos adicionais serão convertidos em atributos HTML
    attrs = kwargs
    
    # Get a custom function by extension
    custom = custom_html_media.get(ext)
    if custom:
        try:
            # Executa a função específica e permite que altere os atributos
            attrs = custom(object_context, src, **kwargs) or {}
        except:
            pass
        
    str_attrs = ''
    if attrs.has_key('attrs'):
        str_attrs = attrs['attrs']
        del attrs['attrs']
    
    str_attrs += ' ' + ' '.join(['%s="%s"' % i for i in attrs.items()])
    
    object_context['attrs'] = mark_safe(str_attrs)
    
    return template.loader.render_to_string('utils/html/%s.html' % ext.lower(), object_context)

