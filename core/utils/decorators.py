from django.http import Http404
from functools import wraps


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.user_type in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise Http404("Бет табылмады")
        return _wrapped_view
    return decorator