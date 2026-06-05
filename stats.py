import numpy as np
from scipy import stats as scipy_Stats
from dataclasses import dataclass

@dataclass
class TestResult:
    test_name: str
    statistic:float
    p_value:float
    significant:bool
    confidence_level:float

    def __str__(self):
        verdict="Significant" if self.significant else "not Significant"
        return(
            f"[{self.test_name}]\n"
            f"statistic:{self.statistic:.4f}\n"
            f"p-value: {self.p_value:.4f}\n"
            f" result: {verdict} (alpha={1-self.confidence_level:.2f})"

        )
    
def z_test(conv_a:int,n_a:int,conv_b:int,n_b:int,alpha:float=0.05)->TestResult:
    p_a = conv_a / n_a
    p_b = conv_b / n_b
    p_pool = (conv_a + conv_b) / (n_a + n_b)

    se = np.sqrt(p_pool * (1 - p_pool) * (1/n_a + 1/n_b))
    z_stat = (p_b - p_a) / se
    p_value = 2 * (1 - scipy_Stats.norm.cdf(abs(z_stat)))  

    return TestResult("Z-test", z_stat, p_value, p_value < alpha, 1 - alpha)

def t_test(group_a: list, group_b: list, alpha: float = 0.05) -> TestResult:
   
    t_stat, p_value = scipy_Stats.ttest_ind(group_a, group_b, equal_var=False)
    return TestResult("T-test", t_stat, p_value, p_value < alpha, 1 - alpha)


def chi_square_test(
    success_a: int, fail_a: int,
    success_b: int, fail_b: int,
    alpha: float = 0.05
) -> TestResult:
   
    table = np.array([[success_a, fail_a], [success_b, fail_b]])
    chi2, p_value, _, _ = scipy_Stats.chi2_contingency(table)
    return TestResult("Chi-square", chi2, p_value, p_value < alpha, 1 - alpha)

