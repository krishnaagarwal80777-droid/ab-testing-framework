
import numpy as np
from scipy import stats as scipy_stats
from dataclasses import dataclass

@dataclass
class PowerResult:
    baseline_rate: float
    min_detectable_effect: float
    required_sample_per_group: int
    alpha: float
    power: float

    def __str__(self):
        return (
            f"[Power Analysis]\n"
            f"  Baseline rate        : {self.baseline_rate:.1%}\n"
            f"  Min detectable effect: +{self.min_detectable_effect:.1%}\n"
            f"  Required n per group : {self.required_sample_per_group:,}\n"
            f"  Alpha (false +ve)    : {self.alpha}\n"
            f"  Power (sensitivity)  : {self.power:.0%}"
        )


def compute_sample_size(
    baseline_rate: float,
    min_detectable_effect: float,
    alpha: float = 0.05,
    power: float = 0.80
) -> PowerResult:
    """
    How many users do you need per group to detect a real effect?

    baseline_rate        : current conversion rate e.g. 0.05 = 5%
    min_detectable_effect: smallest improvement worth detecting e.g. 0.01 = +1%
    alpha                : false positive tolerance (default 5%)
    power                : probability of catching a real effect (default 80%)
    """
    p1 = baseline_rate
    p2 = baseline_rate + min_detectable_effect

    
    z_alpha = scipy_stats.norm.ppf(1 - alpha / 2)
    z_power = scipy_stats.norm.ppf(power)

    pooled = (p1 + p2) / 2
    n = (
        (z_alpha * np.sqrt(2 * pooled * (1 - pooled)) +
         z_power * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
        / (p2 - p1) ** 2
    )

    return PowerResult(
        baseline_rate=baseline_rate,
        min_detectable_effect=min_detectable_effect,
        required_sample_per_group=int(np.ceil(n)),
        alpha=alpha,
        power=power
    )


def minimum_detectable_effect(
    baseline_rate: float,
    n: int,
    alpha: float = 0.05,
    power: float = 0.80
) -> float:
    """
    Reverse lookup: given a fixed sample size, what's the
    smallest effect you can reliably detect?
    Useful when you already know how many users you'll get.
    """
    z_alpha = scipy_stats.norm.ppf(1 - alpha / 2)
    z_power = scipy_stats.norm.ppf(power)

  
    lo, hi = 0.0001, 1 - baseline_rate
    for _ in range(100):
        mid = (lo + hi) / 2
        result = compute_sample_size(baseline_rate, mid, alpha, power)
        if result.required_sample_per_group > n:
            lo = mid
        else:
            hi = mid

    return round(hi, 6)