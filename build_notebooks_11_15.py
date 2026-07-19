# -*- coding: utf-8 -*-
"""Build NB11-NB15: Ridge, Lasso, ElasticNet, Cross-validation, Gradient Descent"""
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
# NB11 — Ridge Regression (L2)
# ─────────────────────────────────────────────────────────────────────────────
cells_11 = [
md("""# NB11 — Ridge Regression (L2 Regularisation)

> **Shrink large coefficients to reduce overfitting and handle multicollinearity.**

OLS minimises:  `SSR = Σ(yᵢ − ŷᵢ)²`

Ridge minimises: `SSR + λ·Σβⱼ²`

The penalty `λ·Σβⱼ²` (L2 norm) discourages large coefficients.
λ = 0 → OLS.   λ → ∞ → all coefficients → 0.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

np.random.seed(42)
n = 50
X = np.sort(np.random.uniform(-2, 2, n))
y = np.sin(X * np.pi) + np.random.normal(0, 0.3, n)

X_2d = X.reshape(-1,1)
X_tr, X_te, y_tr, y_te = train_test_split(X_2d, y, test_size=0.3, random_state=0)
X_plot = np.linspace(-2, 2, 200).reshape(-1,1)

alphas = [0, 0.01, 1, 100]   # lambda values
fig, axes = plt.subplots(1, 4, figsize=(17, 4))

for ax, alpha in zip(axes, alphas):
    pipe = Pipeline([
        ('poly',   PolynomialFeatures(degree=10, include_bias=False)),
        ('scaler', StandardScaler()),
        ('model',  Ridge(alpha=alpha) if alpha > 0 else LinearRegression()),
    ])
    pipe.fit(X_tr, y_tr)
    tr_r2 = pipe.score(X_tr, y_tr)
    te_r2 = pipe.score(X_te, y_te)
    ax.scatter(X, y, s=15, alpha=0.5, color='steelblue')
    ax.plot(X_plot, pipe.predict(X_plot), 'r-', linewidth=2)
    label = f'λ={alpha}' if alpha > 0 else 'OLS (λ=0)'
    ax.set_title(f'{label}\\nTrain R²={tr_r2:.3f}\\nTest R²={te_r2:.3f}')
    ax.set_ylim(-2, 2); ax.grid(alpha=0.3)

plt.suptitle('Ridge: higher λ → smoother fit (less overfitting)', fontsize=12)
plt.tight_layout(); plt.show()
"""),
md("""## Ridge closed-form solution

```
β̂_ridge = (XᵀX + λI)⁻¹ Xᵀy
```

The `λI` term makes the matrix invertible even when XᵀX is near-singular (multicollinearity).
This is why Ridge is the standard fix for multicollinearity.
"""),
code("""# Implement Ridge from scratch using normal equations
import numpy as np

def ridge_fit(X_design, y, lam):
    n, p = X_design.shape
    # Don't penalise the intercept column (column 0)
    I_pen = np.eye(p)
    I_pen[0, 0] = 0
    beta = np.linalg.solve(X_design.T @ X_design + lam * I_pen,
                           X_design.T @ y)
    return beta

np.random.seed(1)
X_raw = np.random.randn(100, 3)
y_true = 2*X_raw[:,0] - X_raw[:,1] + 0.5*X_raw[:,2]
y = y_true + np.random.normal(0, 0.5, 100)

X_d = np.column_stack([np.ones(100), X_raw])

for lam in [0, 0.1, 1, 10, 100]:
    b = ridge_fit(X_d, y, lam)
    print(f"λ={lam:>5}: β = [{b[1]:.3f}, {b[2]:.3f}, {b[3]:.3f}]  (true: [2, -1, 0.5])")
"""),
code("""# Regularisation path: how coefficients shrink as λ increases
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import RidgeCV
from sklearn.datasets import fetch_california_housing
from sklearn.preprocessing import StandardScaler

housing = fetch_california_housing()
X_std = StandardScaler().fit_transform(housing.data)
y     = housing.target

lambdas = np.logspace(-3, 5, 200)
coefs   = []

for lam in lambdas:
    from sklearn.linear_model import Ridge
    m = Ridge(alpha=lam).fit(X_std, y)
    coefs.append(m.coef_)

coefs = np.array(coefs)

plt.figure(figsize=(10, 5))
for j, name in enumerate(housing.feature_names):
    plt.semilogx(lambdas, coefs[:, j], label=name)
plt.xlabel('λ (log scale)'); plt.ylabel('Coefficient value')
plt.title('Ridge regularisation path — all coefficients shrink to 0 as λ→∞')
plt.legend(fontsize=8, loc='upper right'); plt.grid(alpha=0.3)
plt.tight_layout(); plt.show()

# Find optimal λ via cross-validation
rc = RidgeCV(alphas=lambdas, cv=5).fit(X_std, y)
print(f"Optimal λ (RidgeCV): {rc.alpha_:.4f}")
"""),
md("""## Key Takeaways

| Property | Ridge |
|---------|-------|
| Penalty | λ·Σβⱼ² (L2 norm) |
| Effect | Shrinks all coefficients toward 0 |
| Variable selection | No — keeps all features, just smaller |
| Best for | Multicollinearity, when all features contribute |
| Closed form | Yes: β̂ = (XᵀX + λI)⁻¹Xᵀy |

**Next:** NB12 — Lasso (L1) which performs variable selection.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB12 — Lasso Regression (L1)
# ─────────────────────────────────────────────────────────────────────────────
cells_12 = [
md("""# NB12 — Lasso Regression (L1 Regularisation)

> **L1 penalty drives coefficients to exactly zero — automatic feature selection.**

Lasso minimises: `SSR + λ·Σ|βⱼ|`

The L1 (absolute value) penalty has a sharp corner at zero.
The OLS solution often lands exactly at that corner → coefficient = 0 → feature dropped.

Ridge keeps all features (just small). Lasso selects features.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso, LassoCV
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import fetch_california_housing

housing = fetch_california_housing()
X_std = StandardScaler().fit_transform(housing.data)
y     = housing.target

lambdas = np.logspace(-4, 1, 200)
coefs   = []
for lam in lambdas:
    m = Lasso(alpha=lam, max_iter=10000).fit(X_std, y)
    coefs.append(m.coef_)
coefs = np.array(coefs)

plt.figure(figsize=(10, 5))
for j, name in enumerate(housing.feature_names):
    plt.semilogx(lambdas, coefs[:, j], label=name)
plt.xlabel('λ (log scale)'); plt.ylabel('Coefficient value')
plt.title('Lasso path — coefficients hit exactly zero (feature selection)')
plt.legend(fontsize=8, loc='upper right'); plt.grid(alpha=0.3)
plt.tight_layout(); plt.show()
"""),
code("""# LassoCV — find optimal lambda by cross-validation
from sklearn.linear_model import LassoCV
import numpy as np

lasso_cv = LassoCV(cv=5, max_iter=20000, n_alphas=200).fit(X_std, y)
print(f"Optimal λ: {lasso_cv.alpha_:.6f}")
print(f"\\nCoefficients at optimal λ:")
for name, coef in zip(housing.feature_names, lasso_cv.coef_):
    status = 'SELECTED' if coef != 0 else 'zeroed out'
    print(f"  {name:<15} {coef:>10.4f}   {status}")
n_selected = np.sum(lasso_cv.coef_ != 0)
print(f"\\n{n_selected}/{len(housing.feature_names)} features selected")
"""),
md("""## Why L1 produces sparsity — geometric intuition

The feasible region for L1 is a **diamond** (in 2D), which has corners on the axes.
The OLS objective (elliptical contours) tends to first touch the diamond at a corner → one coefficient = 0.

Ridge uses a **circle** — no corners → solution rarely lands on an axis.
"""),
code("""# Visualise the geometry in 2D
import numpy as np
import matplotlib.pyplot as plt

theta = np.linspace(0, 2*np.pi, 500)
fig, axes = plt.subplots(1, 2, figsize=(11, 5))

# OLS contours (ellipse centred at the "true" OLS solution)
true_ols = np.array([1.5, 0.8])
for ax, title, boundary_fn, label in zip(axes,
    ['Ridge (L2): circle, no corners', 'Lasso (L1): diamond, corners on axes'],
    [lambda r: (r*np.cos(theta), r*np.sin(theta)),   # circle
     lambda r: None],
    ['L2 ball', 'L1 ball']):

    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5)
    ax.set_aspect('equal')
    ax.axhline(0, color='k', linewidth=0.5); ax.axvline(0, color='k', linewidth=0.5)

    # Constraint ball
    if 'Ridge' in title:
        ax.plot(np.cos(theta), np.sin(theta), 'b-', linewidth=2, label='L2 ball (r=1)')
    else:
        d = np.array([[1,0],[-1,0],[0,-1],[0,1],[1,0]])
        ax.plot(d[:,0], d[:,1], 'b-', linewidth=2, label='L1 ball (r=1)')

    # OLS contours
    for r in [0.4, 0.8, 1.2, 1.8]:
        cx = true_ols[0] + r*np.cos(theta)
        cy = true_ols[1] + 0.6*r*np.sin(theta)
        ax.plot(cx, cy, 'r-', alpha=0.4, linewidth=1)

    ax.plot(*true_ols, 'r*', markersize=14, label='OLS solution')
    # Approximate constrained solution
    if 'Lasso' in title:
        ax.plot(1, 0, 'go', markersize=12, label='Lasso solution (β₂=0!)')
    else:
        ax.plot(0.78, 0.62, 'go', markersize=12, label='Ridge solution')

    ax.set_title(title); ax.legend(fontsize=8); ax.grid(alpha=0.3)

plt.suptitle('Why L1 selects features: the diamond has corners on the axes', fontsize=11)
plt.tight_layout(); plt.show()
"""),
md("""## Ridge vs Lasso: when to use which

| | Ridge | Lasso |
|--|-------|-------|
| Penalty | Σβⱼ² | Σ|βⱼ| |
| Variable selection | No | Yes |
| Sparse solution | No | Yes |
| When many features matter | Better | Worse |
| When few features matter | OK | Better |
| Stable with correlated features | Yes | Can be unstable |

**Next:** NB13 — ElasticNet combines both penalties.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB13 — ElasticNet & Regularisation Paths
# ─────────────────────────────────────────────────────────────────────────────
cells_13 = [
md("""# NB13 — ElasticNet & Regularisation Paths

> **Best of both worlds: L1 sparsity + L2 stability for correlated features.**

ElasticNet minimises:
```
SSR + λ₁·Σ|βⱼ| + λ₂·Σβⱼ²
```

Or equivalently (sklearn convention):
```
SSR + α [ (1-l1_ratio)·Σβⱼ²/2 + l1_ratio·Σ|βⱼ| ]
```

- `l1_ratio = 0` → Ridge
- `l1_ratio = 1` → Lasso
- `0 < l1_ratio < 1` → ElasticNet
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import ElasticNet, ElasticNetCV
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_regression

# Dataset with correlated features — Lasso struggles here
X, y, true_coef = make_regression(n_samples=200, n_features=20,
                                   n_informative=5, noise=10,
                                   coef=True, random_state=0)
X_std = StandardScaler().fit_transform(X)

from sklearn.linear_model import Ridge, Lasso
models = {
    'Ridge (l1=0)':       Ridge(alpha=1).fit(X_std, y),
    'Lasso (l1=1)':       Lasso(alpha=0.1).fit(X_std, y),
    'ElasticNet (l1=0.5)': ElasticNet(alpha=0.1, l1_ratio=0.5).fit(X_std, y),
}

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, (name, m) in zip(axes, models.items()):
    colors = ['steelblue' if c != 0 else 'lightgray' for c in m.coef_]
    ax.bar(range(20), m.coef_, color=colors)
    ax.axhline(0, color='black', linewidth=0.5)
    n_nonzero = np.sum(m.coef_ != 0)
    ax.set_title(f'{name}\\n{n_nonzero}/20 non-zero features')
    ax.set_xlabel('Feature index'); ax.grid(alpha=0.3, axis='y')

plt.suptitle('ElasticNet: sparse like Lasso but more stable than Lasso on correlated features')
plt.tight_layout(); plt.show()
"""),
code("""# ElasticNetCV — tune both alpha and l1_ratio simultaneously
from sklearn.linear_model import ElasticNetCV
import numpy as np

en_cv = ElasticNetCV(
    l1_ratio=[0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 1.0],
    n_alphas=100, cv=5, max_iter=10000
).fit(X_std, y)

print(f"Optimal alpha   : {en_cv.alpha_:.6f}")
print(f"Optimal l1_ratio: {en_cv.l1_ratio_:.2f}")
print(f"Non-zero coefs  : {np.sum(en_cv.coef_ != 0)}/{X.shape[1]}")
print(f"R² (train)      : {en_cv.score(X_std, y):.4f}")
"""),
code("""# Compare all three on the same dataset: train/test R²
from sklearn.model_selection import cross_val_score
import pandas as pd

results = []
for name, m in models.items():
    cv_r2 = cross_val_score(m.__class__(**m.get_params()),
                            X_std, y, cv=5, scoring='r2')
    results.append({'Model': name, 'CV R² mean': cv_r2.mean(), 'CV R² std': cv_r2.std()})

df = pd.DataFrame(results)
print(df.to_string(index=False))
"""),
md("""## When to use ElasticNet

- You have many correlated features
- You want some variable selection (Lasso-like) but Ridge's group stability
- In practice: try `l1_ratio ∈ [0.5, 0.9]` and tune via cross-validation

**Next:** NB14 — Cross-validation and model selection.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB14 — Cross-Validation & Model Selection
# ─────────────────────────────────────────────────────────────────────────────
cells_14 = [
md("""# NB14 — Cross-Validation and Model Selection

> **Never use train R² alone to select a model. Use CV.**
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold, cross_val_score, learning_curve
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline

np.random.seed(42)
n = 150
X = np.sort(np.random.uniform(-3, 3, n)).reshape(-1, 1)
y = np.sin(X.ravel()) + np.random.normal(0, 0.4, n)

# Compare models using 5-fold CV
models = {
    'Linear (deg=1)':   Pipeline([('poly', PolynomialFeatures(1)), ('ols', LinearRegression())]),
    'Poly deg=3':       Pipeline([('poly', PolynomialFeatures(3)), ('ols', LinearRegression())]),
    'Poly deg=10':      Pipeline([('poly', PolynomialFeatures(10)), ('ols', LinearRegression())]),
    'Poly deg=10+Ridge':Pipeline([('poly', PolynomialFeatures(10)),
                                   ('sc', StandardScaler()),
                                   ('ridge', Ridge(alpha=1.0))]),
}

print(f"{'Model':<25}  {'CV R² mean':>10}  {'CV R² std':>10}  {'Train R²':>10}")
print("-"*65)
for name, m in models.items():
    cv = cross_val_score(m, X, y, cv=5, scoring='r2')
    m.fit(X, y)
    tr_r2 = m.score(X, y)
    print(f"{name:<25}  {cv.mean():>10.4f}  {cv.std():>10.4f}  {tr_r2:>10.4f}")
"""),
code("""# Learning curves — diagnose bias vs variance
from sklearn.model_selection import learning_curve

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
selected = {
    'Linear (underfitting)': Pipeline([('poly', PolynomialFeatures(1)), ('ols', LinearRegression())]),
    'Poly deg=3 (good fit)': Pipeline([('poly', PolynomialFeatures(3)), ('ols', LinearRegression())]),
    'Poly deg=10 (overfit)': Pipeline([('poly', PolynomialFeatures(10)), ('ols', LinearRegression())]),
}

for ax, (name, m) in zip(axes, selected.items()):
    sizes, tr_sc, te_sc = learning_curve(
        m, X, y, cv=5, scoring='r2',
        train_sizes=np.linspace(0.1, 1.0, 12))

    tr_mean = tr_sc.mean(axis=1); tr_std = tr_sc.std(axis=1)
    te_mean = te_sc.mean(axis=1); te_std = te_sc.std(axis=1)

    ax.fill_between(sizes, tr_mean-tr_std, tr_mean+tr_std, alpha=0.15, color='steelblue')
    ax.fill_between(sizes, te_mean-te_std, te_mean+te_std, alpha=0.15, color='crimson')
    ax.plot(sizes, tr_mean, 'o-', color='steelblue', label='Train')
    ax.plot(sizes, te_mean, 's-', color='crimson',   label='CV')
    ax.set_title(name); ax.set_xlabel('Training set size')
    ax.set_ylabel('R²'); ax.legend(); ax.grid(alpha=0.3)

plt.suptitle('Learning curves: diagnose bias/variance trade-off', fontsize=12)
plt.tight_layout(); plt.show()
"""),
md("""## Reading learning curves

| Pattern | Diagnosis | Fix |
|---------|-----------|-----|
| Both curves low, close together | High bias (underfitting) | More features, higher degree |
| Train high, CV much lower | High variance (overfitting) | More data, regularisation |
| Both curves converge high | Good model | Ship it |
"""),
code("""# Nested CV: unbiased estimate of generalisation performance
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.linear_model import Ridge
import numpy as np

# Inner CV: tune hyperparameter
# Outer CV: estimate true test performance
param_grid = {'alpha': np.logspace(-3, 3, 30)}
inner_cv = KFold(n_splits=5, shuffle=True, random_state=1)
outer_cv = KFold(n_splits=5, shuffle=True, random_state=2)

ridge_gs = GridSearchCV(Ridge(), param_grid, cv=inner_cv, scoring='r2')
nested_scores = cross_val_score(ridge_gs, X, y, cv=outer_cv, scoring='r2')

print(f"Nested CV R²: {nested_scores.mean():.4f} ± {nested_scores.std():.4f}")
print("This is an unbiased estimate of how well the model will do on new data.")
print("(Simple CV can overestimate if you tune hyperparameters using the same fold.)")
"""),
md("""## Key Takeaways

| Technique | Use for |
|-----------|---------|
| k-fold CV | Selecting models / hyperparameters |
| Learning curve | Diagnosing bias vs variance |
| Nested CV | Unbiased performance estimate when tuning hyperparameters |
| Never | Use train R² alone to report model quality |

**Next:** NB15 — Gradient Descent: implement OLS without the normal equations.
"""),
]

# ─────────────────────────────────────────────────────────────────────────────
# NB15 — Gradient Descent
# ─────────────────────────────────────────────────────────────────────────────
cells_15 = [
md("""# NB15 — Gradient Descent (from scratch)

> **The alternative to the normal equations — essential for large datasets and neural networks.**

Normal equations: solve `(XᵀX)β = Xᵀy` exactly in one step.
Gradient descent: take many small steps in the direction of steepest descent.

For millions of parameters or rows, gradient descent wins.
"""),
md("""## The gradient of SSR

```
SSR = Σ(yᵢ − β₀ − β₁xᵢ)²

∂SSR/∂β₀ = -2 Σ(yᵢ − ŷᵢ)
∂SSR/∂β₁ = -2 Σ xᵢ(yᵢ − ŷᵢ)

Update rule:
  β₀ ← β₀ − α · ∂SSR/∂β₀ / n
  β₁ ← β₁ − α · ∂SSR/∂β₁ / n
```

α is the **learning rate** — controls step size.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
X = np.array([1.,2.,3.,4.,5.,6.,7.,8.,9.,10.])
y = np.array([40.,45.,50.,55.,65.,70.,75.,85.,90.,95.])
n = len(X)

def ols_gradient_descent(X, y, lr=0.001, epochs=5000):
    b0, b1 = 0.0, 0.0
    history = []

    for epoch in range(epochs):
        y_hat = b0 + b1 * X
        resid  = y - y_hat
        ssr    = np.sum(resid**2)

        # Gradients
        grad_b0 = -2 * np.sum(resid) / n
        grad_b1 = -2 * np.sum(X * resid) / n

        # Update
        b0 -= lr * grad_b0
        b1 -= lr * grad_b1

        history.append({'epoch': epoch, 'ssr': ssr, 'b0': b0, 'b1': b1})

    return b0, b1, history

b0_gd, b1_gd, hist = ols_gradient_descent(X, y, lr=0.001, epochs=5000)
print(f"Gradient Descent: β₀={b0_gd:.4f}, β₁={b1_gd:.4f}")

# Compare with normal equations
xbar, ybar = X.mean(), y.mean()
b1_ols = np.sum((X-xbar)*(y-ybar)) / np.sum((X-xbar)**2)
b0_ols = ybar - b1_ols * xbar
print(f"Normal Equations: β₀={b0_ols:.4f}, β₁={b1_ols:.4f}")
print(f"Match: {np.allclose([b0_gd, b1_gd], [b0_ols, b1_ols], atol=0.01)}")

# Plot SSR convergence
ssrs = [h['ssr'] for h in hist]
plt.figure(figsize=(8,4))
plt.plot(ssrs, color='steelblue', linewidth=1.5)
plt.xlabel('Epoch'); plt.ylabel('SSR')
plt.title('Gradient Descent: SSR decreases each epoch')
plt.yscale('log'); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
code("""# Visualise the descent on the SSR surface
import numpy as np
import matplotlib.pyplot as plt

# SSR surface over (b0, b1) grid
b0_vals = np.linspace(10, 60, 100)
b1_vals = np.linspace(3, 8, 100)
B0, B1  = np.meshgrid(b0_vals, b1_vals)
SSR = np.sum((y - (B0[:,:,None] + B1[:,:,None]*X[None,None,:]))**2, axis=2)

b0_gd2, b1_gd2, hist2 = ols_gradient_descent(X, y, lr=0.0005, epochs=3000)

path_b0 = [h['b0'] for h in hist2[::30]]
path_b1 = [h['b1'] for h in hist2[::30]]

fig, ax = plt.subplots(figsize=(8, 6))
cp = ax.contour(B0, B1, np.log(SSR+1), levels=25, cmap='viridis')
ax.plot(path_b0, path_b1, 'r.-', markersize=6, linewidth=1.5, label='GD path')
ax.plot(b0_ols, b1_ols, 'w*', markersize=15, label='OLS minimum')
ax.set_xlabel('β₀ (intercept)'); ax.set_ylabel('β₁ (slope)')
ax.set_title('Gradient Descent on SSR surface')
ax.legend(); plt.colorbar(cp, label='log(SSR+1)')
plt.tight_layout(); plt.show()
"""),
code("""# Mini-batch Stochastic Gradient Descent (SGD)
import numpy as np

def sgd(X, y, lr=0.01, epochs=100, batch_size=4, seed=0):
    np.random.seed(seed)
    b0, b1 = 0.0, 0.0
    n = len(X)
    history = []
    for epoch in range(epochs):
        idx = np.random.permutation(n)
        X_s, y_s = X[idx], y[idx]
        for i in range(0, n, batch_size):
            Xb = X_s[i:i+batch_size]
            yb = y_s[i:i+batch_size]
            resid     = yb - (b0 + b1*Xb)
            b0 += lr * 2*resid.mean()
            b1 += lr * 2*(Xb*resid).mean()
        y_hat = b0 + b1*X
        history.append(np.sum((y-y_hat)**2))
    return b0, b1, history

b0_s, b1_s, hist_s = sgd(X, y, lr=0.005, epochs=300, batch_size=3)
print(f"SGD result:  β₀={b0_s:.4f}, β₁={b1_s:.4f}")
print(f"OLS result:  β₀={b0_ols:.4f}, β₁={b1_ols:.4f}")

import matplotlib.pyplot as plt
plt.figure(figsize=(8,4))
plt.plot(hist_s, color='orange', linewidth=1.5, label='SGD (batch=3)')
plt.axhline(np.sum((y-(b0_ols+b1_ols*X))**2), color='green',
            linestyle='--', linewidth=1.5, label='OLS minimum SSR')
plt.xlabel('Epoch'); plt.ylabel('SSR')
plt.title('Mini-batch SGD convergence')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
md("""## Key Takeaways

| Method | When to use |
|--------|------------|
| Normal equations | Small/medium n, exact solution needed |
| Batch GD | Medium n, when normal equations too slow |
| Mini-batch SGD | Large n, foundation of deep learning |
| Learning rate | Too large → diverges. Too small → slow. Use adaptive (Adam, RMSProp) |

**Next:** NB16 — Robust regression (handling outliers).
"""),
]

save(nb(cells_11), "NB11_Ridge_L2.ipynb")
save(nb(cells_12), "NB12_Lasso_L1.ipynb")
save(nb(cells_13), "NB13_ElasticNet.ipynb")
save(nb(cells_14), "NB14_Cross_Validation.ipynb")
save(nb(cells_15), "NB15_Gradient_Descent.ipynb")
print("Done — NB11 to NB15 written.")
