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
