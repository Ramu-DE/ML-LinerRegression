# -*- coding: utf-8 -*-
"""Rebuild NB11-NB20 with StatQuest intuition + flow diagrams"""
import nbformat, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks")
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

FLOW_HELPER = """\
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def flow_diagram(steps, title, colors=None, notes=None, figsize=(14, 2.8)):
    n = len(steps)
    default_colors = ['#1565C0','#2E7D32','#E65100','#6A1B9A',
                      '#00695C','#AD1457','#37474F','#4E342E',
                      '#0277BD','#558B2F','#C62828','#F57F17']
    colors = (colors or default_colors)[:n]
    notes  = notes or ['']*n
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(-0.3, n*3.1); ax.set_ylim(-1.2, 2.4); ax.axis('off')
    bw, bh = 2.6, 1.3
    for i,(step,color,note) in enumerate(zip(steps,colors,notes)):
        x = i*3.1
        box = FancyBboxPatch((x,0.2),bw,bh,boxstyle="round,pad=0.12",
                             facecolor=color,edgecolor='white',linewidth=1.5,alpha=0.90)
        ax.add_patch(box)
        ax.text(x+bw/2,0.2+bh/2,step,ha='center',va='center',fontsize=8.5,
                color='white',fontweight='bold',multialignment='center')
        if note:
            ax.text(x+bw/2,0.02,note,ha='center',va='top',fontsize=7,
                    color='#555',style='italic')
        if i < n-1:
            ax.annotate('',xy=(x+bw+0.38,0.2+bh/2),xytext=(x+bw+0.08,0.2+bh/2),
                       arrowprops=dict(arrowstyle='->',color='#444',lw=2.2))
    ax.set_title(title,fontsize=11,fontweight='bold',pad=6,color='#222')
    plt.tight_layout(pad=0.4); plt.show()
"""

# =============================================================================
# NB11 — Ridge (L2)
# =============================================================================
cells_11 = [
md("""# NB11 — Ridge Regression (L2 Regularisation)

> **StatQuest: "Ridge adds a penalty that shrinks large coefficients — preventing them from going crazy just to fit the noise."**

---

## The main ideas:

1. OLS minimises SSR. Ridge minimises: **SSR + lambda * sum(b_j^2)**
2. The lambda * sum(b_j^2) term is the "L2 penalty"
3. Large lambda -> coefficients are forced toward zero -> less overfitting
4. lambda = 0 -> pure OLS. lambda -> infinity -> all slopes = 0
5. Ridge NEVER sets a coefficient exactly to zero (it shrinks, but doesn't eliminate)
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'OLS objective:\\nminimise SSR\\n(no constraint)',
        'Ridge adds\\nL2 penalty:\\nSSR + lambda*sum(b^2)',
        'Larger lambda\\n-> smaller\\ncoefficients',
        'Tune lambda\\nwith\\n5-fold CV',
        'Closed form:\\nb = (XtX + lI)^-1 Xty',
        'Stabilises\\nmulticollinear\\nfeatures',
        'No variable\\nselection\\n(all kept)',
    ],
    title='NB11 Conceptual Flow: Ridge Regression (L2)',
    colors=['#37474F','#1565C0','#2E7D32','#E65100','#6A1B9A','#C62828','#00695C'],
    figsize=(16, 2.8),
)
"""),
md("""## Why L2 stabilises multicollinear models

The OLS normal equations: `(XtX) b = Xty`

When predictors are correlated, XtX is near-singular (almost uninvertible).
Ridge adds `lambda*I` to the diagonal:

```
b_ridge = (XtX + lambda*I)^-1  Xty
```

Adding lambda to the diagonal makes the matrix **always invertible** — no matter how bad the multicollinearity.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge, RidgeCV, LinearRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.datasets import fetch_california_housing

np.random.seed(42)
n = 50
X = np.sort(np.random.uniform(-2, 2, n)).reshape(-1,1)
y = np.sin(X.ravel()*np.pi) + np.random.normal(0, 0.3, n)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0)
X_plot = np.linspace(-2,2,200).reshape(-1,1)

lambdas = [0, 0.01, 1, 100]
fig, axes = plt.subplots(1, 4, figsize=(17, 4))

for ax, lam in zip(axes, lambdas):
    pipe = Pipeline([
        ('poly',  PolynomialFeatures(degree=10, include_bias=False)),
        ('scale', StandardScaler()),
        ('model', Ridge(alpha=lam) if lam > 0 else LinearRegression()),
    ])
    pipe.fit(X_tr, y_tr)
    tr_r2 = pipe.score(X_tr, y_tr)
    te_r2 = pipe.score(X_te, y_te)
    ax.scatter(X, y, s=15, alpha=0.5, color='steelblue')
    ax.plot(X_plot, pipe.predict(X_plot), 'r-', linewidth=2.5)
    label = f'lambda={lam}' if lam > 0 else 'OLS (lambda=0)'
    ax.set_title(f'{label}\\nTrain R^2={tr_r2:.3f}\\nTest  R^2={te_r2:.3f}', fontsize=9)
    ax.set_ylim(-2, 2); ax.grid(alpha=0.3)

plt.suptitle('Ridge: increasing lambda reduces overfitting (smoother curves)', fontsize=12)
plt.tight_layout(); plt.show()
"""),
code("""# Regularisation path: trace how coefficients shrink as lambda increases
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import fetch_california_housing

housing = fetch_california_housing()
X_std   = StandardScaler().fit_transform(housing.data)
y       = housing.target
names   = list(housing.feature_names)

lambdas = np.logspace(-3, 5, 200)
coefs   = np.array([Ridge(alpha=l).fit(X_std, y).coef_ for l in lambdas])

fig, ax = plt.subplots(figsize=(10, 5))
for j, name in enumerate(names):
    ax.semilogx(lambdas, coefs[:, j], linewidth=2, label=name)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_xlabel('lambda (log scale)'); ax.set_ylabel('Coefficient value')
ax.set_title('Ridge regularisation path: coefficients shrink toward 0 but never reach it')
ax.legend(fontsize=8, loc='upper right'); ax.grid(alpha=0.3)
plt.tight_layout(); plt.show()

# Find optimal lambda
from sklearn.linear_model import RidgeCV
rc = RidgeCV(alphas=lambdas, cv=5).fit(X_std, y)
print(f"Optimal lambda (5-fold RidgeCV): {rc.alpha_:.4f}")
print(f"Test R^2 at optimal lambda: {rc.score(X_std, y):.4f}")
"""),
md("""## Key Takeaways

| | OLS | Ridge |
|--|-----|-------|
| Objective | Minimise SSR | Minimise SSR + lambda * sum(b^2) |
| Variable selection | No | No (keeps all, just smaller) |
| Multicollinearity | Unstable SEs | Stabilised |
| Tuning | None | Choose lambda via CV |
| Closed form | Yes | Yes: (XtX + lI)^-1 Xty |
| lambda=0 | OLS | OLS |

**Next: NB12 — Lasso (L1) which actually eliminates variables.**
"""),
]

# =============================================================================
# NB12 — Lasso (L1)
# =============================================================================
cells_12 = [
md("""# NB12 — Lasso Regression (L1 Regularisation)

> **StatQuest: "Lasso has a sharp corner at zero, so some coefficients land exactly on it — those features are dropped."**

---

## The main ideas:

1. Lasso minimises: **SSR + lambda * sum(|b_j|)**
2. The L1 penalty (absolute value) has a **diamond shape** in 2D with corners on the axes
3. The OLS solution often "hits" one of those corners -> coefficient = exactly 0 -> feature eliminated
4. Ridge uses a circle (no corners) -> rarely gets exactly zero
5. Lasso = automatic feature selection
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Many features\\n(some useless)',
        'Lasso adds\\nL1 penalty:\\nSSR + lambda*sum(|b|)',
        'Geometric\\nview: L1 ball\\nhas CORNERS',
        'OLS hits\\ncorner -> b_j=0\\nfeature dropped',
        'Tune lambda\\nwith LassoCV',
        'Only selected\\nfeatures\\nremain',
        'Interpret\\nremaining\\ncoefficients',
    ],
    title='NB12 Conceptual Flow: Lasso Regression (L1) for Feature Selection',
    colors=['#37474F','#C62828','#1565C0','#2E7D32','#E65100','#6A1B9A','#00695C'],
    figsize=(16, 2.8),
)
"""),
md("""## Geometric intuition: why L1 creates sparsity

In 2D, the constraint region for:
- **Ridge (L2):** a circle — smooth, no special points
- **Lasso (L1):** a diamond — 4 corners, each ON an axis (b_j = 0)

The OLS objective (elliptical contours) moves toward the minimum until it first touches the constraint region.
**A circle has no corners — it rarely hits an axis.**
**A diamond has corners ON the axes — the first contact is often at a corner.**
Corner contact = one coefficient exactly zero = that feature eliminated.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

theta = np.linspace(0, 2*np.pi, 500)
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
true_ols = np.array([1.4, 0.9])

for ax, title, is_lasso in zip(axes,
    ['Ridge (L2): circle, no corners', 'Lasso (L1): diamond, corners on axes'],
    [False, True]):

    ax.set_xlim(-2.2, 2.2); ax.set_ylim(-2.2, 2.2); ax.set_aspect('equal')
    ax.axhline(0, color='k', linewidth=0.5); ax.axvline(0, color='k', linewidth=0.5)
    ax.set_xlabel('b1'); ax.set_ylabel('b2')

    if is_lasso:
        diamond = np.array([[1,0],[-1,0],[0,-1],[0,1],[1,0]])
        ax.fill(diamond[:,0], diamond[:,1], alpha=0.2, color='steelblue')
        ax.plot(diamond[:,0], diamond[:,1], 'b-', linewidth=2.5, label='L1 ball')
        constrained = np.array([1, 0])
        ax.plot(*constrained, 'go', markersize=12, zorder=5, label='Lasso solution (b2=0!)')
    else:
        ax.fill(np.cos(theta), np.sin(theta), alpha=0.2, color='steelblue')
        ax.plot(np.cos(theta), np.sin(theta), 'b-', linewidth=2.5, label='L2 ball')
        ax.plot(0.77, 0.64, 'go', markersize=12, zorder=5, label='Ridge solution')

    for r in [0.5, 0.9, 1.4, 2.0]:
        cx = true_ols[0] + r*np.cos(theta)
        cy = true_ols[1] + 0.6*r*np.sin(theta)
        ax.plot(cx, cy, 'r-', alpha=0.35, linewidth=1)

    ax.plot(*true_ols, 'r*', markersize=16, label='OLS solution (unconstrained)')
    ax.set_title(title); ax.legend(fontsize=8); ax.grid(alpha=0.3)

plt.suptitle('Why Lasso performs variable selection: the diamond has corners on the axes',
             fontsize=11, fontweight='bold')
plt.tight_layout(); plt.show()
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso, LassoCV
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import fetch_california_housing

housing = fetch_california_housing()
X_std   = StandardScaler().fit_transform(housing.data)
y       = housing.target
names   = list(housing.feature_names)

# Regularisation path
lambdas = np.logspace(-4, 1, 200)
coefs   = np.array([Lasso(alpha=l, max_iter=10000).fit(X_std, y).coef_
                    for l in lambdas])

fig, ax = plt.subplots(figsize=(10, 5))
for j, name in enumerate(names):
    ax.semilogx(lambdas, coefs[:, j], linewidth=2, label=name)
ax.axhline(0, color='black', linewidth=1.5)
ax.set_xlabel('lambda (log scale)'); ax.set_ylabel('Coefficient value')
ax.set_title('Lasso path: coefficients HIT zero (hard cutoff) as lambda increases\\n'
             '(Compare Ridge: they approach but never reach zero)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
plt.tight_layout(); plt.show()

# Optimal lambda
lasso_cv = LassoCV(cv=5, max_iter=20000).fit(X_std, y)
print(f"Optimal lambda: {lasso_cv.alpha_:.6f}")
print(f"\\nSelected features at optimal lambda:")
for name, coef in zip(names, lasso_cv.coef_):
    status = 'SELECTED' if coef != 0 else 'zeroed out'
    bar    = '#' * int(abs(coef)*20) if coef != 0 else ''
    print(f"  {name:<15} {coef:>8.4f}  {status}  {bar}")
print(f"\\n{sum(lasso_cv.coef_ != 0)}/{len(names)} features kept")
"""),
md("""## Ridge vs Lasso at a glance

| | Ridge | Lasso |
|--|-------|-------|
| Penalty | sum(b^2) | sum(|b|) |
| Shape of constraint | Circle (smooth) | Diamond (corners) |
| Variable selection | No — all kept | Yes — some b_j = 0 |
| Correlated features | Shares credit equally | Picks one, drops others |
| When to use | All features matter | Many features, few relevant |
| Interpretability | Moderate | High (sparse model) |

**Next: NB13 — ElasticNet combines both, getting the best of each.**
"""),
]

# =============================================================================
# NB13 — ElasticNet
# =============================================================================
cells_13 = [
md("""# NB13 — ElasticNet: Best of Ridge and Lasso

> **StatQuest: "ElasticNet mixes L1 and L2 — you get sparsity like Lasso AND stability like Ridge."**

Minimises: **SSR + alpha * [ l1_ratio * sum(|b|) + (1-l1_ratio) * sum(b^2)/2 ]**

- `l1_ratio = 0` -> Ridge
- `l1_ratio = 1` -> Lasso
- `0 < l1_ratio < 1` -> ElasticNet

ElasticNet handles correlated features better than Lasso:
Lasso picks ONE from a group; ElasticNet can keep several (with smaller coefficients).
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Many correlated\\nfeatures\\n(Lasso unstable)',
        'ElasticNet:\\nL1 + L2\\npenalty mix',
        'l1_ratio\\ncontrols\\nL1/L2 balance',
        'alpha controls\\noverall\\nshrinkage',
        'Tune both\\nwith\\nElasticNetCV',
        'Result:\\nSparse + stable\\ncoefficients',
    ],
    title='NB13 Conceptual Flow: ElasticNet (L1 + L2 Combined)',
    colors=['#C62828','#1565C0','#2E7D32','#E65100','#6A1B9A','#00695C'],
)
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge, Lasso, ElasticNet, ElasticNetCV
from sklearn.datasets import make_regression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

# Dataset with many correlated features
X, y, true_coef = make_regression(n_samples=200, n_features=20,
                                   n_informative=5, noise=10,
                                   coef=True, random_state=0)
X_std = StandardScaler().fit_transform(X)

models = {
    'Ridge (l1=0)':         Ridge(alpha=1),
    'Lasso (l1=1)':         Lasso(alpha=0.1),
    'ElasticNet (l1=0.5)':  ElasticNet(alpha=0.1, l1_ratio=0.5),
}

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, (name, m) in zip(axes, models.items()):
    m.fit(X_std, y)
    cv_r2 = cross_val_score(m.__class__(**m.get_params()), X_std, y, cv=5).mean()
    nonzero = np.sum(m.coef_ != 0)
    colors = ['#1565C0' if c != 0 else '#BDBDBD' for c in m.coef_]
    ax.bar(range(20), m.coef_, color=colors)
    ax.axhline(0, color='black', linewidth=0.7)
    ax.set_title(f'{name}\\n{nonzero}/20 non-zero  CV R^2={cv_r2:.3f}', fontsize=9)
    ax.set_xlabel('Feature index'); ax.grid(alpha=0.3, axis='y')

plt.suptitle('ElasticNet: Lasso-like sparsity + Ridge-like stability on correlated features',
             fontsize=11)
plt.tight_layout(); plt.show()
"""),
code("""# Tune both alpha and l1_ratio simultaneously
from sklearn.linear_model import ElasticNetCV
import numpy as np

en_cv = ElasticNetCV(
    l1_ratio=[0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 1.0],
    n_alphas=100, cv=5, max_iter=10000
).fit(X_std, y)

print(f"Optimal alpha   : {en_cv.alpha_:.6f}")
print(f"Optimal l1_ratio: {en_cv.l1_ratio_:.2f}")
print(f"Non-zero coefs  : {np.sum(en_cv.coef_ != 0)}/{X.shape[1]}")
print(f"R^2 (train)     : {en_cv.score(X_std, y):.4f}")
print()
print("Rule of thumb: l1_ratio in [0.5, 0.9] works well for most problems")
"""),
md("""## When to choose which regulariser

| Situation | Best choice |
|-----------|------------|
| All features probably matter | Ridge |
| Few features out of many matter | Lasso |
| Many correlated features, want some selection | ElasticNet |
| You don't know | Try all three with cross-validation |

**Next: NB14 — Cross-validation and model selection.**
"""),
]

# =============================================================================
# NB14 — Cross-Validation
# =============================================================================
cells_14 = [
md("""# NB14 — Cross-Validation and Model Selection

> **StatQuest: "Never use the same data to both train and evaluate your model."**

---

## The main ideas:

1. Train R^2 always improves with complexity — useless for model selection
2. Train/test split: better, but wastes data and has high variance
3. **k-fold cross-validation:** split data into k folds, train on k-1, test on 1, rotate — use all data for both
4. **Learning curves:** diagnose whether you have a bias or variance problem
5. **Nested CV:** unbiased performance estimate when ALSO tuning hyperparameters
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Split data\\ninto k=5\\nequal folds',
        'Fold 1 = test\\nFolds 2-5 = train\\nRecord test R^2',
        'Fold 2 = test\\nFolds 1,3-5 = train\\nRecord test R^2',
        '...repeat 5x\\n(each fold is\\ntest exactly once)',
        'Average the\\n5 test R^2s\\n= CV score',
        'Pick model\\nwith best\\nCV score',
        'Final fit\\non ALL data\\nwith best model',
    ],
    title='NB14 Conceptual Flow: 5-Fold Cross-Validation',
    colors=['#37474F','#1565C0','#2E7D32','#E65100','#6A1B9A','#C62828','#00695C'],
    figsize=(16, 2.8),
)
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline

np.random.seed(42)
n = 100
X = np.sort(np.random.uniform(-3, 3, n)).reshape(-1,1)
y = np.sin(X.ravel()) + np.random.normal(0, 0.4, n)

degrees = range(1, 13)
train_r2, cv_r2 = [], []

for deg in degrees:
    pipe = Pipeline([('poly', PolynomialFeatures(deg)), ('ols', LinearRegression())])
    # Train R^2
    pipe.fit(X, y)
    train_r2.append(pipe.score(X, y))
    # 5-fold CV R^2
    scores = cross_val_score(pipe, X, y, cv=5, scoring='r2')
    cv_r2.append(scores.mean())

best_deg = degrees[np.argmax(cv_r2)]
plt.figure(figsize=(9, 4))
plt.plot(degrees, train_r2, 'o-', color='crimson', linewidth=2, label='Train R^2')
plt.plot(degrees, cv_r2,   's-', color='steelblue', linewidth=2, label='5-fold CV R^2')
plt.axvline(best_deg, color='gold', linewidth=2, linestyle='--',
            label=f'Best degree = {best_deg}')
plt.xlabel('Polynomial degree'); plt.ylabel('R^2')
plt.title('Cross-validation selects the right model; train R^2 always rises (misleading)')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
print(f"Best degree by CV: {best_deg}")
print(f"Train R^2 at degree {best_deg}: {train_r2[best_deg-1]:.4f}")
print(f"CV    R^2 at degree {best_deg}: {cv_r2[best_deg-1]:.4f}")
"""),
code("""# Learning curves — diagnose bias vs variance
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

models = {
    'Degree 1 (high bias)':    Pipeline([('p', PolynomialFeatures(1)), ('m', LinearRegression())]),
    'Degree 3 (good fit)':     Pipeline([('p', PolynomialFeatures(3)), ('m', LinearRegression())]),
    'Degree 10 (high variance)':Pipeline([('p', PolynomialFeatures(10)),('m', LinearRegression())]),
}

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
for ax, (name, m) in zip(axes, models.items()):
    sizes, tr_sc, te_sc = learning_curve(
        m, X, y, cv=5, scoring='r2',
        train_sizes=np.linspace(0.1, 1.0, 10))
    tr_mean = tr_sc.mean(axis=1); tr_std = tr_sc.std(axis=1)
    te_mean = te_sc.mean(axis=1); te_std = te_sc.std(axis=1)

    ax.fill_between(sizes, tr_mean-tr_std, tr_mean+tr_std, alpha=0.15, color='crimson')
    ax.fill_between(sizes, te_mean-te_std, te_mean+te_std, alpha=0.15, color='steelblue')
    ax.plot(sizes, tr_mean, 'o-', color='crimson',   linewidth=2, label='Train')
    ax.plot(sizes, te_mean, 's-', color='steelblue', linewidth=2, label='CV')
    ax.set_title(name, fontsize=9); ax.set_xlabel('Training size')
    ax.set_ylabel('R^2'); ax.legend(fontsize=8); ax.grid(alpha=0.3)

plt.suptitle('Learning curves — how to read them:', fontsize=11)
plt.tight_layout(); plt.show()
print("High bias: both curves low and converge (add features or complexity)")
print("High variance: big gap between train and CV curves (add more data or regularise)")
"""),
md("""## Key Takeaways

| Technique | Use for | Watch out for |
|-----------|---------|--------------|
| Train R^2 alone | Nothing | Always misleading for model selection |
| k-fold CV | Model selection, hyperparameter tuning | Still can overfit if you tune on CV score |
| Nested CV | Unbiased performance estimate | More expensive |
| Learning curve | Diagnosing bias vs variance | Need enough range of sizes |

**Next: NB15 — Gradient Descent: the iterative alternative to normal equations.**
"""),
]

# =============================================================================
# NB15 — Gradient Descent
# =============================================================================
cells_15 = [
md("""# NB15 — Gradient Descent from Scratch

> **StatQuest: "Instead of solving the equation exactly, take small steps downhill until you reach the bottom of the bowl."**

---

## The main ideas:

1. Normal equations solve (XtX)b = Xty in ONE step — but for massive data, inverting XtX is too slow
2. Gradient Descent takes many small steps in the **downhill direction** of the SSR surface
3. Step size = **learning rate** (alpha) — too large -> overshoots; too small -> slow
4. Mini-batch SGD: compute gradient on a small batch -> faster, foundation of deep learning
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Initialise:\\nb0=0, b1=0',
        'Compute SSR\\nfor current\\nb0, b1',
        'Compute\\ngradients:\\ndSSR/db0, dSSR/db1',
        'Update:\\nb0 -= lr * grad_b0\\nb1 -= lr * grad_b1',
        'Convergence?\\nSSR not\\ndecreasing?',
        'Return\\nfinal b0, b1\\n(OLS solution)',
    ],
    title='NB15 Conceptual Flow: Gradient Descent for OLS',
    colors=['#37474F','#1565C0','#2E7D32','#E65100','#6A1B9A','#C62828'],
)
"""),
md("""## The gradient of SSR

```
SSR = sum(y_i - b0 - b1*x_i)^2

d(SSR)/d(b0) = -2 * sum(y_i - y_hat_i)           <- gradient w.r.t. intercept
d(SSR)/d(b1) = -2 * sum(x_i * (y_i - y_hat_i))   <- gradient w.r.t. slope

Update rule (gradient DESCENT = move OPPOSITE to gradient):
  b0 <- b0 - lr * d(SSR)/d(b0) / n
  b1 <- b1 - lr * d(SSR)/d(b1) / n
```

**Intuition:** if the gradient is positive (SSR increases as b0 increases), we decrease b0.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

X = np.array([1.,2.,3.,4.,5.,6.,7.,8.,9.,10.])
y = np.array([40.,45.,50.,55.,65.,70.,75.,85.,90.,95.])
n = len(X)

def gradient_descent(X, y, lr=0.001, epochs=5000):
    b0, b1 = 0.0, 0.0
    history = {'ssr':[], 'b0':[], 'b1':[]}
    for _ in range(epochs):
        y_hat = b0 + b1*X
        resid = y - y_hat
        grad_b0 = -2*resid.mean()
        grad_b1 = -2*(X*resid).mean()
        b0 -= lr * grad_b0
        b1 -= lr * grad_b1
        history['ssr'].append(np.sum(resid**2))
        history['b0'].append(b0); history['b1'].append(b1)
    return b0, b1, history

b0_gd, b1_gd, hist = gradient_descent(X, y, lr=0.001, epochs=6000)

# OLS exact solution
xbar, ybar = X.mean(), y.mean()
b1_ols = np.sum((X-xbar)*(y-ybar))/np.sum((X-xbar)**2)
b0_ols = ybar - b1_ols*xbar

print(f"GD result:  b0={b0_gd:.5f}  b1={b1_gd:.5f}")
print(f"OLS exact:  b0={b0_ols:.5f}  b1={b1_ols:.5f}")
print(f"Close?      {np.allclose([b0_gd,b1_gd],[b0_ols,b1_ols],atol=0.01)}")

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].semilogy(hist['ssr'], color='steelblue', linewidth=1.5)
axes[0].set_xlabel('Epoch'); axes[0].set_ylabel('SSR (log scale)')
axes[0].set_title('SSR decreasing each epoch — converging to minimum')
axes[0].grid(alpha=0.3)

axes[1].plot(hist['b0'][::50], hist['b1'][::50], 'o-', color='steelblue',
             markersize=4, linewidth=1, label='GD path (every 50th step)')
axes[1].plot(b0_ols, b1_ols, 'r*', markersize=16, label='OLS minimum')
axes[1].set_xlabel('b0'); axes[1].set_ylabel('b1')
axes[1].set_title('Path of GD through (b0, b1) space')
axes[1].legend(); axes[1].grid(alpha=0.3)
plt.tight_layout(); plt.show()
"""),
code("""# Effect of learning rate
import numpy as np, matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, lr, label in zip(axes,
    [0.0001, 0.001, 0.003],
    ['Too slow (lr=0.0001)', 'Good (lr=0.001)', 'Diverges (lr=0.003)']):
    b0, b1 = 0., 0.
    ssrs = []
    for _ in range(3000):
        yhat = b0 + b1*X
        res  = y - yhat
        b0  -= lr * (-2*res.mean())
        b1  -= lr * (-2*(X*res).mean())
        ssrs.append(np.sum(res**2))
    ax.semilogy(ssrs, color='steelblue', linewidth=1.5)
    ax.set_title(label); ax.set_xlabel('Epoch'); ax.set_ylabel('SSR')
    ax.grid(alpha=0.3)

plt.suptitle('Learning rate: too small = slow, just right = converges, too large = diverges',
             fontsize=11)
plt.tight_layout(); plt.show()
"""),
md("""## Normal Equations vs Gradient Descent

| | Normal Equations | Gradient Descent |
|--|-----------------|-----------------|
| Solution | Exact, one step | Approximate, many steps |
| Time | O(n * k^2) + O(k^3) | O(n * k * epochs) |
| When wins | Small/medium k | Very large n or k |
| Foundation of | Classical statistics | Deep learning |
| Requires tuning | No | Yes — learning rate |

**Next: NB16 — Robust regression when your data has outliers.**
"""),
]

# =============================================================================
# NB16 — Robust Regression
# =============================================================================
cells_16 = [
md("""# NB16 — Robust Regression: Handling Outliers

> **StatQuest: "OLS squares residuals — so a single huge outlier can pull the entire line far from the truth."**

---

## The main ideas:

1. OLS squares residuals: a point 10x away from the line gets 100x the penalty
2. That one outlier can completely dominate the OLS fit
3. Robust methods use losses that grow SLOWER than quadratic for large errors
4. **Huber:** quadratic for small errors, linear for large ones
5. **RANSAC:** ignore outliers by finding consensus among majority inliers
6. **Theil-Sen:** use the MEDIAN slope instead of the mean slope
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Data with\\noutliers',
        'OLS: squares\\nall residuals\\n(outlier dominates)',
        'Huber: quadratic\\nfor small e,\\nlinear for large',
        'RANSAC:\\nrandom consensus\\ncount inliers',
        'Theil-Sen:\\nmedian of all\\npairwise slopes',
        'Compare all\\nthree vs\\nOLS',
        'Choose method\\nbased on\\ncontamination %',
    ],
    title='NB16 Conceptual Flow: Robust Regression Methods',
    colors=['#C62828','#37474F','#1565C0','#2E7D32','#E65100','#6A1B9A','#00695C'],
    figsize=(16, 2.8),
)
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import (LinearRegression, HuberRegressor,
                                  RANSACRegressor, TheilSenRegressor)

np.random.seed(42)
n = 60
X_clean = np.linspace(0, 10, n).reshape(-1,1)
y_clean = 2*X_clean.ravel() + 3 + np.random.normal(0, 1.5, n)

# Add 8 gross outliers
X_out = np.array([[1],[3],[5],[9],[9.5],[2],[8],[7]])
y_out = np.array([22, 26, 28, -5, -8, 24, -3, -4])
X_all = np.vstack([X_clean, X_out])
y_all = np.concatenate([y_clean, y_out])

models = {
    'OLS':       LinearRegression(),
    'Huber':     HuberRegressor(epsilon=1.35),
    'RANSAC':    RANSACRegressor(random_state=42),
    'Theil-Sen': TheilSenRegressor(random_state=42),
}
colors_m = ['red','green','orange','purple']

X_plot = np.linspace(-1, 11, 200).reshape(-1,1)
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(X_clean, y_clean, s=25, color='steelblue', alpha=0.7, zorder=3, label='Clean data')
ax.scatter(X_out, y_out, s=100, color='black', marker='x', linewidths=2.5, zorder=4, label='Outliers')

for (name, m), col in zip(models.items(), colors_m):
    m.fit(X_all, y_all)
    if hasattr(m, 'estimator_'):
        pred = m.estimator_.predict(X_plot)
    else:
        pred = m.predict(X_plot)
    ax.plot(X_plot, pred, color=col, linewidth=2.5, label=name)

ax.set_xlabel('X'); ax.set_ylabel('y')
ax.set_title('Robust methods resist outliers; OLS is pulled away from the truth')
ax.legend(); ax.grid(alpha=0.3); plt.tight_layout(); plt.show()

print("True slope = 2.0")
for (name, m), col in zip(models.items(), colors_m):
    slope = m.estimator_.coef_[0] if hasattr(m,'estimator_') else m.coef_[0]
    print(f"  {name:<12}: estimated slope = {slope:.4f}")
"""),
md("""## Huber loss explained

```
L_Huber(r) =  r^2 / 2              if |r| <= epsilon
              epsilon * (|r| - epsilon/2)   if |r| > epsilon
```

- For small residuals (|r| < epsilon): behaves exactly like OLS (quadratic)
- For large residuals (outliers): switches to LINEAR growth — outlier is penalised linearly, not quadratically
- epsilon = 1.35 gives 95% efficiency on normally distributed data

**Theil-Sen:** slope = median of ALL pairwise slopes between every pair of points.
Can handle up to 29.3% contamination.

**RANSAC:** randomly sample minimal subsets, fit, count inliers, keep best model.
"""),
md("""## When to use which

| Method | Breakdown point | Speed | Use when |
|--------|----------------|-------|----------|
| OLS | 0% (one outlier can ruin it) | Fastest | Data is clean |
| Huber | ~20% | Fast | Moderate contamination |
| RANSAC | >30% | Moderate | Known to have gross outliers |
| Theil-Sen | 29.3% | Slow O(n^2) | Small n, high contamination |

**Next: NB17 — Quantile regression (model the median, not the mean).**
"""),
]

# =============================================================================
# NB17 — Quantile Regression
# =============================================================================
cells_17 = [
md("""# NB17 — Quantile Regression

> **StatQuest: "OLS models the average. Quantile regression models the median — or any percentile."**

---

## The main ideas:

1. OLS models E[y|x] — the **conditional mean**
2. Quantile regression models Q_tau[y|x] — the conditional **tau-th quantile**
3. tau=0.5 -> median (robust to outliers); tau=0.9 -> 90th percentile
4. Uses **pinball loss** (asymmetric): penalises over-prediction more or less depending on tau
5. Gives you natural **prediction intervals** without assuming normality
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Choose quantile\\ntau (e.g. 0.5\\nfor median)',
        'Minimise\\npinball loss:\\ntau*max(r,0)\\n+ (1-tau)*max(-r,0)',
        'Different tau\\ngives different\\nregression lines',
        'tau=0.1 and\\ntau=0.9 give\\nprediction band',
        'Works with\\nheteroscedastic\\ndata',
        'No normality\\nassumption\\nneeded',
    ],
    title='NB17 Conceptual Flow: Quantile Regression',
    colors=['#37474F','#1565C0','#2E7D32','#E65100','#6A1B9A','#C62828'],
)
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import QuantileRegressor

np.random.seed(0)
n = 200
X = np.sort(np.random.uniform(0, 10, n))
y = 2*X + 5 + np.random.normal(0, 0.5*X + 0.5, n)   # heteroscedastic

X_2d   = X.reshape(-1,1)
X_plot = np.linspace(0, 10, 200).reshape(-1,1)

quantiles = [0.1, 0.25, 0.5, 0.75, 0.9]
line_colors = ['#1565C0','#4CAF50','crimson','#FF9800','#9C27B0']

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: all quantile lines
ax = axes[0]
ax.scatter(X, y, s=12, alpha=0.3, color='lightgray')
for q, col in zip(quantiles, line_colors):
    qr = QuantileRegressor(quantile=q, alpha=0, solver='highs').fit(X_2d, y)
    ax.plot(X_plot, qr.predict(X_plot), color=col, linewidth=2.5, label=f'Q={q}')
ax.set_xlabel('X'); ax.set_ylabel('y')
ax.set_title('Multiple quantile lines\\n(notice they fan out = heteroscedastic data)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Right: prediction interval
qr_lo = QuantileRegressor(quantile=0.1, alpha=0, solver='highs').fit(X_2d, y)
qr_md = QuantileRegressor(quantile=0.5, alpha=0, solver='highs').fit(X_2d, y)
qr_hi = QuantileRegressor(quantile=0.9, alpha=0, solver='highs').fit(X_2d, y)

ax = axes[1]
ax.scatter(X, y, s=12, alpha=0.3, color='lightgray')
ax.fill_between(X_plot.ravel(), qr_lo.predict(X_plot), qr_hi.predict(X_plot),
                alpha=0.25, color='orange', label='80% prediction band (Q0.1-Q0.9)')
ax.plot(X_plot, qr_md.predict(X_plot), 'r-', linewidth=2.5, label='Median (Q0.5)')
ax.set_xlabel('X'); ax.set_ylabel('y')
ax.set_title('Prediction band from Q0.1 and Q0.9\\n(no normality assumption!)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

plt.suptitle('Quantile regression captures the full conditional distribution of y',
             fontsize=11)
plt.tight_layout(); plt.show()
"""),
md("""## When to use Quantile Regression

| Scenario | Why quantile regression helps |
|---------|------------------------------|
| Skewed outcome (e.g. income) | Median more meaningful than mean |
| Heteroscedastic data | Captures how spread changes with x |
| Outliers in y | Median regression is robust |
| Need prediction intervals | Q0.1 and Q0.9 directly give 80% band |
| Care about extremes | Model Q0.95 directly for risk/SLA purposes |

**Next: NB18 — Bayesian linear regression (get a full distribution over coefficients).**
"""),
]

# =============================================================================
# NB18 — Bayesian Regression
# =============================================================================
cells_18 = [
md("""# NB18 — Bayesian Linear Regression

> **StatQuest: "Instead of asking 'what is the slope?', Bayesian regression asks 'what distribution of slopes is consistent with the data?'"**

---

## The main ideas:

1. Frequentist: b1 is a fixed (unknown) constant — we estimate it
2. Bayesian: b1 is a **random variable** — we assign a prior and update with data
3. **Prior** = what we believe before seeing data
4. **Likelihood** = probability of data given parameters
5. **Posterior** = prior updated by data (via Bayes' theorem)
6. Output: not a single b1, but a **distribution** over b1 — captures uncertainty naturally
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Choose prior:\\nb ~ N(mu_0, Sigma_0)\\n(prior belief)',
        'Observe data\\n(x, y)',
        'Compute\\nposterior:\\nGaussian x Gaussian',
        'Posterior:\\nb | y, X ~ N(mu_n, Sigma_n)\\nanalytic formula',
        'Sample lines\\nfrom posterior\\n(uncertainty)',
        'Predictive\\ndistribution:\\nincludes noise',
        'More data ->\\nnarrower\\nposterior',
    ],
    title='NB18 Conceptual Flow: Bayesian Linear Regression',
    colors=['#1565C0','#2E7D32','#E65100','#6A1B9A','#C62828','#00695C','#AD1457'],
    figsize=(16, 2.8),
)
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
true_b0, true_b1, sigma = 3.0, 2.0, 2.0
n_total = 40
X_all = np.random.uniform(0, 5, n_total)
y_all = true_b0 + true_b1*X_all + np.random.normal(0, sigma, n_total)

def bayesian_lr_posterior(X, y, sigma2_noise, mu_0, Sigma_0_inv):
    \"\"\"Conjugate Gaussian-Gaussian posterior for linear regression.\"\"\"
    X_d        = np.column_stack([np.ones(len(X)), X])
    Sigma_n_inv = Sigma_0_inv + X_d.T @ X_d / sigma2_noise
    Sigma_n     = np.linalg.inv(Sigma_n_inv)
    mu_n        = Sigma_n @ (Sigma_0_inv @ mu_0 + X_d.T @ y / sigma2_noise)
    return mu_n, Sigma_n

mu_0        = np.array([0., 0.])
Sigma_0_inv = np.eye(2) / 10.0   # weakly informative prior: variance = 10

X_plot = np.linspace(-0.5, 5.5, 200)
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for ax, n_obs in zip(axes, [3, 10, 40]):
    X_sub  = X_all[:n_obs]; y_sub = y_all[:n_obs]
    mu_n, Sigma_n = bayesian_lr_posterior(X_sub, y_sub, sigma**2, mu_0, Sigma_0_inv)

    # Draw 60 lines from the posterior
    samples = np.random.multivariate_normal(mu_n, Sigma_n, 60)
    ax.scatter(X_sub, y_sub, color='steelblue', s=40, zorder=3, label='Data')
    for s in samples:
        ax.plot(X_plot, s[0]+s[1]*X_plot, 'r-', alpha=0.07, linewidth=1)
    ax.plot(X_plot, mu_n[0]+mu_n[1]*X_plot, 'k-', linewidth=2.5, label='Posterior mean')
    ax.plot(X_plot, true_b0+true_b1*X_plot, 'g--', linewidth=1.5, label='True line')
    ax.set_title(f'n = {n_obs} observations\\nb1 mean = {mu_n[1]:.2f}  std = {Sigma_n[1,1]**0.5:.3f}')
    ax.legend(fontsize=7); ax.grid(alpha=0.3)
    ax.set_xlabel('X'); ax.set_ylabel('y')

plt.suptitle('Bayesian regression: each red line = one plausible fit.\\n'
             'More data -> narrower posterior -> less uncertainty', fontsize=11)
plt.tight_layout(); plt.show()
"""),
md("""## Connection to Ridge regression

With a Gaussian prior `b ~ N(0, I/lambda)`:

```
Posterior MAP estimate  =  argmax p(b | y, X)
                        =  argmin  SSR + lambda * sum(b_j^2)
                        =  Ridge regression!
```

**Ridge is Bayesian MAP with a Gaussian prior.**
The lambda in Ridge = 1/prior_variance in Bayesian language.
"""),
code("""# Show that Bayesian MAP = Ridge with matching lambda
import numpy as np
from sklearn.linear_model import Ridge

np.random.seed(1)
n = 50
X_r = np.random.randn(n, 3)
y_r = 2*X_r[:,0] - X_r[:,1] + np.random.normal(0, 1, n)

lam = 1.0   # Ridge lambda
prior_var = 1/lam  # Bayesian prior variance

X_d   = np.column_stack([np.ones(n), X_r])
Sigma_0_inv = np.eye(4) / prior_var
Sigma_0_inv[0,0] = 0  # don't penalise intercept
mu_0  = np.zeros(4)

mu_n, Sigma_n = bayesian_lr_posterior(X_r, y_r, sigma2_noise=1.0,
                                       mu_0=mu_0, Sigma_0_inv=Sigma_0_inv)

ridge = Ridge(alpha=lam).fit(X_r, y_r)
print("Bayesian MAP b1,b2,b3:", np.round(mu_n[1:], 5))
print("Ridge        b1,b2,b3:", np.round(ridge.coef_, 5))
print("Match:", np.allclose(mu_n[1:], ridge.coef_, atol=0.01))
print("\\nRidge = Bayesian MAP with a Gaussian prior (variance = 1/lambda)")
"""),
md("""## Key Takeaways

| | Frequentist OLS | Bayesian |
|--|----------------|---------|
| Output | Point estimate b_hat | Full posterior distribution |
| Uncertainty | From t-distribution (large n) | Directly from posterior |
| Prior knowledge | Not used | Incorporated naturally |
| Small n | Can give wide CI | Prior regularises |
| Equivalent to | OLS | Ridge (with Gaussian prior, MAP) |

**Next: NB19 — applying linear regression to time-series data.**
"""),
]

# =============================================================================
# NB19 — Time Series
# =============================================================================
cells_19 = [
md("""# NB19 — Linear Regression for Time Series

> **StatQuest: "Time-series data has structure — trend, seasonality, momentum. Linear regression can capture all three if you engineer the right features."**

---

## The main ideas:

1. Standard OLS assumes independence — time series violates this (autocorrelation)
2. Feature engineering turns time series structure into regression features:
   - **Trend:** add `t` (index) as a numeric feature
   - **Seasonality:** add `sin(2*pi*t/period)` and `cos(2*pi*t/period)` — Fourier features
   - **Momentum/AR:** add `y_{t-1}, y_{t-2}, ...` as lag features
3. Check residual ACF to see if structure remains unexplained
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Plot time\\nseries\\n(visualise)',
        'Detect trend:\\nupward/downward\\nslope',
        'Detect\\nseasonality:\\nannual/weekly',
        'Detect\\nautocorrelation:\\nACF/PACF plot',
        'Build features:\\nt, sin/cos,\\nlag_1...lag_k',
        'Fit OLS\\non features',
        'Check residual\\nACF: is\\nstructure gone?',
    ],
    title='NB19 Conceptual Flow: Linear Regression for Time Series',
    colors=['#37474F','#1565C0','#2E7D32','#E65100','#6A1B9A','#C62828','#00695C'],
    figsize=(16, 2.8),
)
"""),
code("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(0)
n    = 120   # 10 years of monthly data
t    = np.arange(n)
trend    = 0.3*t
seasonal = 5*np.sin(2*np.pi*t/12)
noise    = np.random.normal(0, 1.5, n)
y = 10 + trend + seasonal + noise

dates = pd.date_range('2014-01', periods=n, freq='ME')

fig, axes = plt.subplots(3, 1, figsize=(12, 8))

axes[0].plot(dates, y, linewidth=1.5, color='steelblue')
axes[0].set_title('Raw time series = trend + seasonality + noise'); axes[0].grid(alpha=0.3)

axes[1].plot(dates, trend + 10, color='crimson', linewidth=2, label='Trend component')
axes[1].plot(dates, seasonal,   color='green',   linewidth=2, label='Seasonal component')
axes[1].legend(); axes[1].set_title('Components'); axes[1].grid(alpha=0.3)

import statsmodels.api as sm
acf_vals = [np.corrcoef(y[:-lag], y[lag:])[0,1] for lag in range(1,25)]
axes[2].bar(range(1,25), acf_vals, color='steelblue')
axes[2].axhline(1.96/n**0.5,  color='blue', linestyle='--', linewidth=1, label='95% CI')
axes[2].axhline(-1.96/n**0.5, color='blue', linestyle='--', linewidth=1)
axes[2].axhline(0, color='black', linewidth=0.5)
axes[2].set_title('ACF of raw series (lag-12 spike = annual seasonality)')
axes[2].set_xlabel('Lag (months)'); axes[2].legend(); axes[2].grid(alpha=0.3)

plt.tight_layout(); plt.show()
"""),
code("""import numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def make_features(t, n_fourier=2, period=12, lags=[1,2,3]):
    df = pd.DataFrame({'t': t.astype(float)})
    for k in range(1, n_fourier+1):
        df[f'sin_{k}'] = np.sin(2*np.pi*k*t/period)
        df[f'cos_{k}'] = np.cos(2*np.pi*k*t/period)
    if lags:
        df['y'] = y   # temporary for lagging
        for lag in lags:
            df[f'lag_{lag}'] = df['y'].shift(lag)
        df = df.drop(columns='y').dropna()
    return df

# Model 1: trend + Fourier only
X_tf = make_features(t, n_fourier=2, lags=[])
m1   = LinearRegression().fit(X_tf, y)
y_hat1 = m1.predict(X_tf)
print(f"Trend+Fourier     R^2 = {r2_score(y, y_hat1):.4f}")

# Model 2: trend + Fourier + lags
X_tfl = make_features(t, n_fourier=2, lags=[1,2,3])
y_lag = y[len(y)-len(X_tfl):]
m2    = LinearRegression().fit(X_tfl, y_lag)
y_hat2 = m2.predict(X_tfl)
print(f"Trend+Fourier+Lag R^2 = {r2_score(y_lag, y_hat2):.4f}")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(dates, y, color='steelblue', linewidth=1.5, alpha=0.7, label='Actual')
ax.plot(dates, y_hat1, 'r-', linewidth=2, label=f'Trend+Fourier')
ax.plot(dates[len(y)-len(y_hat2):], y_hat2, 'g-', linewidth=2, label=f'Trend+Fourier+Lags')
ax.legend(); ax.grid(alpha=0.3)
ax.set_title('Linear regression captures trend and seasonality well')
plt.tight_layout(); plt.show()
"""),
md("""## Key Takeaways

| Feature type | Captures | Formula |
|-------------|---------|---------|
| t (index) | Linear trend | t = 0, 1, 2, ... |
| sin/cos | Fixed-period seasonality | sin(2*pi*k*t/period) |
| Lag y_{t-k} | Autocorrelation/momentum | y value k steps ago |
| Residual ACF | Unexplained structure | Should be within CI bands |

**Caution:** with lag features, observations are NOT independent -> t-tests technically invalid.
Use this for forecasting, not causal inference.

**Next: NB20 — Sklearn Pipelines: the production-ready workflow.**
"""),
]

# =============================================================================
# NB20 — Pipelines
# =============================================================================
cells_20 = [
md("""# NB20 — Sklearn Pipelines: Production-Ready Workflow

> **StatQuest: "All your preprocessing steps must be INSIDE the pipeline — otherwise you're cheating (data leakage)."**

---

## The main ideas:

1. **Data leakage:** fitting the scaler on ALL data before CV means test-fold info leaks into training -> CV score is optimistic
2. **Pipeline:** chains preprocessing + model into ONE object -> CV is applied correctly
3. **GridSearchCV on a pipeline:** tunes ALL steps together, prevents leakage automatically
4. **joblib:** serialise and load the pipeline for production serving
5. One `predict()` call applies all preprocessing + model automatically
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Raw data\\n(missing values,\\nunscaled)',
        'Pipeline step 1:\\nImputer\\n(fill missing)',
        'Pipeline step 2:\\nStandardScaler\\n(mean=0, std=1)',
        'Pipeline step 3:\\nRegression\\nmodel',
        'GridSearchCV\\non whole\\npipeline',
        'joblib.dump\\n-> .pkl file\\n(deployment)',
        'joblib.load\\n-> predict()\\n(one call)',
    ],
    title='NB20 Conceptual Flow: sklearn Pipeline for Production ML',
    colors=['#37474F','#1565C0','#2E7D32','#E65100','#6A1B9A','#C62828','#00695C'],
    figsize=(16, 2.8),
)
"""),
code("""import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.datasets import fetch_california_housing
import warnings; warnings.filterwarnings('ignore')

housing = fetch_california_housing()
X = pd.DataFrame(housing.data, columns=housing.feature_names)
y = housing.target

# Inject 3% missing values
np.random.seed(42)
mask = np.random.rand(*X.shape) < 0.03
X_miss = X.copy(); X_miss[mask] = np.nan

X_tr, X_te, y_tr, y_te = train_test_split(X_miss, y, test_size=0.2, random_state=0)

print(f"Missing values in train: {X_tr.isna().sum().sum()}")
print(f"Missing values in test:  {X_te.isna().sum().sum()}")
print()
print("--- WRONG way (data leakage) ---")
# Scaler fitted on ALL data before split -> leaks test set info
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_scaled_all = sc.fit_transform(X_miss.fillna(X_miss.median()))
X_tr_wrong, X_te_wrong, y_tr_wrong, y_te_wrong = train_test_split(X_scaled_all, y, test_size=0.2, random_state=0)
m_wrong = Ridge(alpha=1).fit(X_tr_wrong, y_tr_wrong)
print(f"  CV R^2 (inflated): {m_wrong.score(X_tr_wrong, y_tr_wrong):.4f}")

print()
print("--- RIGHT way (Pipeline) ---")
pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler',  StandardScaler()),
    ('model',   Ridge(alpha=1.0)),
])
pipe.fit(X_tr, y_tr)
print(f"  Test R^2: {pipe.score(X_te, y_te):.4f}  <- honest estimate")
"""),
code("""# GridSearchCV on the whole pipeline — no leakage
import numpy as np
from sklearn.model_selection import GridSearchCV

param_grid = {
    'model__alpha': np.logspace(-2, 3, 15),  # prefix = step_name + __
}
grid = GridSearchCV(pipe, param_grid, cv=5, scoring='r2', n_jobs=-1)
grid.fit(X_tr, y_tr)

print(f"Best alpha:      {grid.best_params_['model__alpha']:.4f}")
print(f"Best 5-fold CV R^2: {grid.best_score_:.4f}")
print(f"Test R^2:           {grid.score(X_te, y_te):.4f}")

import pandas as pd
cv_df = pd.DataFrame(grid.cv_results_)[['param_model__alpha','mean_test_score','std_test_score']]
cv_df.columns = ['alpha','mean_R2','std_R2']
print("\\nAll alpha values tested:")
print(cv_df.round(4).to_string(index=False))
"""),
code("""# Save and load pipeline for production
import joblib, os, pandas as pd, numpy as np

save_path = os.path.join(r'C:/Users/Administrator/ML/Linear Regression', 'best_pipeline.pkl')
joblib.dump(grid.best_estimator_, save_path)
print(f"Saved to: {save_path}")

loaded = joblib.load(save_path)
y_pred = loaded.predict(X_te)
from sklearn.metrics import r2_score, mean_squared_error
print(f"Loaded pipeline Test R^2:  {r2_score(y_te, y_pred):.4f}")
print(f"Loaded pipeline Test RMSE: {np.sqrt(mean_squared_error(y_te, y_pred)):.4f}")

# Predict a single new observation (with missing value — handled automatically)
new_obs = pd.DataFrame([X.median().values], columns=X.columns)
new_obs.iloc[0, 0] = np.nan
pred = loaded.predict(new_obs)
print(f"\\nPrediction for median house: ${pred[0]*100:.0f}k")
print("(Imputer and scaler applied automatically inside predict())")
"""),
md("""## Complete curriculum summary

| NB | Topic | Core concept (one line) |
|----|-------|------------------------|
| 01 | Intuition | OLS = find the line that minimises sum of squared residuals |
| 02 | Derivation | b1 = Cov(x,y)/Var(x) comes from setting dSSR/db=0 |
| 03 | From scratch | Implement every formula in pure Python |
| 04 | R^2 | R^2 = SS_reg/SS_tot = fraction of variance explained |
| 05 | Inference | t = b/SE; p-value = probability of this t if H0 true |
| 06 | Assumptions | LINE: Linearity, Independence, Normality, Equal variance |
| 07 | Diagnostics | 4 plots: residuals vs fitted, Q-Q, scale-location, leverage |
| 08 | Multiple | b = (XtX)^-1 Xty; each b_j is ceteris paribus |
| 09 | Collinearity | VIF > 10 = severe; Ridge is the fix |
| 10 | Poly/interact | Add x^2 as feature; x1*x2 for "it depends" effects |
| 11 | Ridge (L2) | SSR + lambda*sum(b^2); shrinks but never zeroes |
| 12 | Lasso (L1) | SSR + lambda*sum(|b|); diamond corners -> exact zeros |
| 13 | ElasticNet | L1+L2; sparsity + stability for correlated features |
| 14 | Cross-val | k-fold CV; learning curves for bias/variance diagnosis |
| 15 | GD | Take steps downhill; foundation of deep learning |
| 16 | Robust | Huber/RANSAC/Theil-Sen resist outliers |
| 17 | Quantile | Model median or any percentile; natural prediction bands |
| 18 | Bayesian | Prior + likelihood = posterior distribution over b |
| 19 | Time series | Add t, sin/cos, lag features for temporal structure |
| 20 | Pipelines | Chain imputer + scaler + model; no leakage; one predict() |
"""),
]

# ── Save all 10 ───────────────────────────────────────────────────────────────
save(nb(cells_11), "NB11_Ridge_L2.ipynb")
save(nb(cells_12), "NB12_Lasso_L1.ipynb")
save(nb(cells_13), "NB13_ElasticNet.ipynb")
save(nb(cells_14), "NB14_Cross_Validation.ipynb")
save(nb(cells_15), "NB15_Gradient_Descent.ipynb")
save(nb(cells_16), "NB16_Robust_Regression.ipynb")
save(nb(cells_17), "NB17_Quantile_Regression.ipynb")
save(nb(cells_18), "NB18_Bayesian_Regression.ipynb")
save(nb(cells_19), "NB19_Time_Series.ipynb")
save(nb(cells_20), "NB20_Pipelines_Production.ipynb")
print("Done - NB11 to NB20 rebuilt.")
