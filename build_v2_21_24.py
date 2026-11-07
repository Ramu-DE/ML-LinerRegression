# -*- coding: utf-8 -*-
"""Build NB21-NB24: topics missing from NB01-NB20.

NB21 Feature scaling & gradient descent (conditioning, lr, SGD/mini-batch)
NB22 Categorical encoding & the dummy-variable trap
NB23 Confidence vs prediction intervals
NB24 Why least squares? Gauss-Markov, MLE, numerical stability
"""
import nbformat, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "notebooks")
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

# Re-use the exact flow-diagram helper from build_v2_01_05.py (read as text,
# not imported, so that builder does not re-run).
_src = open(os.path.join(HERE, "build_v2_01_05.py"), encoding="utf-8").read()
import ast
FLOW_HELPER = ast.literal_eval(re.search(r'FLOW_HELPER = ("""\\\n.*?\n""")', _src, re.S).group(1))

# =============================================================================
# NB21 — Feature scaling & gradient descent
# =============================================================================
cells_21 = [
md("""# NB21 — Feature Scaling and Gradient Descent

> **StatQuest principle: gradient descent takes steps downhill — but if the valley is a long thin canyon, it zig-zags forever. Scaling turns the canyon into a round bowl.**

---

## The main ideas are:

1. Gradient descent (NB15) minimises SSR by stepping against the gradient
2. The **shape** of the SSR bowl is set by the Hessian $H = \\frac{2}{n}X^TX$
3. Its eigenvalues decide everything: the step size must satisfy $\\eta < 2/\\lambda_{max}$,
   and convergence speed depends on the **condition number** $\\kappa = \\lambda_{max}/\\lambda_{min}$
4. Unscaled features → huge $\\kappa$ → tiny safe step → very slow convergence
5. Standardising $x$ (mean 0, sd 1) makes $\\kappa \\approx 1$ → fast, robust convergence
6. Batch vs stochastic vs mini-batch GD trade exactness for speed per step
7. Scaling also changes what Ridge/Lasso penalise — the penalty depends on units
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Raw feature x\\n(units: years,\\n$, metres...)',
        'SSR bowl shape\\nHessian\\nH = (2/n) XtX',
        'Eigenvalues\\nlambda_max,\\nlambda_min',
        'Stable step:\\neta < 2 / lambda_max',
        'Speed ~\\ncondition number\\nkappa',
        'Standardise x\\n-> kappa ~ 1\\n-> fast GD',
    ],
    title='NB21 Conceptual Flow: Why Scaling Makes Gradient Descent Work',
    figsize=(16, 2.8),
)
"""),
md("""## Step 1 — The same salary data as NB03

`X` = years of experience 1..10, `y` = salary in $1000s.
The exact OLS answer (NB03) is **b0 = 32.0000, b1 = 6.3636**.

With MSE loss $L = \\frac{1}{n}\\sum (y - b_0 - b_1x)^2$ the gradient is

$$\\nabla L = -\\frac{2}{n} X^T (y - Xb), \\qquad H = \\frac{2}{n}X^TX$$

where $X$ includes the column of 1s. $H$ is constant — the loss is a perfect quadratic bowl.
"""),
code("""import numpy as np

X = np.arange(1, 11, dtype=float)
y = np.array([40, 45, 50, 55, 65, 70, 75, 85, 90, 95], dtype=float)
n = len(X)

Xd = np.column_stack([np.ones(n), X])
b_ols = np.linalg.lstsq(Xd, y, rcond=None)[0]
print(f"OLS (exact):  b0 = {b_ols[0]:.4f}   b1 = {b_ols[1]:.4f}")

H = 2 / n * Xd.T @ Xd
eig = np.linalg.eigvalsh(H)
print(f"\\nRAW x  -> Hessian eigenvalues: {eig[0]:.4f}, {eig[1]:.4f}")
print(f"          condition number kappa = {eig[1]/eig[0]:.1f}")
print(f"          largest stable step  eta < 2/lambda_max = {2/eig[1]:.5f}")

xs = (X - X.mean()) / X.std()
Xs = np.column_stack([np.ones(n), xs])
Hs = 2 / n * Xs.T @ Xs
eig_s = np.linalg.eigvalsh(Hs)
print(f"\\nSTANDARDISED x -> eigenvalues: {eig_s[0]:.4f}, {eig_s[1]:.4f}")
print(f"          condition number kappa = {eig_s[1]/eig_s[0]:.1f}")
print(f"          largest stable step  eta < {2/eig_s[1]:.5f}")
"""),
md("""## Step 2 — Learning-rate sweep on RAW x (the correct story)

For a quadratic bowl the rule is exact:

| Step size | What happens |
|---|---|
| $\\eta$ far below $2/\\lambda_{max}$ | converges, but slowly along the flat direction |
| $\\eta$ close to (but below) $2/\\lambda_{max}$ | fastest convergence |
| $\\eta > 2/\\lambda_{max}$ | **diverges** — every step overshoots further |

Here $2/\\lambda_{max} \\approx 0.0255$, so 0.001 is *slow*, 0.003 is *fine*, 0.03 *diverges*.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

def batch_gd(Xd, y, lr, epochs):
    b = np.zeros(Xd.shape[1])
    hist = []
    with np.errstate(over='ignore', invalid='ignore'):
        for _ in range(epochs):
            grad = -2 / len(y) * Xd.T @ (y - Xd @ b)
            b = b - lr * grad
            hist.append(np.sum((y - Xd @ b) ** 2))
    return b, np.array(hist)

epochs = 6000
print(f"Batch GD on RAW x, {epochs} epochs (OLS SSR = {np.sum((y - Xd @ b_ols)**2):.4f})\\n")
results = {}
for lr, label in [(0.001, 'slow'), (0.003, 'good'), (0.03, 'diverges')]:
    b, hist = batch_gd(Xd, y, lr, epochs)
    results[lr] = hist
    if np.all(np.isfinite(b)):
        print(f"  lr={lr:<6} ({label:8s}) b0={b[0]:9.4f}  b1={b[1]:7.4f}  SSR={hist[-1]:10.4f}")
    else:
        print(f"  lr={lr:<6} ({label:8s}) DIVERGED (values overflow to inf/nan)")

fig, ax = plt.subplots(figsize=(10, 4))
for lr, c in [(0.001, '#1565C0'), (0.003, '#2E7D32'), (0.03, '#C62828')]:
    h = results[lr]
    h = np.where(np.isfinite(h) & (h < 1e12), h, np.nan)
    ax.semilogy(h[:3000], color=c, lw=2, label=f'lr = {lr}')
ax.axhline(np.sum((y - Xd @ b_ols)**2), color='k', ls='--', lw=1, label='OLS minimum')
ax.set_ylim(10, 1e7)
ax.set_xlabel('epoch'); ax.set_ylabel('SSR (log scale)')
ax.set_title('Raw x: too small = slow, just right = converges, too big = diverges')
ax.legend(); plt.tight_layout(); plt.show()
"""),
md("""## Step 3 — Standardise x: the canyon becomes a bowl

After standardising, $\\kappa \\approx 1$ and a step of 0.1 (33× bigger than the best raw step) is safe.
The coefficients are in **standardised units**, so convert back:

$$b_1 = \\frac{b_1^{std}}{s_x}, \\qquad b_0 = b_0^{std} - b_1\\,\\bar x$$
"""),
code("""import numpy as np

def epochs_to_converge(Xd, y, lr, tol=1e-6, max_epochs=200000):
    b = np.zeros(Xd.shape[1])
    target = np.sum((y - Xd @ np.linalg.lstsq(Xd, y, rcond=None)[0]) ** 2)
    with np.errstate(over='ignore', invalid='ignore'):
        for ep in range(1, max_epochs + 1):
            b = b - lr * (-2 / len(y) * Xd.T @ (y - Xd @ b))
            ssr = np.sum((y - Xd @ b) ** 2)
            if not np.isfinite(ssr):
                return None, b
            if ssr - target < tol * target:
                return ep, b
    return max_epochs, b

ep_raw, b_raw = epochs_to_converge(Xd, y, lr=0.02)
ep_std, b_std = epochs_to_converge(Xs, y, lr=0.1)

b1 = b_std[1] / X.std()
b0 = b_std[0] - b1 * X.mean()
print(f"RAW x,  lr=0.02 (near its limit): {ep_raw} epochs to reach the OLS SSR")
print(f"STD x,  lr=0.1                  : {ep_std} epochs")
print(f"Speed-up: {ep_raw/ep_std:.0f}x fewer epochs")
print(f"\\nBack-transformed from standardised fit: b0 = {b0:.4f}, b1 = {b1:.4f}  (OLS: 32.0000, 6.3636)")
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

def contour_panel(ax, Xmat, title, lr, steps):
    bopt = np.linalg.lstsq(Xmat, y, rcond=None)[0]
    g0 = np.linspace(bopt[0] - 40, bopt[0] + 40, 200)
    g1 = np.linspace(bopt[1] - 12, bopt[1] + 12, 200)
    B0, B1 = np.meshgrid(g0, g1)
    L = ((y[None, None, :] - B0[..., None] - B1[..., None] * Xmat[:, 1][None, None, :]) ** 2).mean(-1)
    ax.contour(B0, B1, L, levels=np.geomspace(L.min() + 1e-3, L.max(), 25), cmap='viridis', linewidths=0.8)
    b = np.array([bopt[0] - 35, bopt[1] - 10.0])
    path = [b.copy()]
    for _ in range(steps):
        b = b - lr * (-2 / len(y) * Xmat.T @ (y - Xmat @ b))
        path.append(b.copy())
    path = np.array(path)
    ax.plot(path[:, 0], path[:, 1], 'o-', color='#C62828', ms=3, lw=1.2)
    ax.plot(*bopt, 'k*', ms=14)
    ax.set_title(title, fontsize=10); ax.set_xlabel('b0'); ax.set_ylabel('b1')

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
contour_panel(axes[0], Xd, 'RAW x: long thin valley, 40 steps (lr=0.02)', 0.02, 40)
contour_panel(axes[1], Xs, 'STANDARDISED x: round bowl, 40 steps (lr=0.1)', 0.1, 40)
plt.tight_layout(); plt.show()
"""),
md("""## Step 4 — Batch vs Stochastic vs Mini-batch gradient descent

| Variant | Gradient uses | Cost per step | Path |
|---|---|---|---|
| **Batch** | all n rows | O(n·p) | smooth, exact gradient |
| **Stochastic (SGD)** | 1 random row | O(p) | noisy, needs decaying lr |
| **Mini-batch** | b rows (e.g. 32) | O(b·p) | the practical default (GPUs, big data) |

We use a larger synthetic problem (n = 5,000, true b0 = 4, b1 = 3, standardised x) so the difference is visible.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(21)
N = 5000
xb = rng.normal(0, 1, N)
yb = 4 + 3 * xb + rng.normal(0, 1, N)
Xb = np.column_stack([np.ones(N), xb])
b_true_ols = np.linalg.lstsq(Xb, yb, rcond=None)[0]

def run(batch, lr0, epochs=5, decay=False, seed=0):
    r = np.random.default_rng(seed)
    b = np.zeros(2); losses = []; t = 0
    for ep in range(epochs):
        idx = r.permutation(N)
        for s in range(0, N, batch):
            j = idx[s:s + batch]
            lr = lr0 / (1 + 0.001 * t) if decay else lr0
            b = b - lr * (-2 / len(j) * Xb[j].T @ (yb[j] - Xb[j] @ b))
            t += 1
            losses.append(np.mean((yb - Xb @ b) ** 2))
    return b, np.array(losses), t

b_batch, l_batch, u_batch = run(N, 0.1, epochs=50)
b_sgd, l_sgd, u_sgd = run(1, 0.01, epochs=1, decay=True)
b_mini, l_mini, u_mini = run(32, 0.05, epochs=2)

print(f"OLS exact          : b0={b_true_ols[0]:.4f}  b1={b_true_ols[1]:.4f}  MSE={np.mean((yb - Xb @ b_true_ols)**2):.4f}")
for name, b, l, u in [('Batch (50 epochs)', b_batch, l_batch, u_batch),
                      ('SGD (1 epoch)', b_sgd, l_sgd, u_sgd),
                      ('Mini-batch 32 (2 ep)', b_mini, l_mini, u_mini)]:
    print(f"{name:19s}: b0={b[0]:.4f}  b1={b[1]:.4f}  MSE={l[-1]:.4f}  updates={u}")

fig, axes = plt.subplots(1, 3, figsize=(15, 3.8), sharey=True)
for ax, (name, l, c) in zip(axes, [('Batch: 1 update per epoch', l_batch, '#1565C0'),
                                   ('SGD: 1 update per row (noisy)', l_sgd, '#C62828'),
                                   ('Mini-batch (32 rows)', l_mini, '#2E7D32')]):
    ax.plot(l, color=c, lw=1); ax.set_yscale('log'); ax.set_title(name, fontsize=10)
    ax.set_xlabel('update number'); ax.axhline(np.mean((yb - Xb @ b_true_ols)**2), color='k', ls='--', lw=1)
axes[0].set_ylabel('full-data MSE')
plt.tight_layout(); plt.show()
"""),
md("""## Step 5 — Scaling changes what Ridge and Lasso penalise

Ridge minimises $SSR + \\lambda\\sum b_j^2$. A coefficient's size depends on the **units** of its feature:
measure income in $ instead of $1000s and its slope becomes 1000× smaller — so it is penalised a million times less.
Without scaling, the penalty is arbitrary. **Always standardise before Ridge/Lasso/ElasticNet** (in a Pipeline, NB20).
"""),
code("""import numpy as np
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(3)
n = 200
income_k = rng.normal(50, 15, n)              # income in $1000s
age = rng.normal(40, 10, n)                   # age in years
yy = 2.0 * income_k + 1.5 * age + rng.normal(0, 10, n)

def fit(Xm, scaled):
    if scaled:
        Xm = StandardScaler().fit_transform(Xm)
    return Ridge(alpha=5000).fit(Xm, yy).coef_

X_k = np.column_stack([income_k, age])
X_dollars = np.column_stack([income_k * 1000, age])

print("OLS slopes (income in $k):", LinearRegression().fit(X_k, yy).coef_.round(4))
print("\\nRidge(alpha=5000), NO scaling:")
print("  income in $1000s ->", fit(X_k, False).round(4))
c = fit(X_dollars, False)
print("  income in dollars ->", c.round(6), "  (= per $1000:", round(c[0] * 1000, 4), ")")
print("\\nRidge(alpha=5000), WITH StandardScaler:")
print("  income in $1000s ->", fit(X_k, True).round(4))
print("  income in dollars ->", fit(X_dollars, True).round(4), " <- identical: units no longer matter")
"""),
md("""## Key Takeaways

| Concept | What to remember |
|---|---|
| Hessian | $H=\\frac{2}{n}X^TX$ is fixed for linear regression: the loss is a perfect bowl |
| Stability | Gradient descent converges only if $\\eta < 2/\\lambda_{max}$ |
| Speed | Number of steps grows with the condition number $\\kappa=\\lambda_{max}/\\lambda_{min}$ |
| Scaling | Standardising x makes $\\kappa \\approx 1$ → larger safe steps, far fewer epochs |
| Variants | Batch = exact & smooth; SGD = cheap & noisy (decay lr); mini-batch = practical default |
| Penalties | Ridge/Lasso penalties depend on units → standardise first, inside a Pipeline |
| Correction to NB15 | With raw x, lr = 0.003 converges (best of the three); lr = 0.03 is the one that diverges |
"""),
]

# =============================================================================
# NB22 — Categorical encoding
# =============================================================================
cells_22 = [
md("""# NB22 — Categorical Features and the Dummy-Variable Trap

> **StatQuest principle: regression only understands numbers — so we turn each category into its own little on/off switch.**

---

## The main ideas are:

1. A category like `city = {A, B, C}` cannot be used as 1, 2, 3 — that invents an order and equal spacing
2. **One-hot encoding** makes one 0/1 column per category
3. With an intercept, keeping ALL dummies creates **perfect multicollinearity** (the dummy-variable trap):
   the dummies always sum to 1 = the intercept column
4. Fix: drop one category — it becomes the **reference (baseline)**
5. Each dummy coefficient = **difference vs the baseline**, holding other features constant
6. In production use `OneHotEncoder` inside a `ColumnTransformer` + `Pipeline`
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Categorical\\ncolumn\\ncity = A/B/C',
        'One-hot:\\n0/1 column\\nper category',
        'Trap! dummies\\nsum to 1 =\\nintercept column',
        'Drop one\\n(reference\\ncategory)',
        'Fit OLS:\\ncoef = gap vs\\nbaseline',
        'Pipeline:\\nColumnTransformer\\n+ OneHotEncoder',
    ],
    title='NB22 Conceptual Flow: Encoding Categories for Linear Regression',
    figsize=(16, 2.8),
)
"""),
md("""## Step 1 — A synthetic housing dataset with a category

Price ($1000s) = 50 + 3·size(m²) + city effect + noise, with true city effects
**A = 0 (baseline), B = +90, C = +40** — the categories have no natural order.
"""),
code("""import numpy as np
import pandas as pd

rng = np.random.default_rng(22)
n = 300
city = rng.choice(['A', 'B', 'C'], size=n, p=[0.4, 0.35, 0.25])
size = rng.uniform(40, 160, n).round(0)
effect = pd.Series(city).map({'A': 0, 'B': 90, 'C': 40}).to_numpy()
price = 50 + 3 * size + effect + rng.normal(0, 20, n)

df = pd.DataFrame({'size_m2': size, 'city': city, 'price_k': price.round(1)})
print(df.head(6))
print("\\nRows per city:", df['city'].value_counts().sort_index().to_dict())
print("\\nMean price by city:")
print(df.groupby('city')['price_k'].mean().round(1))
"""),
md("""## Step 2 — Why not just code A=1, B=2, C=3?

Label-encoding forces the model to assume B−A = C−B (equal steps) and one slope for "city".
The true gaps are A→B = +90 and B→C = −50 — not equal, not even the same sign.
"""),
code("""import numpy as np
import statsmodels.api as sm

codes = df['city'].map({'A': 1, 'B': 2, 'C': 3})
X_bad = sm.add_constant(np.column_stack([df['size_m2'], codes]))
res_bad = sm.OLS(df['price_k'], X_bad).fit()
print("Label-encoded city (A=1, B=2, C=3):")
print(f"  one 'city' slope = {res_bad.params.iloc[2]:.2f} per step  -> forces A->B gap = B->C gap")
print(f"  R^2 = {res_bad.rsquared:.4f}")
"""),
md("""## Step 3 — The dummy-variable trap, shown numerically

With an intercept plus **all three** dummies, column `const` = `A + B + C` exactly.
$X^TX$ is singular (rank deficient), so $(X^TX)^{-1}$ does not exist and the coefficients are not unique.
"""),
code("""import numpy as np
import pandas as pd

D_all = pd.get_dummies(df['city'], dtype=float)                 # A, B, C
X_trap = np.column_stack([np.ones(n), df['size_m2'], D_all])
XtX = X_trap.T @ X_trap
print("Columns: const, size, A, B, C")
print("Check: A + B + C equals the constant column for every row:",
      bool(np.allclose(D_all.sum(axis=1), 1)))
print(f"rank(X) = {np.linalg.matrix_rank(X_trap)}  but number of columns = {X_trap.shape[1]}")
print(f"det(XtX) = {np.linalg.det(XtX):.3e}")
print(f"condition number of XtX = {np.linalg.cond(XtX):.3e}   (infinite in exact arithmetic)")

# Two different coefficient vectors give IDENTICAL predictions:
b1 = np.linalg.lstsq(X_trap, df['price_k'], rcond=None)[0]
shift = np.array([10, 0, -10, -10, -10])        # +10 to intercept, -10 to every dummy
b2 = b1 + shift
print("\\nSolution 1:", b1.round(3))
print("Solution 2:", b2.round(3))
print("Max prediction difference:", float(np.abs(X_trap @ b1 - X_trap @ b2).max().round(10)))
print("-> infinitely many 'best' fits: the coefficients are meaningless")
"""),
md("""## Step 4 — Drop one category: the reference level

`drop_first=True` drops **A**. Now:
- intercept = expected price for city **A** (at size 0)
- `B` coefficient = how much more B costs than A, **same size**
- `C` coefficient = how much more C costs than A, same size
"""),
code("""import numpy as np
import pandas as pd
import statsmodels.api as sm

D = pd.get_dummies(df['city'], drop_first=True, dtype=float)   # B, C
X_ok = sm.add_constant(pd.concat([df[['size_m2']], D], axis=1))
res = sm.OLS(df['price_k'], X_ok).fit()
print(f"rank(X) = {np.linalg.matrix_rank(X_ok)} = number of columns {X_ok.shape[1]}  -> unique solution\\n")
print(res.summary().tables[1])
print(f"\\nR^2 = {res.rsquared:.4f}  (label-encoded version: {res_bad.rsquared:.4f})")
print(f"\\nInterpretation (true values: B=+90, C=+40):")
print(f"  B vs A: {res.params['B']:+.2f}k   C vs A: {res.params['C']:+.2f}k   per m2: {res.params['size_m2']:.3f}k")
print(f"  C vs B: {res.params['C'] - res.params['B']:+.2f}k  (difference of the two dummies)")
"""),
md("""## Step 5 — Changing the baseline changes the numbers, not the model

Choosing **C** as the reference gives different coefficients but **identical predictions and R²**.
Pick the baseline that makes the story easiest to tell (e.g. the most common category).
"""),
code("""import numpy as np
import pandas as pd
import statsmodels.api as sm

D_c = pd.get_dummies(df['city'], dtype=float).drop(columns='C')   # keep A, B; C = reference
res_c = sm.OLS(df['price_k'], sm.add_constant(pd.concat([df[['size_m2']], D_c], axis=1))).fit()
print("Reference = C:", res_c.params.round(2).to_dict())
print("Reference = A:", res.params.round(2).to_dict())
print(f"\\nSame R^2: {res_c.rsquared:.6f} vs {res.rsquared:.6f}")
print("Max prediction difference:", float(np.abs(res_c.fittedvalues - res.fittedvalues).max().round(8)))
"""),
md("""## Step 6 — The production way: ColumnTransformer + OneHotEncoder

`OneHotEncoder(drop='first', handle_unknown='ignore')` learns the categories on the **training** data only
(no leakage) and, with `handle_unknown='ignore'`, maps an unseen category to all-zeros instead of crashing.
"""),
code("""import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

X_tr, X_te, y_tr, y_te = train_test_split(df[['size_m2', 'city']], df['price_k'],
                                          test_size=0.25, random_state=0)
pre = ColumnTransformer([
    ('num', 'passthrough', ['size_m2']),
    ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), ['city']),
])
pipe = Pipeline([('pre', pre), ('ols', LinearRegression())]).fit(X_tr, y_tr)
names = pipe.named_steps['pre'].get_feature_names_out()
print("Features:", list(names))
print("Coefficients:", dict(zip(names, pipe.named_steps['ols'].coef_.round(2))))
print(f"Intercept: {pipe.named_steps['ols'].intercept_:.2f}")
print(f"Test R^2: {pipe.score(X_te, y_te):.4f}")
new = pd.DataFrame({'size_m2': [100, 100, 100], 'city': ['A', 'C', 'Z']})
print("\\nPredictions for 100 m2 in A, C and an unseen city 'Z' (treated like the baseline):")
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')      # sklearn warns that 'Z' was unseen -> encoded as all zeros
    print(pipe.predict(new).round(1))
"""),
md("""## Key Takeaways

| Concept | What to remember |
|---|---|
| Label encoding | A=1, B=2, C=3 invents order and equal spacing — wrong for nominal categories |
| One-hot | one 0/1 column per category |
| Dummy-variable trap | intercept + all k dummies → columns sum to the constant → singular $X^TX$, non-unique coefficients |
| Fix | drop one category (k−1 dummies); it becomes the reference |
| Interpretation | dummy coefficient = difference vs the reference category, other features held constant |
| Baseline choice | changes coefficients, never predictions or R² |
| Production | `OneHotEncoder(drop='first', handle_unknown='ignore')` inside a `ColumnTransformer` + `Pipeline` |
| Note | Ridge/Lasso can keep all k dummies (the penalty makes the solution unique) — but plain OLS cannot |
"""),
]

# =============================================================================
# NB23 — Confidence vs prediction intervals
# =============================================================================
cells_23 = [
md("""# NB23 — Confidence Intervals vs Prediction Intervals

> **StatQuest principle: "Where is the average?" and "Where will the next point land?" are two different questions — and the second one always has a wider answer.**

---

## The main ideas are:

1. A **confidence interval (CI)** brackets the **mean** response $E[y\\mid x_0]$ — uncertainty in the fitted line only
2. A **prediction interval (PI)** brackets a **new single observation** $y_0$ — line uncertainty **plus** the noise $\\sigma^2$
3. Formulas (simple regression):
   $se_{fit}(x_0) = \\hat\\sigma\\sqrt{\\frac{1}{n} + \\frac{(x_0-\\bar x)^2}{S_{xx}}}$,
   $\\;\\; se_{pred}(x_0) = \\hat\\sigma\\sqrt{1 + \\frac{1}{n} + \\frac{(x_0-\\bar x)^2}{S_{xx}}}$
4. Both are narrowest at $\\bar x$ and **widen** as $x_0$ moves away
5. As n grows, the CI shrinks to zero width; the PI never shrinks below $\\approx \\pm 1.96\\sigma$
6. Far outside the data (extrapolation), both formulas assume the line stays straight — they can be badly wrong
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Fit OLS\\nb0, b1,\\nsigma_hat',
        'New x0',
        'se_fit:\\nline\\nuncertainty',
        'CI = y_hat\\n+/- t * se_fit\\n(the MEAN)',
        'se_pred:\\nadd sigma^2\\n(the noise)',
        'PI = y_hat\\n+/- t * se_pred\\n(ONE new y)',
    ],
    title='NB23 Conceptual Flow: Two Different Questions, Two Different Intervals',
    figsize=(16, 2.8),
)
"""),
md("""## Step 1 — Data and fit

Synthetic: n = 30, x ~ U(0, 10), y = 5 + 2x + N(0, 3²), seed 23.
"""),
code("""import numpy as np
import statsmodels.api as sm

rng = np.random.default_rng(23)
n = 30
x = np.sort(rng.uniform(0, 10, n))
y = 5 + 2 * x + rng.normal(0, 3, n)
res = sm.OLS(y, sm.add_constant(x)).fit()
b0, b1 = res.params
sigma = np.sqrt(res.scale)
print(f"Fit: y_hat = {b0:.3f} + {b1:.3f} x     sigma_hat = {sigma:.3f}  (true sigma = 3)")
print(f"x_bar = {x.mean():.3f}, n = {n}, df = {n-2}")
"""),
md("""## Step 2 — Compute both intervals by hand, then with statsmodels

`get_prediction(...).summary_frame(alpha=0.05)` returns:
- `mean_ci_lower / mean_ci_upper` → the **CI** for the mean
- `obs_ci_lower / obs_ci_upper` → the **PI** for a new observation
"""),
code("""import numpy as np
import pandas as pd
from scipy import stats

Sxx = np.sum((x - x.mean()) ** 2)
tcrit = stats.t.ppf(0.975, n - 2)
x0s = np.array([x.mean(), 2.0, 9.0, 15.0])

rows = []
for x0 in x0s:
    yhat = b0 + b1 * x0
    se_fit = sigma * np.sqrt(1 / n + (x0 - x.mean()) ** 2 / Sxx)
    se_pred = sigma * np.sqrt(1 + 1 / n + (x0 - x.mean()) ** 2 / Sxx)
    rows.append([x0, yhat, se_fit, yhat - tcrit * se_fit, yhat + tcrit * se_fit,
                 se_pred, yhat - tcrit * se_pred, yhat + tcrit * se_pred])
by_hand = pd.DataFrame(rows, columns=['x0', 'y_hat', 'se_fit', 'CI_low', 'CI_high',
                                      'se_pred', 'PI_low', 'PI_high']).round(3)
print(f"t critical (95%, df={n-2}) = {tcrit:.4f}\\n")
print("By hand:")
print(by_hand.to_string(index=False))

sf = res.get_prediction(np.column_stack([np.ones(len(x0s)), x0s])).summary_frame(alpha=0.05)
print("\\nstatsmodels summary_frame:")
print(sf.round(3).to_string())
print("\\nMatch:", bool(np.allclose(sf['mean_ci_lower'], by_hand['CI_low'], atol=1e-3)
                    and np.allclose(sf['obs_ci_upper'], by_hand['PI_high'], atol=1e-3)))
w = by_hand.iloc[0]
print(f"\\nAt x_bar: CI width = {w.CI_high - w.CI_low:.2f}, PI width = {w.PI_high - w.PI_low:.2f}  "
      f"({(w.PI_high - w.PI_low)/(w.CI_high - w.CI_low):.1f}x wider)")
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

grid = np.linspace(-2, 16, 300)
sf_g = res.get_prediction(np.column_stack([np.ones_like(grid), grid])).summary_frame(alpha=0.05)

fig, ax = plt.subplots(figsize=(11, 5))
ax.fill_between(grid, sf_g['obs_ci_lower'], sf_g['obs_ci_upper'], color='#FFB74D', alpha=0.35, label='95% PREDICTION interval (one new y)')
ax.fill_between(grid, sf_g['mean_ci_lower'], sf_g['mean_ci_upper'], color='#1565C0', alpha=0.35, label='95% CONFIDENCE interval (the mean)')
ax.plot(grid, sf_g['mean'], color='#0D47A1', lw=2, label='fitted line')
ax.scatter(x, y, color='k', s=18, zorder=3, label='data (n=30)')
ax.axvspan(10, 16, color='#C62828', alpha=0.06)
ax.text(12.8, ax.get_ylim()[0] + 3, 'extrapolation zone:\\nno data here', ha='center', color='#C62828', fontsize=9)
ax.axvline(x.mean(), color='gray', ls=':', lw=1); ax.text(x.mean(), ax.get_ylim()[1] - 3, '  x_bar', color='gray')
ax.set_xlabel('x'); ax.set_ylabel('y')
ax.set_title('Both bands are narrowest at x_bar and widen away from it; the PI is always wider')
ax.legend(loc='upper left', fontsize=9); plt.tight_layout(); plt.show()
"""),
md("""## Step 3 — Coverage simulation: does each interval do its job?

Repeat 2,000 times: draw a new dataset from the true model, build both intervals at $x_0 = 9$, and check
- does the **CI** contain the true mean $5 + 2\\cdot 9 = 23$?
- does the **PI** contain a **fresh** observation $y_0$?

And the common mistake: using the CI to bracket a new observation.
"""),
code("""import numpy as np
import statsmodels.api as sm

rng = np.random.default_rng(230)
reps, x0 = 2000, 9.0
true_mean = 5 + 2 * x0
ci_hit = pi_hit = ci_for_new = 0
for _ in range(reps):
    xs = rng.uniform(0, 10, n)
    ys = 5 + 2 * xs + rng.normal(0, 3, n)
    r = sm.OLS(ys, sm.add_constant(xs)).fit()
    f = r.get_prediction(np.array([[1.0, x0]])).summary_frame(alpha=0.05).iloc[0]
    y_new = true_mean + rng.normal(0, 3)
    ci_hit += f.mean_ci_lower <= true_mean <= f.mean_ci_upper
    pi_hit += f.obs_ci_lower <= y_new <= f.obs_ci_upper
    ci_for_new += f.mean_ci_lower <= y_new <= f.mean_ci_upper
print(f"CI contains the true MEAN      : {ci_hit/reps:.1%}   (target 95%)")
print(f"PI contains a NEW observation  : {pi_hit/reps:.1%}   (target 95%)")
print(f"CI misused for a new observation: {ci_for_new/reps:.1%}   <- far below 95%: the classic mistake")
"""),
md("""## Step 4 — More data shrinks the CI, but not the PI

$se_{fit} \\to 0$ as $n \\to \\infty$, but $se_{pred} \\to \\sigma$. Irreducible noise stays.
"""),
code("""import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

rng = np.random.default_rng(231)
ns = [10, 30, 100, 300, 1000, 3000]
ci_w, pi_w = [], []
for m in ns:
    xs = rng.uniform(0, 10, m)
    ys = 5 + 2 * xs + rng.normal(0, 3, m)
    f = sm.OLS(ys, sm.add_constant(xs)).fit().get_prediction(np.array([[1.0, 5.0]])).summary_frame(alpha=0.05).iloc[0]
    ci_w.append(f.mean_ci_upper - f.mean_ci_lower)
    pi_w.append(f.obs_ci_upper - f.obs_ci_lower)
    print(f"n={m:5d}:  CI width = {ci_w[-1]:6.2f}   PI width = {pi_w[-1]:6.2f}")
print(f"\\nPI width floor = 2 x 1.96 x sigma = {2*1.96*3:.2f}")

fig, ax = plt.subplots(figsize=(8, 3.8))
ax.semilogx(ns, ci_w, 'o-', color='#1565C0', lw=2, label='CI width (mean)')
ax.semilogx(ns, pi_w, 'o-', color='#E65100', lw=2, label='PI width (new y)')
ax.axhline(2 * 1.96 * 3, color='k', ls='--', lw=1, label='2 x 1.96 sigma')
ax.set_xlabel('n (log scale)'); ax.set_ylabel('interval width at x0 = 5'); ax.legend()
ax.set_title('More data: CI -> 0, PI -> irreducible noise'); plt.tight_layout(); plt.show()
"""),
md("""## Step 5 — Extrapolation: the intervals only know about the model you assumed

If the truth curves outside the data range, both intervals (built on the straight-line assumption) miss completely.
"""),
code("""import numpy as np
import statsmodels.api as sm

rng = np.random.default_rng(232)
xs = rng.uniform(0, 10, 60)
truth = lambda v: 5 + 2 * v + 0.15 * np.maximum(v - 10, 0) ** 2 * 10   # straight on [0,10], bends after 10
ys = truth(xs) + rng.normal(0, 3, 60)
r = sm.OLS(ys, sm.add_constant(xs)).fit()
for x0 in [5, 10, 15, 20]:
    f = r.get_prediction(np.array([[1.0, x0]])).summary_frame(alpha=0.05).iloc[0]
    inside = f.obs_ci_lower <= truth(x0) <= f.obs_ci_upper
    print(f"x0={x0:>2}: PI = [{f.obs_ci_lower:6.1f}, {f.obs_ci_upper:6.1f}]   true mean = {truth(x0):6.1f}   "
          f"{'inside' if inside else 'OUTSIDE  <- extrapolation failure'}")
"""),
md("""## Key Takeaways

| Question | Interval | Standard error | Shrinks with more data? |
|---|---|---|---|
| Where is the **average** y at x0? | Confidence interval | $\\hat\\sigma\\sqrt{1/n + (x_0-\\bar x)^2/S_{xx}}$ | Yes → 0 |
| Where will **one new** y land? | Prediction interval | $\\hat\\sigma\\sqrt{1 + 1/n + (x_0-\\bar x)^2/S_{xx}}$ | No → about ±1.96σ |

- Both are narrowest at $\\bar x$ and widen away from it
- statsmodels: `get_prediction(X0).summary_frame()` → `mean_ci_*` (CI) and `obs_ci_*` (PI)
- Using a CI to bracket a new observation badly under-covers
- Outside the data range, both intervals inherit the (untested) assumption that the model still holds
- Both assume homoscedastic, roughly normal errors (NB06); otherwise consider quantile regression (NB17)
"""),
]

# =============================================================================
# NB24 — Why least squares
# =============================================================================
cells_24 = [
md("""# NB24 — Why Least Squares? Gauss–Markov, MLE and Numerical Stability

> **StatQuest principle: we didn't pick "sum of squared residuals" because it looks nice — two theorems say it is the best choice, and good numerics make sure the computer actually finds it.**

---

## The main ideas are:

1. **Gauss–Markov theorem:** under linearity, exogeneity (E[ε|X]=0), homoscedasticity and no autocorrelation
   (plus full-rank X), OLS is **BLUE** — the Best (lowest-variance) Linear Unbiased Estimator
2. **Normality is NOT required** for BLUE — it is only needed for exact small-sample t/F tests
3. **MLE:** if errors are Gaussian, maximising the likelihood is *exactly* minimising SSR → OLS = MLE
4. If the assumptions fail, OLS can lose its crown (WLS/GLS more efficient) or become biased
5. **Numerics:** never invert $X^TX$. It squares the condition number. Use QR or SVD (`np.linalg.lstsq`)
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Assumptions:\\nlinear, E[e|X]=0,\\nequal var,\\nno autocorr',
        'Gauss-Markov:\\nOLS = BLUE\\n(min variance)',
        'Add normal\\nerrors:\\nOLS = MLE',
        'Compute it\\nstably:\\nQR / SVD',
        'Avoid:\\ninv(XtX)\\nkappa squared',
    ],
    title='NB24 Conceptual Flow: Why Least Squares Is the Right Answer (and How to Compute It)',
    figsize=(15, 2.8),
)
"""),
md("""## Step 1 — Gauss–Markov: OLS beats any other linear unbiased estimator

Any estimator of the form $\\tilde b = Cy$ with $CX = I$ is linear and unbiased.
Gauss–Markov says $Var(\\tilde b_j) \\ge Var(\\hat b_j^{OLS})$.

**Competitor:** the "two-group slope" — split the data at the median x and use
$\\tilde b_1 = (\\bar y_{high} - \\bar y_{low}) / (\\bar x_{high} - \\bar x_{low})$.
It is linear in y and unbiased. We simulate 10,000 datasets with **non-normal** (uniform) errors to show
normality is not needed.
"""),
code("""import numpy as np

rng = np.random.default_rng(24)
n, reps = 40, 10000
x = np.linspace(0, 10, n)
X = np.column_stack([np.ones(n), x])
hi = x > np.median(x)
b_ols, b_grp = [], []
for _ in range(reps):
    eps = rng.uniform(-3, 3, n)                      # NON-normal errors, mean 0, equal variance
    y = 1 + 2 * x + eps
    b_ols.append(np.linalg.lstsq(X, y, rcond=None)[0][1])
    b_grp.append((y[hi].mean() - y[~hi].mean()) / (x[hi].mean() - x[~hi].mean()))
b_ols, b_grp = np.array(b_ols), np.array(b_grp)
print("True slope = 2.0, errors ~ Uniform(-3, 3)  (not normal!)\\n")
print(f"OLS slope       : mean = {b_ols.mean():.4f}   variance = {b_ols.var():.5f}")
print(f"Two-group slope : mean = {b_grp.mean():.4f}   variance = {b_grp.var():.5f}")
print(f"\\nBoth unbiased. OLS variance is {b_grp.var()/b_ols.var():.2f}x smaller -> OLS is 'Best'")
"""),
code("""import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(9, 3.8))
bins = np.linspace(1.6, 2.4, 60)
ax.hist(b_grp, bins=bins, alpha=0.55, color='#E65100', label=f'two-group slope (var {b_grp.var():.4f})')
ax.hist(b_ols, bins=bins, alpha=0.65, color='#1565C0', label=f'OLS slope (var {b_ols.var():.4f})')
ax.axvline(2, color='k', ls='--', lw=1)
ax.set_xlabel('estimated slope across 10,000 datasets'); ax.legend()
ax.set_title('Both estimators are centred on the truth; OLS is tighter (Gauss-Markov)')
plt.tight_layout(); plt.show()
"""),
md("""## Step 2 — When an assumption breaks, OLS is no longer "best"

With **heteroscedastic** errors (sd grows with x), OLS is still unbiased but **WLS** (weights $1/\\sigma_i^2$) has lower variance.
This is why NB06's statement "OLS is still the best among linear models when assumptions break" is not correct.
"""),
code("""import numpy as np

rng = np.random.default_rng(241)
sd = 0.3 + 0.6 * x                                    # error sd grows with x
W = 1 / sd ** 2
b_o, b_w = [], []
for _ in range(reps):
    y = 1 + 2 * x + rng.normal(0, sd)
    b_o.append(np.linalg.lstsq(X, y, rcond=None)[0][1])
    sw = np.sqrt(W)
    b_w.append(np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0][1])
b_o, b_w = np.array(b_o), np.array(b_w)
print("Heteroscedastic errors (sd = 0.3 + 0.6x):")
print(f"  OLS slope: mean = {b_o.mean():.4f}, variance = {b_o.var():.5f}")
print(f"  WLS slope: mean = {b_w.mean():.4f}, variance = {b_w.var():.5f}")
print(f"  -> both unbiased, WLS variance {b_o.var()/b_w.var():.2f}x smaller: Gauss-Markov's 'equal variance' assumption matters")
"""),
md("""## Step 3 — Maximum likelihood: Gaussian noise ⇒ OLS

If $y_i = b_0 + b_1x_i + \\varepsilon_i$ with $\\varepsilon_i \\sim N(0,\\sigma^2)$, the log-likelihood is

$$\\ell(b,\\sigma) = -\\frac{n}{2}\\log(2\\pi\\sigma^2) - \\frac{1}{2\\sigma^2}\\underbrace{\\sum (y_i - b_0 - b_1x_i)^2}_{SSR}$$

For any fixed σ, maximising ℓ means **minimising SSR**. So the MLE of b is the OLS estimate,
and the MLE of σ² is SSR/n (biased; OLS reports the unbiased SSR/(n−2)).
We check numerically by maximising ℓ with `scipy.optimize.minimize` — no least-squares formula used.
"""),
code("""import numpy as np
from scipy.optimize import minimize
import statsmodels.api as sm

rng = np.random.default_rng(242)
y = 1 + 2 * x + rng.normal(0, 2, n)

def neg_loglik(theta):
    b0, b1, log_sigma = theta
    s2 = np.exp(2 * log_sigma)
    r = y - b0 - b1 * x
    return 0.5 * n * np.log(2 * np.pi * s2) + 0.5 * np.sum(r ** 2) / s2

mle = minimize(neg_loglik, x0=[0.0, 0.0, 0.0], method='BFGS')
ols = sm.OLS(y, X).fit()
ssr = np.sum(ols.resid ** 2)
print(f"MLE (numerical optimiser): b0 = {mle.x[0]:.5f}  b1 = {mle.x[1]:.5f}  sigma^2 = {np.exp(2*mle.x[2]):.5f}")
print(f"OLS (closed form)        : b0 = {ols.params[0]:.5f}  b1 = {ols.params[1]:.5f}")
print(f"SSR / n       = {ssr/n:.5f}   <- MLE of sigma^2 (biased)")
print(f"SSR / (n - 2) = {ssr/(n-2):.5f}   <- what OLS reports (unbiased)")
print(f"\\nMax log-likelihood = {-mle.fun:.4f}   statsmodels llf = {ols.llf:.4f}")
print("This is the 'Log-Likelihood' line in every statsmodels summary (NB05, NB08).")
"""),
md("""## Step 4 — Computing OLS stably: normal equations vs QR vs SVD

The normal equations solve $(X^TX)b = X^Ty$. But $\\kappa(X^TX) = \\kappa(X)^2$: every digit of
ill-conditioning in X is **doubled**. With float64 (~16 digits), κ(X) ≈ 10⁸ leaves almost nothing.

- **QR:** $X = QR$, solve $Rb = Q^Ty$ — works with κ(X), not κ(X)²
- **SVD / `np.linalg.lstsq`:** most robust; also handles rank-deficient X (pseudo-inverse)

Test: a polynomial design $x, x^2, …, x^{p}$ on x ∈ [1, 2] — columns nearly identical. True coefficients all = 1.
"""),
code("""import numpy as np
import warnings

rng = np.random.default_rng(243)
xx = np.linspace(1, 2, 200)
print(f"{'degree':>6} {'cond(X)':>10} {'cond(XtX)':>10} | {'max coef error':>45}")
print(f"{'':>6} {'':>10} {'':>10} | {'inv(XtX)':>11} {'solve(XtX)':>11} {'QR':>10} {'lstsq/SVD':>10}")
for p in [3, 6, 9, 12]:
    Xp = np.vander(xx, p + 1, increasing=True)
    b_true = np.ones(p + 1)
    yy = Xp @ b_true                                  # noise-free: the exact answer is all ones
    XtX = Xp.T @ Xp
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        e_inv = np.abs(np.linalg.inv(XtX) @ Xp.T @ yy - b_true).max()
        e_solve = np.abs(np.linalg.solve(XtX, Xp.T @ yy) - b_true).max()
    Q, R = np.linalg.qr(Xp)
    e_qr = np.abs(np.linalg.solve(R, Q.T @ yy) - b_true).max()
    e_svd = np.abs(np.linalg.lstsq(Xp, yy, rcond=None)[0] - b_true).max()
    print(f"{p:>6} {np.linalg.cond(Xp):>10.1e} {np.linalg.cond(XtX):>10.1e} | "
          f"{e_inv:>11.1e} {e_solve:>11.1e} {e_qr:>10.1e} {e_svd:>10.1e}")
print("\\ncond(XtX) = cond(X)^2. The normal-equation errors blow up first; QR and SVD stay accurate far longer.")
"""),
md("""## Key Takeaways

| Result | Needs | Says |
|---|---|---|
| **Gauss–Markov (BLUE)** | linearity, E[ε\\|X]=0, equal variance, no autocorrelation, full rank | OLS has the smallest variance among linear unbiased estimators |
| — | **not** normality | uniform errors in Step 1 still give OLS the win |
| Broken equal variance | heteroscedastic errors | OLS still unbiased, but WLS is more efficient (Step 2) |
| **MLE** | Gaussian errors | maximising likelihood = minimising SSR → OLS = MLE; σ²_MLE = SSR/n |
| **Numerics** | — | κ(XᵀX) = κ(X)²: avoid `inv(XtX)`; use QR or `np.linalg.lstsq` (SVD) — sklearn and statsmodels already do |

**Correction to NB06:** when assumptions break, OLS is *not* automatically "the best among linear models":
heteroscedasticity/autocorrelation → GLS/WLS is more efficient; broken linearity or exogeneity → OLS is biased.
"""),
]

save(nb(cells_21), "NB21_Feature_Scaling_GD.ipynb")
save(nb(cells_22), "NB22_Categorical_Encoding.ipynb")
save(nb(cells_23), "NB23_Confidence_vs_Prediction_Intervals.ipynb")
save(nb(cells_24), "NB24_Why_Least_Squares.ipynb")
