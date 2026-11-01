import os
import re

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def highlight(text, terms):
    """Wrap every searched word found in text with <mark>. Text is HTML-escaped first."""
    safe = escape(text)
    if not terms:
        return safe
    words = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
    pattern = re.compile(r"\b(" + words + r")\b", re.IGNORECASE)
    # Skip HTML entities such as &amp; so they are never broken.
    parts = re.split(r"(&[#a-zA-Z0-9]+;)", safe)
    marked = [p if p.startswith("&") else pattern.sub(r"<mark>\1</mark>", p) for p in parts]
    return mark_safe("".join(marked))


@register.simple_tag
def static_v(path):
    """Static file URL with the file's change time, so browsers never show an old copy."""
    found = finders.find(path)
    version = int(os.path.getmtime(found)) if found else 0
    return static(path) + "?v=" + str(version)
