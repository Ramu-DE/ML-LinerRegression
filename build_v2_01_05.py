# -*- coding: utf-8 -*-
"""Rebuild NB01-NB05: StatQuest-style intuition + flow diagrams"""
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

# ── Shared flow-diagram helper (embedded in every notebook) ──────────────────
FLOW_HELPER = """\
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

def flow_diagram(steps, title, colors=None, notes=None, figsize=(14, 2.8)):
    \"\"\"Draw a horizontal flow diagram.  steps = list of strings.\"\"\"
    n = len(steps)
    default_colors = [
        '#1565C0','#2E7D32','#E65100','#6A1B9A',
        '#00695C','#AD1457','#37474F','#4E342E',
        '#0277BD','#558B2F',
    ]
    colors = (colors or default_colors[:n]) + default_colors
    notes  = notes or [''] * n

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(-0.3, n * 3.1)
    ax.set_ylim(-1.2, 2.4)
    ax.axis('off')

    bw, bh = 2.6, 1.3
    for i, (step, color, note) in enumerate(zip(steps, colors, notes)):
        x = i * 3.1
        box = FancyBboxPatch((x, 0.2), bw, bh,
                             boxstyle="round,pad=0.12",
                             facecolor=color, edgecolor='white', linewidth=1.5, alpha=0.90)
        ax.add_patch(box)
        ax.text(x + bw/2, 0.2 + bh/2, step,
                ha='center', va='center', fontsize=8.5,
                color='white', fontweight='bold', multialignment='center')
        if note:
            ax.text(x + bw/2, 0.02, note,
                    ha='center', va='top', fontsize=7, color='#555', style='italic')
        if i < n - 1:
            ax.annotate('',
                xy=(x + bw + 0.38, 0.2 + bh/2),
                xytext=(x + bw + 0.08, 0.2 + bh/2),
                arrowprops=dict(arrowstyle='->', color='#444', lw=2.2))

    ax.set_title(title, fontsize=11, fontweight='bold', pad=6, color='#222')
    plt.tight_layout(pad=0.4)
    plt.show()
"""

# =============================================================================
# NB01 — Intuition
# =============================================================================
cells_01 = [
md("""# NB01 — Linear Regression: Statistical Intuition

> **StatQuest principle: build the picture first, formula second.**

---

## The main ideas are:

1. You have two variables and you suspect one can **predict** the other
2. You fit a straight line through the data
3. The line is chosen to **minimise prediction errors** (residuals)
4. OLS = Ordinary Least Squares = the method that finds that unique best line

---

### Josh Starmer's framing (StatQuest):
> *"We want to fit a line to data. But which line? The one that makes the vertical distances between the points and the line as small as possible. And we square those distances so big errors are penalised more."*
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Collect\\n(x, y) pairs',
        'Scatter plot:\\nspot the trend',
        'Try many\\nlines',
        'Measure each\\nline\'s SSR',
        'Pick the line\\nwith min SSR',
        'Use it to\\npredict new y',
    ],
    notes=[
        'e.g. hours & score',
        'is it roughly linear?',
        'different b0, b1',
        'SSR = sum of\\nsquared residuals',
        'that\'s OLS!',
        'y = b0 + b1*x',
    ],
    title='NB01 Conceptual Flow: How Linear Regression Works',
    colors=['#1565C0','#2E7D32','#E65100','#6A1B9A','#C62828','#00695C'],
)
"""),
md("""## Step 1 — What does "fitting a line" mean?

A line has exactly **two numbers** to choose:

| Symbol | Name | Meaning |
|--------|------|---------|
| beta_0 (b0) | Intercept | predicted y when x = 0 |
| beta_1 (b1) | Slope | how much y changes for +1 unit of x |

**Equation:** `y_hat = b0 + b1 * x`

The hat on y_hat means "predicted value" (not the real y).
"""),
code("""import numpy as np
import matplotlib.pyplot as plt

# Study hours vs exam score — our running example
hours  = np.array([1,2,3,4,5,6,7,8,9,10], dtype=float)
scores = np.array([50,53,61,67,70,75,79,84,89,95], dtype=float)

# --- StatQuest moment: visualise the raw relationship first ---
fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(hours, scores, s=90, color='steelblue', zorder=3, label='Observed data')
ax.set_xlabel('Study hours', fontsize=12)
ax.set_ylabel('Exam score', fontsize=12)
ax.set_title('Step 1: Look at the data — is there a linear trend?', fontsize=12)
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout(); plt.show()

print("Key question: can we draw ONE straight line that is 'close' to all points?")
print("If yes -> linear regression is appropriate.")
"""),
md("""## Step 2 — Residuals: the core idea

For each data point the **residual** (error) is:

```
residual_i  =  y_i  -  y_hat_i   =  actual  -  predicted
```

- Positive residual: line **under**-predicted
- Negative residual: line **over**-predicted
- Zero residual: perfect prediction

**Why do we care?** Because OLS finds the line that makes ALL residuals as small as possible simultaneously.
"""),
code("""# Show two different lines and their residuals
import numpy as np
import matplotlib.pyplot as plt

def plot_line_residuals(ax, hours, scores, b0, b1, title, color):
    y_pred = b0 + b1 * hours
    ssr    = np.sum((scores - y_pred)**2)
    ax.scatter(hours, scores, s=70, color='steelblue', zorder=4)
    ax.plot(hours, y_pred, color=color, linewidth=2.5, label=f'b0={b0}, b1={b1}')
    for xi, yi, yp in zip(hours, scores, y_pred):
        ax.vlines(xi, min(yi,yp), max(yi,yp), color='tomato', linewidth=2, alpha=0.7)
    ax.set_title(f'{title}\\nSSR = {ssr:.1f}', fontsize=10)
    ax.set_xlabel('Hours'); ax.set_ylabel('Score')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

# True OLS line
xbar = hours.mean(); ybar = scores.mean()
b1_ols = np.sum((hours-xbar)*(scores-ybar)) / np.sum((hours-xbar)**2)
b0_ols = ybar - b1_ols * xbar

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
plot_line_residuals(axes[0], hours, scores, 30, 7,   'Bad line (b1=7)', 'orange')
plot_line_residuals(axes[1], hours, scores, 40, 5.5, 'Better line (b1=5.5)', 'purple')
plot_line_residuals(axes[2], hours, scores, b0_ols, b1_ols, 'OLS best-fit (minimum SSR)', 'crimson')

plt.suptitle('Red lines = residuals. OLS picks the line with the SMALLEST total squared residuals.',
             fontsize=11, y=1.01)
plt.tight_layout(); plt.show()

print(f"OLS line: score = {b0_ols:.2f} + {b1_ols:.2f} * hours")
print(f"Interpretation: each extra study hour adds {b1_ols:.2f} points on average")
"""),
md("""## Step 3 — Why SQUARE the residuals?

**StatQuest explanation:**
- If we just summed residuals, positives and negatives cancel out — a terrible line could score zero!
- Squaring makes ALL residuals positive
- Squaring penalises **big** errors much more than small ones (2x error = 4x penalty)
- The SSR surface is a smooth bowl with exactly ONE minimum — easy to find
"""),
code("""# Visualise why squaring works — show residuals as physical squares
import numpy as np
import matplotlib.pyplot as plt

b0, b1 = b0_ols, b1_ols
y_pred = b0 + b1*hours

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: residuals as vertical lines
ax = axes[0]
ax.scatter(hours, scores, s=70, color='steelblue', zorder=4)
ax.plot(hours, y_pred, 'r-', linewidth=2.5, label='Best-fit line')
for xi, yi, yp in zip(hours, scores, y_pred):
    ax.vlines(xi, min(yi,yp), max(yi,yp), color='orange', linewidth=2.5)
ax.set_title('Residuals as vertical distances', fontsize=10)
ax.set_xlabel('Hours'); ax.set_ylabel('Score')
ax.legend(); ax.grid(alpha=0.3)

# Right: residuals as squares (area = squared residual)
ax = axes[1]
ax.scatter(hours, scores, s=70, color='steelblue', zorder=4)
ax.plot(hours, y_pred, 'r-', linewidth=2.5, label='Best-fit line')
for xi, yi, yp in zip(hours, scores, y_pred):
    res   = yi - yp
    side  = abs(res)
    scale = 0.12          # visual scale factor for x-axis
    sq_x  = [xi, xi + side*scale, xi + side*scale, xi, xi]
    sq_y  = [yp, yp, yp + res, yp + res, yp]
    ax.fill(sq_x, sq_y, alpha=0.25, color='orange')
    ax.vlines(xi, min(yi,yp), max(yi,yp), color='orange', linewidth=2)

total_area = np.sum((scores - y_pred)**2)
ax.set_title(f'Squared residuals as squares\\nOLS minimises total area = {total_area:.1f}',
             fontsize=10)
ax.set_xlabel('Hours'); ax.set_ylabel('Score')
ax.legend(); ax.grid(alpha=0.3)

plt.suptitle('"Least Squares" = minimize the total area of all orange squares', fontsize=12)
plt.tight_layout(); plt.show()
"""),
md("""## Key Takeaways

| Term | StatQuest plain-English version |
|------|-------------------------------|
| Linear regression | Draw the best-fitting straight line through the data |
| b0 (intercept) | Where the line crosses the y-axis |
| b1 (slope) | How steep the line is — y change per x change |
| Residual | How far each point is from the line (vertically) |
| SSR | Total area of all squared-residual boxes |
| OLS | The method that finds the unique line with minimum SSR |

**Next: NB02 — where the formula `b1 = cov(x,y)/var(x)` comes from, derived step by step.**
"""),
]

# =============================================================================
# NB02 — OLS Derivation
# =============================================================================
cells_02 = [
md("""# NB02 — Where Does the OLS Formula Come From?

> **StatQuest principle: show the derivation step by step so it's never a black box.**

---

## The main ideas are:

1. SSR is a function of b0 and b1 — it's a **bowl-shaped surface**
2. At the lowest point of the bowl, the **slope** (derivative) is **zero**
3. Setting both partial derivatives to zero gives us two equations
4. Solving those two equations gives the formulas for b0 and b1
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Write SSR\\nas a function\\nof b0, b1',
        'Take partial\\nderivative\\nd(SSR)/db0 = 0',
        'Take partial\\nderivative\\nd(SSR)/db1 = 0',
        'Solve the 2\\nnormal\\nequations',
        'Get formulas:\\nb0 = y_bar - b1*x_bar\\nb1 = cov/var',
        'Matrix form:\\nb = (XtX)^-1 Xty',
    ],
    notes=[
        'SSR = sum(y - b0 - b1*x)^2',
        'minimum w.r.t. intercept',
        'minimum w.r.t. slope',
        '2 unknowns, 2 equations',
        'closed-form solution',
        'generalises to multiple X',
    ],
    title='NB02 Conceptual Flow: Deriving OLS Coefficients from Calculus',
    colors=['#1565C0','#2E7D32','#6A1B9A','#E65100','#C62828','#00695C'],
)
"""),
md("""## Step 1 — The SSR surface

SSR is a function of two unknowns: b0 and b1.

```
SSR(b0, b1) = sum_i ( y_i - b0 - b1*x_i )^2
```

Imagine a bowl: every (b0, b1) combination gives one SSR value.
The bowl has exactly ONE minimum — that's the OLS solution.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

hours  = np.array([1.,2.,3.,4.,5.,6.,7.,8.,9.,10.])
scores = np.array([50.,53.,61.,67.,70.,75.,79.,84.,89.,95.])

xbar = hours.mean();  ybar = scores.mean()
b1_ols = np.sum((hours-xbar)*(scores-ybar)) / np.sum((hours-xbar)**2)
b0_ols = ybar - b1_ols*xbar

# SSR on a grid
b0_grid = np.linspace(b0_ols - 20, b0_ols + 20, 60)
b1_grid = np.linspace(b1_ols - 3,  b1_ols + 3,  60)
B0, B1  = np.meshgrid(b0_grid, b1_grid)
SSR     = np.sum((scores - (B0[:,:,None] + B1[:,:,None]*hours[None,None,:]))**2, axis=2)

fig = plt.figure(figsize=(12, 4.5))

ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(B0, B1, SSR, cmap='viridis', alpha=0.7)
ax1.scatter([b0_ols], [b1_ols], [np.min(SSR)], color='red', s=80, zorder=5)
ax1.set_xlabel('b0'); ax1.set_ylabel('b1'); ax1.set_zlabel('SSR')
ax1.set_title('SSR bowl — one global minimum')

ax2 = fig.add_subplot(122)
cp = ax2.contourf(B0, B1, np.log(SSR+1), levels=25, cmap='viridis')
ax2.plot(b0_ols, b1_ols, 'r*', markersize=16, label='OLS minimum')
ax2.set_xlabel('b0 (intercept)'); ax2.set_ylabel('b1 (slope)')
ax2.set_title('Top-down view: contours of log(SSR)')
plt.colorbar(cp, ax=ax2, label='log(SSR+1)')
ax2.legend(fontsize=9)

plt.tight_layout(); plt.show()
print("The red star = OLS solution = the lowest point of the bowl")
"""),
md("""## Step 2 — Partial derivative with respect to b0

At the minimum, changing b0 by a tiny amount should NOT change SSR.
That means the partial derivative is zero:

```
d(SSR)/d(b0) = -2 * sum(y_i - b0 - b1*x_i) = 0

=> sum(y_i) = n*b0 + b1*sum(x_i)

=> b0 = y_bar - b1 * x_bar       <-- intercept formula
```

**Plain-English insight:** the regression line ALWAYS passes through the point (x_bar, y_bar).
The average point is always ON the line — guaranteed.
"""),
md("""## Step 3 — Partial derivative with respect to b1

Similarly for b1:

```
d(SSR)/d(b1) = -2 * sum( x_i*(y_i - b0 - b1*x_i) ) = 0

Substitute b0 = y_bar - b1*x_bar and simplify:

=> b1 = sum[(x_i - x_bar)(y_i - y_bar)]  /  sum[(x_i - x_bar)^2]

     = Cov(x, y)  /  Var(x)       <-- slope formula
```

**Plain-English insight:** the slope equals how much x and y move together (covariance), divided by how spread out x is (variance). If x and y move together a lot relative to x's spread -> steep slope.
"""),
code("""import numpy as np

X = np.array([1.,2.,3.,4.,5.])
y = np.array([2.,4.,5.,4.,5.])

xbar, ybar = X.mean(), y.mean()

# Every intermediate value shown
print(f"x_bar = {xbar:.2f},  y_bar = {ybar:.2f}")
print(f"{'x':>4} {'y':>4} {'x-xb':>6} {'y-yb':>6} {'(x-xb)(y-yb)':>14} {'(x-xb)^2':>10}")
print("-"*55)
num = 0; den = 0
for xi, yi in zip(X, y):
    xd, yd = xi-xbar, yi-ybar
    num += xd*yd; den += xd**2
    print(f"{xi:>4.0f} {yi:>4.0f} {xd:>6.2f} {yd:>6.2f} {xd*yd:>14.4f} {xd**2:>10.4f}")
print("-"*55)
print(f"{'Sum':>24} {num:>14.4f} {den:>10.4f}")
b1 = num/den;  b0 = ybar - b1*xbar
print(f"\\nb1 = {num:.4f} / {den:.4f} = {b1:.6f}")
print(f"b0 = {ybar:.4f} - {b1:.4f}*{xbar:.4f} = {b0:.6f}")
"""),
md("""## Step 4 — Matrix form (generalises to multiple X)

For multiple predictors, the same calculus gives:

```
Normal equations:  (X^T X) b = X^T y

Solution:  b_hat = (X^T X)^-1  X^T y
```

**X** is called the **design matrix**: one row per observation, one column per predictor, plus a column of 1s for the intercept.

The column of 1s captures b0 — that's why we add it.
"""),
code("""import numpy as np

X_raw = np.array([1.,2.,3.,4.,5.])
y     = np.array([2.,4.,5.,4.,5.])

# Design matrix: prepend a column of 1s
X_design = np.column_stack([np.ones(len(X_raw)), X_raw])
print("Design matrix X:")
print(X_design)

# Normal equations
XtX  = X_design.T @ X_design   # (X^T)(X) — 2x2 matrix
Xty  = X_design.T @ y          # (X^T)(y) — 2x1 vector
beta = np.linalg.solve(XtX, Xty)   # solve vs inv() — numerically safer

print(f"\\n(X^T X) =\\n{XtX}")
print(f"\\n(X^T y) = {Xty}")
print(f"\\nb_hat = [b0, b1] = {beta}")
print(f"\\nSame as formulas above: b0={b0:.6f}, b1={b1:.6f}")
print(f"Match: {np.allclose(beta, [b0, b1])}")
"""),
md("""## Key Takeaways

| Result | Formula | Intuition |
|--------|---------|-----------|
| Intercept | b0 = y_bar - b1*x_bar | line passes through (x_bar, y_bar) |
| Slope | b1 = Cov(x,y) / Var(x) | how much x and y co-vary, scaled by x's spread |
| Matrix form | b = (XtX)^-1 Xty | generalises to any number of predictors |
| Uniqueness | SSR bowl has one minimum | OLS solution is always unique (if X has full rank) |

**Next: NB03 — implement everything from scratch in pure Python.**
"""),
]

# =============================================================================
# NB03 — From Scratch
# =============================================================================
cells_03 = [
md("""# NB03 — Build OLS from Scratch (Pure Python)

> **The best way to understand a formula is to code it yourself, step by step.**

---

## The main ideas are:

1. Compute means of x and y
2. Use the slope formula: b1 = Cov / Var
3. Use the intercept formula: b0 = y_bar - b1 * x_bar
4. Compute residuals, SSR, MSE, RMSE, R²
5. Compute standard errors, t-statistics (for NB05 preview)
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Input\\nx, y arrays',
        'Compute\\nmeans\\nx_bar, y_bar',
        'Compute\\nb1 = Cov/Var\\n(slope)',
        'Compute\\nb0 = y_bar\\n- b1*x_bar',
        'Predict\\ny_hat =\\nb0 + b1*x',
        'Compute\\nresiduals\\ne = y - y_hat',
        'Compute\\nSSR, MSE\\nRMSE, R^2',
        'Compute\\nSE, t-stat',
    ],
    title='NB03 Conceptual Flow: OLS from Scratch',
    colors=['#37474F','#1565C0','#2E7D32','#E65100','#6A1B9A','#C62828','#00695C','#AD1457'],
)
"""),
code("""class OLSRegression:
    \"\"\"
    Full OLS simple linear regression built from scratch.
    Every formula is coded explicitly — no numpy linalg, no sklearn.
    \"\"\"

    def __init__(self):
        self.b0 = self.b1 = None

    # ── 1. Fit ────────────────────────────────────────────────────────────────
    def fit(self, X, y):
        n = len(X)
        assert n >= 2,          "Need at least 2 data points"
        assert len(y) == n,     "X and y must have the same length"

        x_bar = sum(X) / n
        y_bar = sum(y) / n

        # Slope: b1 = Cov(x,y) / Var(x)
        cov_xy = sum((X[i]-x_bar)*(y[i]-y_bar) for i in range(n))
        var_x  = sum((X[i]-x_bar)**2              for i in range(n))

        if var_x == 0:
            raise ValueError("All X values identical — cannot fit a line.")

        self.b1   = cov_xy / var_x
        self.b0   = y_bar - self.b1 * x_bar
        self._n   = n
        self._X   = X
        self._y   = y
        return self

    # ── 2. Predict ────────────────────────────────────────────────────────────
    def predict(self, X):
        return [self.b0 + self.b1 * xi for xi in X]

    # ── 3. Residuals ──────────────────────────────────────────────────────────
    def residuals(self, X=None, y=None):
        X = X or self._X;  y = y or self._y
        yhat = self.predict(X)
        return [y[i] - yhat[i] for i in range(len(y))]

    # ── 4. Error metrics ──────────────────────────────────────────────────────
    def ssr(self,   X=None, y=None): return sum(r**2 for r in self.residuals(X,y))
    def mse(self,   X=None, y=None): return self.ssr(X,y) / len(y or self._y)
    def rmse(self,  X=None, y=None): return self.mse(X,y)**0.5

    def r_squared(self, X=None, y=None):
        y  = y or self._y
        ym = sum(y)/len(y)
        ss_tot = sum((yi-ym)**2 for yi in y)
        if ss_tot == 0: return float('nan')
        return 1 - self.ssr(X,y) / ss_tot

    # ── 5. Standard errors (needed for t-tests) ────────────────────────────────
    def se_of_coefficients(self):
        \"\"\"
        sigma^2 = SSR / (n-2)   <- unbiased: divides by (n-2) NOT n
        SE(b1)  = sqrt(sigma^2 / sum(x - x_bar)^2)
        SE(b0)  = sqrt(sigma^2 * (1/n + x_bar^2 / sum(x-x_bar)^2))
        \"\"\"
        n, X, y = self._n, self._X, self._y
        sigma2  = self.ssr() / (n - 2)
        x_bar   = sum(X)/n
        sxx     = sum((xi-x_bar)**2 for xi in X)
        se_b1   = (sigma2 / sxx)**0.5
        se_b0   = (sigma2 * (1/n + x_bar**2/sxx))**0.5
        return se_b0, se_b1

    # ── 6. Summary ────────────────────────────────────────────────────────────
    def summary(self, X=None, y=None):
        X = X or self._X;  y = y or self._y
        se_b0, se_b1 = self.se_of_coefficients()
        t_b0 = self.b0 / se_b0
        t_b1 = self.b1 / se_b1
        r2   = self.r_squared(X, y)
        w = 60
        print("=" * w)
        print(f"  OLS Regression Summary")
        print("=" * w)
        print(f"  {'':12} {'Coef':>10}  {'SE':>10}  {'t-stat':>10}")
        print(f"  {'-'*47}")
        print(f"  {'b0 (intercept)':12} {self.b0:>10.4f}  {se_b0:>10.4f}  {t_b0:>10.4f}")
        print(f"  {'b1 (slope)':12}     {self.b1:>10.4f}  {se_b1:>10.4f}  {t_b1:>10.4f}")
        print("=" * w)
        print(f"  R^2  = {r2:.6f}   ({r2*100:.2f}% of variance explained)")
        print(f"  SSR  = {self.ssr():.4f}")
        print(f"  RMSE = {self.rmse():.4f}")
        print(f"  n    = {self._n}")
"""),
code("""# -- Run it on our salary dataset --
X = [1,2,3,4,5,6,7,8,9,10]
y = [40,45,50,55,65,70,75,85,90,95]

model = OLSRegression().fit(X, y)
model.summary()

import matplotlib.pyplot as plt
import numpy as np

y_hat = model.predict(X)
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Fit
axes[0].scatter(X, y, s=70, color='steelblue', zorder=3, label='Data')
axes[0].plot(X, y_hat, 'r-', linewidth=2.5, label=f'y = {model.b0:.2f} + {model.b1:.2f}x')
axes[0].set_xlabel('Years experience'); axes[0].set_ylabel('Salary ($k)')
axes[0].set_title('Fitted regression line'); axes[0].legend(); axes[0].grid(alpha=0.3)

# Residuals
resid = model.residuals()
axes[1].bar(range(1,11), resid, color=['steelblue' if r>0 else 'tomato' for r in resid])
axes[1].axhline(0, color='black', linewidth=1)
axes[1].set_xlabel('Observation'); axes[1].set_ylabel('Residual')
axes[1].set_title('Residuals — should look random, no pattern')
axes[1].grid(alpha=0.3, axis='y')

plt.tight_layout(); plt.show()
print("Residuals sum:", sum(resid))   # always exactly 0 for OLS
"""),
code("""# Cross-check against sklearn
from sklearn.linear_model import LinearRegression as SkLR
import numpy as np

X_arr = np.array(X).reshape(-1,1)
sk = SkLR().fit(X_arr, np.array(y))
print(f"Scratch:  b0={model.b0:.8f}  b1={model.b1:.8f}")
print(f"sklearn:  b0={sk.intercept_:.8f}  b1={sk.coef_[0]:.8f}")
print(f"Match: {np.allclose([model.b0,model.b1],[sk.intercept_,sk.coef_[0]])}")
"""),
md("""## Key Takeaways

| Step | Code | Why |
|------|------|-----|
| Slope | Cov(x,y)/Var(x) | How much x and y co-vary per unit of x spread |
| Intercept | y_bar - b1*x_bar | Anchors line through the mean point |
| Residuals sum | Always = 0 | OLS guarantees this by construction |
| sigma^2 = SSR/(n-2) | NOT n | We estimated 2 parameters, losing 2 degrees of freedom |

**Next: NB04 — what R^2 really measures, with SS decomposition.**
"""),
]

# =============================================================================
# NB04 — R^2, Residuals, SS Decomposition
# =============================================================================
cells_04 = [
md("""# NB04 — R-Squared: What Does It Actually Measure?

> **StatQuest: "R-squared is just the square of the correlation... but let's understand WHY."**

---

## The main ideas are:

1. Without a model, your best prediction for any y is just the **mean** (y_bar)
2. The regression model improves on that — it explains SOME of the variance
3. R^2 measures exactly HOW MUCH of the variance the model explains
4. R^2 = 1 means perfect. R^2 = 0 means your line is no better than guessing the mean.
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Baseline model:\\ny_hat = y_bar\\n(just the mean)',
        'Compute SS_tot:\\nsum(y - y_bar)^2\\ntotal variance in y',
        'Fit regression\\nmodel:\\ny_hat = b0 + b1*x',
        'Compute SS_res:\\nsum(y - y_hat)^2\\nunexplained variance',
        'SS_reg =\\nSS_tot - SS_res\\nexplained variance',
        'R^2 =\\nSS_reg / SS_tot\\n= 1 - SS_res/SS_tot',
        'Interpretation:\\n0 = no improvement\\n1 = perfect fit',
    ],
    title='NB04 Conceptual Flow: R-Squared via Sum-of-Squares Decomposition',
    colors=['#37474F','#1565C0','#2E7D32','#E65100','#6A1B9A','#C62828','#00695C'],
    figsize=(16, 2.8),
)
"""),
md("""## The key decomposition

```
SS_tot = SS_reg + SS_res        (always true — variance partitions perfectly)

SS_tot = sum(y_i - y_bar)^2    <- total spread in y  (baseline model)
SS_res = sum(y_i - y_hat_i)^2  <- unexplained spread  (residuals)
SS_reg = sum(y_hat_i - y_bar)^2 <- explained spread   (what regression adds)

R^2 = 1 - SS_res / SS_tot   =   SS_reg / SS_tot
```

**StatQuest framing:** imagine SS_tot is $100. If SS_res = $20, then SS_reg = $80, so R^2 = 0.80. The model explained 80% of the variation in y.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

np.random.seed(42)
X = np.linspace(1, 10, 40)
y = 3*X + np.random.normal(0, 4, 40) + 5

m     = LinearRegression().fit(X.reshape(-1,1), y)
y_hat = m.predict(X.reshape(-1,1))
y_bar = y.mean()

ss_tot = np.sum((y - y_bar)**2)
ss_res = np.sum((y - y_hat)**2)
ss_reg = np.sum((y_hat - y_bar)**2)
r2     = 1 - ss_res/ss_tot

print("SS decomposition")
print(f"  SS_tot = {ss_tot:.2f}   (total variance in y)")
print(f"  SS_res = {ss_res:.2f}   (unexplained — residuals)")
print(f"  SS_reg = {ss_reg:.2f}   (explained by regression)")
print(f"  SS_tot - SS_reg - SS_res = {ss_tot-ss_reg-ss_res:.10f}  (exactly 0)")
print(f"  R^2    = 1 - {ss_res:.2f}/{ss_tot:.2f} = {r2:.4f}")
print(f"  Meaning: the model explains {r2*100:.1f}% of the variance in y")
"""),
code("""# Visualise all three SS components on the same plot
import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
configs = [
    (y_bar*np.ones_like(X), 'SS_tot',  y_bar,  '#1565C0', 'Each bar = (y_i - y_bar)^2\\n= Total variance in y'),
    (y_hat,                  'SS_res',  y_hat,  '#C62828', 'Each bar = (y_i - y_hat_i)^2\\n= Unexplained variance'),
    (y_hat,                  'SS_reg',  y_bar,  '#2E7D32', 'Each bar = (y_hat_i - y_bar)^2\\n= Explained variance'),
]

for ax, (ref_line, ss_name, lower, color, desc) in zip(axes, configs):
    ax.scatter(X, y, s=20, color='steelblue', alpha=0.7, zorder=3)
    ax.plot(X, y_hat, 'r-', linewidth=1.5, label='Fitted line')
    ax.axhline(y_bar, color='gray', linestyle='--', linewidth=1.2, label='y_bar')

    if ss_name == 'SS_reg':
        ax.vlines(X, y_bar, y_hat, color=color, alpha=0.6, linewidth=2)
    elif ss_name == 'SS_res':
        ax.vlines(X, y_hat, y, color=color, alpha=0.6, linewidth=2)
    else:
        ax.vlines(X, y_bar, y, color=color, alpha=0.6, linewidth=2)

    ax.set_title(f'{ss_name}\\n{desc}', fontsize=9)
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

plt.suptitle(f'SS_tot = SS_reg + SS_res    |    R^2 = SS_reg/SS_tot = {r2:.3f}',
             fontsize=12, fontweight='bold')
plt.tight_layout(); plt.show()
"""),
code("""# Show intuitively: compare mean-only model vs regression model
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

# Mean-only model
ax = axes[0]
ax.scatter(X, y, s=30, color='steelblue', alpha=0.7, zorder=3)
ax.axhline(y_bar, color='gray', linestyle='--', linewidth=2.5, label=f'Mean model: y = {y_bar:.1f}')
ax.vlines(X, y_bar, y, color='#1565C0', alpha=0.5, linewidth=1.5)
ax.set_title(f'Baseline: always predict mean\\nSS_tot = {ss_tot:.1f}  (R^2 = 0.0)', fontsize=10)
ax.legend(); ax.grid(alpha=0.3)

# Regression model
ax = axes[1]
ax.scatter(X, y, s=30, color='steelblue', alpha=0.7, zorder=3)
ax.plot(X, y_hat, 'r-', linewidth=2.5, label='Regression line')
ax.vlines(X, y_hat, y, color='#C62828', alpha=0.5, linewidth=1.5)
ax.set_title(f'Regression: predict with x\\nSS_res = {ss_res:.1f}  (R^2 = {r2:.3f})', fontsize=10)
ax.legend(); ax.grid(alpha=0.3)

plt.suptitle('R^2 answers: "How much better is the regression line than just guessing the mean?"',
             fontsize=11)
plt.tight_layout(); plt.show()
"""),
md("""## What R^2 does NOT tell you

| Misconception | Truth |
|---------------|-------|
| High R^2 -> model is correct | Wrong relationship can still have high R^2 |
| R^2 = 0.9 means the model is good | Depends on the domain (astronomy vs. social science) |
| Adding predictors improves the model | R^2 always increases — use Adjusted R^2 |
| R^2 measures prediction accuracy | It measures variance explained, not forecast accuracy |

**Adjusted R^2 corrects for number of predictors:**
```
R^2_adj = 1 - (1-R^2) * (n-1) / (n-k-1)
```
"""),
code("""# Demonstrate Adjusted R^2 vs R^2
import numpy as np
from sklearn.linear_model import LinearRegression

np.random.seed(0)
n = 60
y_rand = np.random.randn(n)

r2s, r2adjs = [], []
for k in range(1, 25):
    X_noise = np.random.randn(n, k)
    m = LinearRegression().fit(X_noise, y_rand)
    yh = m.predict(X_noise)
    ssr = np.sum((y_rand-yh)**2)
    sst = np.sum((y_rand-y_rand.mean())**2)
    r2  = 1 - ssr/sst
    r2a = 1 - (1-r2)*(n-1)/(n-k-1)
    r2s.append(r2); r2adjs.append(r2a)

import matplotlib.pyplot as plt
plt.figure(figsize=(8, 4))
plt.plot(range(1,25), r2s,    'o-', label='R^2',          color='crimson',   linewidth=2)
plt.plot(range(1,25), r2adjs, 's--',label='Adjusted R^2', color='steelblue', linewidth=2)
plt.axhline(0, color='gray', linewidth=0.8)
plt.xlabel('Number of NOISE (useless) predictors'); plt.ylabel('R^2 score')
plt.title('R^2 rises with irrelevant features; Adjusted R^2 correctly stays near 0')
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
md("""## Key Takeaways

| Metric | Formula | Meaning |
|--------|---------|---------|
| SS_tot | sum(y - y_bar)^2 | Total variability in y |
| SS_res | sum(y - y_hat)^2 | What the model COULDN'T explain |
| SS_reg | SS_tot - SS_res | What the model DID explain |
| R^2 | 1 - SS_res/SS_tot | Fraction of variance explained (0 to 1) |
| Adjusted R^2 | 1 - (1-R^2)(n-1)/(n-k-1) | R^2 penalised for adding useless predictors |

**Next: NB05 — how we decide whether a coefficient is statistically significant.**
"""),
]

# =============================================================================
# NB05 — Statistical Inference
# =============================================================================
cells_05 = [
md("""# NB05 — Statistical Inference: t-tests, p-values, Confidence Intervals

> **This is the heart of the StatQuest video: "Is this slope real, or could it be zero by chance?"**

---

## The main ideas are:

1. Our estimated b1 is based on a **sample** — if we got new data, b1 would be slightly different
2. The **Standard Error (SE)** measures how much b1 varies from sample to sample
3. The **t-statistic** = b1 / SE asks: "how many standard errors away from zero is our estimate?"
4. The **p-value** answers: "if the true slope were zero, how often would we get a t-stat this large by chance?"
5. A **confidence interval** gives a range of plausible values for b1
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Null hypothesis:\\nb1 = 0\\n(no relationship)',
        'Estimate b1\\nfrom data\\n(OLS)',
        'Compute SE(b1):\\nhow uncertain\\nis b1?',
        't-stat =\\nb1 / SE(b1)\\nsignal/noise',
        'p-value:\\nP(|t| > t_obs)\\nif H0 true',
        'Decision:\\np < 0.05?\\n-> reject H0',
        '95% CI:\\nb1 +/- t* * SE\\nplausible range',
    ],
    title='NB05 Conceptual Flow: Statistical Inference for Regression Coefficients',
    colors=['#C62828','#1565C0','#2E7D32','#E65100','#6A1B9A','#00695C','#AD1457'],
    figsize=(16, 2.8),
)
"""),
md("""## Step 1 — The Null Hypothesis

The null hypothesis is always:
```
H0: b1 = 0   (x has NO linear relationship with y)
```

We don't believe the null — we test it. We ask: *"If the slope really were zero, how surprising would our data be?"*

If the answer is "very surprising (p < 0.05)" -> we reject H0 -> the slope is statistically significant.
"""),
code("""import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

np.random.seed(7)
n = 40
X = np.linspace(1, 10, n)
true_b1 = 2.5
y = true_b1*X + 5 + np.random.normal(0, 4, n)

xbar, ybar = X.mean(), y.mean()
b1 = np.sum((X-xbar)*(y-ybar)) / np.sum((X-xbar)**2)
b0 = ybar - b1*xbar

print(f"True slope: {true_b1}")
print(f"Estimated slope (b1): {b1:.4f}")
print(f"Null hypothesis: H0: b1 = 0")
"""),
md("""## Step 2 — Standard Error of b1

**Key intuition (StatQuest style):**
- If you ran this experiment 1000 times and got a b1 each time, those b1s would form a distribution
- The **standard deviation of that sampling distribution** is the Standard Error
- SE measures uncertainty: large SE = b1 could be very different with new data

```
sigma^2 = SSR / (n-2)        <- estimated variance of residuals
SE(b1)  = sqrt(sigma^2 / sum(x - x_bar)^2)
```

Note: divides by **(n-2)** not n, because we estimated 2 parameters (b0 and b1).
"""),
code("""import numpy as np, scipy.stats as stats, matplotlib.pyplot as plt

y_hat  = b0 + b1*X
resid  = y - y_hat
n      = len(y)
df     = n - 2                                # degrees of freedom

sigma2 = np.sum(resid**2) / df               # unbiased residual variance
sxx    = np.sum((X-xbar)**2)

se_b1 = np.sqrt(sigma2 / sxx)
se_b0 = np.sqrt(sigma2 * (1/n + xbar**2/sxx))

print(f"Residual variance sigma^2 = {sigma2:.4f}")
print(f"SE(b0) = {se_b0:.4f}   (uncertainty in intercept)")
print(f"SE(b1) = {se_b1:.4f}   (uncertainty in slope)")
print()
print("Intuition: if SE(b1) is large, b1 could vary a lot with new data.")
print(f"Our b1 = {b1:.4f} is about {b1/se_b1:.1f} SE's away from zero.")
"""),
md("""## Step 3 — The t-statistic

```
t = b1 / SE(b1)
```

Think of it as a **signal-to-noise ratio**:
- b1 is the signal (size of the effect)
- SE(b1) is the noise (uncertainty)
- t = signal / noise

Rule of thumb: |t| > 2 is roughly significant at the 5% level (for large n).
"""),
code("""# Compute t-statistics and visualise where they fall on the t-distribution
import numpy as np, scipy.stats as stats, matplotlib.pyplot as plt

t_b0 = b0 / se_b0
t_b1 = b1 / se_b1
p_b0 = 2 * stats.t.sf(abs(t_b0), df)    # two-sided p-value
p_b1 = 2 * stats.t.sf(abs(t_b1), df)

print(f"{'':15} {'Coef':>10}  {'SE':>10}  {'t-stat':>10}  {'p-value':>12}")
print("-"*62)
print(f"{'b0 (intercept)':15} {b0:>10.4f}  {se_b0:>10.4f}  {t_b0:>10.4f}  {p_b0:>12.6f}")
print(f"{'b1 (slope)':15}     {b1:>10.4f}  {se_b1:>10.4f}  {t_b1:>10.4f}  {p_b1:>12.6f}")

# Visualise the t-distribution and p-value for b1
t_vals = np.linspace(-6, 6, 400)
t_pdf  = stats.t.pdf(t_vals, df)

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(t_vals, t_pdf, 'b-', linewidth=2, label=f't-distribution (df={df})')
# Shade the p-value area
ax.fill_between(t_vals, t_pdf,
                where=(t_vals >= abs(t_b1)), color='crimson', alpha=0.4,
                label=f'p/2 (right tail)')
ax.fill_between(t_vals, t_pdf,
                where=(t_vals <= -abs(t_b1)), color='crimson', alpha=0.4,
                label=f'p/2 (left tail)')
ax.axvline(t_b1, color='crimson', linestyle='--', linewidth=2,
           label=f'Observed t = {t_b1:.2f}')
ax.axvline(-t_b1, color='crimson', linestyle='--', linewidth=2)
ax.set_xlabel('t value'); ax.set_ylabel('Probability density')
ax.set_title(f'p-value = {p_b1:.6f} = shaded area\\n'
             f'"If H0: b1=0 were true, we would see |t| >= {abs(t_b1):.2f} only {p_b1*100:.4f}% of the time"')
ax.legend(fontsize=8); ax.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
md("""## Step 4 — Confidence Intervals

```
95% CI for b1:  [ b1 - t* * SE(b1),   b1 + t* * SE(b1) ]
```

where t* is the critical value (about 1.96 for large n).

**StatQuest interpretation:**
> "If we repeated this experiment 100 times, about 95 of the resulting CIs would contain the true slope."

**NOT:** "There is a 95% probability the true slope is in this interval."
(The true slope is a fixed number — it's either in the interval or it isn't.)

**Connection:** if the 95% CI does NOT include 0 -> p < 0.05 (they are mathematically equivalent).
"""),
code("""import numpy as np, scipy.stats as stats, matplotlib.pyplot as plt

t_crit = stats.t.ppf(0.975, df)    # t* for 95% CI, two-sided
print(f"t* (critical value, df={df}): {t_crit:.4f}")

ci_b0 = (b0 - t_crit*se_b0, b0 + t_crit*se_b0)
ci_b1 = (b1 - t_crit*se_b1, b1 + t_crit*se_b1)
print(f"95% CI for b0: [{ci_b0[0]:.3f}, {ci_b0[1]:.3f}]")
print(f"95% CI for b1: [{ci_b1[0]:.3f}, {ci_b1[1]:.3f}]")
print(f"True slope ({true_b1}) inside CI: {ci_b1[0] < true_b1 < ci_b1[1]}")
print(f"CI excludes 0: {ci_b1[0] > 0 or ci_b1[1] < 0}  -> same as p < 0.05")

# Simulate many experiments to verify "95 out of 100 CIs contain true value"
np.random.seed(42)
contains = 0
ci_list  = []
for _ in range(200):
    y_sim  = true_b1*X + 5 + np.random.normal(0, 4, n)
    ybar_s = y_sim.mean()
    b1_s   = np.sum((X-xbar)*(y_sim-ybar_s)) / sxx
    b0_s   = ybar_s - b1_s*xbar
    resid_s= y_sim - (b0_s + b1_s*X)
    sig2_s = np.sum(resid_s**2)/(n-2)
    se_s   = np.sqrt(sig2_s/sxx)
    lo, hi = b1_s - t_crit*se_s, b1_s + t_crit*se_s
    ci_list.append((lo, hi, lo < true_b1 < hi))
    if lo < true_b1 < hi: contains += 1

print(f"\\nSimulation: {contains}/200 CIs contain the true slope ({contains/2:.1f}%)")
print("Expected: ~95%")

fig, ax = plt.subplots(figsize=(10, 5))
for i, (lo, hi, hit) in enumerate(ci_list[:80]):
    color = 'steelblue' if hit else 'crimson'
    ax.hlines(i, lo, hi, color=color, linewidth=1.5, alpha=0.7)
ax.axvline(true_b1, color='gold', linewidth=2.5, label=f'True slope = {true_b1}')
ax.set_xlabel('b1 value'); ax.set_ylabel('Simulation run')
ax.set_title(f'80 simulated 95% CIs — red ones MISS the true value (~5%)')
ax.legend(); ax.grid(alpha=0.3, axis='x'); plt.tight_layout(); plt.show()
"""),
code("""# Full statsmodels output — shows everything at once
import statsmodels.api as sm
import numpy as np

Xsm = sm.add_constant(X)
res = sm.OLS(y, Xsm).fit()
print(res.summary())
print("\\nAnnotations:")
print("  coef      = estimated coefficient")
print("  std err   = SE of the coefficient")
print("  t         = coef / std_err")
print("  P>|t|     = two-sided p-value")
print("  [0.025 0.975] = lower and upper 95% CI bounds")
"""),
md("""## Key Takeaways

| Term | Plain-English meaning |
|------|----------------------|
| SE(b1) | How much b1 would vary if we collected new data |
| t-stat | Signal-to-noise: how many SEs away from zero |
| p-value | "If H0 is true, how often do we see t this extreme?" |
| p < 0.05 | Statistically significant at 5% level |
| 95% CI | 95% of such intervals would contain the true b1 |
| CI excludes 0 | Exactly equivalent to p < 0.05 |

**Warning (StatQuest always says this):**
- p < 0.05 does NOT mean the effect is large
- p < 0.05 does NOT mean the result will replicate
- A large dataset can make tiny, useless effects "significant"

**Next: NB06 — the four assumptions OLS requires to be valid.**
"""),
]

# ── Save all 5 ────────────────────────────────────────────────────────────────
save(nb(cells_01), "NB01_Intuition.ipynb")
save(nb(cells_02), "NB02_OLS_Derivation.ipynb")
save(nb(cells_03), "NB03_From_Scratch.ipynb")
save(nb(cells_04), "NB04_R2_Residuals.ipynb")
save(nb(cells_05), "NB05_Statistical_Inference.ipynb")
print("Done - NB01 to NB05 rebuilt.")
