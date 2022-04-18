import re
from typing import Sequence, Any

from utils.special_chars import (bracket_start as brkt_s, bracket_end as brkt_e)

def non_null(seq: Sequence[Any]):
    """Returns the first non-None item in the given sequence, or returns None."""
    for o in seq:
        if o is None:
            continue
        return o
    return None

# Match has 2 groups, first is for text within 2 brackets, the second for if the second is missing.
dialog_title_regex = re.compile(f'(?:{brkt_s}(.+){brkt_e})|(?:{brkt_s}(.+))', re.UNICODE)
def dialog_title_text(line: str) -> str:
    """
    Returns the text part of a dialogue title.
    If the line is missing the ending bracket, the text will still be returned.
    """
    return non_null(dialog_title_regex.search(line).groups())
