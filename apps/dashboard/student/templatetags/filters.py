from django import template
import re


register = template.Library()


@register.filter
def dict_get(d, key):
    return d.get(key, [])


@register.filter
def video_embed(url):
    regex = r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)'
    match = re.search(regex, url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    return ''
