from __future__ import annotations

import re
from typing import Tuple


SAFE_REPLACEMENTS = {
    r"(刀|剪|火|药|电)": "安全工具",
    r"(打|揍|骂)": "不友善的行为",
}


def inspect_and_rewrite(text: str) -> Tuple[bool, str]:
    """Return (rewritten, output). rewritten=True if content was changed."""
    out = text
    changed = False
    for pat, rep in SAFE_REPLACEMENTS.items():
        if re.search(pat, out):
            out = re.sub(pat, rep, out)
            changed = True
    return changed, out

