from django import template
from urllib.parse import urlparse, parse_qs

register = template.Library()


@register.filter
def youtube_embed(url):
    try:
        parsed_url = urlparse(url)
        if 'youtube.com' in parsed_url.netloc:
            query = parse_qs(parsed_url.query)
            video_id = query.get('v')
            if video_id:
                return f'https://www.youtube.com/embed/{video_id[0]}'
        elif 'youtu.be' in parsed_url.netloc:
            video_id = parsed_url.path.strip('/')
            return f'https://www.youtube.com/embed/{video_id}'
    except Exception:
        pass
    return url
