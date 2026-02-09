import arviz as az
import numpy as np
import pymc as pm


def build_single_changepoint_model(data: np.ndarray) -> pm.Model:
    n = len(data)
    idx = np.arange(n)

    with pm.Model() as model:
        tau = pm.DiscreteUniform("tau", lower=0, upper=n - 1)
        mu1 = pm.Normal("mu1", mu=0, sigma=1)
        mu2 = pm.Normal("mu2", mu=0, sigma=1)
        sigma1 = pm.HalfNormal("sigma1", sigma=1)
        sigma2 = pm.HalfNormal("sigma2", sigma=1)

        mu = pm.math.switch(idx <= tau, mu1, mu2)
        sigma = pm.math.switch(idx <= tau, sigma1, sigma2)

        pm.Normal("obs", mu=mu, sigma=sigma, observed=data)

    return model


class BayesianChangePointAnalyzer:
    """Bayesian change point analysis for time series."""

    def __init__(self, price_data: np.ndarray, dates):
        self.price_data = price_data
        self.log_returns = np.log(price_data[1:]) - np.log(price_data[:-1])
        self.dates = dates
        self.models = {}
        self.traces = {}

    def build_single_changepoint_model(
        self, data: np.ndarray, model_name: str = "single_cp"
    ) -> pm.Model:
        n = len(data)
        idx = np.arange(n)
        with pm.Model(name=model_name) as model:
            tau = pm.DiscreteUniform("tau", lower=1, upper=n - 2)
            mu1 = pm.Normal("mu1", mu=0, sigma=1)
            mu2 = pm.Normal("mu2", mu=0, sigma=1)
            sigma1 = pm.HalfNormal("sigma1", sigma=1)
            sigma2 = pm.HalfNormal("sigma2", sigma=1)

            mu = pm.math.switch(idx < tau, mu1, mu2)
            sigma = pm.math.switch(idx < tau, sigma1, sigma2)

            pm.Normal("returns", mu=mu, sigma=sigma, observed=data)
        self.models[model_name] = model
        return model

    def build_multiple_changepoint_model(
        self, data: np.ndarray, n_changepoints: int = 3, model_name: str = "multi_cp"
    ) -> pm.Model:
        n = len(data)
        idx = np.arange(n)
        with pm.Model(name=model_name) as model:
            taus = []
            for i in range(n_changepoints):
                lower = 0 if i == 0 else taus[i - 1] + 1
                taus.append(pm.DiscreteUniform(f"tau_{i}", lower=lower, upper=n - 2))

            mus = [
                pm.Normal(f"mu_{i}", mu=0, sigma=1) for i in range(n_changepoints + 1)
            ]
            sigmas = [
                pm.HalfNormal(f"sigma_{i}", sigma=1) for i in range(n_changepoints + 1)
            ]

            mu_expr, sigma_expr = mus[0], sigmas[0]
            for i in range(n_changepoints):
                mu_expr = pm.math.switch(idx >= taus[i], mus[i + 1], mu_expr)
                sigma_expr = pm.math.switch(idx >= taus[i], sigmas[i + 1], sigma_expr)

            pm.Normal("returns", mu=mu_expr, sigma=sigma_expr, observed=data)
        self.models[model_name] = model
        return model

    def sample_model(
        self,
        model_name: str = "single_cp",
        draws: int = 2000,
        tune: int = 1000,
        chains: int = 4,
    ):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not built")
        with self.models[model_name]:
            trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                random_seed=42,
                progressbar=True,
                return_inferencedata=True,
            )
        self.traces[model_name] = trace
        return trace

    def analyze_convergence(self, model_name: str = "single_cp"):
        try:
            import arviz as az
        except Exception as exc:
            raise ImportError("arviz is required for convergence diagnostics") from exc
        if model_name not in self.traces:
            raise ValueError(f"No trace for model {model_name}")
        trace = self.traces[model_name]
        rhat = az.rhat(trace)
        ess = az.ess(trace)
        summary = az.summary(trace)
        return {
            "rhat": rhat,
            "ess": ess,
            "summary": summary,
            "converged": all(rhat[var].max() < 1.05 for var in rhat.data_vars),
        }

    def get_changepoint_posterior(self, model_name: str = "single_cp"):
        try:
            import arviz as az
        except Exception as exc:
            raise ImportError("arviz is required for posterior summaries") from exc
        if model_name not in self.traces:
            raise ValueError(f"No trace for model {model_name}")
        trace = self.traces[model_name]
        if model_name == "single_cp" or "tau" in trace.posterior:
            tau_samples = trace.posterior["tau"].values.flatten()
            tau_dates = [self.dates[int(t)] for t in tau_samples]
            return {
                "tau_samples": tau_samples,
                "tau_dates": tau_dates,
                "mean_tau": float(np.mean(tau_samples)),
                "mean_date": self.dates[int(np.mean(tau_samples))],
                "hdi_95": az.hdi(tau_samples, hdi_prob=0.95),
            }
        return {}

    def quantify_impact(self, model_name: str = "single_cp"):
        try:
            import arviz as az
        except Exception as exc:
            raise ImportError("arviz is required for impact summaries") from exc
        if model_name not in self.traces:
            raise ValueError(f"No trace for model {model_name}")
        posterior = self.traces[model_name].posterior
        if "mu1" in posterior and "mu2" in posterior:
            mu1 = posterior["mu1"].values.flatten()
            mu2 = posterior["mu2"].values.flatten()
            sigma1 = posterior["sigma1"].values.flatten()
            sigma2 = posterior["sigma2"].values.flatten()
            mu_change = mu2 - mu1
            sigma_change = sigma2 - sigma1
            mu_change_pct = (mu2 - mu1) / np.abs(mu1) * 100
            return {
                "mu_change_mean": float(np.mean(mu_change)),
                "mu_change_std": float(np.std(mu_change)),
                "mu_change_hdi": az.hdi(mu_change, hdi_prob=0.95),
                "sigma_change_mean": float(np.mean(sigma_change)),
                "sigma_change_std": float(np.std(sigma_change)),
                "mu_change_percent_mean": float(np.mean(mu_change_pct)),
                "mu_change_percent_hdi": az.hdi(mu_change_pct, hdi_prob=0.95),
            }
        return {}
