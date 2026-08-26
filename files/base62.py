"""
Custom base62 encoder for generating short codes.

Why base62 instead of base10/base16?
- It uses 62 characters (0-9, a-z, A-Z) instead of just 10 or 16,
  so the same number produces a much SHORTER string.
- Example: the number 1,000,000 is "1000000" in base10 (7 chars)
  but just "4c92" in base62 (4 chars) — exactly what a URL shortener needs.

We store each shortened URL as an auto-incrementing row ID in the database,
then convert that ID into a base62 string to use as the short code.
"""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)  # 62


def encode(num: int) -> str:
    """Convert a non-negative integer into a base62 string."""
    if num == 0:
        return ALPHABET[0]

    digits = []
    while num > 0:
        num, remainder = divmod(num, BASE)
        digits.append(ALPHABET[remainder])

    # We built the digits from least-significant to most-significant,
    # so reverse before joining.
    return "".join(reversed(digits))


def decode(short_code: str) -> int:
    """Convert a base62 string back into its original integer."""
    num = 0
    for char in short_code:
        num = num * BASE + ALPHABET.index(char)
    return num
