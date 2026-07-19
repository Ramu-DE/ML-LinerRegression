# -*- coding: utf-8 -*-
"""Build NB01-NB05: Linear Regression foundations"""
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
# NB01 — Intuition
# ─────────────────────────────────────────────────────────────────────────────
cells_01 = [
md("""# NB01 — Linear Regression: Intuition

> **What problem does it solve, and why a straight line?**

Before any formula, let's build the mental picture.
"""),
md("""## 1. The core question

You have two things that are related.
- Years of study → exam score
- House size → house price
- Temperature → ice cream sales

You want to **predict one from the other**.
Linear regression is the simplest model that does this: it fits a **straight line** through your data.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

# Toy dataset: study hours vs exam score
np.random.seed(42)
hours  = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=float)
scores = np.array([50, 53, 61, 67, 70, 75, 79, 84, 89, 95], dtype=float)

plt.figure(figsize=(7, 4))
plt.scatter(hours, scores, color='steelblue', s=80, zorder=3, label='Observed data')
plt.xlabel('Study hours'); plt.ylabel('Exam score')
plt.title('Study hours vs Exam score')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
print("Each dot = one student.")
print("The trend is clear: more hours → higher score.")
"""),
md("""## 2. What 'fitting a line' means

A line is defined by **two numbers**:

```
ŷ = β₀ + β₁ · x
```

| Symbol | Name | Meaning |
|--------|------|---------|
| β₀ | Intercept | Score when hours = 0 |
| β₁ | Slope | Score increase per extra hour |
| ŷ | Predicted y | Our best guess for the score |

We want the line that is **as close as possible** to all the dots.
"""),
code("""# Manually try two different lines and see which fits better
def plot_line(hours, scores, b0, b1, label, color):
    y_pred = b0 + b1 * hours
    residuals = scores - y_pred
    ssr = np.sum(residuals ** 2)
    plt.scatter(hours, scores, color='steelblue', s=80, zorder=3)
    plt.plot(hours, y_pred, color=color, linewidth=2, label=f'{label}  SSR={ssr:.1f}')
    for xi, yi, yp in zip(hours, scores, y_pred):
        plt.vlines(xi, min(yi, yp), max(yi, yp), color=color, alpha=0.4, linewidth=1.5)

fig, axes = plt.subplots(1, 2, figsize=(13, 4))

plt.sca(axes[0])
plot_line(hours, scores, b0=40, b1=5.0, label='Line A (b0=40, b1=5)', color='orange')
plt.xlabel('Hours'); plt.ylabel('Score'); plt.legend(); plt.grid(alpha=0.3)
plt.title('Line A — a guess')

plt.sca(axes[1])
# Compute the true OLS line manually
x_mean, y_mean = hours.mean(), scores.mean()
b1_ols = np.sum((hours - x_mean) * (scores - y_mean)) / np.sum((hours - x_mean) ** 2)
b0_ols = y_mean - b1_ols * x_mean
plot_line(hours, scores, b0=b0_ols, b1=b1_ols, label=f'OLS best-fit (b0={b0_ols:.1f}, b1={b1_ols:.2f})', color='crimson')
plt.xlabel('Hours'); plt.ylabel('Score'); plt.legend(); plt.grid(alpha=0.3)
plt.title('OLS best-fit line — minimum SSR')

plt.tight_layout(); plt.show()
print(f"OLS line: score = {b0_ols:.2f} + {b1_ols:.2f} * hours")
"""),
md("""## 3. The vertical distances are the key

Those coloured vertical lines are called **residuals**:

```
εᵢ = yᵢ − ŷᵢ   (actual minus predicted)
```

OLS (Ordinary Least Squares) finds the line that makes
**Σ εᵢ²  as small as possible** — the "least squares" part.

Why square them?
- Squaring makes all residuals positive (no cancellation).
- It penalises large errors more than small ones.
"""),
code("""# Visualise residuals as squares
fig, ax = plt.subplots(figsize=(8, 5))
y_pred = b0_ols + b1_ols * hours
ax.scatter(hours, scores, color='steelblue', s=80, zorder=4, label='Data')
ax.plot(hours, y_pred, 'r-', linewidth=2, label='Best-fit line')

for xi, yi, yp in zip(hours, scores, y_pred):
    res = yi - yp
    # Draw square whose side = |residual|
    sq_x = [xi, xi + abs(res)*0.08, xi + abs(res)*0.08, xi, xi]
    sq_y = [yp, yp, yp + res, yp + res, yp]
    ax.fill(sq_x, sq_y, alpha=0.2, color='orange')
    ax.vlines(xi, min(yi, yp), max(yi, yp), color='orange', linewidth=2)

ax.set_xlabel('Study hours'); ax.set_ylabel('Score')
ax.set_title('Residuals as squares — OLS minimises total area')
ax.legend(); ax.grid(alpha=0.3); plt.tight_layout(); plt.show()

ssr = np.sum((scores - y_pred) ** 2)
print(f"Sum of Squared Residuals (SSR) = {ssr:.2f}")
print(f"No other straight line produces a smaller SSR.")
"""),
md("""## 4. Key takeaways

| Concept | Plain English |
|---------|---------------|
| Linear regression | Fit a straight line to data |
| Intercept β₀ | y value when x = 0 |
| Slope β₁ | Change in y for +1 unit of x |
| Residual εᵢ | Prediction error for observation i |
| SSR | Total squared prediction error |
| OLS | The method that minimises SSR — gives the unique best-fit line |

**Next:** NB02 — where the formula `β₁ = Σ(x−x̄)(y−ȳ) / Σ(x−x̄)²` comes from (derived from scratch).
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB02 — OLS Derivation from first principles
# ─────────────────────────────────────────────────────────────────────────────
cells_02 = [
md("""# NB02 — OLS Derivation from First Principles

> **Where does β₁ = Σ(x−x̄)(y−ȳ) / Σ(x−x̄)² come from?**

We derive it step by step using calculus — no black boxes.
"""),
md("""## 1. Set up the objective

We want to find β₀ and β₁ that minimise:

```
SSR(β₀, β₁) = Σᵢ (yᵢ − β₀ − β₁xᵢ)²
```

This is a smooth bowl-shaped function.
At the minimum, both partial derivatives are **zero**.
"""),
md("""## Step 1 — Partial derivative with respect to β₀

```
∂SSR/∂β₀ = -2 Σ (yᵢ − β₀ − β₁xᵢ) = 0

⟹  Σyᵢ = n·β₀ + β₁·Σxᵢ

⟹  β₀ = ȳ − β₁·x̄          ← Intercept formula
```

The fitted line **always passes through the point (x̄, ȳ)**.
"""),
md("""## Step 2 — Partial derivative with respect to β₁

```
∂SSR/∂β₁ = -2 Σ xᵢ(yᵢ − β₀ − β₁xᵢ) = 0

⟹  Σ xᵢyᵢ = β₀·Σxᵢ + β₁·Σxᵢ²
```

Substitute β₀ = ȳ − β₁·x̄:

```
Σ xᵢyᵢ − n·x̄·ȳ = β₁ (Σxᵢ² − n·x̄²)

⟹  β₁ = Σ(xᵢ − x̄)(yᵢ − ȳ)  /  Σ(xᵢ − x̄)²    ← Slope formula
```
"""),
code("""import numpy as np

# Verify derivation on a small dataset
X = np.array([1., 2., 3., 4., 5.])
y = np.array([2., 4., 5., 4., 5.])

n    = len(X)
xbar = X.mean()
ybar = y.mean()

# Derived formula
b1 = np.sum((X - xbar) * (y - ybar)) / np.sum((X - xbar) ** 2)
b0 = ybar - b1 * xbar

print(f"x̄ = {xbar:.2f},  ȳ = {ybar:.2f}")
print(f"β₁ (slope)     = {b1:.6f}")
print(f"β₀ (intercept) = {b0:.6f}")
print(f"Line: ŷ = {b0:.4f} + {b1:.4f}·x")

# Cross-check with numpy polyfit
b1_np, b0_np = np.polyfit(X, y, 1)
print(f"\\nnumpy polyfit: β₁={b1_np:.6f}, β₀={b0_np:.6f}")
print(f"Match: {np.isclose(b1, b1_np) and np.isclose(b0, b0_np)}")
"""),
md("""## 3. Matrix form — generalises to multiple regression

For multiple predictors, the same idea becomes:

```
β̂ = (XᵀX)⁻¹ Xᵀy
```

Where **X** is the **design matrix** — one row per observation, columns are [1, x₁, x₂, ...].
The column of 1s captures the intercept β₀.
"""),
code("""import numpy as np

X_raw = np.array([1., 2., 3., 4., 5.])
y     = np.array([2., 4., 5., 4., 5.])

# Design matrix: column of 1s + X
X_design = np.column_stack([np.ones(len(X_raw)), X_raw])
print("Design matrix X:")
print(X_design)

# OLS normal equations: β̂ = (XᵀX)⁻¹ Xᵀy
XtX     = X_design.T @ X_design
Xty     = X_design.T @ y
beta    = np.linalg.inv(XtX) @ Xty

print(f"\\nβ̂ = (XᵀX)⁻¹Xᵀy = {beta}")
print(f"β₀ = {beta[0]:.6f}  (intercept)")
print(f"β₁ = {beta[1]:.6f}  (slope)")
"""),
md("""## 4. Geometric interpretation

The OLS solution projects **y** onto the **column space of X**:

```
ŷ = X · β̂  =  X(XᵀX)⁻¹Xᵀy  =  H · y
```

**H** is the **hat matrix** (it puts a "hat" on y).
ŷ is the closest point in the column space of X to the observed y —
closest measured by Euclidean distance (= minimising SSR).
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

X_raw = np.array([1., 2., 3., 4., 5.])
y     = np.array([2., 4., 5., 4., 5.])
X_design = np.column_stack([np.ones(len(X_raw)), X_raw])

# Hat matrix
H     = X_design @ np.linalg.inv(X_design.T @ X_design) @ X_design.T
y_hat = H @ y

residuals = y - y_hat
print("Fitted values ŷ:", np.round(y_hat, 3))
print("Residuals e    :", np.round(residuals, 3))
print(f"SSR            : {np.sum(residuals**2):.6f}")

# Verify: residuals are orthogonal to X columns
print(f"\\nOrthogonality check (should be ~0):")
print(f"  Xᵀe = {X_design.T @ residuals}")  # should be [0, 0]

plt.figure(figsize=(7, 4))
plt.scatter(X_raw, y, s=80, color='steelblue', zorder=3, label='Observed y')
plt.plot(X_raw, y_hat, 'r-', linewidth=2, label='Fitted ŷ')
for xi, yi, yp in zip(X_raw, y, y_hat):
    plt.vlines(xi, min(yi,yp), max(yi,yp), color='gray', linewidth=1.5, linestyle='--')
plt.xlabel('x'); plt.ylabel('y')
plt.title('OLS fit via normal equations')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
md("""## Key Takeaways

| Result | Formula |
|--------|---------|
| Slope | β₁ = Σ(xᵢ−x̄)(yᵢ−ȳ) / Σ(xᵢ−x̄)² |
| Intercept | β₀ = ȳ − β₁x̄ |
| Matrix form | β̂ = (XᵀX)⁻¹Xᵀy |
| Hat matrix | H = X(XᵀX)⁻¹Xᵀ |
| Orthogonality | Xᵀe = 0 always |

**Next:** NB03 — implement OLS completely from scratch in Python (no numpy linalg).
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB03 — From scratch in pure Python
# ─────────────────────────────────────────────────────────────────────────────
cells_03 = [
md("""# NB03 — Linear Regression from Scratch (Pure Python)

> **Implement every formula by hand. No sklearn, no numpy linalg.**

Build the entire OLS pipeline step by step.
"""),
code("""# Pure Python — no imports needed for the core class
class OLSRegression:
    \"\"\"Simple linear regression built from scratch.\"\"\"

    def __init__(self):
        self.slope     = None
        self.intercept = None
        self._fitted   = False

    # ── fitting ──────────────────────────────────────────────────────────────

    def fit(self, X, y):
        n = len(X)
        assert n >= 2, "Need at least 2 data points"
        assert len(y) == n, "X and y must have same length"

        x_mean = sum(X) / n
        y_mean = sum(y) / n

        # β₁ = Σ(xᵢ−x̄)(yᵢ−ȳ) / Σ(xᵢ−x̄)²
        numerator   = sum((X[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((X[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            raise ValueError("All X values are identical — cannot fit a line.")

        self.slope     = numerator / denominator
        self.intercept = y_mean - self.slope * x_mean
        self._fitted   = True
        return self

    # ── prediction ───────────────────────────────────────────────────────────

    def predict(self, X):
        assert self._fitted, "Call fit() first"
        return [self.intercept + self.slope * x for x in X]

    # ── metrics ──────────────────────────────────────────────────────────────

    def residuals(self, X, y):
        y_pred = self.predict(X)
        return [y[i] - y_pred[i] for i in range(len(y))]

    def ssr(self, X, y):
        res = self.residuals(X, y)
        return sum(r ** 2 for r in res)

    def mse(self, X, y):
        return self.ssr(X, y) / len(y)

    def rmse(self, X, y):
        return self.mse(X, y) ** 0.5

    def r_squared(self, X, y):
        n = len(y)
        y_mean  = sum(y) / n
        ss_tot  = sum((yi - y_mean) ** 2 for yi in y)
        ss_res  = self.ssr(X, y)
        if ss_tot == 0:
            return float('nan')
        return 1 - ss_res / ss_tot

    # ── standard errors & inference ──────────────────────────────────────────

    def standard_errors(self, X, y):
        \"\"\"SE of intercept and slope.\"\"\"
        n       = len(y)
        res     = self.residuals(X, y)
        sigma2  = sum(r**2 for r in res) / (n - 2)   # unbiased: divide by n-2
        x_mean  = sum(X) / n
        sxx     = sum((xi - x_mean) ** 2 for xi in X)
        se_b1   = (sigma2 / sxx) ** 0.5
        se_b0   = (sigma2 * (1/n + x_mean**2 / sxx)) ** 0.5
        return se_b0, se_b1

    def t_statistics(self, X, y):
        se_b0, se_b1 = self.standard_errors(X, y)
        t_b0 = self.intercept / se_b0
        t_b1 = self.slope     / se_b1
        return t_b0, t_b1

    def summary(self, X, y):
        se_b0, se_b1 = self.standard_errors(X, y)
        t_b0, t_b1   = self.t_statistics(X, y)
        r2            = self.r_squared(X, y)
        print(f"{'='*55}")
        print(f"  OLS Regression Results")
        print(f"{'='*55}")
        print(f"  {'Coef':>10}  {'SE':>10}  {'t':>10}")
        print(f"  {'-'*40}")
        print(f"  intercept  {self.intercept:>10.4f}  {se_b0:>10.4f}  {t_b0:>10.4f}")
        print(f"  slope      {self.slope:>10.4f}  {se_b1:>10.4f}  {t_b1:>10.4f}")
        print(f"{'='*55}")
        print(f"  R²  = {r2:.6f}")
        print(f"  MSE = {self.mse(X,y):.6f}")
        print(f"  RMSE= {self.rmse(X,y):.6f}")
        print(f"  SSR = {self.ssr(X,y):.6f}")
        print(f"  n   = {len(y)}")


# ── test it ──────────────────────────────────────────────────────────────────
X = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y = [40, 45, 50, 55, 65, 70, 75, 85, 90, 95]

model = OLSRegression()
model.fit(X, y)
model.summary(X, y)
"""),
code("""# Cross-check against sklearn
from sklearn.linear_model import LinearRegression as SklearnLR
import numpy as np

X_arr = np.array(X).reshape(-1, 1)
y_arr = np.array(y)

sk = SklearnLR().fit(X_arr, y_arr)
print(f"sklearn  slope={sk.coef_[0]:.6f}  intercept={sk.intercept_:.6f}")
print(f"scratch  slope={model.slope:.6f}  intercept={model.intercept:.6f}")
print(f"Match: slope={abs(sk.coef_[0]-model.slope)<1e-8}, intercept={abs(sk.intercept_-model.intercept)<1e-8}")
"""),
code("""# Manual step-by-step table — shows every arithmetic step
import numpy as np
import pandas as pd

X = np.array([1.,2.,3.,4.,5.])
y = np.array([2.,4.,5.,4.,5.])
xbar, ybar = X.mean(), y.mean()

rows = []
for xi, yi in zip(X, y):
    rows.append({
        'x': xi, 'y': yi,
        'x - x̄': xi - xbar,
        'y - ȳ': yi - ybar,
        '(x-x̄)(y-ȳ)': (xi-xbar)*(yi-ybar),
        '(x-x̄)²': (xi-xbar)**2,
    })

df = pd.DataFrame(rows)
sums = df.sum(numeric_only=True)

print(df.to_string(index=False))
print("\\nSums:")
print(f"  Σ(x-x̄)(y-ȳ) = {sums['(x-x̄)(y-ȳ)']:.2f}")
print(f"  Σ(x-x̄)²     = {sums['(x-x̄)²']:.2f}")
b1 = sums['(x-x̄)(y-ȳ)'] / sums['(x-x̄)²']
b0 = ybar - b1 * xbar
print(f"\\nβ₁ = {sums['(x-x̄)(y-ȳ)']:.2f} / {sums['(x-x̄)²']:.2f} = {b1:.4f}")
print(f"β₀ = {ybar:.2f} - {b1:.4f}×{xbar:.2f} = {b0:.4f}")
"""),
md("""## Key takeaways

- The entire algorithm is ~20 lines of pure Python
- Standard errors need `n-2` in the denominator (2 parameters estimated)
- `t = coef / SE` — measures how many standard errors away from zero
- Cross-check always: scratch vs sklearn results must match to 8 decimal places

**Next:** NB04 — R², residuals, and sum-of-squares decomposition explained visually.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB04 — R², Residuals, SS Decomposition
# ─────────────────────────────────────────────────────────────────────────────
cells_04 = [
md("""# NB04 — R², Residuals, and Sum-of-Squares Decomposition

> **Understanding what R² really measures — not just a formula.**
"""),
md("""## 1. The three sums of squares

```
SS_tot = Σ(yᵢ − ȳ)²        Total variance in y
SS_res = Σ(yᵢ − ŷᵢ)²       Unexplained variance (residuals)
SS_reg = Σ(ŷᵢ − ȳ)²        Explained variance (regression)

SS_tot = SS_reg + SS_res     ← always true

R² = SS_reg / SS_tot  =  1 − SS_res / SS_tot
```

R² = 0.80 means "the model explains 80% of the variance in y".
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

np.random.seed(0)
X = np.linspace(1, 10, 30)
y = 3 * X + np.random.normal(0, 4, 30) + 5

model = LinearRegression().fit(X.reshape(-1,1), y)
y_hat = model.predict(X.reshape(-1,1))
y_bar = y.mean()

ss_tot = np.sum((y - y_bar) ** 2)
ss_res = np.sum((y - y_hat) ** 2)
ss_reg = np.sum((y_hat - y_bar) ** 2)
r2     = 1 - ss_res / ss_tot

print(f"SS_tot = {ss_tot:.2f}")
print(f"SS_reg = {ss_reg:.2f}   (explained)")
print(f"SS_res = {ss_res:.2f}   (unexplained)")
print(f"SS_tot = SS_reg + SS_res: {np.isclose(ss_tot, ss_reg + ss_res)}")
print(f"R²     = {r2:.4f}  → model explains {r2*100:.1f}% of variance")
"""),
code("""# Visualise the decomposition for one data point
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
colors = {'tot':'#2196F3','res':'#F44336','reg':'#4CAF50'}

for ax, (ss_name, y_ref, color, title) in zip(axes, [
    ('SS_tot', y_bar,  colors['tot'], 'SS_tot = Σ(y − ȳ)²\n(total spread around mean)'),
    ('SS_res', y_hat,  colors['res'], 'SS_res = Σ(y − ŷ)²\n(residuals around fitted line)'),
    ('SS_reg', y_bar,  colors['reg'], 'SS_reg = Σ(ŷ − ȳ)²\n(fitted line spread around mean)'),
]):
    ax.scatter(X, y, color='steelblue', s=30, zorder=3, label='data')
    ax.plot(X, y_hat, 'k-', linewidth=1.5, label='fitted')
    ax.axhline(y_bar, color='gray', linestyle='--', linewidth=1, label='ȳ mean')
    ref = y_ref if hasattr(y_ref, '__len__') else np.full_like(X, y_ref)
    for xi, yi, ri in zip(X, y, ref):
        ax.vlines(xi, min(yi, ri), max(yi, ri), color=color, linewidth=2, alpha=0.6)
    ax.set_title(title); ax.legend(fontsize=7); ax.grid(alpha=0.3)

plt.tight_layout(); plt.show()
"""),
code("""# Show how R² changes with noise level
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

np.random.seed(1)
X_base = np.linspace(1, 10, 50)
noise_levels = [1, 4, 8, 15]

fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for ax, noise in zip(axes, noise_levels):
    y = 3 * X_base + noise * np.random.randn(50) + 5
    m = LinearRegression().fit(X_base.reshape(-1,1), y)
    r2 = m.score(X_base.reshape(-1,1), y)
    ax.scatter(X_base, y, s=20, alpha=0.6, color='steelblue')
    ax.plot(X_base, m.predict(X_base.reshape(-1,1)), 'r-', linewidth=2)
    ax.set_title(f'noise={noise}\\nR²={r2:.3f}')
    ax.grid(alpha=0.3)

plt.suptitle('R² decreases as noise increases', fontsize=12)
plt.tight_layout(); plt.show()
"""),
md("""## 2. Limitations of R²

| Situation | R² misleads because... |
|-----------|----------------------|
| Adding irrelevant predictors | R² always increases even if predictors add no real information |
| Non-linear data | High R² on a linear fit doesn't mean the linear model is correct |
| Outliers | One outlier can dramatically change R² |
| No intercept | R² formula breaks down |

**Adjusted R²** corrects for the number of predictors:

```
R²_adj = 1 − (1−R²)(n−1)/(n−k−1)
```

where k = number of predictors, n = sample size.
"""),
code("""# Demonstrate R²_adj penalises irrelevant features
import numpy as np
from sklearn.linear_model import LinearRegression

np.random.seed(42)
n = 50
y = np.random.randn(n)    # y has NO real predictors

r2s, r2adjs = [], []
for k in range(1, 20):
    X_noise = np.random.randn(n, k)   # pure noise predictors
    m = LinearRegression().fit(X_noise, y)
    yh = m.predict(X_noise)
    ss_res = np.sum((y - yh)**2)
    ss_tot = np.sum((y - y.mean())**2)
    r2 = 1 - ss_res / ss_tot
    r2_adj = 1 - (1-r2)*(n-1)/(n-k-1)
    r2s.append(r2); r2adjs.append(r2_adj)

import matplotlib.pyplot as plt
plt.figure(figsize=(8,4))
plt.plot(range(1,20), r2s,    'o-', label='R²', color='crimson')
plt.plot(range(1,20), r2adjs, 's--', label='Adjusted R²', color='steelblue')
plt.axhline(0, color='gray', linewidth=0.8)
plt.xlabel('Number of noise predictors'); plt.ylabel('Score')
plt.title('R² rises with irrelevant predictors; Adjusted R² stays near 0')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
print("With pure noise X, true R² should be ~0. R² inflates; Adjusted R² doesn't.")
"""),
md("""## Key Takeaways

| Metric | Formula | When it's high |
|--------|---------|----------------|
| SS_tot | Σ(y−ȳ)² | y has lots of variance |
| SS_res | Σ(y−ŷ)² | model predicts poorly |
| SS_reg | Σ(ŷ−ȳ)² | model captures the variance |
| R² | 1 − SS_res/SS_tot | model explains most of the variance |
| Adjusted R² | 1 − (1−R²)(n−1)/(n−k−1) | even with multiple predictors |

**Next:** NB05 — t-statistics, p-values, and confidence intervals.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB05 — Statistical Inference
# ─────────────────────────────────────────────────────────────────────────────
cells_05 = [
md("""# NB05 — Statistical Inference: t-stats, p-values, Confidence Intervals

> **How do we know if a coefficient is "real" and not just noise?**
"""),
md("""## 1. Standard Error of a coefficient

β̂₁ is an estimate — it would be different if we collected new data.
The **Standard Error (SE)** measures how much it would vary:

```
SE(β̂₁) = √[ σ² / Σ(xᵢ−x̄)² ]

where σ² = SS_res / (n−2)   ← residual variance (unbiased, divides by n−2)
```

Larger SE → more uncertainty → less trustworthy estimate.
"""),
code("""import numpy as np
import scipy.stats as stats

np.random.seed(7)
n = 30
X = np.linspace(1, 10, n)
true_slope = 2.5
y = true_slope * X + 5 + np.random.normal(0, 4, n)

xbar = X.mean()
ybar = y.mean()

b1 = np.sum((X-xbar)*(y-ybar)) / np.sum((X-xbar)**2)
b0 = ybar - b1*xbar

y_hat  = b0 + b1*X
resid  = y - y_hat
sigma2 = np.sum(resid**2) / (n-2)     # unbiased residual variance
sxx    = np.sum((X-xbar)**2)

se_b1 = np.sqrt(sigma2 / sxx)
se_b0 = np.sqrt(sigma2 * (1/n + xbar**2/sxx))

print(f"True slope:      {true_slope}")
print(f"Estimated slope: {b1:.4f}")
print(f"SE(slope):       {se_b1:.4f}")
print(f"SE(intercept):   {se_b0:.4f}")
"""),
md("""## 2. t-statistic

```
t = β̂ / SE(β̂)
```

Measures: how many standard errors is our estimate away from **zero**?

Under H₀: β = 0, this follows a **t-distribution with n−2 degrees of freedom**.

Rule of thumb: |t| > 2 is roughly significant at the 5% level.
"""),
code("""# t-statistics and p-values
df = n - 2   # degrees of freedom

t_b0 = b0 / se_b0
t_b1 = b1 / se_b1

# Two-sided p-value: P(|T| > |t_obs|) under H₀
p_b0 = 2 * stats.t.sf(abs(t_b0), df)
p_b1 = 2 * stats.t.sf(abs(t_b1), df)

print(f"{'':12}{'Coef':>10}  {'SE':>10}  {'t':>10}  {'p-value':>12}")
print("-"*58)
print(f"{'intercept':12}{b0:>10.4f}  {se_b0:>10.4f}  {t_b0:>10.4f}  {p_b0:>12.6f}")
print(f"{'slope':12}{b1:>10.4f}  {se_b1:>10.4f}  {t_b1:>10.4f}  {p_b1:>12.6f}")

print(f"\\np_slope = {p_b1:.6f}")
if p_b1 < 0.05:
    print("Slope is statistically significant at 5% level (p < 0.05)")
else:
    print("Slope is NOT statistically significant at 5% level")
"""),
md("""## 3. Confidence Intervals

```
CI₉₅ = β̂ ± t*(df, 0.025) × SE(β̂)
```

The critical value `t*` = 1.96 for large n (comes from the normal approximation).
For small samples, use the exact t-table value.

**Interpretation:** if we repeated the experiment 100 times, ~95 of the resulting CIs would contain the true β.
*(Not: "95% probability the true β is in this interval.")*
"""),
code("""import numpy as np, scipy.stats as stats, matplotlib.pyplot as plt

t_crit = stats.t.ppf(0.975, df)   # t*(n-2, 0.025) for 95% CI
print(f"t* (critical value, df={df}): {t_crit:.4f}  (≈1.96 for large n)")

ci_b0 = (b0 - t_crit*se_b0, b0 + t_crit*se_b0)
ci_b1 = (b1 - t_crit*se_b1, b1 + t_crit*se_b1)

print(f"\\n95% CI for intercept: [{ci_b0[0]:.3f}, {ci_b0[1]:.3f}]")
print(f"95% CI for slope:      [{ci_b1[0]:.3f}, {ci_b1[1]:.3f}]")
print(f"True slope {true_slope} inside CI: {ci_b1[0] < true_slope < ci_b1[1]}")

# Visualise: coefficient plot with error bars
fig, ax = plt.subplots(figsize=(6,3))
coefs  = [b0, b1]
ses    = [se_b0, se_b1]
labels = ['Intercept', 'Slope']
ax.errorbar([0,1], coefs, yerr=[t_crit*s for s in ses],
            fmt='o', capsize=8, capthick=2, color='steelblue', markersize=8)
ax.axhline(0, color='red', linewidth=0.8, linestyle='--', label='Zero')
ax.set_xticks([0,1]); ax.set_xticklabels(labels)
ax.set_ylabel('Coefficient value'); ax.set_title('Coefficients ± 95% CI')
ax.legend(); ax.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
code("""# Verify with statsmodels — shows the full regression table
import statsmodels.api as sm
import numpy as np

X_sm = sm.add_constant(X)    # adds the intercept column
result = sm.OLS(y, X_sm).fit()
print(result.summary())
"""),
md("""## 4. Connection: p-value ↔ confidence interval

These two are equivalent:
- p < 0.05   ↔   95% CI does not include 0
- p < 0.01   ↔   99% CI does not include 0

| p-value | Interpretation |
|---------|---------------|
| p < 0.001 | Very strong evidence against H₀ |
| p < 0.01  | Strong evidence |
| p < 0.05  | Conventional threshold — "statistically significant" |
| p ≥ 0.05  | Insufficient evidence to reject H₀ |
| p = 0.04  | Not "almost significant" — just above the threshold means just above |

**Warning:** p < 0.05 does NOT mean:
- The effect is large (check the coefficient size)
- The model is correct
- The result will replicate
"""),
md("""## Key Takeaways

| Term | Formula | Meaning |
|------|---------|---------|
| SE | √(σ²/Sxx) | Uncertainty of the estimate |
| t-stat | β̂/SE | Signal-to-noise ratio |
| p-value | 2·P(T>|t|) | Probability of seeing this result if H₀ true |
| 95% CI | β̂ ± t*·SE | Range of plausible coefficient values |

**Next:** NB06 — the four OLS assumptions (LINE) and what happens when they break.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# Save all 5 notebooks
# ─────────────────────────────────────────────────────────────────────────────
save(nb(cells_01), "NB01_Intuition.ipynb")
save(nb(cells_02), "NB02_OLS_Derivation.ipynb")
save(nb(cells_03), "NB03_From_Scratch.ipynb")
save(nb(cells_04), "NB04_R2_Residuals.ipynb")
save(nb(cells_05), "NB05_Statistical_Inference.ipynb")
print("Done — NB01 to NB05 written.")
