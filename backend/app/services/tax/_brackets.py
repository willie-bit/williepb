"""Shared progressive-bracket evaluator.

Each bracket table is list[(upper_bound_exclusive_or_None, marginal_rate)].
`None` upper bound means "and above".
"""

from __future__ import annotations

from decimal import Decimal


def apply_brackets(base: Decimal, brackets: list[tuple[Decimal | None, Decimal]]) -> Decimal:
    if base <= 0:
        return Decimal("0")
    total = Decimal("0")
    prev: Decimal = Decimal("0")
    remaining = base
    for upper, rate in brackets:
        span: Decimal
        if upper is None:
            span = remaining
        else:
            span = min(remaining, upper - prev)
            if span < 0:
                span = Decimal("0")
        total += span * rate
        remaining -= span
        prev = upper if upper is not None else prev
        if remaining <= 0:
            break
    return total
