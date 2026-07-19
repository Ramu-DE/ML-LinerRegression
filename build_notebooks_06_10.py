# -*- coding: utf-8 -*-
"""Build NB06-NB10: OLS assumptions, diagnostics, multiple regression, multicollinearity, polynomial"""
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
# NB06 — OLS Assumptions (LINE)
# ─────────────────────────────────────────────────────────────────────────────
cells_06 = [
md("""# NB06 — OLS Assumptions: LINE

> **When are OLS estimates valid? What breaks when assumptions fail?**

The four classical OLS assumptions:

| Letter | Assumption | What it means |
|--------|-----------|---------------|
| L | Linearity | True relationship is linear in parameters |
| I | Independence | Observations are independent of each other |
| N | Normality | Residuals are normally distributed |
| E | Equal variance | Residuals have constant variance (homoscedasticity) |
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

np.random.seed(42)
n = 100
X = np.linspace(1, 10, n)

# --- Good data: all assumptions met ---
y_good = 2*X + 5 + np.random.normal(0, 2, n)

# --- L violated: non-linear relationship ---
y_nonlinear = 2*X**2 + np.random.normal(0, 5, n)

# --- E violated: heteroscedasticity ---
y_hetero = 2*X + 5 + np.random.normal(0, X*0.8, n)  # variance grows with X

fig, axes = plt.subplots(2, 3, figsize=(15, 8))

for col, (y_data, title) in enumerate([
    (y_good,       "Good data (all assumptions met)"),
    (y_nonlinear,  "L violated: non-linear data"),
    (y_hetero,     "E violated: heteroscedasticity"),
]):
    m = LinearRegression().fit(X.reshape(-1,1), y_data)
    yhat = m.predict(X.reshape(-1,1))
    resid = y_data - yhat

    ax_top = axes[0, col]
    ax_top.scatter(X, y_data, s=15, alpha=0.5, color='steelblue')
    ax_top.plot(X, yhat, 'r-', linewidth=2)
    ax_top.set_title(title); ax_top.grid(alpha=0.3)

    ax_bot = axes[1, col]
    ax_bot.scatter(yhat, resid, s=15, alpha=0.5, color='orange')
    ax_bot.axhline(0, color='red', linewidth=1)
    ax_bot.set_xlabel('Fitted values'); ax_bot.set_ylabel('Residuals')
    ax_bot.set_title('Residuals vs Fitted'); ax_bot.grid(alpha=0.3)

plt.tight_layout(); plt.show()
print("Top row: scatter + fit.  Bottom row: residuals vs fitted (key diagnostic plot).")
print("Good data: random scatter around 0.")
print("Non-linear: curved pattern in residuals.")
print("Hetero: funnel pattern — variance increases with fitted value.")
"""),
md("""## L — Linearity

**Assumption:** E[y | x] = β₀ + β₁x  (the mean of y is a linear function of x)

**What breaks:** biased coefficients, biased predictions

**How to detect:** residuals vs fitted — look for a curved pattern

**Fix:** add polynomial terms, log-transform, or use a non-linear model
"""),
md("""## I — Independence

**Assumption:** ε₁, ε₂, ..., εₙ are independent of each other

**What breaks:** standard errors are wrong → t-tests and CIs are invalid

**Common causes:** time-series data, clustered data, repeated measures

**How to detect:** Durbin-Watson test, ACF plot of residuals

**Fix:** use time-series models (ARIMA), mixed effects models, clustered SEs
"""),
code("""# Demonstrate autocorrelation in residuals
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.stats.stattools import durbin_watson

np.random.seed(0)
n = 100
X = np.linspace(0, 10, n)

# Independent residuals (good)
e_indep = np.random.normal(0, 1, n)

# Autocorrelated residuals (bad) — AR(1) process
e_auto = np.zeros(n)
e_auto[0] = np.random.normal()
for i in range(1, n):
    e_auto[i] = 0.85 * e_auto[i-1] + np.random.normal(0, 0.5)

y_indep = 2*X + 5 + e_indep
y_auto  = 2*X + 5 + e_auto

from sklearn.linear_model import LinearRegression
resid_indep = y_indep - LinearRegression().fit(X.reshape(-1,1), y_indep).predict(X.reshape(-1,1))
resid_auto  = y_auto  - LinearRegression().fit(X.reshape(-1,1), y_auto).predict(X.reshape(-1,1))

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, resid, title in zip(axes,
    [resid_indep, resid_auto],
    ['Independent residuals', 'Autocorrelated residuals (AR1 rho=0.85)']):
    ax.plot(resid, color='steelblue', linewidth=0.8)
    ax.axhline(0, color='red', linewidth=1)
    ax.set_title(title); ax.grid(alpha=0.3)

plt.tight_layout(); plt.show()

dw_i = durbin_watson(resid_indep)
dw_a = durbin_watson(resid_auto)
print(f"Durbin-Watson (independent):    {dw_i:.3f}  (want ~2.0)")
print(f"Durbin-Watson (autocorrelated): {dw_a:.3f}  (<2 = positive autocorrelation)")
"""),
md("""## N — Normality of residuals

**Assumption:** residuals ~ Normal(0, σ²)

**What breaks:** t-tests and p-values are approximate (not exact).
For large n, CLT saves you. For small n, this matters more.

**How to detect:** Q-Q plot of residuals; Shapiro-Wilk test

**Fix:** transform y (log, Box-Cox); robust regression
"""),
code("""import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

np.random.seed(1)
n = 80

# Normal residuals
e_normal = np.random.normal(0, 1, n)
# Skewed residuals
e_skewed = np.random.exponential(1, n) - 1

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, resid, title in zip(axes,
    [e_normal, e_skewed],
    ['Normal residuals', 'Skewed residuals']):
    (osm, osr), (slope, intercept, r) = stats.probplot(resid)
    ax.scatter(osm, osr, s=20, color='steelblue', alpha=0.7)
    xs = np.array([osm.min(), osm.max()])
    ax.plot(xs, slope*xs+intercept, 'r-', linewidth=2, label='Normal line')
    sw_stat, sw_p = stats.shapiro(resid)
    ax.set_title(f'{title}\\nShapiro-Wilk p={sw_p:.4f}')
    ax.set_xlabel('Theoretical quantiles'); ax.set_ylabel('Sample quantiles')
    ax.legend(); ax.grid(alpha=0.3)

plt.suptitle('Q-Q Plots: points on the diagonal = normal residuals')
plt.tight_layout(); plt.show()
"""),
md("""## E — Equal variance (Homoscedasticity)

**Assumption:** Var(εᵢ) = σ² for all i (constant variance)

**What breaks:** SEs are wrong → invalid t-tests and CIs.
Predictions are still unbiased, but inefficient.

**How to detect:** scale-location plot; Breusch-Pagan test

**Fix:** weighted least squares (WLS); log-transform y; robust SEs (HC3)
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan

np.random.seed(3)
n = 100
X = np.linspace(1, 10, n)

# Homoscedastic
y_homo  = 2*X + 5 + np.random.normal(0, 2, n)
# Heteroscedastic
y_hetero = 2*X + 5 + np.random.normal(0, 0.5*X, n)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, y_data, title in zip(axes,
    [y_homo, y_hetero],
    ['Homoscedastic', 'Heteroscedastic']):
    Xsm = sm.add_constant(X)
    res = sm.OLS(y_data, Xsm).fit()
    std_resid = np.sqrt(np.abs(res.resid / res.resid.std()))
    ax.scatter(res.fittedvalues, std_resid, s=20, alpha=0.6, color='steelblue')
    ax.set_xlabel('Fitted values'); ax.set_ylabel('√|Standardised residuals|')
    bp_stat, bp_p, *_ = het_breuschpagan(res.resid, Xsm)
    ax.set_title(f'{title}\\nBreusch-Pagan p={bp_p:.4f}')
    ax.grid(alpha=0.3)

plt.suptitle('Scale-Location Plot: flat band = homoscedastic')
plt.tight_layout(); plt.show()
print("Breusch-Pagan p < 0.05 → reject homoscedasticity")
"""),
md("""## Summary

| Assumption | Key test | Fix |
|-----------|---------|-----|
| Linearity | Residuals vs Fitted (curved?) | Polynomial, log transform |
| Independence | Durbin-Watson (~2), ACF plot | Time-series model, cluster SEs |
| Normality | Q-Q plot, Shapiro-Wilk | Log/Box-Cox transform |
| Equal variance | Scale-Location, Breusch-Pagan | WLS, robust SEs |

**Next:** NB07 — diagnostic plots in detail (4 standard plots from R's `plot(lm)`)
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB07 — Diagnostic Plots
# ─────────────────────────────────────────────────────────────────────────────
cells_07 = [
md("""# NB07 — Diagnostic Plots

> **The four standard plots every regression analysis should include.**

1. Residuals vs Fitted
2. Normal Q-Q
3. Scale-Location (spread-location)
4. Residuals vs Leverage (Cook's distance)
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.api as sm

np.random.seed(42)
n = 60
X_raw = np.linspace(1, 10, n)
y = 2.5*X_raw + 4 + np.random.normal(0, 3, n)

# Inject one outlier
y[50] = y[50] + 30

Xsm = sm.add_constant(X_raw)
result = sm.OLS(y, Xsm).fit()
influence = result.get_influence()

fitted       = result.fittedvalues
resid        = result.resid
std_resid    = influence.resid_studentized_internal
leverage     = influence.hat_matrix_diag
cooks_d      = influence.cooks_distance[0]

fig, axes = plt.subplots(2, 2, figsize=(13, 10))

# 1. Residuals vs Fitted
ax = axes[0, 0]
ax.scatter(fitted, resid, s=25, alpha=0.6, color='steelblue')
ax.axhline(0, color='red', linewidth=1.2)
# Lowess smoother
from statsmodels.nonparametric.smoothers_lowess import lowess
lo = lowess(resid, fitted, frac=0.4)
ax.plot(lo[:,0], lo[:,1], 'r-', linewidth=2, label='Lowess')
ax.set_xlabel('Fitted values'); ax.set_ylabel('Residuals')
ax.set_title('1. Residuals vs Fitted')
ax.legend(); ax.grid(alpha=0.3)

# 2. Normal Q-Q
ax = axes[0, 1]
(osm, osr), (slope, intercept, _) = stats.probplot(std_resid)
ax.scatter(osm, osr, s=25, alpha=0.6, color='steelblue')
xs = np.array([osm.min(), osm.max()])
ax.plot(xs, slope*xs+intercept, 'r-', linewidth=2)
ax.set_xlabel('Theoretical quantiles'); ax.set_ylabel('Standardised residuals')
ax.set_title('2. Normal Q-Q')
ax.grid(alpha=0.3)

# 3. Scale-Location
ax = axes[1, 0]
sqrt_std_resid = np.sqrt(np.abs(std_resid))
ax.scatter(fitted, sqrt_std_resid, s=25, alpha=0.6, color='steelblue')
lo2 = lowess(sqrt_std_resid, fitted, frac=0.4)
ax.plot(lo2[:,0], lo2[:,1], 'r-', linewidth=2)
ax.set_xlabel('Fitted values'); ax.set_ylabel('√|Std. residuals|')
ax.set_title('3. Scale-Location')
ax.grid(alpha=0.3)

# 4. Residuals vs Leverage (Cook's D)
ax = axes[1, 1]
ax.scatter(leverage, std_resid, s=25, alpha=0.6, color='steelblue')
ax.axhline(0, color='red', linewidth=0.8)
for i in np.argsort(cooks_d)[-5:]:
    ax.annotate(f'obs {i}', (leverage[i], std_resid[i]),
                textcoords='offset points', xytext=(5,5), fontsize=8)
threshold = 4 / n
ax.axvline(threshold, color='orange', linestyle='--', linewidth=1.2, label=f'Leverage = 4/n')
ax.set_xlabel('Leverage'); ax.set_ylabel('Std. residuals')
ax.set_title("4. Residuals vs Leverage (Cook's D)")
ax.legend(); ax.grid(alpha=0.3)

plt.suptitle('Regression Diagnostic Plots', fontsize=14)
plt.tight_layout(); plt.show()
"""),
md("""## How to read each plot

### 1. Residuals vs Fitted
- **Good:** random scatter around y=0, no pattern
- **Curved pattern:** linearity assumption violated
- **Funnel shape:** heteroscedasticity

### 2. Normal Q-Q
- **Good:** points lie on the diagonal line
- **Heavy tails (S-curve):** residuals have heavier tails than normal
- **Skew:** points systematically above or below the line

### 3. Scale-Location
- **Good:** flat horizontal band of points
- **Rising/widening band:** heteroscedasticity (variance increases with fitted value)

### 4. Residuals vs Leverage (Cook's Distance)
- **Leverage:** how unusual is point i in X-space?
- **Influence:** how much does point i change the coefficients if removed?
- **Cook's D > 4/n:** potentially influential observation
"""),
code("""# Cook's distance — identify influential points
import pandas as pd

top5 = np.argsort(cooks_d)[-5:][::-1]
df_inf = pd.DataFrame({
    'obs': top5,
    "Cook's D": cooks_d[top5].round(4),
    'Leverage': leverage[top5].round(4),
    'Std resid': std_resid[top5].round(3),
})
print("Top 5 influential observations:")
print(df_inf.to_string(index=False))
print(f"\\nThreshold Cook's D = 4/n = {4/n:.4f}")
print(f"Observation 50 was our injected outlier.")
"""),
md("""## Key Takeaways

- Run all 4 diagnostic plots **every time** you fit a regression
- Residuals vs Fitted + Scale-Location: check L and E assumptions
- Q-Q plot: check N assumption
- Leverage plot: find influential outliers that distort the fit

**Next:** NB08 — Multiple Linear Regression (matrix form, multiple predictors)
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB08 — Multiple Linear Regression
# ─────────────────────────────────────────────────────────────────────────────
cells_08 = [
md("""# NB08 — Multiple Linear Regression

> **Extending from one predictor to many — the matrix normal equations.**

Simple regression: `y = β₀ + β₁x + ε`
Multiple regression: `y = β₀ + β₁x₁ + β₂x₂ + ... + βₖxₖ + ε`
Matrix form: `y = Xβ + ε`
"""),
code("""import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# California housing dataset — 8 predictors
housing = fetch_california_housing()
X_df = pd.DataFrame(housing.data, columns=housing.feature_names)
y    = housing.target   # median house value (in $100k)

print("Shape:", X_df.shape)
print("\\nFeatures:")
for col, desc in zip(housing.feature_names, housing.feature_names):
    print(f"  {col}")
print("\\nTarget: median house value ($100k)")
print(X_df.describe().round(2))
"""),
code("""# Fit multiple regression via matrix normal equations (from scratch)
import numpy as np

X_arr = X_df.values
n, k  = X_arr.shape

# Design matrix: add intercept column
X_design = np.column_stack([np.ones(n), X_arr])

# β̂ = (XᵀX)⁻¹Xᵀy
XtX  = X_design.T @ X_design
Xty  = X_design.T @ y
beta = np.linalg.solve(XtX, Xty)   # solve() is numerically better than inv()

print("Coefficients from normal equations:")
print(f"  {'Feature':<20} {'Coefficient':>12}")
print("  " + "-"*35)
labels = ['Intercept'] + list(housing.feature_names)
for lab, b in zip(labels, beta):
    print(f"  {lab:<20} {b:>12.6f}")
"""),
code("""# Evaluate: R², Adjusted R²
y_hat   = X_design @ beta
resid   = y - y_hat
ss_res  = np.sum(resid**2)
ss_tot  = np.sum((y - y.mean())**2)
r2      = 1 - ss_res / ss_tot
r2_adj  = 1 - (1 - r2) * (n - 1) / (n - k - 1)

print(f"R²           = {r2:.4f}")
print(f"Adjusted R²  = {r2_adj:.4f}  (penalises for {k} predictors)")
print(f"RMSE         = {np.sqrt(ss_res/n):.4f}")

# Cross-check
from sklearn.linear_model import LinearRegression
sk = LinearRegression().fit(X_arr, y)
print(f"\\nsklearn R²   = {sk.score(X_arr, y):.4f}  (should match)")
"""),
code("""# Coefficient plot — easier to compare on standardised scale
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

scaler  = StandardScaler()
X_std   = scaler.fit_transform(X_arr)
X_std_d = np.column_stack([np.ones(n), X_std])
beta_std = np.linalg.solve(X_std_d.T @ X_std_d, X_std_d.T @ y)

# Standard errors of coefficients
sigma2  = ss_res / (n - k - 1)
cov_b   = sigma2 * np.linalg.inv(XtX)
se_b    = np.sqrt(np.diag(cov_b))

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(housing.feature_names, beta_std[1:], color=[
    'steelblue' if b > 0 else 'crimson' for b in beta_std[1:]])
ax.axvline(0, color='black', linewidth=0.8)
ax.set_xlabel('Standardised coefficient')
ax.set_title('Feature importance (standardised coefficients)')
ax.grid(alpha=0.3, axis='x')
plt.tight_layout(); plt.show()
print("Larger absolute value = stronger effect on house price.")
"""),
code("""# Full statsmodels summary with t-stats and p-values
import statsmodels.api as sm

X_sm = sm.add_constant(X_arr)
res  = sm.OLS(y, X_sm).fit()
print(res.summary(xname=['const'] + list(housing.feature_names)))
"""),
md("""## Interpreting multiple regression coefficients

Each coefficient β_j means:

> "Expected change in y for a 1-unit increase in x_j, **holding all other predictors constant**"

This is the "ceteris paribus" (all else equal) interpretation.

**Example (housing):**
- β(AveRooms) = +0.85 means: one more average room → house price +$85k, *if all other variables stay the same*

**Why this matters:** if x₁ and x₂ are correlated, you CANNOT interpret β₁ without accounting for x₂.

**Next:** NB09 — multicollinearity: what happens when predictors are correlated.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB09 — Multicollinearity
# ─────────────────────────────────────────────────────────────────────────────
cells_09 = [
md("""# NB09 — Multicollinearity

> **When predictors are correlated, coefficients become unstable and uninterpretable.**
"""),
md("""## What is multicollinearity?

When two or more predictors are strongly correlated with each other, the model can't separate their individual effects.

**Consequence:** large standard errors → wide CIs → statistically insignificant coefficients, even when the predictors genuinely explain y.

**Does NOT affect:** predictions, R², model fit.
**Does affect:** coefficient estimates, SEs, t-tests, interpretation.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm

np.random.seed(42)
n = 100

# Two correlated predictors
x1 = np.random.normal(0, 1, n)
x2 = 0.95 * x1 + np.random.normal(0, 0.3, n)   # highly correlated with x1
y  = 3*x1 + 2*x2 + np.random.normal(0, 1, n)

print(f"Correlation(x1, x2) = {np.corrcoef(x1, x2)[0,1]:.3f}")

# Fit model with both predictors
X_both = sm.add_constant(np.column_stack([x1, x2]))
res_both = sm.OLS(y, X_both).fit()
print("\\n--- Model with BOTH x1 and x2 ---")
print(res_both.summary().tables[1])

# Fit models with one predictor each
X1 = sm.add_constant(x1)
X2 = sm.add_constant(x2)
res_x1 = sm.OLS(y, X1).fit()
res_x2 = sm.OLS(y, X2).fit()
print("\\n--- Model with x1 only ---")
print(res_x1.summary().tables[1])
print("\\n--- Model with x2 only ---")
print(res_x2.summary().tables[1])

print("\\nNotice: individually x1 and x2 are significant,")
print("but together their SEs blow up due to multicollinearity.")
"""),
md("""## VIF — Variance Inflation Factor

```
VIF_j = 1 / (1 − R²_j)
```

where R²_j is R² from regressing x_j on all other predictors.

| VIF | Interpretation |
|-----|---------------|
| 1 | No correlation with other predictors |
| 1–5 | Mild multicollinearity |
| 5–10 | Moderate — investigate |
| > 10 | Severe multicollinearity — action required |
"""),
code("""# Compute VIF from scratch
import numpy as np

def compute_vif(X_arr):
    \"\"\"Compute VIF for each column in X_arr (no intercept column).\"\"\"
    n, k = X_arr.shape
    vifs  = []
    for j in range(k):
        y_j = X_arr[:, j]
        X_j = np.delete(X_arr, j, axis=1)
        X_j_d = np.column_stack([np.ones(n), X_j])
        beta = np.linalg.solve(X_j_d.T @ X_j_d, X_j_d.T @ y_j)
        yhat = X_j_d @ beta
        ss_res = np.sum((y_j - yhat)**2)
        ss_tot = np.sum((y_j - y_j.mean())**2)
        r2_j   = 1 - ss_res/ss_tot
        vif    = 1 / max(1 - r2_j, 1e-10)
        vifs.append(vif)
    return vifs

X_mat = np.column_stack([x1, x2])
vifs  = compute_vif(X_mat)
for name, v in zip(['x1', 'x2'], vifs):
    print(f"VIF({name}) = {v:.2f}")

print("\\nVIF > 10 → severe multicollinearity confirmed")

# Cross-check with statsmodels
from statsmodels.stats.outliers_influence import variance_inflation_factor
Xd = sm.add_constant(X_mat)
for i, name in enumerate(['const','x1','x2']):
    print(f"statsmodels VIF({name}) = {variance_inflation_factor(Xd, i):.2f}")
"""),
code("""# Correlation heatmap — another diagnostic
import seaborn as sns
from sklearn.datasets import fetch_california_housing
import pandas as pd

housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['target'] = housing.target

corr = df.corr()
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, ax=ax)
ax.set_title('Correlation matrix — California Housing')
plt.tight_layout(); plt.show()
print("Off-diagonal values near ±1 → potential multicollinearity.")
"""),
md("""## Fixes for multicollinearity

| Method | What it does |
|--------|-------------|
| Remove one of the correlated predictors | Simplest fix |
| PCA before regression | Create uncorrelated components |
| Ridge regression (L2) | Shrinks large coefficients, stable under collinearity |
| Lasso (L1) | Performs automatic variable selection |
| Collect more data | Reduces SEs without changing structure |

**Next:** NB10 — Polynomial regression and interaction terms.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB10 — Polynomial & Interaction Terms
# ─────────────────────────────────────────────────────────────────────────────
cells_10 = [
md("""# NB10 — Polynomial Regression and Interaction Terms

> **Linear regression is linear in *parameters*, not in *variables*.**
> `y = β₀ + β₁x + β₂x²` is still linear regression — x² is just another feature.
"""),
md("""## Polynomial regression

Add powers of x as new features:

```
y = β₀ + β₁x + β₂x² + β₃x³ + ε
```

This is still OLS — we just expand the design matrix with x², x³, etc.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score

np.random.seed(0)
X = np.sort(np.random.uniform(-3, 3, 80))
y = 0.5*X**3 - X**2 + 2*X + np.random.normal(0, 3, 80)

X_2d = X.reshape(-1, 1)
X_plot = np.linspace(-3, 3, 200).reshape(-1, 1)

fig, axes = plt.subplots(1, 4, figsize=(17, 4))
for ax, deg in zip(axes, [1, 2, 3, 8]):
    pipe = Pipeline([
        ('poly', PolynomialFeatures(degree=deg, include_bias=False)),
        ('ols',  LinearRegression()),
    ])
    pipe.fit(X_2d, y)
    y_plot = pipe.predict(X_plot)
    r2 = pipe.score(X_2d, y)

    ax.scatter(X, y, s=15, alpha=0.5, color='steelblue')
    ax.plot(X_plot, y_plot, 'r-', linewidth=2)
    ax.set_title(f'degree={deg}\\nR²={r2:.3f}')
    ax.set_ylim(-25, 30); ax.grid(alpha=0.3)

plt.suptitle('Polynomial regression — degree controls flexibility', fontsize=12)
plt.tight_layout(); plt.show()
"""),
md("""## Underfitting vs Overfitting

| Degree | Situation | Symptom |
|--------|-----------|---------|
| Too low (1) | Underfitting | High train error, high test error |
| Just right (3) | Good fit | Low train error, low test error |
| Too high (8+) | Overfitting | Low train error, HIGH test error |

Always use cross-validation to choose the degree.
"""),
code("""# Train/test split to see overfitting
from sklearn.model_selection import train_test_split, cross_val_score
import numpy as np

X_2d = X.reshape(-1, 1)
X_tr, X_te, y_tr, y_te = train_test_split(X_2d, y, test_size=0.3, random_state=42)

degrees = range(1, 12)
train_r2, test_r2, cv_r2 = [], [], []

for deg in degrees:
    pipe = Pipeline([('poly', PolynomialFeatures(deg)), ('ols', LinearRegression())])
    pipe.fit(X_tr, y_tr)
    train_r2.append(pipe.score(X_tr, y_tr))
    test_r2.append(pipe.score(X_te, y_te))
    cv = cross_val_score(pipe, X_2d, y, cv=5, scoring='r2')
    cv_r2.append(cv.mean())

import matplotlib.pyplot as plt
plt.figure(figsize=(8, 4))
plt.plot(degrees, train_r2, 'o-', label='Train R²', color='steelblue')
plt.plot(degrees, test_r2,  's-', label='Test R²',  color='crimson')
plt.plot(degrees, cv_r2,    '^--',label='5-fold CV R²', color='green')
plt.axvline(3, color='gray', linewidth=1, linestyle='--', label='True degree=3')
plt.xlabel('Polynomial degree'); plt.ylabel('R²')
plt.title('Underfitting → Good fit → Overfitting')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
md("""## Interaction terms

An interaction term captures **when the effect of x₁ on y depends on x₂**:

```
y = β₀ + β₁x₁ + β₂x₂ + β₃(x₁·x₂) + ε
```

Interpretation of β₃:
> "How much does the slope of x₁ change for each unit increase in x₂?"
"""),
code("""import numpy as np
import statsmodels.api as sm

np.random.seed(7)
n = 200
# Two groups: low education (edu=0) and high education (edu=1)
edu   = np.random.binomial(1, 0.5, n)
exper = np.random.uniform(1, 20, n)
# Salary: experience matters MORE for high-education workers
salary = 30 + 2*exper + 15*edu + 3*exper*edu + np.random.normal(0, 5, n)

# Model WITHOUT interaction
X_no  = sm.add_constant(np.column_stack([exper, edu]))
res_no = sm.OLS(salary, X_no).fit()

# Model WITH interaction
X_int  = sm.add_constant(np.column_stack([exper, edu, exper*edu]))
res_int = sm.OLS(salary, X_int).fit()

print("=== Without interaction ===")
print(res_no.summary().tables[1])
print("\\n=== With interaction term (exper × edu) ===")
print(res_int.summary().tables[1])

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 5))
for g, color, label in [(0,'steelblue','Low education'), (1,'crimson','High education')]:
    mask = edu == g
    ax.scatter(exper[mask], salary[mask], s=15, alpha=0.4, color=color)
    xs = np.linspace(1, 20, 100)
    # Fitted line from interaction model
    b = res_int.params
    ys = b[0] + b[1]*xs + b[2]*g + b[3]*xs*g
    ax.plot(xs, ys, color=color, linewidth=2.5, label=label)

ax.set_xlabel('Experience'); ax.set_ylabel('Salary')
ax.set_title('Interaction: slope of experience differs by education group')
ax.legend(); ax.grid(alpha=0.3); plt.tight_layout(); plt.show()
print(f"\\nWithout interaction: same slope for both groups")
print(f"With interaction: slope for high-edu = {res_int.params[1]+res_int.params[3]:.2f}")
print(f"With interaction: slope for low-edu  = {res_int.params[1]:.2f}")
"""),
md("""## Key Takeaways

| Concept | Key point |
|---------|-----------|
| Polynomial | Add x², x³ as new columns — still OLS |
| Degree selection | Use cross-validation, not just train R² |
| Interaction | β₃(x₁x₂) — effect of x₁ depends on x₂ |
| Interpretation | Marginal effect of x₁ = β₁ + β₃x₂ |

**Next:** NB11 — Ridge Regression (L2 regularisation)
"""),
]

# Save
save(nb(cells_06), "NB06_OLS_Assumptions.ipynb")
save(nb(cells_07), "NB07_Diagnostic_Plots.ipynb")
save(nb(cells_08), "NB08_Multiple_Regression.ipynb")
save(nb(cells_09), "NB09_Multicollinearity.ipynb")
save(nb(cells_10), "NB10_Polynomial_Interaction.ipynb")
print("Done — NB06 to NB10 written.")
