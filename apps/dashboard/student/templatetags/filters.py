from django import template
import re


register = template.Library()


@register.filter
def dict_get(d, key):
    return d.get(key, [])



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def video_embed(url):
    regex = r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)'
    match = re.search(regex, url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    return ''


@register.filter
def format_seconds(value):
    try:
        value = int(value)
        minutes = value // 60
        seconds = value % 60
        if minutes > 0:
            return f"{minutes} мин {seconds} сек"
        else:
            return f"{seconds} сек"
    except:
        return ''


@register.filter
def times10(value):
    try:
        return round(float(value) * 10)
    except (TypeError, ValueError):
        return 0