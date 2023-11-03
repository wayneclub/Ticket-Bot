"""
This module is for validation.
"""

from __future__ import annotations
import logging
import string


def check_roc_id(roc_id: str) -> bool:
    """Check if roc_id is valid"""
    if not roc_id:
        return False
    if len(roc_id) != 10:
        return False
    if not roc_id[0].isalpha() or not roc_id[1:].isdigit():
        return False
    # create alphabet for 1st char of ID
    alphabet = list(string.ascii_uppercase[0:8])
    alphabet.extend(list(string.ascii_uppercase[9:]))
    code = list(range(10, 33))
    # create the location mapping code for char of ID
    location_code = dict(zip(alphabet, code))

    # Convert 1st Alphabet to Numeric code
    encode_id = list(str(location_code[roc_id[0].upper()]))
    encode_id.extend(list(roc_id[1:]))
    # print(encodeID)
    check_sum = int(encode_id[0])

    # Calculate the checksum of ID
    para = 9
    for n in encode_id[1:]:
        if para == 0:
            para = 1
        check_sum += int(n)*para
        para -= 1

    # Check the checksum
    if check_sum % 10 == 0:
        return True
    return False


def check_tax_id(tax_id: str) -> bool:
    """Check if tax_id is valid"""
    if len(tax_id) != 10 or not tax_id.isdigit():
        return False
    return True


if __name__:
    logger = logging.getLogger(__name__)
