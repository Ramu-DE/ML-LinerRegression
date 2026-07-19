# -*- coding: utf-8 -*-
"""Rebuild NB06-NB10 with StatQuest intuition + flow diagrams"""
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
import matplotlib.patches as mpatches
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
# NB06 — OLS Assumptions (LINE)
# =============================================================================
cells_06 = [
md("""# NB06 — OLS Assumptions: LINE

> **StatQuest: "The math works perfectly... IF these four conditions hold."**

---

## The four assumptions spelled out:

| Letter | Name | Plain-English version |
|--------|------|-----------------------|
| **L** | Linearity | The true relationship is a straight line (not curved) |
| **I** | Independence | Knowing one observation tells you nothing about another |
| **N** | Normality | The errors (residuals) follow a bell curve |
| **E** | Equal variance | The spread of errors is the same everywhere (homoscedasticity) |

If any assumption breaks, OLS estimates are still the best you can do AMONG linear models,
but standard errors and p-values may be wrong.
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Fit OLS\\nmodel',
        'Check L:\\nResiduals\\nvs Fitted\\n(no curve?)',
        'Check I:\\nDurbin-Watson\\nACF plot\\n(no pattern?)',
        'Check N:\\nQ-Q plot\\nShapiro-Wilk\\n(on diagonal?)',
        'Check E:\\nScale-Location\\nBreusch-Pagan\\n(flat band?)',
        'All pass?\\nInference\\nis valid',
        'Violation?\\nTransform /\\nuse robust\\nmethods',
    ],
    title='NB06 Conceptual Flow: Checking the LINE Assumptions',
    colors=['#37474F','#1565C0','#2E7D32','#E65100','#6A1B9A','#00695C','#C62828'],
    figsize=(16, 2.8),
)
"""),
md("""## Assumption L — Linearity

**What it means:** the conditional mean of y is a linear function of x.
```
E[y | x] = b0 + b1*x
```

**How it breaks:** if the true relationship is curved (e.g. y = x^2), the linear model will under-predict in the middle and over-predict at the extremes.

**Diagnostic:** residuals vs fitted values plot — look for a CURVED pattern.
**Good sign:** random scatter around zero (no curve).
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

np.random.seed(42)
n = 80
X = np.linspace(1, 8, n)

fig, axes = plt.subplots(2, 2, figsize=(13, 8))

# GOOD: linear data
y_good = 2*X + 3 + np.random.normal(0, 1.5, n)
m_g = LinearRegression().fit(X.reshape(-1,1), y_good)
rg  = y_good - m_g.predict(X.reshape(-1,1))

axes[0,0].scatter(X, y_good, s=20, alpha=0.6, color='steelblue')
axes[0,0].plot(X, m_g.predict(X.reshape(-1,1)), 'r-', linewidth=2)
axes[0,0].set_title('GOOD: linear data'); axes[0,0].grid(alpha=0.3)

axes[1,0].scatter(m_g.predict(X.reshape(-1,1)), rg, s=20, alpha=0.6, color='steelblue')
axes[1,0].axhline(0, color='red', linewidth=1.5)
axes[1,0].set_xlabel('Fitted values'); axes[1,0].set_ylabel('Residuals')
axes[1,0].set_title('Good residuals: random scatter around 0'); axes[1,0].grid(alpha=0.3)

# BAD: non-linear data
y_bad = 0.5*X**2 + np.random.normal(0, 2, n)
m_b = LinearRegression().fit(X.reshape(-1,1), y_bad)
rb  = y_bad - m_b.predict(X.reshape(-1,1))

axes[0,1].scatter(X, y_bad, s=20, alpha=0.6, color='tomato')
axes[0,1].plot(X, m_b.predict(X.reshape(-1,1)), 'r-', linewidth=2)
axes[0,1].set_title('L VIOLATED: curved data, fitted with a line'); axes[0,1].grid(alpha=0.3)

axes[1,1].scatter(m_b.predict(X.reshape(-1,1)), rb, s=20, alpha=0.6, color='tomato')
axes[1,1].axhline(0, color='red', linewidth=1.5)
axes[1,1].set_xlabel('Fitted values'); axes[1,1].set_ylabel('Residuals')
axes[1,1].set_title('CURVED pattern in residuals -> linearity violated'); axes[1,1].grid(alpha=0.3)

plt.suptitle('Assumption L (Linearity): residuals vs fitted plot', fontsize=12)
plt.tight_layout(); plt.show()
"""),
md("""## Assumption I — Independence

**What it means:** knowing one observation's error gives you NO information about another's.

**When it breaks (common):**
- **Time series data:** today's residual is correlated with yesterday's (autocorrelation)
- **Clustered data:** students in the same class, patients at the same hospital
- **Repeated measures:** same person measured multiple times

**Consequence:** standard errors are underestimated -> t-tests are too liberal -> false positives.

**Diagnostic:** Durbin-Watson statistic (want ~2.0), ACF plot of residuals.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from statsmodels.stats.stattools import durbin_watson

np.random.seed(0)
n = 80
X = np.linspace(0, 10, n)

# Independent residuals (good)
e_ind  = np.random.normal(0, 1, n)
# Autocorrelated residuals (AR1, rho=0.85)
e_auto = np.zeros(n)
for i in range(1, n):
    e_auto[i] = 0.85*e_auto[i-1] + np.random.normal(0, 0.5)

from sklearn.linear_model import LinearRegression

fig, axes = plt.subplots(2, 2, figsize=(13, 7))
for col, (e, title) in enumerate([(e_ind,'GOOD: independent residuals'),
                                   (e_auto,'I VIOLATED: autocorrelated residuals')]):
    y = 2*X + 5 + e
    m = LinearRegression().fit(X.reshape(-1,1), y)
    resid = y - m.predict(X.reshape(-1,1))
    dw = durbin_watson(resid)

    axes[0,col].plot(resid, color='steelblue', linewidth=1)
    axes[0,col].axhline(0, color='red', linewidth=1)
    axes[0,col].set_title(f'{title}\\nDurbin-Watson = {dw:.2f} (want ~2)')
    axes[0,col].grid(alpha=0.3)

    # ACF manually
    lags = range(1, 21)
    acf_vals = [np.corrcoef(resid[:-lag], resid[lag:])[0,1] for lag in lags]
    axes[1,col].bar(lags, acf_vals, color='steelblue', alpha=0.7)
    axes[1,col].axhline(0, color='black', linewidth=0.8)
    axes[1,col].axhline(1.96/n**0.5,  color='blue', linewidth=1.2, linestyle='--', label='95% CI bounds')
    axes[1,col].axhline(-1.96/n**0.5, color='blue', linewidth=1.2, linestyle='--')
    axes[1,col].set_title('ACF of residuals (bars outside blue lines = autocorrelation)')
    axes[1,col].set_xlabel('Lag'); axes[1,col].legend(fontsize=7); axes[1,col].grid(alpha=0.3)

plt.suptitle('Assumption I (Independence): Durbin-Watson and ACF diagnostics', fontsize=12)
plt.tight_layout(); plt.show()
"""),
md("""## Assumption N — Normality of Residuals

**What it means:** the residuals come from a normal (Gaussian) distribution.

**Why it matters:** the t-test and F-test formulas assume normal residuals.
For large samples (n > 30+), the Central Limit Theorem partially rescues you.
For small samples, non-normality invalidates your p-values.

**Diagnostic:** Q-Q (quantile-quantile) plot — points should lie on a diagonal line.

**StatQuest framing:** "Plot each residual's quantile against what that quantile SHOULD be if the data were normal. Points on the line -> normal."
"""),
code("""import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

np.random.seed(1)
n = 80

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
configs = [
    (np.random.normal(0,1,n),              'GOOD: Normal residuals'),
    (np.random.exponential(1,n) - 1,        'N VIOLATED: Right-skewed'),
    (np.concatenate([np.random.normal(-3,1,10), np.random.normal(3,1,10),
                     np.random.normal(0,0.5,60)]),  'N VIOLATED: Heavy tails'),
]

for ax, (residuals, title) in zip(axes, configs):
    (osm, osr), (slope, intercept, r) = stats.probplot(residuals)
    ax.scatter(osm, osr, s=25, color='steelblue', alpha=0.7, zorder=3)
    xs = np.array([osm.min(), osm.max()])
    ax.plot(xs, slope*xs+intercept, 'r-', linewidth=2, label='Normal reference line')
    sw_stat, sw_p = stats.shapiro(residuals)
    ax.set_title(f'{title}\\nShapiro-Wilk p = {sw_p:.4f}', fontsize=9)
    ax.set_xlabel('Theoretical quantiles (if normal)'); ax.set_ylabel('Sample quantiles')
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

plt.suptitle('Assumption N (Normality): Q-Q plots — points on diagonal = normal residuals',
             fontsize=11)
plt.tight_layout(); plt.show()
print("Shapiro-Wilk: p < 0.05 -> reject normality")
"""),
md("""## Assumption E — Equal Variance (Homoscedasticity)

**What it means:** the spread of residuals is the SAME regardless of the fitted value.

**When it breaks (heteroscedasticity):**
- Income data: rich people have more variability in spending
- Size data: larger objects have larger absolute errors
- Time series: volatility clusters

**Consequence:** OLS is still unbiased, but SE is wrong -> invalid t-tests.

**Fix:** log-transform y, Weighted Least Squares (WLS), or use heteroscedasticity-robust standard errors (HC3).
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan

np.random.seed(3)
n = 100
X = np.linspace(1, 10, n)

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
configs = [
    (2*X + 5 + np.random.normal(0, 2, n),            'GOOD: Equal variance (homoscedastic)'),
    (2*X + 5 + np.random.normal(0, 0.4*X, n),        'E VIOLATED: Variance grows with x (hetero)'),
]
for ax, (y, title) in zip(axes, configs):
    Xsm = sm.add_constant(X)
    res = sm.OLS(y, Xsm).fit()
    std_resid = np.sqrt(np.abs(res.resid / (res.resid.std()+1e-10)))
    bp_stat, bp_p, *_ = het_breuschpagan(res.resid, Xsm)
    ax.scatter(res.fittedvalues, std_resid, s=25, alpha=0.6, color='steelblue')
    ax.axhline(np.sqrt(0.8), color='red', linewidth=1.5, linestyle='--',
               label='Approximate expected level')
    ax.set_xlabel('Fitted values'); ax.set_ylabel('sqrt(|standardised residuals|)')
    ax.set_title(f'{title}\\nBreusch-Pagan p = {bp_p:.4f}', fontsize=9)
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

plt.suptitle('Assumption E (Equal Variance): Scale-Location plot\\n'
             'Flat horizontal band = OK. Widening/narrowing = heteroscedasticity', fontsize=11)
plt.tight_layout(); plt.show()
print("Breusch-Pagan: p < 0.05 -> reject homoscedasticity")
"""),
md("""## Summary — What breaks when each assumption fails

| Assumption | What breaks | How bad? | Fix |
|-----------|------------|---------|-----|
| L (Linearity) | Biased coefficients and predictions | SEVERE | Polynomial, log-transform |
| I (Independence) | SE underestimated, too many false positives | SEVERE | Clustered SEs, mixed models |
| N (Normality) | p-values approximate, not exact | MILD for large n | Log/Box-Cox transform |
| E (Equal variance) | SE wrong, invalid t-tests | MODERATE | Robust SEs, WLS |

**Next: NB07 — the four standard diagnostic plots explained in detail.**
"""),
]

# =============================================================================
# NB07 — Diagnostic Plots
# =============================================================================
cells_07 = [
md("""# NB07 — Diagnostic Plots: The Four You Should Always Run

> **StatQuest: "Before trusting any regression result, look at the residuals."**

---

## The four standard plots:

1. **Residuals vs Fitted** — checks L and E (linearity, equal variance)
2. **Normal Q-Q** — checks N (normality of residuals)
3. **Scale-Location** — checks E again (heteroscedasticity)
4. **Residuals vs Leverage** — finds influential points that distort the fit

These four plots are what R's `plot(lm())` produces automatically.
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Fit OLS\\nmodel',
        'Plot 1:\\nResiduals\\nvs Fitted\\n(L and E)',
        'Plot 2:\\nNormal Q-Q\\n(N check)',
        'Plot 3:\\nScale-\\nLocation\\n(E check)',
        'Plot 4:\\nResiduals vs\\nLeverage\\n(influential pts)',
        'All clear?\\n-> Conclusions\\nvalid',
        'Problem found?\\n-> Diagnose\\nand fix',
    ],
    title='NB07 Conceptual Flow: Running the Four Diagnostic Plots',
    colors=['#37474F','#1565C0','#2E7D32','#E65100','#6A1B9A','#00695C','#C62828'],
    figsize=(16, 2.8),
)
"""),
code("""import numpy as np, matplotlib.pyplot as plt, scipy.stats as stats
import statsmodels.api as sm
from statsmodels.nonparametric.smoothers_lowess import lowess

np.random.seed(42)
n = 70
X_raw = np.linspace(1, 10, n)
y = 2.5*X_raw + 4 + np.random.normal(0, 2.5, n)
y[60] += 28    # inject one influential outlier

Xsm = sm.add_constant(X_raw)
result    = sm.OLS(y, Xsm).fit()
influence = result.get_influence()

fitted    = result.fittedvalues
resid     = result.resid
std_resid = influence.resid_studentized_internal
leverage  = influence.hat_matrix_diag
cooks_d   = influence.cooks_distance[0]

fig, axes = plt.subplots(2, 2, figsize=(13, 10))

# ── Plot 1: Residuals vs Fitted ──────────────────────────────────────────────
ax = axes[0,0]
ax.scatter(fitted, resid, s=25, alpha=0.6, color='steelblue')
ax.axhline(0, color='red', linewidth=1.5)
lo = lowess(resid, fitted, frac=0.4)
ax.plot(lo[:,0], lo[:,1], 'r-', linewidth=2.5, label='Lowess smoother')
ax.set_xlabel('Fitted values'); ax.set_ylabel('Residuals')
ax.set_title('1. Residuals vs Fitted\\nGood: random scatter around 0 (no curve, no funnel)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# ── Plot 2: Normal Q-Q ────────────────────────────────────────────────────────
ax = axes[0,1]
(osm, osr), (slope, intercept, _) = stats.probplot(std_resid)
ax.scatter(osm, osr, s=25, alpha=0.6, color='steelblue')
xs = np.array([osm.min(), osm.max()])
ax.plot(xs, slope*xs+intercept, 'r-', linewidth=2.5, label='Normal reference')
for i in np.argsort(np.abs(std_resid))[-3:]:
    ax.annotate(f'obs {i}', (osm[np.argsort(std_resid)[i]], osr[np.argsort(std_resid)[i]]),
                textcoords='offset points', xytext=(5,5), fontsize=7)
ax.set_xlabel('Theoretical quantiles'); ax.set_ylabel('Standardised residuals')
ax.set_title('2. Normal Q-Q\\nGood: points on diagonal line')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# ── Plot 3: Scale-Location ────────────────────────────────────────────────────
ax = axes[1,0]
sqrt_abs = np.sqrt(np.abs(std_resid))
ax.scatter(fitted, sqrt_abs, s=25, alpha=0.6, color='steelblue')
lo2 = lowess(sqrt_abs, fitted, frac=0.4)
ax.plot(lo2[:,0], lo2[:,1], 'r-', linewidth=2.5, label='Lowess smoother')
ax.set_xlabel('Fitted values'); ax.set_ylabel('sqrt(|Std. residuals|)')
ax.set_title('3. Scale-Location\\nGood: flat horizontal band (homoscedastic)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# ── Plot 4: Residuals vs Leverage ─────────────────────────────────────────────
ax = axes[1,1]
ax.scatter(leverage, std_resid, s=25, alpha=0.6, color='steelblue')
ax.axhline(0, color='gray', linewidth=0.8)
ax.axvline(4/n, color='orange', linewidth=1.5, linestyle='--', label=f'High leverage = 4/n')
ax.axhline(3,  color='red', linewidth=1.5, linestyle='--', label='|Std resid| = 3')
ax.axhline(-3, color='red', linewidth=1.5, linestyle='--')
for i in np.argsort(cooks_d)[-4:]:
    ax.annotate(f'obs {i}', (leverage[i], std_resid[i]),
                textcoords='offset points', xytext=(5,5), fontsize=7)
ax.set_xlabel('Leverage'); ax.set_ylabel('Standardised residuals')
ax.set_title("4. Residuals vs Leverage\\nWatch: top-right corner = influential points")
ax.legend(fontsize=8); ax.grid(alpha=0.3)

plt.suptitle("The Four Diagnostic Plots — Run EVERY TIME you fit a regression",
             fontsize=13, fontweight='bold')
plt.tight_layout(); plt.show()
"""),
md("""## How to read each plot — step by step

### Plot 1: Residuals vs Fitted
| Pattern | Meaning | Action |
|---------|---------|--------|
| Random scatter around y=0 | L and E both OK | None needed |
| U-shape or arch | Linearity violated | Add polynomial term |
| Funnel (wider on right) | Heteroscedasticity | Log-transform y or use WLS |

### Plot 2: Normal Q-Q
| Pattern | Meaning | Action |
|---------|---------|--------|
| Points on the diagonal | Normality OK | None needed |
| S-curve | Heavy tails | Robust regression |
| Skewed upward | Right skew | Log-transform y |

### Plot 3: Scale-Location
| Pattern | Meaning | Action |
|---------|---------|--------|
| Flat horizontal band | Homoscedastic | None needed |
| Rising band | Variance grows with fitted value | WLS, log(y) |

### Plot 4: Residuals vs Leverage (Cook's D)
| Zone | Meaning | Action |
|------|---------|--------|
| Low leverage + small residual | Normal point | None |
| High leverage + small residual | Unusual x, but fits well | Usually fine |
| Low leverage + large residual | Outlier in y (not influential) | Check for data error |
| **High leverage + large residual** | **Influential — changes the line!** | **Investigate carefully** |
"""),
code("""# Show what happens when you remove the influential point
import numpy as np, statsmodels.api as sm, matplotlib.pyplot as plt

mask_no_outlier = np.ones(n, dtype=bool)
mask_no_outlier[60] = False   # remove the injected outlier

Xsm_clean = sm.add_constant(X_raw[mask_no_outlier])
res_clean  = sm.OLS(y[mask_no_outlier], Xsm_clean).fit()

X_plot = np.linspace(1, 11, 200)
Xp_sm  = sm.add_constant(X_plot)

fig, ax = plt.subplots(figsize=(9, 5))
ax.scatter(X_raw, y, s=30, color='steelblue', alpha=0.7, label='Data', zorder=3)
ax.scatter([X_raw[60]], [y[60]], s=120, color='red', marker='*', zorder=4, label='Influential outlier')
ax.plot(X_plot, result.predict(Xp_sm),    'r-',  linewidth=2.5, label=f'With outlier  (b1={result.params[1]:.2f})')
ax.plot(X_plot, res_clean.predict(Xp_sm), 'g--', linewidth=2.5, label=f'Without outlier (b1={res_clean.params[1]:.2f})')
ax.set_xlabel('X'); ax.set_ylabel('y')
ax.set_title('Influential outlier pulls the regression line significantly')
ax.legend(); ax.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
md("""## Key Takeaways

| Plot | Assumption checked | Red flag |
|------|--------------------|----------|
| Residuals vs Fitted | Linearity (L), Equal variance (E) | Curve, funnel |
| Normal Q-Q | Normality (N) | Points off diagonal |
| Scale-Location | Equal variance (E) again | Rising trend |
| Residuals vs Leverage | Influential observations | Top-right cluster |

**Always run all four before reporting results.**

**Next: NB08 — Multiple regression: extend to many predictors.**
"""),
]

# =============================================================================
# NB08 — Multiple Regression
# =============================================================================
cells_08 = [
md("""# NB08 — Multiple Linear Regression

> **StatQuest: "Adding more variables means OLS needs to hold ALL other variables constant when estimating each coefficient."**

---

## The main ideas are:

1. Simple regression: one predictor, one slope
2. Multiple regression: many predictors, one slope PER predictor
3. Each slope means "effect of x_j, holding everything else constant"
4. The matrix normal equations generalise perfectly: b = (XtX)^-1 Xty
5. R^2 always increases with more variables — use Adjusted R^2 instead
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Multiple\\npredictors\\nx1, x2,...,xk',
        'Build design\\nmatrix X\\n(add col of 1s)',
        'Solve normal\\nequations:\\nb = (XtX)^-1 Xty',
        'Coefficients\\nb1...bk\\n(ceteris paribus)',
        'Evaluate:\\nR^2, Adj R^2\\nF-statistic',
        'Check VIF:\\nany collinear\\npredictors?',
        'Diagnostic\\nplots\\n(same 4 plots)',
    ],
    title='NB08 Conceptual Flow: Multiple Linear Regression',
    colors=['#1565C0','#2E7D32','#E65100','#6A1B9A','#C62828','#00695C','#AD1457'],
    figsize=(16, 2.8),
)
"""),
md("""## The "ceteris paribus" interpretation

**This is the single most important concept in multiple regression.**

When you have:
```
y = b0 + b1*x1 + b2*x2 + e
```

b1 means: *"Expected change in y for a 1-unit increase in x1, holding x2 CONSTANT."*

This is called **ceteris paribus** (Latin: all else equal).

**StatQuest example:** if y = salary, x1 = experience, x2 = education:
- b1 = 3000 means: one more year of experience -> $3000 more salary, *assuming same education level*
- This is DIFFERENT from the slope of experience in a simple regression (which ignores education)
"""),
code("""import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

housing  = fetch_california_housing()
X_df     = pd.DataFrame(housing.data, columns=housing.feature_names)
y        = housing.target   # median house value ($100k)

print("Dataset: California Housing")
print(f"  n = {len(y)} census blocks")
print(f"  k = {X_df.shape[1]} predictors")
print(f"  y = median house value (in $100k)")
print()
print(X_df.describe().round(2))
"""),
code("""import numpy as np
import statsmodels.api as sm
import pandas as pd
from sklearn.datasets import fetch_california_housing

housing = fetch_california_housing()
X_arr   = housing.data
y       = housing.target
names   = housing.feature_names

Xsm  = sm.add_constant(X_arr)
res  = sm.OLS(y, Xsm).fit()
print(res.summary(xname=['const']+list(names)))

print("\\n--- How to read this table ---")
print("coef     : slope for that predictor (holding all others constant)")
print("std err  : uncertainty (SE) of that coefficient")
print("t        : coef / std_err  (signal-to-noise ratio)")
print("P>|t|    : p-value  (< 0.05 = statistically significant)")
print("[0.025 0.975]: 95% confidence interval for the coefficient")
"""),
code("""# Coefficient plot — shows which predictors matter and their direction
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

scaler  = StandardScaler()
X_std   = scaler.fit_transform(X_arr)
Xsm_std = sm.add_constant(X_std)
res_std = sm.OLS(y, Xsm_std).fit()

coefs    = res_std.params[1:]    # skip intercept
ci_lo    = res_std.conf_int()[1:, 0]
ci_hi    = res_std.conf_int()[1:, 1]
pvals    = res_std.pvalues[1:]
sig      = pvals < 0.05

fig, ax = plt.subplots(figsize=(9, 5))
colors = ['#1565C0' if c > 0 else '#C62828' for c in coefs]
alpha  = [1.0 if s else 0.35 for s in sig]
for i, (c, lo, hi, color, a) in enumerate(zip(coefs, ci_lo, ci_hi, colors, alpha)):
    ax.errorbar(c, i, xerr=[[c-lo],[hi-c]], fmt='o', color=color,
                capsize=6, capthick=2, markersize=7, alpha=a)
ax.axvline(0, color='gray', linewidth=1.2, linestyle='--')
ax.set_yticks(range(len(names))); ax.set_yticklabels(names)
ax.set_xlabel('Standardised coefficient (+/- 95% CI)')
ax.set_title('Feature effects on house price (standardised)\\n'
             'Blue = positive, Red = negative, Faded = not significant')
ax.grid(alpha=0.3, axis='x'); plt.tight_layout(); plt.show()
print("Standardised coefficients let you compare effect SIZES across predictors")
print("(each predictor is on the same scale: 1 SD change)")
"""),
code("""# F-statistic: does the WHOLE model explain something?
import statsmodels.api as sm
import numpy as np

# Full model vs intercept-only model
Xsm  = sm.add_constant(X_arr)
full = sm.OLS(y, Xsm).fit()

print("F-statistic:", round(full.fvalue, 2))
print("F p-value:  ", round(full.f_pvalue, 10))
print()
print("H0 for F-test: ALL slopes are zero simultaneously")
print("If F p-value < 0.05: at least ONE predictor is useful")
print()
print("Compare: individual t-tests vs F-test")
print("  t-test: 'is THIS specific predictor useful?'")
print("  F-test: 'is the WHOLE MODEL better than just the mean?'")
"""),
md("""## Key Takeaways

| Concept | One-liner |
|---------|-----------|
| Multiple regression | y = b0 + b1*x1 + ... + bk*xk |
| Ceteris paribus | Each b_j is "effect of x_j, holding others constant" |
| Design matrix X | Rows = observations, Columns = [1, x1, x2,...,xk] |
| F-statistic | Does the whole model explain more than nothing? |
| Adjusted R^2 | R^2 penalised for adding useless predictors |

**Next: NB09 — what happens when x1 and x2 are correlated (multicollinearity).**
"""),
]

# =============================================================================
# NB09 — Multicollinearity
# =============================================================================
cells_09 = [
md("""# NB09 — Multicollinearity

> **StatQuest: "When two predictors tell the same story, the model can't figure out which one to credit."**

---

## The main ideas are:

1. Multicollinearity = two or more predictors are highly correlated with each other
2. This does NOT ruin predictions — R^2 is unaffected
3. This DOES ruin coefficient interpretation — SEs blow up, t-tests become unreliable
4. VIF (Variance Inflation Factor) measures how bad it is
5. Fixes: drop one predictor, use Ridge, use PCA first
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Suspected\\nmulticollinearity\\n(correlated X)',
        'Check correlation\\nheatmap',
        'Compute VIF\\nfor each X_j\\n(1 / (1 - R^2_j))',
        'VIF > 10?\\nSevere problem',
        'Diagnose:\\nSEs large?\\nt-stats low\\nbut R^2 high?',
        'Fix options:\\nDrop one X,\\nRidge, PCA,\\nmore data',
        'Re-check VIF\\nafter fix',
    ],
    title='NB09 Conceptual Flow: Detecting and Fixing Multicollinearity',
    colors=['#C62828','#1565C0','#2E7D32','#E65100','#6A1B9A','#00695C','#37474F'],
    figsize=(16, 2.8),
)
"""),
md("""## Why multicollinearity hurts interpretation

Imagine you want to know the effect of x1 on y, but x1 and x2 are nearly identical.
The model says: "I can explain y equally well by crediting x1, or x2, or half-and-half."
This ambiguity makes both coefficients unstable and their SEs huge.

**Key insight (StatQuest):**
> "Predictions are fine. Interpretations break."
"""),
code("""import numpy as np
import statsmodels.api as sm

np.random.seed(42)
n = 100
x1 = np.random.normal(0, 1, n)
x2 = 0.97*x1 + np.random.normal(0, 0.2, n)   # nearly identical to x1
y  = 3*x1 + 2*x2 + np.random.normal(0, 1, n)

print(f"Correlation(x1, x2) = {np.corrcoef(x1,x2)[0,1]:.3f}")
print()

# Individually: both are significant and correctly estimated
for name, xi in [('x1 only', x1), ('x2 only', x2)]:
    Xsm = sm.add_constant(xi)
    res = sm.OLS(y, Xsm).fit()
    print(f"--- {name} ---")
    print(f"  coef = {res.params[1]:.3f}  SE = {res.bse[1]:.3f}  p = {res.pvalues[1]:.4f}")

print()
# Together: SEs explode, both become "insignificant"
Xsm_both = sm.add_constant(np.column_stack([x1, x2]))
res_both = sm.OLS(y, Xsm_both).fit()
print("--- x1 AND x2 together ---")
print(f"  b1: coef = {res_both.params[1]:.3f}  SE = {res_both.bse[1]:.3f}  p = {res_both.pvalues[1]:.4f}")
print(f"  b2: coef = {res_both.params[2]:.3f}  SE = {res_both.bse[2]:.3f}  p = {res_both.pvalues[2]:.4f}")
print(f"  R^2 = {res_both.rsquared:.4f}  (unchanged — predictions are fine)")
print()
print("Notice: R^2 is high but individual p-values are not significant.")
print("This is the multicollinearity symptom.")
"""),
code("""# VIF — Variance Inflation Factor
# VIF_j = 1 / (1 - R^2_j)
# where R^2_j = R^2 from regressing x_j on all other x's

import numpy as np
import statsmodels.api as sm

def compute_vif(X_arr, names):
    n, k = X_arr.shape
    print(f"{'Feature':<15} {'VIF':>8}  Interpretation")
    print("-"*50)
    for j, name in enumerate(names):
        y_j  = X_arr[:,j]
        X_oth = np.delete(X_arr, j, axis=1)
        Xd    = sm.add_constant(X_oth)
        r2_j  = sm.OLS(y_j, Xd).fit().rsquared
        vif   = 1 / max(1-r2_j, 1e-9)
        interp = ('OK' if vif < 5 else
                  'Moderate' if vif < 10 else 'SEVERE -- action needed')
        print(f"{name:<15} {vif:>8.2f}  {interp}")

X_mat = np.column_stack([x1, x2])
print("VIF analysis:")
compute_vif(X_mat, ['x1','x2'])

print()
# VIF on real housing data
from sklearn.datasets import fetch_california_housing
housing = fetch_california_housing()
print("\\nCalifornia Housing VIF:")
compute_vif(housing.data, list(housing.feature_names))
"""),
code("""# Visualise the collinearity problem geometrically
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
n = 80

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

for ax, corr, title in zip(axes,
    [0.0, 0.7, 0.97],
    ['No collinearity (r=0.0)', 'Moderate (r=0.7)', 'Severe (r=0.97)']):
    x1 = np.random.normal(0,1,n)
    x2 = corr*x1 + np.sqrt(1-corr**2)*np.random.normal(0,1,n)
    y  = 3*x1 + 2*x2 + np.random.normal(0,1,n)
    X  = sm.add_constant(np.column_stack([x1,x2]))
    res = sm.OLS(y,X).fit()
    se1, se2 = res.bse[1], res.bse[2]
    ax.scatter(x1, x2, s=15, alpha=0.5, color='steelblue')
    ax.set_xlabel('x1'); ax.set_ylabel('x2')
    ax.set_title(f'{title}\\nSE(b1)={se1:.2f}  SE(b2)={se2:.2f}')
    ax.grid(alpha=0.3)

plt.suptitle('Higher correlation between predictors -> larger standard errors -> less reliable t-tests',
             fontsize=11)
plt.tight_layout(); plt.show()
"""),
md("""## Key Takeaways

| Symptom | What it means |
|---------|--------------|
| VIF > 10 | Severe multicollinearity — take action |
| High R^2, low t-stats | Classic multicollinearity fingerprint |
| Coefficients change sign when predictor added/removed | Severe multicollinearity |
| Predictions stable, interpretations unstable | Multicollinearity confirmed |

**Fixes ranked by simplicity:**
1. Drop one of the correlated predictors (if domain knowledge allows)
2. Collect more data (reduces SE naturally)
3. Ridge regression (NB11) — penalises large coefficients, stabilises SEs
4. PCA on correlated predictors, then regress on components

**Next: NB10 — polynomial regression and interaction terms.**
"""),
]

# =============================================================================
# NB10 — Polynomial & Interaction Terms
# =============================================================================
cells_10 = [
md("""# NB10 — Polynomial Regression and Interaction Terms

> **StatQuest: "A curved relationship is still linear regression — you just add x^2 as a new feature."**

---

## The main ideas are:

1. Linear in **parameters** (b0, b1, b2...) != linear in **variables** (x)
2. Adding x^2, x^3 as new columns -> still OLS, just more flexible
3. Risk: too many polynomial terms -> overfitting -> use cross-validation to choose degree
4. Interaction: b3*(x1*x2) -> effect of x1 DEPENDS on value of x2
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=[
        'Curved\\nrelationship\\ndetected',
        'Create polynomial\\nfeatures:\\nx, x^2, x^3, ...',
        'Fit OLS on\\nexpanded\\ndesign matrix',
        'Select degree\\nwith 5-fold\\ncross-validation',
        'Interaction?\\nAdd x1*x2\\nterm',
        'Interpret\\nb3 = how b1\\nchanges with x2',
        'Run all 4\\ndiagnostic\\nplots',
    ],
    title='NB10 Conceptual Flow: Polynomial Regression and Interaction Terms',
    colors=['#C62828','#1565C0','#2E7D32','#E65100','#6A1B9A','#00695C','#AD1457'],
    figsize=(16, 2.8),
)
"""),
md("""## Polynomial regression — the key insight

```
y = b0 + b1*x + b2*x^2 + b3*x^3 + e
```

This is STILL linear regression because:
- b0, b1, b2, b3 appear **linearly** (no b^2 or b*c terms)
- We just create new columns: X1=x, X2=x^2, X3=x^3
- Then OLS solves exactly as before

**Caution:** x^2 and x^3 are HIGHLY correlated with x -> VIF can be large.
Centre x first (subtract mean) to reduce this.
"""),
code("""import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, train_test_split

np.random.seed(0)
n = 80
X = np.sort(np.random.uniform(-3, 3, n))
y = 0.5*X**3 - X**2 + 2*X + np.random.normal(0, 3, n)

X_2d    = X.reshape(-1,1)
X_plot  = np.linspace(-3, 3, 300).reshape(-1,1)
X_tr, X_te, y_tr, y_te = train_test_split(X_2d, y, test_size=0.25, random_state=1)

fig, axes = plt.subplots(2, 4, figsize=(17, 8))
degrees = [1, 2, 3, 10]

for col, deg in enumerate(degrees):
    pipe = Pipeline([('poly', PolynomialFeatures(deg)), ('ols', LinearRegression())])
    pipe.fit(X_tr, y_tr)
    tr_r2 = pipe.score(X_tr, y_tr)
    te_r2 = pipe.score(X_te, y_te)
    cv_r2 = cross_val_score(pipe, X_2d, y, cv=5, scoring='r2').mean()

    ax = axes[0, col]
    ax.scatter(X, y, s=12, alpha=0.4, color='steelblue')
    ax.plot(X_plot, pipe.predict(X_plot), 'r-', linewidth=2.5)
    ax.set_title(f'Degree {deg}\\nTrain R^2={tr_r2:.3f}  Test R^2={te_r2:.3f}', fontsize=9)
    ax.set_ylim(-25, 30); ax.grid(alpha=0.3)

    ax = axes[1, col]
    y_hat_tr  = pipe.predict(X_tr)
    resid_tr  = y_tr - y_hat_tr
    ax.scatter(y_hat_tr, resid_tr, s=15, alpha=0.5, color='tomato')
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xlabel('Fitted'); ax.set_ylabel('Residual')
    label = 'UNDERFIT' if deg == 1 else ('GOOD FIT' if deg == 3 else
             'OK' if deg == 2 else 'OVERFIT')
    ax.set_title(f'{label}\\n5-fold CV R^2={cv_r2:.3f}', fontsize=9)
    ax.grid(alpha=0.3)

plt.suptitle('Polynomial regression: degree 1=underfit, 3=good, 10=overfit',
             fontsize=12, fontweight='bold')
plt.tight_layout(); plt.show()
"""),
md("""## Interaction terms — the "it depends" story

```
y = b0 + b1*x1 + b2*x2 + b3*(x1*x2) + e

Slope of x1 = b1 + b3*x2    <- depends on x2!
```

**StatQuest example:**
> "Does the effect of exercise on weight loss depend on diet? If yes, add an interaction term."

If b3 is large and significant: the effect of x1 is DIFFERENT for different values of x2.
If b3 is near zero: x1 and x2 have independent additive effects.
"""),
code("""import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

np.random.seed(7)
n = 200
edu   = np.random.binomial(1, 0.5, n).astype(float)    # 0 = no degree, 1 = degree
exper = np.random.uniform(1, 20, n)
# True DGP: experience matters MORE for degree holders
salary = 30 + 2.0*exper + 10*edu + 3.5*exper*edu + np.random.normal(0, 4, n)

# Model WITHOUT interaction
X_no = sm.add_constant(np.column_stack([exper, edu]))
res_no = sm.OLS(salary, X_no).fit()

# Model WITH interaction
X_int = sm.add_constant(np.column_stack([exper, edu, exper*edu]))
res_int = sm.OLS(salary, X_int).fit()

print("=== WITHOUT interaction ===")
print(res_no.summary().tables[1])
print("\\n=== WITH interaction (exper * edu) ===")
print(res_int.summary().tables[1])

print(f"\\nInterpretation of interaction coefficient ({res_int.params[3]:.2f}):")
print(f"  Slope of experience for NO-degree workers: {res_int.params[1]:.2f}")
print(f"  Slope of experience for YES-degree workers: {res_int.params[1]+res_int.params[3]:.2f}")

# Plot
xs = np.linspace(1, 20, 100)
b  = res_int.params
fig, ax = plt.subplots(figsize=(8, 5))
for g, color, label in [(0,'steelblue','No degree'), (1,'crimson','Has degree')]:
    mask = edu == g
    ax.scatter(exper[mask], salary[mask], s=12, alpha=0.3, color=color)
    ys = b[0] + b[1]*xs + b[2]*g + b[3]*xs*g
    ax.plot(xs, ys, color=color, linewidth=2.5, label=f'{label} (slope={b[1]+b[3]*g:.2f})')
ax.set_xlabel('Years experience'); ax.set_ylabel('Salary ($k)')
ax.set_title('Interaction: slope of experience is different per education group')
ax.legend(); ax.grid(alpha=0.3); plt.tight_layout(); plt.show()
"""),
md("""## Key Takeaways

| Technique | When to use | Watch out for |
|-----------|-------------|--------------|
| Polynomial (degree 2-3) | Clearly curved residuals | Overfitting; always use CV |
| Polynomial (degree > 5) | Rarely needed | Almost always overfits |
| Interaction x1*x2 | "Does effect of x1 depend on x2?" | Hard to interpret with 3+ way interactions |

**Cross-validation is mandatory for polynomial regression** — never choose degree by train R^2 alone.

**Next: NB11 — Ridge Regression (L2) to handle overfitting and multicollinearity.**
"""),
]

save(nb(cells_06), "NB06_OLS_Assumptions.ipynb")
save(nb(cells_07), "NB07_Diagnostic_Plots.ipynb")
save(nb(cells_08), "NB08_Multiple_Regression.ipynb")
save(nb(cells_09), "NB09_Multicollinearity.ipynb")
save(nb(cells_10), "NB10_Polynomial_Interaction.ipynb")
print("Done - NB06 to NB10 rebuilt.")
