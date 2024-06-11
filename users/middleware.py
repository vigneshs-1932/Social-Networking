import time
from django.core.cache import cache
from django.http import JsonResponse

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.method == 'POST' and request.path == '/api/users/friend-requests/':
            user = request.user
            key = f'rate-limit-{user.id}'
            count = cache.get(key, 0)
            if count >= 3:
                return JsonResponse({"error": "Too many requests"}, status=429)
            cache.set(key, count + 1, timeout=60)
        return self.get_response(request)
