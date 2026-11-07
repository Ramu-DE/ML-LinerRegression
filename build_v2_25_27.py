# -*- coding: utf-8 -*-
"""Build NB25-NB27: heteroscedasticity fixes, target transformations, model selection & pitfalls"""
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
# NB25 — Heteroscedasticity: detect it, then fix the standard errors
# =============================================================================
cells_25 = [
md("""# NB25 — Heteroscedasticity Fixes: Robust SEs, WLS and HAC

> **StatQuest principle: when the spread of the residuals changes, the line is still fine — it's the error bars that lie.**

---

## The main ideas are:

1. **Heteroscedasticity** = the variance of the residuals changes with x (a "funnel" in the residual plot)
2. OLS **coefficients stay unbiased**, but the classic standard errors, p-values and confidence intervals are **wrong**
3. **Detect** it: residual plot + Breusch–Pagan test (+ White test)
4. **Fix #1 — robust (HC3) standard errors:** same coefficients, honest uncertainty
5. **Fix #2 — Weighted Least Squares (WLS):** weight each point by 1/σᵢ² → more *efficient* (less noisy) estimates
6. **Autocorrelated errors** (time order) break SEs too → **HAC / Newey–West** standard errors

NB06 showed how to *diagnose* unequal variance. This notebook shows what to *do* about it.
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=['Fit OLS\\nas usual', 'Residual plot:\\nfunnel?', 'Breusch-Pagan /\\nWhite test', 'Fix 1:\\nHC3 robust SEs',
           'Fix 2:\\nWLS (1/sigma^2\\nweights)', 'Time order?\\nHAC / Newey-West'],
    title='NB25 Conceptual Flow: Heteroscedasticity — detect, then fix',
    notes=['coefficients OK', 'spread grows?', 'p < 0.05 = hetero', 'same b, new SE', 'more efficient', 'autocorrelation'],
    figsize=(16, 2.8),
)
"""),
md("""## Step 1 — Detect: residual plot + Breusch–Pagan + White

Data: the noise standard deviation grows with x:  σᵢ = 0.3 + 0.5·xᵢ, true line y = 3 + 2x.

- **Breusch–Pagan:** regress the squared residuals on X. If X explains them → variance depends on X.
- **White test:** same idea, but also uses squares and cross-products of X (catches non-linear variance patterns).
- H0 for both: *constant variance* (homoscedasticity). Small p-value → reject H0.
"""),
code("""import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan, het_white
import matplotlib.pyplot as plt

rng   = np.random.default_rng(3)
n     = 200
x     = rng.uniform(0, 10, n)
sigma = 0.3 + 0.5 * x                      # true noise SD grows with x
y     = 3 + 2 * x + rng.normal(0, sigma)
X     = sm.add_constant(x)

ols = sm.OLS(y, X).fit()
bp_lm, bp_p, _, _ = het_breuschpagan(ols.resid, X)
w_lm,  w_p,  _, _ = het_white(ols.resid, X)

print(f"OLS fit: y = {ols.params[0]:.4f} + {ols.params[1]:.4f} x   (true: 3 + 2x)")
print(f"Breusch-Pagan: LM = {bp_lm:.2f}, p = {bp_p:.2e}")
print(f"White test   : LM = {w_lm:.2f}, p = {w_p:.2e}")
print("-> p < 0.05: reject constant variance. Heteroscedasticity confirmed.")

fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].scatter(x, y, s=12, alpha=0.5); ax[0].plot(np.sort(x), ols.params[0] + ols.params[1]*np.sort(x), 'r', lw=2)
ax[0].set_title('Data + OLS line'); ax[0].set_xlabel('x'); ax[0].set_ylabel('y')
ax[1].scatter(ols.fittedvalues, ols.resid, s=12, alpha=0.5); ax[1].axhline(0, color='k', lw=1)
ax[1].set_title('Residuals vs fitted: the funnel'); ax[1].set_xlabel('fitted'); ax[1].set_ylabel('residual')
plt.tight_layout(); plt.show()
"""),
md("""## Step 2 — Fix #1: robust (heteroscedasticity-consistent) standard errors

The classic formula Var(b) = σ²(XᵀX)⁻¹ assumes **one** σ² for every point.
The **sandwich** estimator drops that assumption:

```
Var(b) = (XᵀX)⁻¹ · [ Σ wᵢ eᵢ² xᵢxᵢᵀ ] · (XᵀX)⁻¹        HC3: wᵢ = 1/(1 − hᵢᵢ)²
```

HC3 inflates residuals of high-leverage points (hᵢᵢ = hat-matrix diagonal) and is the recommended default for small/medium n.

**Key point:** the coefficients are *identical* — only SEs, t, p and CIs change.

In a **single** sample the robust SE can come out larger *or* smaller than the classic one — robust SEs are themselves noisy estimates.
What matters is their behaviour **on average**, which the coverage simulation below checks.
"""),
code("""hc3 = sm.OLS(y, X).fit(cov_type='HC3')

print(f"{'':10s}{'coef':>9s}{'classic SE':>12s}{'HC3 SE':>10s}{'classic 95% CI':>22s}{'HC3 95% CI':>22s}")
for i, name in enumerate(['const', 'x']):
    c_lo, c_hi = ols.conf_int()[i]
    h_lo, h_hi = hc3.conf_int()[i]
    print(f"{name:10s}{ols.params[i]:9.4f}{ols.bse[i]:12.4f}{hc3.bse[i]:10.4f}"
          f"   [{c_lo:7.4f}, {c_hi:7.4f}]   [{h_lo:7.4f}, {h_hi:7.4f}]")
print(f"\\nSame coefficients? {np.allclose(ols.params, hc3.params)}")
print(f"HC3 / classic SE  slope: {hc3.bse[1]/ols.bse[1]:.3f}   intercept: {hc3.bse[0]/ols.bse[0]:.3f}")
print("In this sample the HC3 slope SE happens to be a bit smaller; the intercept SE is much smaller.")
print("Classic SEs spread ONE average sigma^2 over all points, so they misstate uncertainty where noise is low or high.")
"""),
md("""### Does it matter? A coverage simulation

A correct 95% confidence interval should contain the true slope (2.0) in **95%** of repeated samples.
We repeat the experiment 2,000 times and count.
"""),
code("""def one_sample(rng, n=200):
    x = rng.uniform(0, 10, n)
    y = 3 + 2 * x + rng.normal(0, 0.3 + 0.5 * x)
    return x, y

rng_sim = np.random.default_rng(2024)
reps = 2000
cover_classic = cover_hc3 = 0
for _ in range(reps):
    xs, ys = one_sample(rng_sim)
    Xs = sm.add_constant(xs)
    lo, hi = sm.OLS(ys, Xs).fit().conf_int()[1]
    cover_classic += lo <= 2 <= hi
    lo, hi = sm.OLS(ys, Xs).fit(cov_type='HC3').conf_int()[1]
    cover_hc3 += lo <= 2 <= hi

print(f"95% CI coverage of the true slope over {reps} samples:")
print(f"  classic SEs : {cover_classic/reps:.1%}")
print(f"  HC3 SEs     : {cover_hc3/reps:.1%}")
print("-> on average the classic slope intervals are too narrow: they claim 95% but cover less; HC3 is on target.")
"""),
md("""## Step 3 — Fix #2: Weighted Least Squares (WLS)

Robust SEs fix the *error bars*. WLS goes further and fixes the *estimate itself*:
noisy points get **less say**, precise points get **more**.

```
minimise  Σ wᵢ (yᵢ − b0 − b1·xᵢ)²       with  wᵢ = 1 / σᵢ²
```

Under the right weights WLS is the **Best Linear Unbiased Estimator** (Gauss–Markov holds again after reweighting).

In practice σᵢ is unknown → **Feasible WLS**: model the variance from the OLS residuals
(here: regress log(eᵢ²) on x, then wᵢ = 1 / exp(fitted)).
"""),
code("""# Known weights
wls_known = sm.WLS(y, X, weights=1 / sigma**2).fit()

# Feasible WLS: estimate the variance function from OLS residuals
aux       = sm.OLS(np.log(ols.resid**2), X).fit()
w_hat     = 1 / np.exp(aux.fittedvalues)
wls_feas  = sm.WLS(y, X, weights=w_hat).fit()

for name, r in [('OLS', ols), ('WLS (known sigma)', wls_known), ('Feasible WLS', wls_feas)]:
    print(f"{name:18s} slope = {r.params[1]:.4f}   SE = {r.bse[1]:.4f}")
"""),
code("""# Efficiency: how much do the slope estimates scatter across repeated samples?
rng_sim = np.random.default_rng(7)
b_ols, b_wls, b_fwls = [], [], []
for _ in range(2000):
    xs = rng_sim.uniform(0, 10, 200); sd = 0.3 + 0.5 * xs
    ys = 3 + 2 * xs + rng_sim.normal(0, sd)
    Xs = sm.add_constant(xs)
    o  = sm.OLS(ys, Xs).fit()
    b_ols.append(o.params[1])
    b_wls.append(sm.WLS(ys, Xs, weights=1/sd**2).fit().params[1])
    a  = sm.OLS(np.log(o.resid**2), Xs).fit()
    b_fwls.append(sm.WLS(ys, Xs, weights=1/np.exp(a.fittedvalues)).fit().params[1])

b_ols, b_wls, b_fwls = map(np.array, (b_ols, b_wls, b_fwls))
print("Slope estimates over 2000 samples (true = 2.0):")
for name, b in [('OLS', b_ols), ('WLS known', b_wls), ('Feasible WLS', b_fwls)]:
    print(f"  {name:13s} mean = {b.mean():.4f}   SD = {b.std():.4f}")
print(f"\\nVariance ratio OLS / WLS(known): {b_ols.var()/b_wls.var():.2f}x")
print("-> all three are unbiased; WLS is noticeably more precise.")

fig, ax = plt.subplots(figsize=(9, 4))
bins = np.linspace(1.75, 2.25, 50)
ax.hist(b_ols, bins, alpha=0.5, label='OLS'); ax.hist(b_wls, bins, alpha=0.5, label='WLS (known weights)')
ax.axvline(2, color='k', ls='--', label='true slope')
ax.set_title('WLS estimates cluster tighter around the truth'); ax.set_xlabel('estimated slope'); ax.legend()
plt.tight_layout(); plt.show()
"""),
md("""## Step 4 — Autocorrelated errors: HAC (Newey–West) standard errors

With time-ordered data the errors are often **correlated** with their neighbours (NB06: Durbin–Watson far from 2).
Again the coefficients are unbiased, but classic SEs are typically **too small** when both x and the errors are positively autocorrelated.

**HAC** (heteroscedasticity- and autocorrelation-consistent, Newey–West) SEs account for correlation up to `maxlags` lags.
Rule of thumb: maxlags ≈ 4·(n/100)^(2/9).
"""),
code("""from statsmodels.stats.stattools import durbin_watson

rng = np.random.default_rng(0)
n   = 200
def ar1(rho, sd, n, rng):
    e = np.zeros(n)
    for t in range(1, n):
        e[t] = rho * e[t-1] + rng.normal(0, sd)
    return e
xt = ar1(0.8, 1.0, n, rng)               # a slowly moving predictor
et = ar1(0.8, 1.0, n, rng)               # autocorrelated errors
yt = 1 + 0.5 * xt + et
Xt = sm.add_constant(xt)

maxlags = int(np.floor(4 * (n / 100) ** (2 / 9)))
classic = sm.OLS(yt, Xt).fit()
hac     = sm.OLS(yt, Xt).fit(cov_type='HAC', cov_kwds={'maxlags': maxlags})

print(f"Durbin-Watson = {durbin_watson(classic.resid):.3f}   (2 = no autocorrelation)")
print(f"maxlags = {maxlags}")
print(f"slope = {classic.params[1]:.4f}")
print(f"  classic SE = {classic.bse[1]:.4f}   p = {classic.pvalues[1]:.2e}")
print(f"  HAC SE     = {hac.bse[1]:.4f}   p = {hac.pvalues[1]:.2e}")
print(f"HAC / classic SE: {hac.bse[1]/classic.bse[1]:.2f}x")
"""),
md("""## Key Takeaways

| Problem | Coefficients | Classic SEs | Fix |
|---|---|---|---|
| Heteroscedasticity | unbiased | wrong (here: too small) | **HC3 robust SEs** (always safe) or **WLS** (more efficient if you can model σᵢ) |
| Autocorrelation | unbiased | wrong (usually too small) | **HAC / Newey–West SEs**, or model the time structure (NB19) |
| Non-linearity | **biased** | — | Fix the model (NB10, NB26), not the SEs |

1. Heteroscedasticity does **not** bias OLS coefficients — it breaks their **uncertainty**.
2. `fit(cov_type='HC3')` is a one-line fix that keeps the coefficients and corrects SEs, p-values and CIs.
3. WLS with weights 1/σᵢ² is **BLUE** again → tighter estimates; Feasible WLS estimates the weights from residuals.
4. For time-ordered data use `cov_type='HAC'`.
5. Robust SEs are not a cure for a **wrong model**: if the residual plot curves, change the model.
"""),
]

# =============================================================================
# NB26 — Target transformations: log, Box–Cox and back-transforming
# =============================================================================
cells_26 = [
md("""# NB26 — Target Transformations: Log, Box–Cox and Back-Transforming

> **StatQuest principle: if the effect is a percentage, model it on a log scale.**

---

## The main ideas are:

1. Prices, incomes and counts are often **right-skewed** with effects that are **multiplicative** ("+0.8% per m²", not "+$X per m²")
2. Fitting **log(y)** turns multiplicative effects into additive ones and often fixes skewed, funnel-shaped residuals
3. Each log form has its own interpretation: **log-level, level-log, log-log (elasticity)**
4. **Box–Cox** searches for the best power transform λ (λ = 0 means log)
5. Back on the original scale, **exp(prediction) is a median, not a mean** → correct it with **Duan's smearing estimator**
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=['Skewed y?\\nfunnel residuals?', 'Try log(y)\\nor Box-Cox', 'Fit OLS on\\ntransformed y', 'Check residuals\\nagain',
           'Interpret:\\n% effects /\\nelasticities', 'Predict y:\\nexp(pred) x\\nsmearing factor'],
    title='NB26 Conceptual Flow: transforming the target',
    notes=['multiplicative?', 'lambda ~ 0 => log', '', 'symmetric now?', 'exact % formula', 'avoid bias'],
    figsize=(16, 2.8),
)
"""),
md("""## Step 1 — A right-skewed target: house price vs size

True model (multiplicative):  log(price) = 10 + 0.008·size + ε,  ε ~ N(0, 0.35²),  size in m².

We fit both a **level-level** model (price ~ size) and a **log-level** model (log(price) ~ size) and compare the residuals.
"""),
code("""import numpy as np
import statsmodels.api as sm
from scipy import stats
import matplotlib.pyplot as plt

rng   = np.random.default_rng(11)
n     = 300
size  = rng.uniform(50, 250, n)
price = np.exp(10 + 0.008 * size + rng.normal(0, 0.35, n))
X     = sm.add_constant(size)

lvl = sm.OLS(price, X).fit()
lg  = sm.OLS(np.log(price), X).fit()

from statsmodels.stats.diagnostic import het_breuschpagan
for name, r in [('level-level  price ~ size', lvl), ('log-level  log(price) ~ size', lg)]:
    print(f"{name:30s} residual skew = {stats.skew(r.resid):6.3f}   "
          f"Shapiro p = {stats.shapiro(r.resid).pvalue:.2e}   "
          f"Breusch-Pagan p = {het_breuschpagan(r.resid, X)[1]:.2e}")

fig, ax = plt.subplots(1, 3, figsize=(15, 4))
ax[0].hist(price, 40); ax[0].set_title(f'price is right-skewed (skew = {stats.skew(price):.2f})')
ax[1].scatter(lvl.fittedvalues, lvl.resid, s=10, alpha=0.5); ax[1].axhline(0, color='k')
ax[1].set_title('level model: funnel residuals')
ax[2].scatter(lg.fittedvalues, lg.resid, s=10, alpha=0.5); ax[2].axhline(0, color='k')
ax[2].set_title('log model: even band')
plt.tight_layout(); plt.show()
"""),
md("""## Step 2 — Interpreting log coefficients (exactly)

| Model | Equation | Meaning of b |
|---|---|---|
| level-level | y = a + b·x | +1 unit of x → **+b units** of y |
| **log-level** | ln y = a + b·x | +1 unit of x → y changes by **100·(eᵇ − 1)%** (≈ 100·b% when b is small) |
| level-log | y = a + b·ln x | +1% in x → y changes by ≈ **b/100 units** (exactly b·ln 1.01) |
| **log-log** | ln y = a + b·ln x | +1% in x → y changes by ≈ **b%** — the **elasticity** (exactly 100·(1.01ᵇ − 1)%) |

The "≈ 100·b%" shortcut breaks down for large b — e.g. a dummy with b = 0.15 means **+16.18%**, not +15%.
"""),
code("""b = lg.params[1]
print(f"log-level slope b = {b:.5f}")
print(f"  +1 m^2  -> price x e^b       = +{100*(np.exp(b)-1):.3f}%   (shortcut 100*b = {100*b:.3f}%)")
print(f"  +10 m^2 -> price x e^(10b)   = +{100*(np.exp(10*b)-1):.2f}%  (shortcut 1000*b = {1000*b:.2f}%)")
print()
for coef in [0.05, 0.15, 0.50]:
    print(f"dummy coefficient {coef:.2f}: exact effect = +{100*(np.exp(coef)-1):.2f}%  vs shortcut +{100*coef:.0f}%")
"""),
code("""# log-log: price elasticity of demand
rng_d = np.random.default_rng(5)
p     = rng_d.uniform(1, 20, 250)                         # price
q     = 500 * p ** (-1.5) * np.exp(rng_d.normal(0, 0.2, 250))  # quantity, true elasticity -1.5
ll    = sm.OLS(np.log(q), sm.add_constant(np.log(p))).fit()
e     = ll.params[1]
lo, hi = ll.conf_int()[1]
print(f"log-log elasticity = {e:.4f}  (95% CI [{lo:.4f}, {hi:.4f}], true -1.5)")
print(f"  +1% price  -> quantity {100*(1.01**e - 1):.3f}%")
print(f"  +10% price -> quantity {100*(1.10**e - 1):.2f}%   (not simply 10 x {e:.2f}%)")

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].scatter(p, q, s=10, alpha=0.5); ax[0].set_title('demand curve (curved)'); ax[0].set_xlabel('price'); ax[0].set_ylabel('quantity')
ax[1].scatter(np.log(p), np.log(q), s=10, alpha=0.5)
xx = np.linspace(np.log(p).min(), np.log(p).max(), 50); ax[1].plot(xx, ll.params[0] + e*xx, 'r', lw=2)
ax[1].set_title(f'log-log: straight line, slope = elasticity {e:.2f}'); ax[1].set_xlabel('log price'); ax[1].set_ylabel('log quantity')
plt.tight_layout(); plt.show()
"""),
md("""## Step 3 — Box–Cox: let the data choose the transform

```
y(λ) = (y^λ − 1) / λ     if λ ≠ 0
y(λ) = ln(y)             if λ = 0
```

`scipy.stats.boxcox` picks λ by maximum likelihood. λ ≈ 1 → no transform needed, λ ≈ 0.5 → square root, λ ≈ 0 → log.

Box–Cox needs **y > 0**. For zero/negative values use **Yeo–Johnson** (`sklearn.preprocessing.PowerTransformer`).

Note: here we apply Box–Cox to price alone (marginally). Strictly, λ should be chosen for the **residuals** of the model — `boxcox` on y is a quick first look.
"""),
code("""price_bc, lam = stats.boxcox(price)
lo, hi = stats.boxcox(price, alpha=0.05)[2]
print(f"Box-Cox lambda = {lam:.4f}   (95% CI [{lo:.4f}, {hi:.4f}])")
print("-> the interval contains 0, so a plain log transform is supported.")

lams = np.linspace(-1, 1.5, 101)
llf  = [stats.boxcox_llf(l, price) for l in lams]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.plot(lams, llf); ax.axvline(lam, color='r', ls='--', label=f'best lambda = {lam:.2f}')
ax.axvline(0, color='k', ls=':', label='log (lambda = 0)')
ax.set_xlabel('lambda'); ax.set_ylabel('log-likelihood'); ax.set_title('Box-Cox profile likelihood'); ax.legend()
plt.tight_layout(); plt.show()
"""),
md("""## Step 4 — Back to dollars: retransformation bias and Duan's smearing

If ln y = Xb + ε, then **exp(Xb) estimates the median of y, not the mean** — because E[e^ε] > 1 (Jensen's inequality).

- If ε is normal: E[y|x] = exp(Xb) · exp(σ²/2)
- **Duan's smearing estimator** (no normality needed): E[y|x] ≈ exp(Xb) · mean(exp(eᵢ)), using the training residuals eᵢ

We fit on the 300 observed houses, then score a **large fresh sample (100,000 houses) from the same process**,
so the comparison is not swamped by the noise of a small test set.
"""),
code("""fit    = sm.OLS(np.log(price), X).fit()            # fit on the 300 observed houses
rng_new = np.random.default_rng(99)
size_new  = rng_new.uniform(50, 250, 100_000)              # fresh houses from the same process
price_new = np.exp(10 + 0.008 * size_new + rng_new.normal(0, 0.35, 100_000))
X_new  = sm.add_constant(size_new)

naive  = np.exp(fit.predict(X_new))
smear  = np.mean(np.exp(fit.resid))
normal = np.exp(fit.scale / 2)
actual = price_new.mean()

print(f"Mean actual price (100,000 new houses): {actual:10,.0f}")
print(f"Mean naive exp(pred)                  : {naive.mean():10,.0f}   ({100*(naive.mean()/actual-1):+.1f}%)  <- biased low")
print(f"Duan smearing factor mean(exp(e_i))   : {smear:.4f}")
print(f"Mean smeared prediction               : {(naive*smear).mean():10,.0f}   ({100*((naive*smear).mean()/actual-1):+.1f}%)")
print(f"Normal-theory factor exp(s^2/2)       : {normal:.4f}   (true exp(0.35^2/2) = {np.exp(0.35**2/2):.4f})")
"""),
md("""## Key Takeaways

1. Log-transform a **positive, right-skewed** target when effects are **multiplicative** — residuals usually become symmetric and evenly spread.
2. **Interpretation:** log-level → 100·(eᵇ − 1)% per unit of x; log-log → b is an **elasticity** (% change in y per 1% change in x).
3. The "100·b %" shortcut is only accurate for small b (b = 0.15 → +16.18%, not +15%).
4. **Box–Cox** estimates the best power λ; if its CI contains 0, use the log (easier to interpret). Use **Yeo–Johnson** for y ≤ 0.
5. **exp(prediction) underestimates the mean** — multiply by Duan's smearing factor (or exp(σ²/2) under normality).
6. Compare models on the **same scale**: R² of a log model is about log(y), not y.
"""),
]

# =============================================================================
# NB27 — Model selection & interpretation pitfalls
# =============================================================================
cells_27 = [
md("""# NB27 — Model Selection and Interpretation Pitfalls

> **StatQuest principle: a model that fits well is not the same as a model you can trust.**

---

## The main ideas are:

1. **Metrics:** MSE, RMSE, MAE, R² — and when to prefer MAE over RMSE
2. **AIC / BIC** trade fit against complexity — lower is better
3. **Nested models:** the partial **F-test** asks "do these extra variables help, together?"
4. **Stepwise selection** by AIC is convenient but makes the chosen model look **more significant than it is**
5. **Omitted-variable bias:** leave out a variable correlated with x and x's coefficient absorbs its effect: bias = β₂·δ
6. **Extrapolation:** a line that fits inside the data can be badly wrong outside it
7. **Correlation ≠ causation:** a confounder can create a "significant" slope out of nothing
"""),
code(FLOW_HELPER + """
flow_diagram(
    steps=['Choose\\nmetric\\n(RMSE / MAE)', 'Compare models:\\nAIC / BIC', 'Nested?\\npartial F-test', 'Stepwise?\\nbeware p-values',
           'Missing\\nconfounder?\\n(OVB)', 'Predicting\\noutside range?', 'Causal claim?\\nneed design'],
    title='NB27 Conceptual Flow: choosing and trusting a model',
    figsize=(18, 2.8),
)
"""),
md("""## Step 1 — Metrics: MSE, RMSE, MAE, R²

```
MSE  = mean((y − ŷ)²)          RMSE = √MSE  (same units as y)
MAE  = mean(|y − ŷ|)           R²   = 1 − SS_res / SS_tot
```

- **RMSE** squares errors → large errors dominate. Use it when big misses are disproportionately costly.
- **MAE** treats every unit of error equally → robust to a few huge misses; it is the error of a "typical" prediction.
- Always report metrics on **held-out** data.
"""),
code("""import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt

housing = fetch_california_housing()
X_tr, X_te, y_tr, y_te = train_test_split(housing.data, housing.target, test_size=0.2, random_state=0)
pred = LinearRegression().fit(X_tr, y_tr).predict(X_te)

mse = mean_squared_error(y_te, pred)
print("California Housing, test set (y in $100k):")
print(f"  MSE  = {mse:.4f}")
print(f"  RMSE = {np.sqrt(mse):.4f}   -> typical miss ~ ${np.sqrt(mse)*100:.0f}k (squared-error view)")
print(f"  MAE  = {mean_absolute_error(y_te, pred):.4f}   -> typical miss ~ ${mean_absolute_error(y_te, pred)*100:.0f}k")
print(f"  R^2  = {r2_score(y_te, pred):.4f}")

# How a few big misses move RMSE vs MAE
err  = np.full(100, 1.0)
err2 = err.copy(); err2[:5] = 10.0
print("\\n100 errors of size 1  -> RMSE = %.2f, MAE = %.2f" % (np.sqrt(np.mean(err**2)), np.mean(np.abs(err))))
print("...5 of them become 10 -> RMSE = %.2f, MAE = %.2f" % (np.sqrt(np.mean(err2**2)), np.mean(np.abs(err2))))
"""),
md("""## Step 2 — AIC and BIC

```
AIC = 2k − 2 ln L            BIC = k · ln(n) − 2 ln L
```

k = number of estimated parameters, L = maximised likelihood. Both reward fit (−2 ln L) and penalise complexity;
**BIC penalises more** (ln n > 2 once n ≥ 8) and prefers smaller models. Lower is better; only differences matter, and only between models fitted to the **same y**.

Data: y = 1 + 2·x1 + 1.5·x2 + 0.5·x3 + ε, with x4, x5 pure noise (n = 150, ε ~ N(0, 2²)).
"""),
code("""rng = np.random.default_rng(21)
n   = 150
df  = pd.DataFrame(rng.normal(size=(n, 5)), columns=['x1', 'x2', 'x3', 'x4', 'x5'])
df['y'] = 1 + 2*df.x1 + 1.5*df.x2 + 0.5*df.x3 + rng.normal(0, 2, n)

formulas = ['y ~ x1', 'y ~ x1 + x2', 'y ~ x1 + x2 + x3', 'y ~ x1 + x2 + x3 + x4 + x5']
fits = {f: smf.ols(f, df).fit() for f in formulas}
print(f"{'model':28s}{'k':>3s}{'R^2':>8s}{'adj R^2':>9s}{'AIC':>9s}{'BIC':>9s}")
for f, r in fits.items():
    k = int(r.df_model) + 1
    print(f"{f:28s}{k:3d}{r.rsquared:8.4f}{r.rsquared_adj:9.4f}{r.aic:9.2f}{r.bic:9.2f}")

r = fits['y ~ x1 + x2 + x3']
k = int(r.df_model) + 1
print(f"\\nManual check for y ~ x1 + x2 + x3: AIC = 2*{k} - 2*({r.llf:.3f}) = {2*k - 2*r.llf:.2f};  "
      f"BIC = {k}*ln({n}) - 2*({r.llf:.3f}) = {k*np.log(n) - 2*r.llf:.2f}")
print("Note: statsmodels' k counts the regression coefficients (incl. intercept), not sigma^2;")
print("      that constant offset cancels when comparing models.")
"""),
md("""## Step 3 — Nested models: the partial F-test

Do x4 and x5 add anything **together**, once x1–x3 are in?

```
F = [(SSR_reduced − SSR_full) / q] / [SSR_full / (n − k_full)]       q = number of added variables
```

H0: the added coefficients are all zero.
"""),
code("""from statsmodels.stats.anova import anova_lm
reduced = fits['y ~ x1 + x2 + x3']
full    = fits['y ~ x1 + x2 + x3 + x4 + x5']
print(anova_lm(reduced, full).round(4))
F, p, q = full.compare_f_test(reduced)
print(f"\\nF = {F:.4f}, p = {p:.4f}, extra parameters q = {int(q)}")
print("-> p > 0.05: x4 and x5 do not improve the model. Keep the smaller one.")

reduced2 = fits['y ~ x1 + x2']
F2, p2, q2 = reduced.compare_f_test(reduced2)
print(f"\\nAdding x3 to (x1, x2):  F = {F2:.4f}, p = {p2:.4f}")
"""),
md("""## Step 4 — Forward stepwise selection by AIC (and why its p-values lie)

Algorithm: start empty; at each step add the variable that lowers AIC the most; stop when nothing lowers it.

**Caveat:** the selected model's p-values ignore that we *searched*. On pure noise, stepwise still "finds" significant predictors.
"""),
code("""def forward_aic(data, target, candidates):
    chosen, best_aic = [], smf.ols(f'{target} ~ 1', data).fit().aic
    path = [('(intercept only)', best_aic)]
    while True:
        trials = [(smf.ols(f"{target} ~ {' + '.join(chosen + [c])}", data).fit().aic, c)
                  for c in candidates if c not in chosen]
        if not trials:
            break
        aic, c = min(trials)
        if aic >= best_aic:
            break
        chosen.append(c); best_aic = aic; path.append(('+ ' + c, aic))
    return chosen, path

chosen, path = forward_aic(df, 'y', ['x1', 'x2', 'x3', 'x4', 'x5'])
for step, aic in path:
    print(f"  {step:18s} AIC = {aic:.2f}")
print(f"Selected: {chosen}")
print("Note: x4 is pure noise, yet AIC kept it (AIC only needs a tiny likelihood gain). BIC or a hold-out set would be stricter.")
"""),
code("""# Pure noise: 20 candidate predictors, none related to y
rng0  = np.random.default_rng(4)
noise = pd.DataFrame(rng0.normal(size=(100, 20)), columns=[f'z{i}' for i in range(1, 21)])
noise['y'] = rng0.normal(size=100)
sel, _ = forward_aic(noise, 'y', [f'z{i}' for i in range(1, 21)])
res    = smf.ols('y ~ ' + ' + '.join(sel), noise).fit() if sel else None
print(f"Variables selected from pure noise: {sel}")
if res is not None:
    print(res.pvalues.drop('Intercept').round(4).to_string())
    print(f"-> {int((res.pvalues.drop('Intercept') < 0.05).sum())} of {len(sel)} look 'significant' at 5% — yet y is pure noise.")
print("Fix: validate on held-out data, use cross-validation (NB14) or Lasso (NB12) instead of trusting post-selection p-values.")
"""),
md("""## Step 5 — Omitted-variable bias (OVB)

True model: y = β0 + β1·x1 + β2·x2 + ε. If you **omit x2**, the slope on x1 becomes

```
b1(short) = β1 + β2 · δ        δ = slope from regressing x2 on x1
```

The bias β2·δ is non-zero when x2 **affects y** (β2 ≠ 0) **and** is **correlated with x1** (δ ≠ 0).
This identity holds **exactly** for the fitted OLS coefficients in any sample.

Example: wage depends on education and (unobserved) ability; abler people also get more education.
"""),
code("""rng = np.random.default_rng(8)
n   = 1000
ability = rng.normal(0, 1, n)
edu     = 12 + 2 * ability + rng.normal(0, 1, n)
wage    = 5 + 1.0 * edu + 3.0 * ability + rng.normal(0, 2, n)

long_  = sm.OLS(wage, sm.add_constant(np.column_stack([edu, ability]))).fit()
short  = sm.OLS(wage, sm.add_constant(edu)).fit()
delta  = sm.OLS(ability, sm.add_constant(edu)).fit().params[1]

print(f"True effect of 1 year of education      : 1.000")
print(f"Long regression (with ability)          : {long_.params[1]:.4f}")
print(f"Short regression (ability omitted)      : {short.params[1]:.4f}")
print(f"OVB formula  b_long + b_ability * delta : {long_.params[1]:.4f} + {long_.params[2]:.4f} * {delta:.4f} = {long_.params[1] + long_.params[2]*delta:.4f}")
print(f"Theory: delta = Cov(ability, edu)/Var(edu) = 2/5 = 0.4 -> bias = 3 * 0.4 = 1.2")
"""),
md("""### The same mechanism: a missing interaction term (NB10)

In NB10 the true salary model had an interaction:  salary = 30 + 2·exper + 10·edu + 3.5·exper·edu.
Leaving out **exper·edu** is an omitted variable too — and the degree dummy absorbs it.
"""),
code("""np.random.seed(7)
n = 200
edu_d  = np.random.binomial(1, 0.5, n).astype(float)
exper  = np.random.uniform(1, 20, n)
salary = 30 + 2.0*exper + 10*edu_d + 3.5*exper*edu_d + np.random.normal(0, 4, n)

X_short = sm.add_constant(np.column_stack([exper, edu_d]))
X_long  = sm.add_constant(np.column_stack([exper, edu_d, exper*edu_d]))
s, l    = sm.OLS(salary, X_short).fit(), sm.OLS(salary, X_long).fit()
d       = sm.OLS(exper*edu_d, X_short).fit().params      # regress omitted term on included ones

print(f"edu coefficient WITHOUT interaction : {s.params[2]:.4f}   (true edu effect at exper = 0: 10)")
print(f"edu coefficient WITH interaction    : {l.params[2]:.4f}")
print(f"OVB identity: {l.params[2]:.4f} + {l.params[3]:.4f} * {d[2]:.4f} = {l.params[2] + l.params[3]*d[2]:.4f}")
print(f"(delta = {d[2]:.2f} is roughly the average experience of degree holders: {exper[edu_d==1].mean():.2f})")
"""),
md("""## Step 6 — Extrapolation: right inside the data, wrong outside it

True relationship saturates:  y = 10·(1 − e^(−0.5x)). We only observe x in [0, 5].
"""),
code("""rng = np.random.default_rng(2)
x_tr = rng.uniform(0, 5, 80)
f    = lambda x: 10 * (1 - np.exp(-0.5 * x))
y_tr = f(x_tr) + rng.normal(0, 0.4, 80)
lin  = sm.OLS(y_tr, sm.add_constant(x_tr)).fit()

print(f"Linear fit on x in [0, 5]: R^2 = {lin.rsquared:.4f}")
for x0 in [2.5, 5, 10, 15]:
    p0 = lin.params[0] + lin.params[1] * x0
    print(f"  x = {x0:4.1f}: linear predicts {p0:6.2f}, truth {f(x0):6.2f}  (error {p0 - f(x0):+6.2f})")

xx = np.linspace(0, 15, 200)
fig, ax = plt.subplots(figsize=(9, 4))
ax.scatter(x_tr, y_tr, s=12, alpha=0.6, label='observed (x <= 5)')
ax.plot(xx, f(xx), 'k', lw=2, label='truth'); ax.plot(xx, lin.params[0] + lin.params[1]*xx, 'r--', lw=2, label='linear fit')
ax.axvspan(5, 15, color='orange', alpha=0.1, label='extrapolation zone'); ax.legend(); ax.set_title('Extrapolation danger')
plt.tight_layout(); plt.show()
"""),
md("""## Step 7 — Correlation is not causation: a confounder

Hot days increase both ice-cream sales and swimming (hence drownings). Ice cream does **not** cause drowning.
"""),
code("""rng  = np.random.default_rng(9)
days = 365
temp = rng.uniform(5, 35, days)                       # temperature, the confounder
ice  = 20 + 3.0 * temp + rng.normal(0, 8, days)       # ice-cream sales
drown = 0.5 + 0.10 * temp + rng.normal(0, 0.8, days)  # drownings: depend on temperature only

naive = sm.OLS(drown, sm.add_constant(ice)).fit()
adj   = sm.OLS(drown, sm.add_constant(np.column_stack([ice, temp]))).fit()
print(f"drownings ~ ice cream          : slope = {naive.params[1]:.4f}, p = {naive.pvalues[1]:.2e}  <- 'significant'!")
print(f"drownings ~ ice cream + temp   : slope = {adj.params[1]:.4f}, p = {adj.pvalues[1]:.4f}  <- vanishes")
print(f"                                 temp slope = {adj.params[2]:.4f} (true 0.10)")
print("Regression measures association. Causal claims need design: experiments, or a credible model of the confounders.")
"""),
md("""## Key Takeaways

1. Report **RMSE and MAE on held-out data**; RMSE punishes big misses, MAE is robust to them.
2. **AIC/BIC:** lower is better; BIC prefers smaller models. Compare only models of the same y.
3. **Partial F-test** answers "do these extra variables help together?" for nested models.
4. **Stepwise selection** finds "significant" variables even in pure noise — validate out-of-sample instead.
5. **Omitted-variable bias = β₂·δ:** leaving out a correlated cause (or an interaction) silently changes coefficients.
6. **Don't extrapolate** a linear fit beyond the range of the data.
7. A significant coefficient is an **association**; confounders can manufacture it.
"""),
]

save(nb(cells_25), "NB25_Heteroscedasticity_Fixes.ipynb")
save(nb(cells_26), "NB26_Target_Transformations.ipynb")
save(nb(cells_27), "NB27_Model_Selection_and_Pitfalls.ipynb")
