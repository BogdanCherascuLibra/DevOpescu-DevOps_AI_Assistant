"""
Utility functions used across the application.

This module currently provides token counting
for estimating prompt size and API usage.
"""

import tiktoken


_ENCODING_NAME = "cl100k_base"


def count_tokens(text: str) -> int:
    """Return the estimated number of tokens in the provided text."""
    if not text:
        return 0

    encoding = tiktoken.get_encoding(_ENCODING_NAME)
    return len(encoding.encode(text))
