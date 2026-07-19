# -*- coding: utf-8 -*-
"""Build NB16-NB20: Robust regression, Quantile, Bayesian, Time series, sklearn Pipelines"""
import nbformat, os

OUT = os.path.join(os.path.dirname(__file__), "notebooks")
os.makedirs(OUT, exist_ok=True)

def md(s):   return nbformat.v4.new_markdown_cell(s)
def code(s): return nbformat.v4.new_code_cell(s)
def nb(cells):
    n = nbformat.v4.new_notebook()
    n.cells = cells
    return n
def save(notebook, name):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        nbformat.write(notebook, f)
    print(f"  wrote {name}")

# ─────────────────────────────────────────────────────────────────────────────
# NB16 — Robust Regression
# ─────────────────────────────────────────────────────────────────────────────
cells_16 = [
md("""# NB16 — Robust Regression

> **OLS squares residuals, so outliers dominate. Robust regression limits their influence.**

Three main approaches:
1. **Huber regression** — quadratic for small residuals, linear for large ones
2. **RANSAC** — random consensus: finds the line supported by the most inliers
3. **Theil-Sen** — median of all pairwise slopes: immune to 29.3% contamination
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, HuberRegressor, RANSACRegressor, TheilSenRegressor

np.random.seed(42)
n = 60
X = np.linspace(0, 10, n).reshape(-1,1)
y = 2*X.ravel() + 3 + np.random.normal(0, 1, n)

# Add 8 gross outliers
X_out = np.array([[1],[2],[3],[4],[9],[9.5],[8],[7]])
y_out = np.array([20, 22, 25, 23, -5, -8, -4, -3])
X_all = np.vstack([X, X_out])
y_all = np.concatenate([y, y_out])

models = {
    'OLS':       LinearRegression(),
    'Huber':     HuberRegressor(epsilon=1.35),
    'RANSAC':    RANSACRegressor(random_state=42),
    'Theil-Sen': TheilSenRegressor(random_state=42),
}

X_plot = np.linspace(-1, 11, 200).reshape(-1,1)
colors = ['red', 'green', 'orange', 'purple']

plt.figure(figsize=(10, 6))
plt.scatter(X.ravel(), y, s=25, color='steelblue', alpha=0.7, zorder=3, label='Clean data')
plt.scatter(X_out.ravel(), y_out, s=80, color='black', marker='x', linewidths=2, zorder=4, label='Outliers')

for (name, m), color in zip(models.items(), colors):
    m.fit(X_all, y_all)
    y_hat = m.predict(X_plot)
    plt.plot(X_plot, y_hat, color=color, linewidth=2.5, label=name)

plt.xlabel('X'); plt.ylabel('y')
plt.title('Robust regression: OLS pulled by outliers, robust methods resist')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()

print("True slope = 2.0")
for name, m in models.items():
    if hasattr(m, 'estimator_'):   # RANSAC
        slope = m.estimator_.coef_[0]
    else:
        slope = m.coef_[0]
    print(f"  {name:<12}: slope = {slope:.4f}")
"""),
md("""## Huber loss

```
L(r) = r²/2          if |r| ≤ ε
       ε(|r|−ε/2)    if |r| > ε
```

- For small residuals: behaves like OLS (squared loss)
- For large residuals: switches to absolute loss → limits outlier influence
- `ε = 1.35` → 95% efficiency on normal data

## RANSAC

1. Sample minimal subset of points
2. Fit a line
3. Count inliers (residual < threshold)
4. Repeat — keep the model with the most inliers

Handles extreme contamination (>30% outliers).

## Theil-Sen

β̂₁ = **median** of all (n choose 2) pairwise slopes

Breakdown point: 29.3% — still correct if up to 29.3% of data are outliers.
"""),
md("""## When to use which

| Method | Pros | Cons |
|--------|------|------|
| OLS | Fast, exact, interpretable | Destroyed by outliers |
| Huber | Fast, efficient, tunable ε | Need to choose ε |
| RANSAC | Handles extreme contamination | Non-deterministic, slow |
| Theil-Sen | Principled, high breakdown | O(n²) — slow for large n |

**Next:** NB17 — Quantile regression.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB17 — Quantile Regression
# ─────────────────────────────────────────────────────────────────────────────
cells_17 = [
md("""# NB17 — Quantile Regression

> **Model the median (or any quantile) of y — not just the mean.**

OLS models E[y | x] — the conditional **mean**.
Quantile regression models Q_τ[y | x] — the conditional **τ-th quantile**.

- τ = 0.5 → median regression (robust to outliers)
- τ = 0.9 → "90th percentile of y given x"
- τ = 0.1 → "10th percentile"

Useful when:
- Data is skewed or heteroscedastic
- You need prediction intervals
- You care about tails (e.g. financial risk, SLAs)
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import QuantileRegressor

np.random.seed(0)
n = 200
X = np.sort(np.random.uniform(0, 10, n))
# Heteroscedastic: variance grows with X
y = 2*X + 5 + np.random.normal(0, 0.5*X + 0.5, n)

X_2d   = X.reshape(-1, 1)
X_plot = np.linspace(0, 10, 200).reshape(-1, 1)

quantiles = [0.1, 0.25, 0.5, 0.75, 0.9]
colors     = ['#2196F3','#4CAF50','crimson','#FF9800','#9C27B0']

plt.figure(figsize=(10, 6))
plt.scatter(X, y, s=12, alpha=0.4, color='lightgray', zorder=1)

for q, color in zip(quantiles, colors):
    qr = QuantileRegressor(quantile=q, alpha=0, solver='highs').fit(X_2d, y)
    plt.plot(X_plot, qr.predict(X_plot), color=color, linewidth=2.5,
             label=f'Q={q}')

plt.xlabel('X'); plt.ylabel('y')
plt.title('Quantile regression: separate lines for each quantile')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
print("Notice the lines fan out — variance increases with X (heteroscedasticity).")
print("OLS would give a single line, missing this structure entirely.")
"""),
code("""# Pinball loss — what quantile regression minimises
import numpy as np
import matplotlib.pyplot as plt

def pinball_loss(r, tau):
    return np.where(r >= 0, tau*r, (tau-1)*r)

r = np.linspace(-3, 3, 300)
fig, ax = plt.subplots(figsize=(8, 4))
for tau, color in [(0.1,'blue'), (0.5,'green'), (0.9,'red')]:
    ax.plot(r, pinball_loss(r, tau), color=color, linewidth=2, label=f'τ={tau}')
ax.axvline(0, color='black', linewidth=0.5)
ax.set_xlabel('Residual r = y − ŷ'); ax.set_ylabel('Loss')
ax.set_title('Pinball loss: asymmetric penalty encourages the right quantile')
ax.legend(); ax.grid(alpha=0.3); plt.tight_layout(); plt.show()

print("τ=0.5 (median): symmetric → equal penalty for over- and under-prediction")
print("τ=0.9: heavy penalty for underestimation → model overshoots → 90th percentile")
print("τ=0.1: heavy penalty for overestimation → model undershoots → 10th percentile")
"""),
code("""# Prediction interval using quantile regression
import numpy as np
from sklearn.linear_model import QuantileRegressor
import matplotlib.pyplot as plt

qr_low  = QuantileRegressor(quantile=0.1, alpha=0, solver='highs').fit(X_2d, y)
qr_med  = QuantileRegressor(quantile=0.5, alpha=0, solver='highs').fit(X_2d, y)
qr_high = QuantileRegressor(quantile=0.9, alpha=0, solver='highs').fit(X_2d, y)

X_plot = np.linspace(0, 10, 200).reshape(-1,1)
low  = qr_low.predict(X_plot)
med  = qr_med.predict(X_plot)
high = qr_high.predict(X_plot)

plt.figure(figsize=(10, 5))
plt.scatter(X, y, s=12, alpha=0.3, color='steelblue')
plt.fill_between(X_plot.ravel(), low, high, alpha=0.2, color='orange', label='80% prediction band (Q0.1–Q0.9)')
plt.plot(X_plot, med, 'r-', linewidth=2, label='Median (Q0.5)')
plt.xlabel('X'); plt.ylabel('y')
plt.title('Prediction band from quantile regression')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
md("""## Key Takeaways

| | OLS | Quantile (τ=0.5) |
|--|-----|-----------------|
| Models | Conditional mean | Conditional median |
| Sensitive to outliers | Yes | No |
| Loss function | Squared | Absolute (pinball) |
| Multiple lines | No | Yes (one per τ) |
| Prediction intervals | From normality assumption | Direct from Q0.1, Q0.9 |

**Next:** NB18 — Bayesian Linear Regression.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB18 — Bayesian Linear Regression
# ─────────────────────────────────────────────────────────────────────────────
cells_18 = [
md("""# NB18 — Bayesian Linear Regression

> **Instead of a single point estimate, get a full posterior distribution over coefficients.**

Frequentist OLS: β̂ is a fixed (unknown) constant. We estimate it.
Bayesian: β is a **random variable** with a prior distribution. Data updates it to a posterior.

```
posterior ∝ likelihood × prior
p(β | data) ∝ p(data | β) × p(β)
```

With a Gaussian prior on β and Gaussian likelihood (normal noise), the posterior is also Gaussian — closed-form solution.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
# True parameters
true_b0, true_b1 = 3.0, 2.0
sigma_noise = 2.0

# Generate data
n = 30
X = np.random.uniform(0, 5, n)
y = true_b0 + true_b1 * X + np.random.normal(0, sigma_noise, n)

# Bayesian linear regression with conjugate Gaussian prior
# Prior: β ~ N(μ₀, Σ₀)
# Posterior: β | y, X ~ N(μₙ, Σₙ)

def bayesian_lr(X, y, sigma2_noise, mu_0, Sigma_0_inv):
    n = len(X)
    X_d = np.column_stack([np.ones(n), X])   # design matrix
    Sigma_n_inv = Sigma_0_inv + X_d.T @ X_d / sigma2_noise
    Sigma_n     = np.linalg.inv(Sigma_n_inv)
    mu_n        = Sigma_n @ (Sigma_0_inv @ mu_0 + X_d.T @ y / sigma2_noise)
    return mu_n, Sigma_n

# Weakly informative prior: β ~ N([0,0], 10I)
mu_0          = np.array([0., 0.])
Sigma_0_inv   = np.eye(2) / 10.0

mu_n, Sigma_n = bayesian_lr(X, y, sigma_noise**2, mu_0, Sigma_0_inv)

print(f"True parameters:     β₀={true_b0:.2f},  β₁={true_b1:.2f}")
print(f"OLS estimates:       β₀={np.polyfit(X,y,1)[1]:.4f},  β₁={np.polyfit(X,y,1)[0]:.4f}")
print(f"Posterior mean (MAP):β₀={mu_n[0]:.4f},  β₁={mu_n[1]:.4f}")
print(f"Posterior std:       β₀={np.sqrt(Sigma_n[0,0]):.4f},  β₁={np.sqrt(Sigma_n[1,1]):.4f}")
"""),
code("""# Show how posterior updates as data arrives
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
X_plot = np.linspace(0, 5, 200)

for ax, n_obs in zip(axes, [3, 10, 30]):
    X_sub = X[:n_obs]; y_sub = y[:n_obs]
    mu_sub, Sig_sub = bayesian_lr(X_sub, y_sub, sigma_noise**2, mu_0, Sigma_0_inv)

    # Sample 50 lines from the posterior
    samples = np.random.multivariate_normal(mu_sub, Sig_sub, 50)
    ax.scatter(X_sub, y_sub, color='steelblue', s=30, zorder=3, label='data')
    for s in samples:
        ax.plot(X_plot, s[0] + s[1]*X_plot, 'r-', alpha=0.08, linewidth=1)
    ax.plot(X_plot, mu_sub[0] + mu_sub[1]*X_plot, 'k-', linewidth=2.5, label='Posterior mean')
    ax.plot(X_plot, true_b0 + true_b1*X_plot, 'g--', linewidth=1.5, label='True line')
    ax.set_title(f'n={n_obs} observations'); ax.legend(fontsize=7); ax.grid(alpha=0.3)

plt.suptitle('Bayesian regression: uncertainty shrinks as data grows', fontsize=12)
plt.tight_layout(); plt.show()
"""),
code("""# Posterior predictive distribution — gives prediction intervals automatically
import numpy as np
import matplotlib.pyplot as plt

X_new = np.linspace(0, 6, 100)   # include extrapolation
mu_n_f, Sigma_n_f = bayesian_lr(X, y, sigma_noise**2, mu_0, Sigma_0_inv)

pred_mean = mu_n_f[0] + mu_n_f[1] * X_new

# Predictive variance = uncertainty in f(x) + measurement noise
n_full = len(X)
X_full = np.column_stack([np.ones(n_full), X])
Xnew_d = np.column_stack([np.ones(len(X_new)), X_new])
pred_var = np.array([Xnew_d[i] @ Sigma_n_f @ Xnew_d[i] + sigma_noise**2
                     for i in range(len(X_new))])
pred_std = np.sqrt(pred_var)

plt.figure(figsize=(10, 5))
plt.scatter(X, y, color='steelblue', s=30, zorder=3, label='Observed data')
plt.plot(X_new, pred_mean, 'r-', linewidth=2, label='Predictive mean')
plt.fill_between(X_new, pred_mean-2*pred_std, pred_mean+2*pred_std,
                 alpha=0.2, color='orange', label='95% predictive interval')
plt.axvline(X.max(), color='gray', linewidth=1, linestyle='--', label='Extrapolation boundary')
plt.xlabel('X'); plt.ylabel('y')
plt.title('Bayesian predictive interval — wider in extrapolation region')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
md("""## Key Takeaways

| | OLS | Bayesian |
|--|-----|---------|
| Output | Point estimate β̂ | Full distribution p(β|data) |
| Prior knowledge | Not used | Incorporated as prior |
| Uncertainty | From t-distribution | From posterior |
| Small n | Unreliable | Prior regularises |
| Closed form | Yes (normal eqns) | Yes (conjugate Gaussian) |

With a Gaussian prior and `σ² = 1/λ`, Bayesian MAP = Ridge regression.

**Next:** NB19 — Linear regression for time series.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB19 — Time Series with Linear Regression
# ─────────────────────────────────────────────────────────────────────────────
cells_19 = [
md("""# NB19 — Linear Regression for Time Series

> **Trend, seasonality, and lag features — linear regression applied to sequential data.**

Time series has structure that standard regression ignores:
- **Trend** — long-run direction
- **Seasonality** — regular periodic patterns
- **Autocorrelation** — past values predict future values

Linear regression handles all three if you create the right features.
"""),
code("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(0)
n = 120   # 10 years of monthly data
t = np.arange(n)

# Generate synthetic time series: trend + seasonality + noise
trend      = 0.3 * t
seasonal   = 5 * np.sin(2 * np.pi * t / 12)   # annual cycle
noise      = np.random.normal(0, 1.5, n)
y          = 10 + trend + seasonal + noise

dates = pd.date_range('2014-01', periods=n, freq='ME')
ts    = pd.Series(y, index=dates)

plt.figure(figsize=(12, 4))
plt.plot(ts, linewidth=1.5, color='steelblue')
plt.title('Synthetic time series: trend + annual seasonality + noise')
plt.xlabel('Date'); plt.ylabel('Value'); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
code("""# Feature engineering: trend + Fourier features for seasonality
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def make_features(t, n_fourier=2, period=12):
    features = {'t': t}
    for k in range(1, n_fourier+1):
        features[f'sin_{k}'] = np.sin(2*np.pi*k*t/period)
        features[f'cos_{k}'] = np.cos(2*np.pi*k*t/period)
    return pd.DataFrame(features)

X_feat = make_features(t, n_fourier=2)
print("Features:"); print(X_feat.head(6))

# Train on first 96 months, test on last 24
train_idx = t < 96
X_tr, X_te = X_feat[train_idx], X_feat[~train_idx]
y_tr, y_te = y[train_idx], y[~train_idx]

m = LinearRegression().fit(X_tr, y_tr)
y_pred_tr = m.predict(X_tr)
y_pred_te = m.predict(X_te)

print(f"\\nTrain R²: {r2_score(y_tr, y_pred_tr):.4f}")
print(f"Test R²:  {r2_score(y_te, y_pred_te):.4f}")

plt.figure(figsize=(12, 4))
plt.plot(dates[:96],  y[:96],        color='steelblue', linewidth=1.2, label='Train')
plt.plot(dates[96:],  y[96:],        color='orange',    linewidth=1.2, label='Test')
plt.plot(dates[:96],  y_pred_tr,     'r-', linewidth=1.5, label='Fitted')
plt.plot(dates[96:],  y_pred_te,     'g-', linewidth=2.5, label='Forecast')
plt.title('Trend + Fourier seasonality model')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
code("""# Lag features — use past values to predict future
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# AR(3) model: y_t = β₁y_{t-1} + β₂y_{t-2} + β₃y_{t-3} + trend + seasonal
def make_lag_features(y, t, lags=[1,2,3], n_fourier=2, period=12):
    df = pd.DataFrame({'t': t, 'y': y})
    for lag in lags:
        df[f'lag_{lag}'] = df['y'].shift(lag)
    for k in range(1, n_fourier+1):
        df[f'sin_{k}'] = np.sin(2*np.pi*k*t/period)
        df[f'cos_{k}'] = np.cos(2*np.pi*k*t/period)
    return df.dropna()

df_lag = make_lag_features(y, t)
feature_cols = [c for c in df_lag.columns if c != 'y']
X_lag = df_lag[feature_cols].values
y_lag = df_lag['y'].values
t_lag = df_lag['t'].values

split = t_lag < 96
X_tr2, X_te2 = X_lag[split], X_lag[~split]
y_tr2, y_te2 = y_lag[split], y_lag[~split]

m2 = LinearRegression().fit(X_tr2, y_tr2)
print(f"AR(3)+Fourier — Train R²: {m2.score(X_tr2,y_tr2):.4f}  Test R²: {m2.score(X_te2,y_te2):.4f}")
print("\\nCoefficients:")
for name, coef in zip(feature_cols, m2.coef_):
    print(f"  {name:<10} {coef:.4f}")
"""),
code("""# Residual autocorrelation check
import statsmodels.api as sm
import matplotlib.pyplot as plt

resid_ts = y_tr2 - m2.predict(X_tr2)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
sm.graphics.tsa.plot_acf(resid_ts, lags=20, ax=ax1)
sm.graphics.tsa.plot_pacf(resid_ts, lags=20, ax=ax2)
ax1.set_title('ACF of residuals'); ax2.set_title('PACF of residuals')
plt.tight_layout(); plt.show()
print("If ACF bars are within the blue band → residuals are white noise → model captured the structure.")
"""),
md("""## Key Takeaways

| Technique | What it captures |
|-----------|-----------------|
| Trend feature (t) | Linear long-run direction |
| Fourier features (sin/cos) | Fixed-period seasonality |
| Lag features | Autocorrelation / momentum |
| Residual ACF | Checks if structure remains unexplained |

**Next:** NB20 — sklearn Pipelines: production-ready workflow.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB20 — sklearn Pipelines: Production-Ready Workflow
# ─────────────────────────────────────────────────────────────────────────────
cells_20 = [
md("""# NB20 — sklearn Pipelines: Production-Ready Workflow

> **Combine preprocessing + model into one object. Prevents data leakage. Easy to deploy.**

A Pipeline applies steps in sequence:
`StandardScaler → PolynomialFeatures → Ridge`

Why Pipeline and not manual steps?
- **No data leakage**: scaler is fitted only on train data, even inside cross-validation
- **One object to serialize and deploy**
- **GridSearchCV works over the whole pipeline**
"""),
code("""import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.datasets import fetch_california_housing
from sklearn.metrics import mean_squared_error, r2_score
import warnings; warnings.filterwarnings('ignore')

housing = fetch_california_housing()
X = pd.DataFrame(housing.data, columns=housing.feature_names)
y = housing.target

# Introduce some missing values for realism
np.random.seed(42)
missing_mask = np.random.rand(*X.shape) < 0.03   # 3% missing
X_missing = X.copy()
X_missing[missing_mask] = np.nan

X_tr, X_te, y_tr, y_te = train_test_split(X_missing, y, test_size=0.2, random_state=0)
print(f"Train: {X_tr.shape}, Test: {X_te.shape}")
print(f"Missing values in train: {X_tr.isna().sum().sum()}")
"""),
code("""# Build a full pipeline
pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),       # step 1: fill missing
    ('scaler',  StandardScaler()),                        # step 2: standardise
    ('model',   Ridge(alpha=1.0)),                        # step 3: model
])

pipe.fit(X_tr, y_tr)
y_pred = pipe.predict(X_te)
print(f"Ridge Pipeline — Test R²:   {r2_score(y_te, y_pred):.4f}")
print(f"Ridge Pipeline — Test RMSE: {np.sqrt(mean_squared_error(y_te, y_pred)):.4f}")
"""),
code("""# GridSearchCV over the entire pipeline
from sklearn.model_selection import GridSearchCV

param_grid = {
    'model__alpha': [0.01, 0.1, 1, 10, 100],    # prefix = step name + __
}
grid = GridSearchCV(pipe, param_grid, cv=5, scoring='r2', n_jobs=-1)
grid.fit(X_tr, y_tr)

print(f"Best alpha: {grid.best_params_['model__alpha']}")
print(f"Best CV R²: {grid.best_score_:.4f}")
print(f"Test R²:    {grid.score(X_te, y_te):.4f}")

import pandas as pd
results = pd.DataFrame(grid.cv_results_)[['param_model__alpha','mean_test_score','std_test_score']]
print("\\nAll results:"); print(results.to_string(index=False))
"""),
code("""# Compare multiple models in one grid search using a custom step
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.model_selection import GridSearchCV
import numpy as np

# Put model choice inside the param_grid
pipes = {
    'Ridge':      Pipeline([('imp', SimpleImputer()), ('sc', StandardScaler()), ('m', Ridge())]),
    'Lasso':      Pipeline([('imp', SimpleImputer()), ('sc', StandardScaler()), ('m', Lasso())]),
    'ElasticNet': Pipeline([('imp', SimpleImputer()), ('sc', StandardScaler()), ('m', ElasticNet())]),
}

alphas = np.logspace(-2, 2, 20)
print(f"{'Model':<15} {'Best alpha':>12} {'CV R²':>8} {'Test R²':>8}")
print("-"*50)
for name, pipe in pipes.items():
    gs = GridSearchCV(pipe, {'m__alpha': alphas}, cv=5, scoring='r2', n_jobs=-1)
    gs.fit(X_tr, y_tr)
    print(f"{name:<15} {gs.best_params_['m__alpha']:>12.4f} {gs.best_score_:>8.4f} {gs.score(X_te, y_te):>8.4f}")
"""),
code("""# Save and load the pipeline (production deployment)
import joblib, os

save_path = os.path.join(os.path.dirname(__file__) if '__file__' in dir() else '.', 'best_pipeline.pkl')
joblib.dump(grid.best_estimator_, save_path)
print(f"Saved pipeline to {save_path}")

loaded_pipe = joblib.load(save_path)
y_loaded    = loaded_pipe.predict(X_te)
from sklearn.metrics import r2_score
print(f"Loaded pipeline Test R²: {r2_score(y_te, y_loaded):.4f}  (should match above)")

# Make a single prediction from new data
new_obs = pd.DataFrame([X.median().values], columns=X.columns)
new_obs.iloc[0, 0] = np.nan   # introduce a missing value
pred = loaded_pipe.predict(new_obs)
print(f"\\nPrediction for median house: ${pred[0]*100:.0f}k")
"""),
md("""## Production checklist

| Step | Why |
|------|-----|
| Imputer inside Pipeline | Impute using train-set statistics only |
| StandardScaler inside Pipeline | Prevents leakage of test-set mean/std into CV |
| GridSearchCV on whole pipeline | Tunes hyperparameters without leakage |
| joblib.dump / load | Serialize for serving |
| Single predict() call | Applies all preprocessing automatically |

## Full curriculum summary

| NB | Topic | Key concept |
|----|-------|-------------|
| 01 | Intuition | Best-fit line minimises SSR |
| 02 | OLS derivation | β̂ = (XᵀX)⁻¹Xᵀy from calculus |
| 03 | From scratch | Pure Python implementation |
| 04 | R² | SS decomposition: SS_tot = SS_reg + SS_res |
| 05 | Inference | t-stats, p-values, confidence intervals |
| 06 | Assumptions | LINE: Linearity, Independence, Normality, Equal variance |
| 07 | Diagnostics | 4 standard plots, Cook's D |
| 08 | Multiple regression | Matrix form, β interpretation |
| 09 | Multicollinearity | VIF, correlation heatmap |
| 10 | Poly & interactions | Feature engineering |
| 11 | Ridge | L2 penalty, multicollinearity fix |
| 12 | Lasso | L1 penalty, automatic feature selection |
| 13 | ElasticNet | L1+L2, correlated features |
| 14 | Cross-validation | k-fold CV, learning curves, nested CV |
| 15 | Gradient Descent | GD & SGD from scratch |
| 16 | Robust regression | Huber, RANSAC, Theil-Sen |
| 17 | Quantile regression | Model any quantile, prediction intervals |
| 18 | Bayesian | Posterior distribution over coefficients |
| 19 | Time series | Trend, Fourier, lag features |
| 20 | Pipelines | Production-ready sklearn workflow |
"""),
]

save(nb(cells_16), "NB16_Robust_Regression.ipynb")
save(nb(cells_17), "NB17_Quantile_Regression.ipynb")
save(nb(cells_18), "NB18_Bayesian_Regression.ipynb")
save(nb(cells_19), "NB19_Time_Series.ipynb")
save(nb(cells_20), "NB20_Pipelines_Production.ipynb")
print("Done — NB16 to NB20 written.")
