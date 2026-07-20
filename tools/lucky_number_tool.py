"""
Lucky Number Tool.

This tool generates a lucky number based on a user's
birth date and the current date.

The implementation is intentionally incomplete and must
be finalized during the laboratory.
"""

from datetime import datetime
from .tool import Tool


def lucky_number(birth_date):
    current_date = datetime.now()
    current_date_str = current_date.strftime("%d%m%Y")
    # Remove any non-digit characters from birth_date to ensure clean input
    birth_date = ''.join(filter(str.isdigit, birth_date))
    all_digits = current_date_str + birth_date
    lucky_number = sum(int(digit) for digit in all_digits)
    return lucky_number
    


