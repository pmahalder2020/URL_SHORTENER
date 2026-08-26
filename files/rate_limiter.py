"""
Sliding-window rate limiter.

How it works:
- For each client IP, we keep a list of timestamps of their recent requests.
- On every new request, we drop any timestamps older than the window
  (e.g. older than 60 seconds), then check how many are left.
- If they're at or over the limit, we reject the request with HTTP 429.

This is an in-memory implementation (a Python dict), which is fine for a
portfolio project / single-process app. In a real production system with
multiple servers, you'd back this with Redis so all instances share state.
"""

import time
from collections import defaultdict

# Maps IP address -> list of request timestamps (seconds since epoch)
request_log = defaultdict(list)


def is_allowed(ip: str, max_requests: int = 5, window_seconds: int = 60) -> bool:
    now = time.time()
    window_start = now - window_seconds

    # Keep only timestamps within the current window
    request_log[ip] = [t for t in request_log[ip] if t > window_start]

    if len(request_log[ip]) >= max_requests:
        return False

    request_log[ip].append(now)
    return True
