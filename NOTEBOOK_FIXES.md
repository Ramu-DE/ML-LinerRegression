# Notebook fixes — NB01–NB20

All 20 notebooks were read in full, re-run, and checked against their own printed output. Each change below fixes a statement or piece of code that was wrong, or that contradicted the notebook's own results.

How the edits were made:
- Cells were edited directly, as small targeted changes. The `build_*.py` scripts were **not** re-run: the notebooks already contain fixes those scripts don't have.
- Every modified notebook was re-executed in place with numpy 2.5.4, scikit-learn 1.9.1 and statsmodels 0.15.0.
- **All 20 notebooks now run without errors**, including NB20, which used to crash on a Windows-only path.
- Nothing has been committed. Review the changes with `git diff`.

NB01, NB02 and NB17 needed no changes.

---

## Changes by severity

### NB15 — Gradient Descent (the learning-rate story was backwards)

**What was wrong.** The notebook's labels contradicted its own output:
- lr = 0.001 was labelled "Good", yet the output printed `Close? False` (b0 = 29.55, b1 = 6.72, against the OLS answer 32.00, 6.36).
- lr = 0.003 was labelled "Diverges", but it actually converges best.
- Root cause: x is not centred, so the problem is badly conditioned (Hessian eigenvalues 0.42 and 78.58, condition number ≈ 187). GD is only stable for lr < 2/λ_max = 0.0255.

**What changed:**
- **Main fit:** now uses lr = 0.003 for 20,000 epochs and prints `Close? True` (b0 = 32.00000, b1 = 6.36364). It also prints the lr = 0.001 result with an explicit "not converged" note, plus the Hessian eigenvalues, the condition number and the stability limit.
- **Learning-rate panel:** now shows 0.001 (too slow, SSR 179.1 after 3,000 epochs), 0.003 (converges, SSR 20.1) and 0.03 (diverges; stopped after 28 epochs when SSR passed 10¹²). The divergence check stops the loop once SSR explodes.
- **New markdown cell** explains conditioning, why standardising x fixes it, and points to NB21 (scaling and SGD). The "main ideas" list now says mini-batch SGD is implemented in NB21.

### NB10 and NB14 — cross-validation on sorted X without shuffling

**What was wrong.** `cross_val_score(cv=5)` (and `learning_curve`) on **sorted** X makes every fold a separate x-range. CV was measuring extrapolation, not generalisation.

**What changed:** both notebooks now use `KFold(5, shuffle=True, random_state=0)`; `learning_curve` also gets `shuffle=True`. NB10 also prints its numbers.

| | Before | After |
|---|---|---|
| NB10 5-fold CV R², degrees 1 / 2 / 3 / 10 | −2.918 / −4.335 / 0.303 / −629,741 (figure) | **0.714 / 0.845 / 0.891 / 0.872** (printed) |
| NB14 best degree / CV R² | 3 / 0.2813 | 3 / **0.7790** |

### NB11 — Ridge: the demo contradicted its own title

**What was wrong:**
- The title said "increasing lambda reduces overfitting", but test R² fell steadily: OLS 0.808 → λ=0.01 0.683 → λ=1 0.007 → λ=100 −0.116. The degree-10 fit on 35 training points wasn't really overfitting.
- `"Test R^2 at optimal lambda"` was computed on the training data.

**What changed:**
- **Toy data** is now a degree-12 polynomial on 25 training points (`test_size=0.5`), which genuinely overfits. λ is now 0 / 1e-4 / 0.01 / 1, and train/test R² are printed:
  - OLS: 0.951 / **0.552** (overfit)
  - λ=1e-4: 0.933 / **0.777** (best)
  - λ=0.01: 0.884 / 0.666
  - λ=1: 0.520 / 0.012 (underfit)
- **Title:** now reads "a little lambda cures overfitting; too much lambda underfits".
- **RidgeCV:** prints the in-sample R² with an honest label (0.6062), plus a real held-out score from a pipeline trained on an 80/20 split: **test R² = 0.5941**, with λ = 21.96 chosen on the training split. The CV-optimal λ on all the data is still 38.2749.
- **New note:** the closed form assumes centred data, and the intercept is not penalised.

### NB09 — Multicollinearity: the wording didn't match the output

**What was wrong.** The text said "SEs explode, both become insignificant", but both p-values were significant.

**What changed:**
- **Wording:** now says the SEs inflate about 4×, with a note that coefficients can become insignificant when collinearity is stronger or the signal weaker.
- **Single-predictor R²** is now printed, so the "R² barely changes" claim can be checked.
- **SE inflation** is computed and printed.
- **p-values** are shown in scientific notation.

| | Before | After |
|---|---|---|
| Joint p-values | "0.0000" / "0.0010" under a claim of "insignificant" | **4.09e-08 / 1.01e-03** (significant) |
| R² comparison | Not shown | x1 only 0.9445, x2 only 0.9322, both 0.9503 |
| SE inflation | Not shown | SE(b1) 0.125 → 0.551 = **4.4×** |

### NB12 — Lasso: the geometry figure was staged

**What was wrong.** The "Lasso solution (b2 = 0!)" point was hard-coded at (1, 0). The true constrained minimum for the ellipses drawn was (0.444, 0.556), which is not a corner. The Ridge point was hard-coded too.

**What changed:**
- **Both solutions are now computed with `scipy.optimize`** for a stated quadratic loss (OLS point (1.5, 0.5), elliptical contours). Results: **Ridge (0.979, 0.202)**, **Lasso (1.000, 0.000)**, which is a genuine corner.
- **The contour that touches the constraint** is drawn darker.
- **California Lasso:** a note explains why it keeps 8 of 8 features at the CV-optimal λ = 0.0026.

### NB13 — ElasticNet

**What was wrong:**
- The comment "Dataset with many correlated features" was false: `make_regression` features are independent (max |r| ≈ 0.22).
- The objective was written without sklearn's 1/(2n) factor on SSR.
- CV choosing l1_ratio = 1.0 contradicted the "rule of thumb 0.5–0.9".

**What changed:**
- **Comment:** now describes a sparse problem with independent features.
- **Objective:** written with the exact sklearn scaling, plus a note that Ridge's alpha uses a different scale.
- **Per-model numbers printed:** Ridge 20/20 non-zero, CV 0.994; Lasso 17/20, 0.995; EN(0.5) 18/20, 0.992.
- **Rule of thumb replaced** by an honest explanation of why CV picked pure Lasso here.

### NB20 — Pipelines

**What was wrong:**
- The save path was a hard-coded Windows path, `C:/Users/Administrator/ML/Linear Regression/best_pipeline.pkl`, so the notebook **crashed** on any other machine.
- The "WRONG way: CV R² (inflated) 0.5612" line was actually the *training* score, so it didn't show leakage at all.

**What changed:**
- **Save path:** now `Path('best_pipeline.pkl')`, next to the notebook.
- **Like-for-like comparison:** test R² and 5-fold CV for preprocessing-before-split vs the pipeline. Leaky: test 0.5349, CV 0.5576. Pipeline: test 0.5350, CV 0.5576. The text honestly says the difference is tiny for median/scaler steps.
- **New leakage demo where it matters:** 2,000 noise features, with a y that is pure noise. Selecting features on all rows and then cross-validating gives **CV R² = 0.363** (fake signal). Doing the selection inside a pipeline gives **CV R² = −0.285**, which correctly shows there is nothing to learn.

### NB06 — Assumptions

**What was wrong:**
- "If any assumption breaks, OLS estimates are still the best you can do among linear models" was incorrect.
- The Scale–Location reference line was drawn at √0.8 = 0.894, but E√|z| = 0.822.

**What changed:**
- **Gauss–Markov stated correctly:** BLUE requires linearity, exogeneity, homoscedasticity and no autocorrelation; normality is not needed. The notebook now also lists what breaks when each assumption fails (L → bias; E/I → not best, wrong SEs, use WLS/GLS or robust SEs; N → approximate small-sample inference) and points to NB24 and NB25.
- **Reference line** set to 0.822.
- **Test statistics are now printed:**
  - Durbin–Watson: 2.03 (independent) vs 0.45 (autocorrelated)
  - Shapiro–Wilk p: 0.7918 / 1.67e-09 / 1.83e-05
  - Breusch–Pagan p: 0.587 / 2.94e-05

### NB07 — Diagnostic plots

**What was wrong:**
- The injected point (obs 60) was **not** influential by the notebook's own rules: leverage 0.037 < 4/n, Cook's D 0.875 < 1. Yet the plot was titled "Influential outlier pulls the regression line significantly".
- The Q-Q labels used the wrong rank, so they were attached to the wrong points.

**What changed:**
- **Two contrasting points.** Obs 60 is kept as a y-outlier with low leverage. A new obs 70 sits at x = 16, y = 15 (the trend predicts about 44), giving high leverage plus a large residual. Printed: obs 60 leverage 0.031, studentised residual 5.54, Cook's D 0.493; obs 70 leverage 0.194, studentised residual −5.44, **Cook's D 3.572**. The threshold is 4/n = 0.056.
- **Refit table:**

  | Fit | b0 | b1 |
  |---|---|---|
  | All points | 5.510 | 2.171 |
  | Without obs 60 | 5.978 | 2.016 (small change) |
  | Without obs 70 | 2.872 | **2.717** (big change) |

  The figure title is now "Only the HIGH-LEVERAGE outlier pulls the regression line".
- **Q-Q label rank** fixed (`np.argsort(np.argsort(...))`).
- **Influential region:** the "top-right corner" wording now reads "far right, top or bottom".

### NB19 — Time series

**What was wrong:**
- The ACF was computed on the raw, trending series, where every lag is about 0.9.
- There was no time-ordered holdout; all R² values were in-sample.
- `make_features` read the global `y`.
- The residual-ACF step in the flow diagram was never actually done.

**What changed:**
- **Raw vs detrended ACF printed:** raw lag 1 / 6 / 12 = 0.97 / 0.75 / 0.98; detrended = **0.74 / −0.82 / 0.86**, where the seasonality becomes visible. The plot now shows the detrended ACF.
- **`make_features(t, series, …)`** takes the series as a parameter.
- **Holdout on the last 24 months:**

  | Model | In-sample R² | Holdout R² |
  |---|---|---|
  | Trend + Fourier | 0.9710 | 0.7701 |
  | Trend + Fourier + lags | 0.9706 | 0.7950 |

  An honest note explains that lags add little when the noise is independent.
- **Residual ACF check:** max |r| = 0.233 against a ±0.200 band; 1 of 12 lags falls outside, which is expected by chance.

### Smaller fixes

| NB | Was | Now |
|---|---|---|
| NB18 | "λ in Ridge = 1/prior_variance"; "uncertainty from t-distribution (large n)" | λ = σ²/τ² (it equals 1/τ² in the demo only because σ² = 1; the code now computes it from σ²). The t-distribution is exact for small n under normal errors. The MAP = Ridge check still prints `Match: True`. |
| NB16 | Huber "breakdown ~20%" | Resists outliers in y; ~0% breakdown against high-leverage x-outliers |
| NB05 | p printed as "0.000000" and "0.0000% of the time" | Scientific notation: p(b1) = **3.55e-11**, p(b0) = 0.00199 |
| NB03 | `X = X or self._X` (crashes when given numpy arrays) | `X if X is not None else self._X`. Added a note that MSE/RMSE divide by n while σ² divides by n − 2. |
| NB04 | R² range "(0 to 1)" | 0–1 in-sample for OLS with an intercept; it can be **negative** on test data |
| NB08 | DW = 0.885 shown but not discussed; plot called "standardised" | Prints a DW note (rows are ordered by location, so the SEs are optimistic). Axis now reads "change in y ($100k) per 1-SD increase in x" (semi-standardised). |
| `Embeddings/LINEAR_REGRESSION_README.md` | Sample output `y = 5.9394x + 34.5455`, R² 0.9897, MSE 6.8595, RMSE 2.6191, predictions 52.36 / 76.12 | Verified by running `linear_regression_simple.py`: **y = 6.3636x + 32.0000**, R² 0.9943, MSE 1.9091, RMSE 1.3817, predictions 51.09 / 76.55. R² range caveat added. |

---

## Files touched

- `notebooks/NB03`–`NB16`, `NB18`, `NB19`, `NB20` (cell edits plus re-execution)
- `Embeddings/LINEAR_REGRESSION_README.md`
- `notebooks/best_pipeline.pkl` (new; written by NB20 next to the notebook)
