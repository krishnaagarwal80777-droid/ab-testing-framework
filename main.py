from experiment import Experiment
from visualize import plot_conversion_rates,plot_confidence_interval, plot_experiment_log
exp = Experiment(
    name="checkout_button_color",
    baseline_rate=0.05,
    min_detectable_effect=0.02,
    metric="conversion",
    alpha=0.05,
    power=0.80
)

exp.log_result("control",   users=1000, conversions=50)
exp.log_result("treatment", users=1000, conversions=70)

result = exp.analyze()
print(result)


exp.save("results.json")

plot_conversion_rates(result, save_path="conversion_rates.png")
plot_confidence_interval(result, save_path="confidence_interval.png")
plot_experiment_log("results.json", save_path="experiment_log.png")