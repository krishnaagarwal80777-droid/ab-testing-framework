
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from experiment import ExperimentResult


def plot_conversion_rates(result: ExperimentResult, save_path: str = None):
    """Bar chart comparing control vs treatment conversion rates."""
    names  = [result.control.name, result.treatment.name]
    rates  = [result.control.conversion_rate, result.treatment.conversion_rate]
    colors = ["#5B8DEF", "#F4845F"]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(names, [r * 100 for r in rates], color=colors,
                  width=0.4, edgecolor="white", linewidth=0.8)

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.1,
                f"{rate:.2%}", ha="center", va="bottom", fontsize=11)

    sig_text = (
        f"Significant (p={result.test_result.p_value:.4f})"
        if result.test_result.significant
        else f" Not significant (p={result.test_result.p_value:.4f})"
    )
    ax.set_title(f"{result.experiment_name}\n{sig_text}", fontsize=12, pad=12)
    ax.set_ylabel("Conversion rate (%)")
    ax.set_ylim(0, max(rates) * 100 * 1.3)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved → {save_path}")
    plt.show()


def plot_confidence_interval(result: ExperimentResult, save_path: str = None):
    """
    Visualize the lift with a 95% confidence interval.
    If the interval excludes 0, the result is significant.
    """
    from scipy import stats as scipy_stats

    p_c = result.control.conversion_rate
    p_t = result.treatment.conversion_rate
    n_c = result.control.users
    n_t = result.treatment.users

    lift = p_t - p_c
    se   = np.sqrt(p_c*(1-p_c)/n_c + p_t*(1-p_t)/n_t)
    z    = scipy_stats.norm.ppf(0.975)
    ci_lo, ci_hi = lift - z*se, lift + z*se

    fig, ax = plt.subplots(figsize=(7, 3))
    color = "#2ECC71" if result.test_result.significant else "#E74C3C"

    ax.axvline(0, color="#888", linewidth=1, linestyle="--", label="No effect")
    ax.errorbar(lift, 0.5, xerr=[[lift - ci_lo], [ci_hi - lift]],
                fmt="o", color=color, markersize=8,
                capsize=6, capthick=2, linewidth=2)

    ax.fill_betweenx([0.3, 0.7], ci_lo, ci_hi, alpha=0.15, color=color)
    ax.set_xlabel("Lift in conversion rate")
    ax.set_title(
        f"95% Confidence interval for lift\n"
        f"[{ci_lo:+.2%}  to  {ci_hi:+.2%}]",
        fontsize=11
    )
    ax.set_yticks([])
    ax.spines[["top", "right", "left"]].set_visible(False)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved → {save_path}")
    plt.show()


def plot_experiment_log(log_path: str, save_path: str = None):
    """Bar chart of p-values from results.json, with significance line."""
    with open(log_path) as f:
        data = json.load(f)

    names   = [d["experiment"] for d in data]
    pvalues = [d["p_value"] for d in data]
    colors  = ["#2ECC71" if d["significant"] else "#E74C3C" for d in data]

    fig, ax = plt.subplots(figsize=(max(6, len(names)*2), 4))
    ax.bar(names, pvalues, color=colors, width=0.4,
           edgecolor="white", linewidth=0.8)
    ax.axhline(0.05, color="#333", linewidth=1,
               linestyle="--", label="α = 0.05")

    sig_patch   = mpatches.Patch(color="#2ECC71", label="Significant")
    insig_patch = mpatches.Patch(color="#E74C3C", label="Not significant")
    ax.legend(handles=[sig_patch, insig_patch, 
              mpatches.Patch(color="#333", label="α = 0.05")])

    ax.set_ylabel("p-value")
    ax.set_title("Experiment log — p-values", fontsize=12)
    ax.set_ylim(0, max(pvalues) * 1.4)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved → {save_path}")
    plt.show()