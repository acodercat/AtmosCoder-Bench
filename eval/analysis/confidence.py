"""Shared statistics for the analysis tools."""

import math


def wilson_interval(passed: int, total: int, z_score: float = 1.96) -> tuple[float, float]:
    """Wilson score confidence interval (default 95%) for a pass rate, as
    fractions in [0, 1]. More reliable than the normal approximation near 0/1
    and for small samples. Callers multiply by 100 to display percentages."""
    if total == 0:
        return (0.0, 0.0)
    proportion = passed / total
    denominator = 1 + z_score ** 2 / total
    center = proportion + z_score ** 2 / (2 * total)
    margin = z_score * math.sqrt(proportion * (1 - proportion) / total
                                 + z_score ** 2 / (4 * total ** 2))
    return ((center - margin) / denominator, (center + margin) / denominator)
