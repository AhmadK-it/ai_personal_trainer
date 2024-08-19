from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied



class BlockUserAgentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_user_agents = [
            'dev-test', 
            'android-app', 
            # Add more allowed user agents here
        ]
        # List of common browser user agents to allow
        self.allowed_browsers = [
            'Mozilla',      # Common prefix for Firefox, Chrome, Safari, Edge, etc.
            'AppleWebKit',  # WebKit-based browsers like Safari
            'Chrome',       # Google Chrome
            'Safari',       # Safari browser
            'Firefox',      # Mozilla Firefox
            'MSIE',         # Internet Explorer
            'Trident',      # Internet Explorer 11+
            'Edge',         # Microsoft Edge
            'Opera',        # Opera browser
            # Add more if needed
        ]

    def __call__(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Allow request if user agent is in the specific allowed list
        if user_agent in self.allowed_user_agents:
            return self.get_response(request)

        # Allow request if user agent matches any common browser patterns
        if any(browser in user_agent for browser in self.allowed_browsers):
            return self.get_response(request)

        # Block all other user agents
        return HttpResponseForbidden("Access denied")
    
class BlockIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        if ip.startswith('149.154.161.'):
            raise PermissionDenied("Access denied")
        return self.get_response(request)