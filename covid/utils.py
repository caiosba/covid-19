import re
from functools import lru_cache, wraps

import numpy as np

N_RE = re.compile(r"(-?)(\d+)(\.\d{,2})?\d*")


def fmt(n):
    """
    Heuristically choose best format option for number.
    """

    try:
        return ", ".join(map(fmt, n))
    except TypeError:
        pass

    m = abs(n)
    if m == 0.0:
        return '0'
    if m < 0.001:
        return "%.2e" % n
    elif 0.001 <= m < 1000:
        if isinstance(n, int):
            return str(n)
        return f"{float(n):.2f}"
    elif 1000 <= m < 100_000:
        return _fmt_aux(n)
    elif 100_000 <= m < 1_000_000_000:
        return _fmt_aux(n / 1e6, "mi")
    elif 1_000_000_000 <= m < 1_000_000_000_000:
        return _fmt_aux(n / 1e9, "bi")
    else:
        return "%e" % n


def _fmt_aux(n, suffix=""):
    m = N_RE.match(str(n))
    sign, number, decimal = m.groups()
    return sign + _fix_int(number, 3) + (decimal or "") + suffix


def _fix_int(s, n):
    return ",".join(map("".join, rpartition(s, n)))


def rpartition(seq, n):
    """
    Partition sequence in groups of n starting from the end of sequence.
    """
    seq = list(seq)
    out = []
    while seq:
        new = []
        for _ in range(n):
            if not seq:
                break
            new.append(seq.pop())
        out.append(new[::-1])
    return out[::-1]


def pc(n):
    """
    Write number as percentages.
    """
    if n == 0:
        return '0.0%'
    return fmt(100 * n) + "%"


def pm(n):
    """
    Write number as parts per thousand.
    """
    if n == 0:
        return '0.0‰'
    return fmt(1000 * n) + "‰"


def p10k(n):
    """
    Write number as parts per ten thousand.
    """
    if n == 0:
        return '0.0‱'
    return fmt(10000 * n) + "‱"


def interpolant(x, y):
    """
    Creates a linear interpolant for the given function passed as sequences of
    x, y points.
    """
    x = np.array(x)
    y = np.array(y)

    @lru_cache
    def fn(t):
        return np.interp(t, x, y)

    return fn


def lru_safe_cache(size):
    """
    A safe LRU cache that returns a copy of the cached element to prevent
    mutations from cached values.
    """

    def decorator(func):
        cached = lru_cache(size)(func)

        @wraps(func)
        def fn(*args, **kwargs):
            return cached(*args, **kwargs).copy()

        fn.unsafe = cached
        return fn

    return decorator


def indent(st, indent=4):
    """
    Indent string.
    """
    if isinstance(indent, int):
        indent = ' ' * indent
    return ''.join(indent + ln for ln in st.splitlines(keepends=True))