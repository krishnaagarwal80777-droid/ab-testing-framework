
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from stats import z_test, t_test, chi_square_test, TestResult
from power import compute_sample_size, PowerResult


@dataclass
class VariantData:
    name: str
    users: int = 0
    conversions: int = 0
    values: list = field(default_factory=list)   

    @property
    def conversion_rate(self) -> float:
        return self.conversions / self.users if self.users > 0 else 0.0


@dataclass
class ExperimentResult:
    experiment_name: str
    control: VariantData
    treatment: VariantData
    test_result: TestResult
    power_check: PowerResult
    underpowered: bool
    timestamp: str

    def __str__(self):
        lines = [
            f"\n{'='*50}",
            f"Experiment : {self.experiment_name}",
            f"Ran at     : {self.timestamp}",
            f"{'='*50}",
            f"Control   ({self.control.name}): "
            f"{self.control.conversions}/{self.control.users} "
            f"= {self.control.conversion_rate:.2%}",
            f"Treatment ({self.treatment.name}): "
            f"{self.treatment.conversions}/{self.treatment.users} "
            f"= {self.treatment.conversion_rate:.2%}",
            f"Lift       : {(self.treatment.conversion_rate - self.control.conversion_rate):.2%}",
            "",
            str(self.test_result),
            "",
        ]
        if self.underpowered:
            lines.append(
                f" Underpowered: needed "
                f"{self.power_check.required_sample_per_group:,} users/group, "
                f"got {min(self.control.users, self.treatment.users):,}"
            )
        else:
            lines.append(" Adequately powered experiment")
        lines.append('='*50)
        return "\n".join(lines)


class Experiment:
    def __init__(
        self,
        name: str,
        baseline_rate: float,
        min_detectable_effect: float,
        metric: str = "conversion",  
        alpha: float = 0.05,
        power: float = 0.80,
    ):
        self.name = name
        self.baseline_rate = baseline_rate
        self.min_detectable_effect = min_detectable_effect
        self.metric = metric
        self.alpha = alpha
        self.power = power
        self.control = VariantData(name="control")
        self.treatment = VariantData(name="treatment")
        self._history: list[ExperimentResult] = []

    def log_result(
        self,
        variant: str,                      
        users: int,
        conversions: Optional[int] = None, # for conversion metric
        values: Optional[list] = None,     # for continuous metric
    ):
        target = self.control if variant == "control" else self.treatment
        target.users = users
        if conversions is not None:
            target.conversions = conversions
        if values is not None:
            target.values = values
            target.conversions = sum(1 for v in values if v > 0)

    def analyze(self) -> ExperimentResult:
        # choose the right test
        if self.metric == "continuous":
            test_result = t_test(
                self.control.values, self.treatment.values, self.alpha
            )
        else:
            test_result = z_test(
                self.control.conversions, self.control.users,
                self.treatment.conversions, self.treatment.users,
                self.alpha
            )

        # power check
        power_check = compute_sample_size(
            self.baseline_rate, self.min_detectable_effect,
            self.alpha, self.power
        )
        n_min = min(self.control.users, self.treatment.users)
        underpowered = n_min < power_check.required_sample_per_group

        result = ExperimentResult(
            experiment_name=self.name,
            control=self.control,
            treatment=self.treatment,
            test_result=test_result,
            power_check=power_check,
            underpowered=underpowered,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self._history.append(result)
        return result

    def save(self, filepath: str):
        """Save experiment results to JSON for logging."""
        data = [
            {
                "experiment": r.experiment_name,
                "timestamp": r.timestamp,
                "control_rate": r.control.conversion_rate,
                "treatment_rate": r.treatment.conversion_rate,
                "p_value": float(r.test_result.p_value),
                "significant": bool(r.test_result.significant),
                "underpowered": bool(r.underpowered),
            }
            for r in self._history
        ]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {len(data)} result(s) to {filepath}")