from rest_framework.throttling import SimpleRateThrottle
from django.conf import settings
import time


class CustomRateThrottle(SimpleRateThrottle):
    """
    Custom rate throttle that applies different rate limits based on the view's throttle scope.
    """
    throttle_config = getattr(settings, 'THROTTLE_CONFIG', {})

    def get_rate(self):
        """
        Retrieve the rate limit for the current view based on its throttle scope.
        Returns:
            str: The rate string (e.g., '5/m').
        """
        throttle_key = self.scope
        rate_config = self.throttle_config.get(throttle_key, self.throttle_config.get('default'))
        return rate_config.get('rate', '5/m')

    def allow_request(self, request, view):
        """
        Determine whether the request should be allowed based on the rate limit and time window.
        Parameters:
            request: The HTTP request object.
            view: The view instance handling the request.
        Returns:
            bool: True if the request is allowed, False otherwise.
        """
        rate = self.get_rate()
        max_requests, window = self.parse_rate(rate)

        key = self.get_cache_key(request, view)
        if key is None:
            return True

        self.history = self.cache.get(key, [])
        now = time.time()

        self.history = [timestamp for timestamp in self.history if now - timestamp < window]
        self.cache.set(key, self.history, timeout=window)

        if len(self.history) < max_requests:
            self.history.append(now)
            self.cache.set(key, self.history, timeout=window)
            return True
        return False

    def parse_rate(self, rate):
        """
        Parse the rate string to extract the maximum number of requests and the window size in seconds.
        Parameters:
            rate: A string representing the rate limit (e.g., '5/m').
        Returns:
            tuple: A tuple containing the maximum number of requests and the window size in seconds.
        """
        if not rate:
            return (5, 60)  # Default to 5 requests per minute if rate is None

        try:
            requests, period = rate.split('/')
            max_requests = int(requests)

            if period == 's':
                window = 1
            elif period == 'm':
                window = 60
            elif period == 'h':
                window = 3600
            elif period == 'd':
                window = 86400
            else:
                raise ValueError("Unsupported time unit")

            return max_requests, window
        except ValueError as e:
            raise ValueError(f"Invalid rate format '{rate}': {e}")

    def get_cache_key(self, request, view):
        """
        Generate a cache key for storing the request history.
        Parameters:
            request: The HTTP request object.
            view: The view instance handling the request.
        Returns:
            str: The cache key string based on the view and user.
        """
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            user_id = 'anon'
        return f"{view.__class__.__name__}:{user_id}:{request.META.get('REMOTE_ADDR')}"
