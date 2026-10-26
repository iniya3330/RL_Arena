"""Template tags for the interface languages.

    {% load i18n_extras %}
    {% tr "login_eyebrow" %}
    {% tr "xp_to_next" xp=5 needed=50 next=3 %}
    {% current_lang as lang %}
    {% lang_options as options %}
"""
from django import template
from django.utils.safestring import mark_safe

from core.i18n import LANGUAGES, get_language, text

register = template.Library()


@register.simple_tag(takes_context=True)
def tr(context, key, **values):
    return mark_safe(text(key, get_language(context.get("request")), **values))


@register.simple_tag(takes_context=True)
def current_lang(context):
    return get_language(context.get("request"))


@register.simple_tag(takes_context=True)
def lang_options(context):
    current = get_language(context.get("request"))
    return [{"code": code, "name": name, "active": code == current} for code, name in LANGUAGES.items()]
