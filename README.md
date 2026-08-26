URL Shortener API

A REST API that shortens long URLs, redirects short codes to their original destination, and tracks click counts — with a custom base62 encoder and a sliding-window rate limiter.

Stack

Python + Flask

SQLite (via Python's built-in sqlite3)

No external frameworks for the core logic — base62 encoding and rate limiting are both implemented from scratch
