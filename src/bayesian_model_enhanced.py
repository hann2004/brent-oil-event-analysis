"""
Enhanced Bayesian change point detection for oil price analysis.
Includes multiple change point models, convergence diagnostics, and impact quantification.
"""

import warnings
from typing import Any, Dict

import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc as pm
import seaborn as sns

warnings.filterwarnings("ignore")


class BayesianChangePointDetector:
    """
    Bayesian change point detection for time series data.
    Supports single and multiple change point detection with comprehensive diagnostics.
    """

    def __init__(self, data: np.ndarray, dates: pd.DatetimeIndex):
        """
        Initialize detector with time series data.

        Parameters:
        -----------
        data : np.ndarray
            Time series data (typically log returns)
        dates : pd.DatetimeIndex
            Corresponding dates for the data
        """
        self.data = data
        self.dates = dates
        self.n = len(data)
        self.models: Dict[str, pm.Model] = {}
        self.traces: Dict[str, az.InferenceData] = {}
        self.results: Dict[str, Dict[str, Any]] = {}

    def build_single_changepoint_model(self, model_name: str = "single_cp") -> pm.Model:
        """
        Build a Bayesian model with a single change point.
        """
        print(f"Building single change point model: {model_name}")

        with pm.Model(name=model_name) as model:
            tau = pm.DiscreteUniform("tau", lower=1, upper=self.n - 2)

            mu1 = pm.Normal("mu1", mu=0, sigma=0.1)
            mu2 = pm.Normal("mu2", mu=0, sigma=0.1)
            sigma1 = pm.HalfNormal("sigma1", sigma=0.1)
            sigma2 = pm.HalfNormal("sigma2", sigma=0.1)

            idx = np.arange(self.n)
            mu = pm.math.switch(idx < tau, mu1, mu2)
            sigma = pm.math.switch(idx < tau, sigma1, sigma2)

            pm.Normal("returns", mu=mu, sigma=sigma, observed=self.data)

            self.models[model_name] = model

        return model

    def build_two_changepoint_model(self, model_name: str = "two_cp") -> pm.Model:
        """
        Build a Bayesian model with two change points (three regimes).
        """
        print(f"Building two change point model: {model_name}")

        with pm.Model(name=model_name) as model:
            tau1 = pm.DiscreteUniform("tau1", lower=1, upper=self.n - 3)
            tau2 = pm.DiscreteUniform("tau2", lower=tau1 + 1, upper=self.n - 2)

            mu1 = pm.Normal("mu1", mu=0, sigma=0.1)
            mu2 = pm.Normal("mu2", mu=0, sigma=0.1)
            mu3 = pm.Normal("mu3", mu=0, sigma=0.1)

            sigma1 = pm.HalfNormal("sigma1", sigma=0.1)
            sigma2 = pm.HalfNormal("sigma2", sigma=0.1)
            sigma3 = pm.HalfNormal("sigma3", sigma=0.1)

            idx = np.arange(self.n)

            regime1 = idx < tau1
            regime2 = (idx >= tau1) & (idx < tau2)

            mu = pm.math.switch(regime1, mu1, pm.math.switch(regime2, mu2, mu3))
            sigma = pm.math.switch(
                regime1, sigma1, pm.math.switch(regime2, sigma2, sigma3)
            )

            pm.Normal("returns", mu=mu, sigma=sigma, observed=self.data)

            self.models[model_name] = model

        return model

    def build_multiple_changepoint_model(
        self, max_changepoints: int = 5, model_name: str = "multiple_cp"
    ) -> pm.Model:
        """
        Build a model with flexible number of change points using a Dirichlet Process.
        """
        print(
            f"Building multiple change point model (max {max_changepoints}): {model_name}"
        )

        with pm.Model(name=model_name) as model:
            n_cp = pm.Poisson("n_cp", mu=3)
            pm.math.clip(n_cp, 0, max_changepoints)

            alpha = 1.0
            beta = pm.Beta("beta", alpha=1, beta=alpha, shape=max_changepoints)
            weights = pm.Deterministic(
                "weights",
                beta * pm.math.concatenate([[1], pm.math.cumprod(1 - beta)[:-1]]),
            )

            assignments = pm.Categorical("assignments", p=weights, shape=self.n)

            cluster_mu = pm.Normal(
                "cluster_mu", mu=0, sigma=0.1, shape=max_changepoints + 1
            )
            cluster_sigma = pm.HalfNormal(
                "cluster_sigma", sigma=0.1, shape=max_changepoints + 1
            )

            pm.Normal(
                "returns",
                mu=cluster_mu[assignments],
                sigma=cluster_sigma[assignments],
                observed=self.data,
            )

            self.models[model_name] = model

        return model

    def sample_model(
        self,
        model_name: str = "single_cp",
        draws: int = 2000,
        tune: int = 1000,
        chains: int = 4,
        target_accept: float = 0.9,
        random_seed: int = 42,
    ) -> az.InferenceData:
        """
        Run MCMC sampling for a specified model.
        """
        print(f"\nSampling model: {model_name}")
        print(f"Parameters: draws={draws}, tune={tune}, chains={chains}")

        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not built. Call build_*_model first.")

        with self.models[model_name]:
            trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                target_accept=target_accept,
                random_seed=random_seed,
                progressbar=True,
                return_inferencedata=True,
            )

        self.traces[model_name] = trace
        print("Sampling completed successfully.")

        return trace

    def analyze_convergence(self, model_name: str = "single_cp") -> Dict[str, Any]:
        """
        Analyze MCMC convergence using various diagnostics.
        """
        if model_name not in self.traces:
            raise ValueError(f"No trace found for model {model_name}")

        print(f"\nAnalyzing convergence for model: {model_name}")
        trace = self.traces[model_name]

        rhat = az.rhat(trace)
        rhat_max = float(rhat.max().to_array())
        rhat_converged = rhat_max < 1.05

        ess = az.ess(trace)
        ess_min = float(ess.min().to_array())

        summary = az.summary(trace)

        try:
            n_divergences = trace.sample_stats.diverging.sum().item()
        except Exception:
            n_divergences = 0

        convergence_stats = {
            "rhat_max": rhat_max,
            "rhat_converged": rhat_converged,
            "ess_min": ess_min,
            "ess_sufficient": ess_min > 400,
            "n_divergences": n_divergences,
            "divergences_ok": n_divergences == 0,
            "summary": summary,
            "converged": rhat_converged and (ess_min > 400) and (n_divergences == 0),
        }

        print(f"  R-hat max: {rhat_max:.3f} {'✓' if rhat_converged else '✗'}")
        print(f"  ESS min: {ess_min:.0f} {'✓' if ess_min > 400 else '✗'}")
        print(f"  Divergences: {n_divergences} {'✓' if n_divergences == 0 else '✗'}")
        print(
            f"  Overall convergence: {'✓' if convergence_stats['converged'] else '✗'}"
        )

        self.results[model_name] = {"convergence": convergence_stats, "trace": trace}

        return convergence_stats

    def plot_convergence_diagnostics(
        self, model_name: str = "single_cp", save_path: str | None = None
    ) -> None:
        """
        Plot convergence diagnostics including trace plots and posterior distributions.
        """
        if model_name not in self.traces:
            raise ValueError(f"No trace found for model {model_name}")

        trace = self.traces[model_name]

        available_vars = list(trace.posterior.data_vars)
        param_vars = [
            var for var in available_vars if not var.startswith(("chain", "draw"))
        ]

        if not param_vars:
            base_params = []
            for var in available_vars:
                if "::" in var:
                    base_params.append(var.split("::")[1])
                else:
                    base_params.append(var)
            param_vars = list(set(base_params))

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        for i, param in enumerate(param_vars[:4]):
            full_param = (
                f"{model_name}::{param}"
                if f"{model_name}::{param}" in available_vars
                else param
            )

            ax = axes[i // 2, i % 2]
            if full_param in trace.posterior:
                ax_twin = ax.twinx()
                try:
                    param_data = trace.posterior[full_param].values
                    if param_data.ndim >= 2:
                        param_samples = param_data.reshape(
                            -1, param_data.shape[-1]
                        ).flatten()
                    else:
                        param_samples = param_data.flatten()

                    ax.plot(param_samples[:500], alpha=0.7, label="Trace")
                    ax.set_title(f"Trace: {param}", fontweight="bold")
                    ax.set_xlabel("Sample")
                    ax.set_ylabel("Value")
                    ax.grid(True, alpha=0.3)
                    ax.legend()

                    ax_twin.hist(
                        param_samples,
                        bins=30,
                        alpha=0.3,
                        color="orange",
                        label="Distribution",
                    )
                    ax_twin.set_ylabel("Frequency")
                    ax_twin.legend(loc="upper right")
                except Exception as e:
                    print(f"  Could not plot {param}: {e}")
                    ax.text(
                        0.5,
                        0.5,
                        f"Could not plot\n{param}",
                        ha="center",
                        va="center",
                        transform=ax.transAxes,
                    )
                    ax.set_title(f"Trace: {param}", fontweight="bold")
            else:
                ax.text(
                    0.5,
                    0.5,
                    f"Parameter not found:\n{param}",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(f"Trace: {param}", fontweight="bold")

        plt.suptitle(
            f"Convergence Diagnostics - {model_name}", fontsize=14, fontweight="bold"
        )
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Convergence diagnostics saved to {save_path}")

        plt.show()

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        for i, param in enumerate(param_vars[:4]):
            full_param = (
                f"{model_name}::{param}"
                if f"{model_name}::{param}" in available_vars
                else param
            )

            ax = axes[i // 2, i % 2]
            if full_param in trace.posterior:
                try:
                    param_data = trace.posterior[full_param].values
                    param_samples = param_data.flatten()

                    ax.hist(
                        param_samples,
                        bins=50,
                        alpha=0.7,
                        edgecolor="black",
                        density=True,
                        label="Posterior",
                    )

                    from scipy import stats

                    kde = stats.gaussian_kde(param_samples)
                    x_range = np.linspace(param_samples.min(), param_samples.max(), 100)
                    ax.plot(x_range, kde(x_range), "r-", linewidth=2, label="KDE")

                    mean_val = np.mean(param_samples)
                    ax.axvline(
                        mean_val,
                        color="green",
                        linestyle="--",
                        linewidth=2,
                        label=f"Mean: {mean_val:.3f}",
                    )

                    hdi = az.hdi(param_samples, hdi_prob=0.95)
                    ax.axvspan(hdi[0], hdi[1], alpha=0.2, color="blue", label="95% HDI")

                    ax.set_title(f"Posterior: {param}", fontweight="bold")
                    ax.set_xlabel("Value")
                    ax.set_ylabel("Density")
                    ax.legend(fontsize=8)
                    ax.grid(True, alpha=0.3)
                except Exception as e:
                    print(f"  Could not plot posterior for {param}: {e}")
                    ax.text(
                        0.5,
                        0.5,
                        f"Could not plot\n{param}",
                        ha="center",
                        va="center",
                        transform=ax.transAxes,
                    )
                    ax.set_title(f"Posterior: {param}", fontweight="bold")
            else:
                ax.text(
                    0.5,
                    0.5,
                    f"Parameter not found:\n{param}",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(f"Posterior: {param}", fontweight="bold")

        plt.suptitle(
            f"Posterior Distributions - {model_name}", fontsize=14, fontweight="bold"
        )
        plt.tight_layout()

        if save_path:
            posterior_path = save_path.replace(".png", "_posterior.png")
            plt.savefig(posterior_path, dpi=150, bbox_inches="tight")
            print(f"Posterior distributions saved to {posterior_path}")

        plt.show()

    def get_changepoint_posterior(
        self, model_name: str = "single_cp"
    ) -> Dict[str, Any]:
        """
        Extract posterior distribution of change points.
        """
        if model_name not in self.traces:
            raise ValueError(f"No trace found for model {model_name}")

        trace = self.traces[model_name]

        if model_name == "single_cp":
            tau_samples = trace.posterior["tau"].values.flatten()
            tau_dates = [self.dates[int(tau)] for tau in tau_samples]
            mean_tau = int(np.mean(tau_samples))
            mean_date = self.dates[mean_tau]
            hdi_95 = az.hdi(tau_samples, hdi_prob=0.95)
            hdi_dates = (self.dates[int(hdi_95[0])], self.dates[int(hdi_95[1])])

            result = {
                "model": "single_changepoint",
                "tau_samples": tau_samples,
                "tau_dates": tau_dates,
                "mean_tau": mean_tau,
                "mean_date": mean_date,
                "hdi_95_indices": hdi_95,
                "hdi_95_dates": hdi_dates,
                "probability": len(tau_samples[tau_samples == mean_tau])
                / len(tau_samples),
            }
        elif model_name == "two_cp":
            tau1_samples = trace.posterior["tau1"].values.flatten()
            tau2_samples = trace.posterior["tau2"].values.flatten()

            mean_tau1 = int(np.mean(tau1_samples))
            mean_tau2 = int(np.mean(tau2_samples))

            result = {
                "model": "two_changepoints",
                "tau1_samples": tau1_samples,
                "tau2_samples": tau2_samples,
                "tau1_dates": [self.dates[int(tau)] for tau in tau1_samples],
                "tau2_dates": [self.dates[int(tau)] for tau in tau2_samples],
                "mean_tau1": mean_tau1,
                "mean_tau2": mean_tau2,
                "mean_date1": self.dates[mean_tau1],
                "mean_date2": self.dates[mean_tau2],
                "regime_duration1": mean_tau1,
                "regime_duration2": mean_tau2 - mean_tau1,
                "regime_duration3": self.n - mean_tau2,
            }
        else:
            result = {
                "model": model_name,
                "message": "Complex model - see trace for details",
            }

        self.results.setdefault(model_name, {})["changepoint_posterior"] = result
        return result

    def quantify_parameter_changes(
        self, model_name: str = "single_cp"
    ) -> Dict[str, Any]:
        """
        Quantify parameter changes between regimes.
        """
        if model_name not in self.traces:
            raise ValueError(f"No trace found for model {model_name}")

        trace = self.traces[model_name]
        posterior = trace.posterior

        if model_name == "single_cp":
            mu1_samples = posterior["mu1"].values.flatten()
            mu2_samples = posterior["mu2"].values.flatten()
            sigma1_samples = posterior["sigma1"].values.flatten()
            sigma2_samples = posterior["sigma2"].values.flatten()

            mu_change = mu2_samples - mu1_samples
            sigma_change = sigma2_samples - sigma1_samples
            mu_change_percent = (
                (mu2_samples - mu1_samples) / np.abs(mu1_samples + 1e-10) * 100
            )
            sigma_change_percent = (
                (sigma2_samples - sigma1_samples) / (sigma1_samples + 1e-10) * 100
            )

            mu_change_hdi = az.hdi(mu_change, hdi_prob=0.95)
            sigma_change_hdi = az.hdi(sigma_change, hdi_prob=0.95)

            result = {
                "mean_change": {
                    "mean": float(np.mean(mu_change)),
                    "std": float(np.std(mu_change)),
                    "hdi_95": [float(mu_change_hdi[0]), float(mu_change_hdi[1])],
                    "probability_positive": float(np.mean(mu_change > 0)),
                    "probability_negative": float(np.mean(mu_change < 0)),
                },
                "volatility_change": {
                    "mean": float(np.mean(sigma_change)),
                    "std": float(np.std(sigma_change)),
                    "hdi_95": [float(sigma_change_hdi[0]), float(sigma_change_hdi[1])],
                    "probability_increase": float(np.mean(sigma_change > 0)),
                    "probability_decrease": float(np.mean(sigma_change < 0)),
                },
                "percentage_changes": {
                    "mean_percent": float(np.mean(mu_change_percent)),
                    "volatility_percent": float(np.mean(sigma_change_percent)),
                },
            }
        elif model_name == "two_cp":
            mu1 = posterior["mu1"].values.flatten()
            mu2 = posterior["mu2"].values.flatten()
            mu3 = posterior["mu3"].values.flatten()

            sigma1 = posterior["sigma1"].values.flatten()
            sigma2 = posterior["sigma2"].values.flatten()
            sigma3 = posterior["sigma3"].values.flatten()

            result = {
                "regime1_to_2": {
                    "mean_change": float(np.mean(mu2 - mu1)),
                    "volatility_change": float(np.mean(sigma2 - sigma1)),
                },
                "regime2_to_3": {
                    "mean_change": float(np.mean(mu3 - mu2)),
                    "volatility_change": float(np.mean(sigma3 - sigma2)),
                },
            }
        else:
            result = {"message": "Parameter changes not quantified for this model"}

        self.results.setdefault(model_name, {})["parameter_changes"] = result
        return result

    def compare_with_events(
        self,
        events_df: pd.DataFrame,
        model_name: str = "single_cp",
        window_days: int = 90,
    ) -> Dict[str, Any]:
        """
        Compare detected change points with known events.
        """
        if (
            model_name not in self.results
            or "changepoint_posterior" not in self.results[model_name]
        ):
            raise ValueError(f"No change point results found for model {model_name}")

        cp_result = self.results[model_name]["changepoint_posterior"]
        events_df = events_df.copy()
        events_df["Date"] = pd.to_datetime(events_df["Date"])

        if model_name == "single_cp":
            change_date = cp_result["mean_date"]
            hdi_start, hdi_end = cp_result["hdi_95_dates"]

            window_start = change_date - pd.Timedelta(days=window_days)
            window_end = change_date + pd.Timedelta(days=window_days)

            nearby_events = events_df[
                (events_df["Date"] >= window_start) & (events_df["Date"] <= window_end)
            ].copy()

            if len(nearby_events) > 0:
                nearby_events["Days_from_Change"] = (
                    nearby_events["Date"] - change_date
                ).dt.days
                nearby_events = nearby_events.sort_values("Days_from_Change", key=abs)

            events_in_hdi = events_df[
                (events_df["Date"] >= hdi_start) & (events_df["Date"] <= hdi_end)
            ]

            correlation_results = {
                "change_date": change_date,
                "hdi_interval": (hdi_start, hdi_end),
                "nearby_events": nearby_events.to_dict("records"),
                "events_in_hdi": events_in_hdi.to_dict("records"),
                "closest_event": nearby_events.iloc[0].to_dict()
                if len(nearby_events) > 0
                else None,
                "event_count_within_window": len(nearby_events),
                "probability_event_caused_change": min(
                    1.0, len(events_in_hdi) * 0.3 + 0.1
                ),
            }
        else:
            change_dates = [cp_result.get("mean_date1"), cp_result.get("mean_date2")]
            correlation_results = {"change_points": []}

            for i, change_date in enumerate(change_dates, 1):
                if change_date is None:
                    continue
                window_start = change_date - pd.Timedelta(days=window_days)
                window_end = change_date + pd.Timedelta(days=window_days)

                nearby_events = events_df[
                    (events_df["Date"] >= window_start)
                    & (events_df["Date"] <= window_end)
                ].copy()

                if len(nearby_events) > 0:
                    nearby_events["Days_from_Change"] = (
                        nearby_events["Date"] - change_date
                    ).dt.days
                    nearby_events = nearby_events.sort_values(
                        "Days_from_Change", key=abs
                    )

                correlation_results["change_points"].append(
                    {
                        "change_point": i,
                        "date": change_date,
                        "nearby_events": nearby_events.to_dict("records"),
                        "closest_event": nearby_events.iloc[0].to_dict()
                        if len(nearby_events) > 0
                        else None,
                    }
                )

        self.results.setdefault(model_name, {})[
            "event_correlations"
        ] = correlation_results
        return correlation_results

    def generate_insights_report(
        self, model_name: str = "single_cp", events_df: pd.DataFrame | None = None
    ) -> str:
        """
        Generate a comprehensive insights report.
        """
        if model_name not in self.results:
            raise ValueError(f"No results found for model {model_name}")

        results = self.results[model_name]
        cp_result = results.get("changepoint_posterior", {})
        param_changes = results.get("parameter_changes", {})
        event_correlations = results.get("event_correlations", {})

        report = [
            "# Bayesian Change Point Analysis Insights",
            f"## Model: {model_name}",
            "",
            "### 1. Detected Change Point",
        ]

        if model_name == "single_cp":
            report.append(f"- **Date**: {cp_result.get('mean_date', 'N/A')}")
            report.append(
                f"- **95% HDI**: {cp_result.get('hdi_95_dates', ('N/A', 'N/A'))[0]} to "
                f"{cp_result.get('hdi_95_dates', ('N/A', 'N/A'))[1]}"
            )
            report.append(
                f"- **Posterior Probability**: {cp_result.get('probability', 0):.2%}"
            )

        report.append("\n### 2. Parameter Changes Between Regimes")
        if "mean_change" in param_changes:
            mean_change = param_changes["mean_change"]
            vol_change = param_changes["volatility_change"]

            report.append("#### Mean Returns:")
            report.append(
                f"- Change: {mean_change.get('mean', 0):.4f} "
                f"(95% HDI: [{mean_change.get('hdi_95', [0, 0])[0]:.4f}, "
                f"{mean_change.get('hdi_95', [0, 0])[1]:.4f}])"
            )
            report.append(
                f"- Probability of increase: {mean_change.get('probability_positive', 0):.2%}"
            )
            report.append(
                f"- Probability of decrease: {mean_change.get('probability_negative', 0):.2%}"
            )

            report.append("\n#### Volatility:")
            report.append(
                f"- Change: {vol_change.get('mean', 0):.4f} "
                f"(95% HDI: [{vol_change.get('hdi_95', [0, 0])[0]:.4f}, "
                f"{vol_change.get('hdi_95', [0, 0])[1]:.4f}])"
            )
            report.append(
                f"- Probability of increase: {vol_change.get('probability_increase', 0):.2%}"
            )
            report.append(
                f"- Probability of decrease: {vol_change.get('probability_decrease', 0):.2%}"
            )

        report.append("\n### 3. Event Correlations")
        if (
            event_correlations
            and events_df is not None
            and "nearby_events" in event_correlations
        ):
            nearby_events = event_correlations["nearby_events"]
            if nearby_events:
                report.append("**Events within ±90 days of change point:**")
                for event in nearby_events[:3]:
                    report.append(
                        f"- **{event.get('Event_Title', 'Unknown')}** "
                        f"({event.get('Date', 'N/A')}) - "
                        f"{abs(event.get('Days_from_Change', 0))} days from change point"
                    )

                closest = event_correlations.get("closest_event")
                if closest:
                    report.append(
                        f"\n**Closest Event:** {closest.get('Event_Title')} "
                        f"({abs(closest.get('Days_from_Change', 0))} days)"
                    )

                    if abs(closest.get("Days_from_Change", 100)) <= 7:
                        assessment = "HIGH likelihood of causation"
                    elif abs(closest.get("Days_from_Change", 100)) <= 30:
                        assessment = "MODERATE likelihood of causation"
                    else:
                        assessment = "LOW likelihood of causation"

                    report.append(f"**Assessment**: {assessment}")

        report.append("\n### 4. Investment Implications")
        if "mean_change" in param_changes:
            mean_change_val = param_changes["mean_change"].get("mean", 0)
            vol_change_val = param_changes["volatility_change"].get("mean", 0)

            if mean_change_val > 0:
                report.append("- **Returns increased** after the change point")
                report.append(
                    "  - Consider strategies that benefit from higher average returns"
                )
            else:
                report.append("- **Returns decreased** after the change point")
                report.append("  - Consider defensive strategies or hedging")

            if vol_change_val > 0:
                report.append("- **Volatility increased** after the change point")
                report.append("  - Increase risk management measures")
                report.append("  - Consider options strategies for volatility")
            else:
                report.append("- **Volatility decreased** after the change point")
                report.append("  - Potentially lower risk environment")
                report.append("  - May allow for more aggressive positioning")

        report.append("\n### 5. Analysis Limitations")
        report.append("- **Single change point**: Assumes only one structural break")
        report.append(
            "- **Correlation ≠ Causation**: Events may correlate with but not cause changes"
        )
        report.append(
            "- **Model simplicity**: Normal distribution may not capture all features"
        )
        report.append("- **Data frequency**: Daily data may miss intraday dynamics")

        return "\n".join(report)

    def save_results(
        self, model_name: str = "single_cp", output_dir: str = "models"
    ) -> None:
        """
        Save all model results to files.
        """
        import json
        from pathlib import Path

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if model_name not in self.results:
            raise ValueError(f"No results found for model {model_name}")

        results_file = output_dir / f"{model_name}_results.json"
        with open(results_file, "w") as f:
            serializable_results = {}
            for key, value in self.results[model_name].items():
                if key == "trace":
                    continue
                try:
                    json.dumps(value)
                    serializable_results[key] = value
                except Exception:
                    serializable_results[key] = str(value)

            json.dump(serializable_results, f, indent=2, default=str)

        trace_file = output_dir / f"{model_name}_trace.nc"
        if model_name in self.traces:
            self.traces[model_name].to_netcdf(trace_file)

        print(f"Results saved to {results_file}")
        if model_name in self.traces:
            print(f"Trace saved to {trace_file}")


__all__ = ["BayesianChangePointDetector"]
