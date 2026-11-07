# Linear Regression — Full Course Guide

Total length: **19:27**

**Video:** [`Linear-Regression-Full-Course.mp4`](Linear-Regression-Full-Course.mp4), 1920×1080, 30 fps, with chapter markers. In VLC use *Playback → Chapter*.
**Editable drawings:** [`Linear-Regression-Full-Course.excalidraw`](Linear-Regression-Full-Course.excalidraw). Open it at excalidraw.com with *Menu → Open*.
**Source notebooks:** [`notebooks/NB01–NB27`](../../notebooks). All 27 were executed, and every number on screen comes from their printed output.

### What changed in the notebooks for this course
- **7 new notebooks** cover topics that were missing:
  - NB21 Feature Scaling & GD (SGD, mini-batch)
  - NB22 Categorical Encoding & the dummy trap
  - NB23 Confidence vs Prediction Intervals
  - NB24 Why Least Squares (Gauss–Markov, MLE, QR/SVD stability)
  - NB25 Heteroscedasticity Fixes (HC3, WLS, Newey–West)
  - NB26 Target Transformations (log interpretation, Box–Cox, smearing)
  - NB27 Model Selection & Pitfalls (MAE/RMSE, AIC/BIC, partial F-test, stepwise, omitted-variable bias, extrapolation, confounding)
- **17 errors fixed in NB01–NB20.** For example:
  - NB15: the learning-rate labels were backwards.
  - NB10 and NB14: cross-validation was run on sorted, unshuffled data.
  - NB06: the Gauss–Markov statement was wrong.
  - NB20: a hard-coded Windows path.

  Details are in [`NOTEBOOK_FIXES.md`](../../NOTEBOOK_FIXES.md).

### How to use this guide
- Each **[mm:ss]** line is the on-screen caption, with its exact time in the full video.
- *On screen* describes the animation; the paragraph under it explains the idea in depth.
- The chapters build in order: fitting (1–2) → judging a fit (3–6) → more predictors (7–9) → controlling complexity (10–11) → beyond plain OLS (12–13) → real-world workflow (14).

> **Accuracy note.** Numbers come from the executed notebooks (seeds fixed). Shapes that only illustrate an idea (residual patterns, contour valleys, some histograms) are labelled *illustrative* on screen.

## Chapters

| Starts | Chapter | Length | Source video |
|---|---|---|---|
| 00:00 | [Introduction](#introduction) | 00:12 | `L00-intro` |
| 00:12 | [Chapter 1 — Fitting a Line](#chapter-1--fitting-a-line) | 01:15 | `L01-intuition-residuals` |
| 01:27 | [Chapter 2 — Deriving the OLS Formula](#chapter-2--deriving-the-ols-formula) | 01:21 | `L02-deriving-ols` |
| 02:49 | [Chapter 3 — R²: What Does It Measure?](#chapter-3--r-what-does-it-measure) | 01:08 | `L03-r2-adjusted-r2` |
| 03:57 | [Chapter 4 — Inference & Intervals](#chapter-4--inference--intervals) | 01:22 | `L04-inference-and-intervals` |
| 05:19 | [Chapter 5 — Assumptions & Gauss–Markov](#chapter-5--assumptions--gaussmarkov) | 01:28 | `L05-assumptions-gauss-markov` |
| 06:48 | [Chapter 6 — Diagnostics & influence](#chapter-6--diagnostics--influence) | 01:16 | `L06-diagnostics-influence` |
| 08:04 | [Chapter 7 — Multiple regression & categories](#chapter-7--multiple-regression--categories) | 01:24 | `L07-multiple-regression-categorical` |
| 09:29 | [Chapter 8 — Multicollinearity](#chapter-8--multicollinearity) | 01:15 | `L08-multicollinearity` |
| 10:44 | [Chapter 9 — Polynomials, Interactions & CV](#chapter-9--polynomials-interactions--cv) | 01:24 | `L09-polynomial-interactions-cv` |
| 12:09 | [Chapter 10 — Ridge, Lasso & ElasticNet](#chapter-10--ridge-lasso--elasticnet) | 01:20 | `L10-regularization` |
| 13:29 | [Chapter 11 — Gradient Descent & Feature Scaling](#chapter-11--gradient-descent--feature-scaling) | 01:18 | `L11-gradient-descent-scaling` |
| 14:48 | [Chapter 12 — Beyond plain OLS](#chapter-12--beyond-plain-ols) | 01:34 | `L12-beyond-ols` |
| 16:23 | [Chapter 13 — Transform, select, beware](#chapter-13--transform-select-beware) | 01:37 | `L13-transforms-selection-pitfalls` |
| 18:00 | [Chapter 14 — Time series & production pipelines](#chapter-14--time-series--production-pipelines) | 01:26 | `L14-time-series-pipelines` |

---

## Introduction

**Starts at 00:00** · length 00:12 · source `L00-intro` · hook: *"27 notebooks, one story: from a single line to production"*

**What you'll learn.** A 12-second agenda for the whole course: 14 chapters that follow the 27 notebooks (NB01–NB27) from fitting a single line to shipping a production pipeline. Every chapter builds only on earlier ones, so watching in order is the fastest path. All scores, coefficients and test values on screen come from the executed, corrected notebooks.

### What we'll cover

**[00:07]** Every number on screen comes from the executed notebooks.

> *On screen:* The agenda builds: 14 numbered circles pop in two columns, each chapter title typing in beside it.

The 14 chapters map onto the notebooks: e.g. Chapter 4 combines NB05 with the new NB23, Chapter 5 combines NB06 with the new NB24, and Chapter 11 pairs the corrected NB15 with the new NB21. Seven of the 27 notebooks (NB21–NB27) were added to cover gaps such as prediction intervals, categorical encoding and model selection, and several original notebooks were corrected first; see NOTEBOOK_FIXES.md in the ML folder. Where a visual is a sketch rather than real data, the video labels it 'illustrative'.


---

## Chapter 1 — Fitting a Line

**Starts at 00:12** · length 01:15 · source `L01-intuition-residuals` · hook: *"What makes one line "better" than another?"*

**What you'll learn.** The core idea behind every later chapter: a regression line is the one that makes the sum of squared residuals (SSR) as small as possible. Source: NB01 (10 students, hours studied vs exam score). No prerequisites. If you understand residuals and SSR, the formulas in Chapter 2 become 'just calculus'.

### Study hours → exam score

**[00:18]** 10 students: hours studied vs exam score (the NB01 data).

> *On screen:* Ten blue points appear on an hours-vs-score scatter plot (1 to 10 hours, scores 50 to 95).

This is the exact NB01 dataset: hours 1–10 and scores [50, 53, 61, 67, 70, 75, 79, 84, 89, 95]. The pattern is clearly rising and close to straight, which is the situation linear regression is built for. Everything in this chapter, including every SSR value, is computed from these ten points.

**[00:22]** Fitting a line means picking an intercept b0 and a slope b1: ŷ = b0 + b1·x.

> *On screen:* A red candidate line is drawn through the cloud, with the equation ŷ = b0 + b1·x shown beside it.

A line has only two numbers to choose: the intercept b0 (where it crosses x = 0) and the slope b1 (how much ŷ rises per unit of x). ŷ ('y-hat') is the line's prediction, not the observed value. 'Fitting' just means choosing b0 and b1 by some rule; the rest of the chapter shows the least-squares rule.

### Residual = actual − predicted

**[00:29]** A residual is the vertical gap between a point and the line.

> *On screen:* Vertical segments drop from each point to the line, one residual per student.

Residual = y − ŷ, the observed value minus the prediction, measured vertically (in y units), not perpendicular to the line. Vertical distance is used because the goal is to predict y from x; the x values are treated as given. Each student gets exactly one residual.

**[00:33]** Points above the line have positive residuals, points below have negative ones.

> *On screen:* Segments above the line are labelled positive and those below negative.

A positive residual means the line under-predicted that student, a negative one means it over-predicted. For a least-squares line with an intercept the residuals always sum to zero (NB03 measures about 2.13e-14), so 'average residual = 0' cannot tell a good line from a bad one. That is why we need something stronger than the plain sum.

### Square every residual

**[00:37]** Square each gap: each square's area is that residual squared.

> *On screen:* Each residual segment grows into a shaded square whose side equals the residual.

Squaring turns each residual into an area: a residual of 5 points becomes a 25-unit square. The picture makes it obvious that one big miss contributes far more than several small ones. This square-per-residual view is the classic StatQuest way to see 'sum of squares'.

**[00:41]** Add up the areas: the sum of squared residuals. For this line, SSR = 510.0.

> *On screen:* The squares' areas add up in a counter: SSR = 510.0 for the starting line 30 + 7x.

SSR (sum of squared residuals) = Σ(y − ŷ)². For the deliberately poor line ŷ = 30 + 7·x the ten squares add to exactly 510.0 (a value you can check by hand). SSR is the single number we will try to make as small as possible.

**[00:46]** Squaring stops positive and negative gaps from cancelling, and punishes big misses.

> *On screen:* The positive and negative gaps are highlighted to show they no longer cancel once squared.

If we summed raw residuals, +8 and −8 would cancel and a terrible line could score 0. Squaring makes every term positive and penalises large errors quadratically, which also makes the minimum easy to find with calculus (Chapter 2). The flip side: squaring makes OLS sensitive to outliers, which Chapter 12 addresses with robust regression.

### Find the line with the smallest SSR

**[00:50]** Change the intercept and slope, and the squares shrink or grow.

> *On screen:* The line starts to tilt and shift; the squares shrink or grow and the SSR counter updates live.

Each candidate (b0, b1) gives its own SSR, so SSR is really a function of two numbers. Moving the line closer to the bulk of the points shrinks the squares; moving it away grows them. The SSR shown during the sweep is recomputed for every in-between line (labels are rounded, so plugging the rounded coefficients in gives a slightly different SSR).

**[00:54]** Line b0 = 40, b1 = 5.5: SSR drops from 510.0 to 80.25.

> *On screen:* The line settles at 40 + 5.5x and the counter drops from 510.0 to 80.25.

Flattening the slope and raising the intercept already cuts SSR by more than 80%. You can verify: residuals for ŷ = 40 + 5.5x at x = 1..10 are 4.5, 2, 4.5, 5, 2.5, 2, 0.5, 0, −0.5, 0, whose squares sum to 80.25. Better, but not yet the best.

**[00:57]** Keep going until no change can make SSR any smaller…

> *On screen:* The line keeps adjusting in small steps as the SSR counter keeps falling.

Searching by trial and error works but is slow; the point of the sweep is to show that there is a single best line where no small change helps. That 'no direction improves it' condition is exactly what the derivative = 0 conditions in Chapter 2 express, and it is also what gradient descent (Chapter 11) searches for numerically.

**[01:00]** …the minimum: SSR = 11.16. This is the ordinary least squares (OLS) line.

> *On screen:* The line locks onto 45.20 + 4.93x and the counter stops at SSR = 11.16.

This is the ordinary least squares (OLS) line from NB01: score = 45.20 + 4.93·hours. No other straight line has a smaller SSR on these ten points; it fits so well that R² = 0.9945. Least squares is a choice of criterion, and Chapter 5 explains when it is the best choice (Gauss–Markov).

### Reading the OLS line

**[01:05]** The slope says each extra study hour adds about 4.93 points, on this data.

> *On screen:* The slope is annotated on the line as 'one more hour → about +4.93 points'.

The slope is an average rate of change: across these students, each extra hour of study goes with about 4.93 more points. It describes association in this data, not proof that studying causes the gain (causation is discussed in Chapter 13). With more predictors, the meaning becomes 'holding the others fixed' (Chapter 7).

**[01:10]** The intercept, 45.20, is the line's prediction at 0 hours. Careful: no student studied 0 hours.

> *On screen:* The intercept is marked where the line crosses 0 hours, with a warning that no student studied 0 hours.

Mathematically the intercept 45.20 is the predicted score at x = 0. But x = 0 lies outside the observed range (1–10 hours), so interpreting it is extrapolation. The intercept is often just an anchor that makes the line fit; treat its real-world meaning with care unless x = 0 is inside your data.

### Key takeaways  `[01:15]`

- Residual = actual − predicted (vertical gap)
- SSR adds up the squared residuals
- Squaring: no cancelling, big misses cost more
- OLS picks the line with the smallest SSR (11.16 here)

---

## Chapter 2 — Deriving the OLS Formula

**Starts at 01:27** · length 01:21 · source `L02-deriving-ols` · hook: *"Where do b0 and b1 actually come from?"*

**What you'll learn.** Where the OLS formulas come from: setting the two derivatives of SSR to zero gives b0 = ȳ − b1·x̄ and b1 = Cov(x,y)/Var(x), and the matrix form (XᵀX)b = Xᵀy generalises to many predictors. Sources: NB02 (5-point toy data) and NB03 (OLS written from scratch, checked against sklearn). Prerequisite: Chapter 1 (SSR).

### Five points, one best line

**[01:33]** The NB02 toy data: five points. Which line has the smallest SSR?

> *On screen:* Five points from the NB02 toy data appear: x = 1..5, y = 2, 4, 5, 4, 5.

A tiny dataset keeps the arithmetic visible: x̄ = 3 and ȳ = 4. We want the line minimising SSR(b0, b1) = Σ(y − b0 − b1·x)². Because SSR is a smooth bowl-shaped function of b0 and b1, its minimum is where both partial derivatives are zero.

**[01:37]** Setting the b0-derivative to zero puts the best line through the mean point (x̄, ȳ).

> *On screen:* Dashed mean lines cross at (x̄, ȳ) = (3, 4) and the best line is pinned through that point.

Setting ∂SSR/∂b0 = −2·Σ(y − b0 − b1·x) = 0 gives Σ residuals = 0 and therefore b0 = ȳ − b1·x̄. Geometrically: the OLS line always passes through the mean point (x̄, ȳ). That leaves only one unknown, the slope.

### The SSR bowl

**[01:45]** Rotate the line around the mean point and record SSR for every slope.

> *On screen:* The line rotates around the mean point while a dot traces the SSR value for each slope on a side plot.

With b0 tied to b1 by b0 = ȳ − b1·x̄, SSR becomes a function of the slope alone. For this data it is exactly SSR(b1) = 6 − 12·b1 + 10·b1², a parabola. Each rotation angle of the line corresponds to one point on that curve.

**[01:51]** SSR traces a bowl. Too flat or too steep both give a large SSR.

> *On screen:* The traced dots form a U-shaped bowl; steep and flat lines sit high on its walls.

A slope that is too small leaves the right-hand points far above the line; a slope that is too large overshoots them. Both raise SSR, so the curve is a bowl with a single lowest point. This convexity is why least squares always has a unique solution when the x values are not all identical.

**[01:57]** At the bottom the bowl is flat: the derivative is zero. That point is the OLS slope.

> *On screen:* A flat tangent touches the bottom of the bowl at b1 = 0.6, where SSR = 2.40.

At the minimum the slope of the bowl is zero: d SSR/d b1 = −12 + 20·b1 = 0 gives b1 = 0.6, and SSR(0.6) = 6 − 7.2 + 3.6 = 2.40. Solving the derivative in general gives the formula on the next slide. Gradient descent (Chapter 11) reaches the same point by walking downhill instead of solving.

### b1 = Σ(x−x̄)(y−ȳ) / Σ(x−x̄)²

**[02:05]** Subtract the means, multiply, and add: the products sum to 6, the squares to 10.

> *On screen:* A table fills in row by row: deviations (x − x̄), (y − ȳ), their products and squares, summing to 6 and 10.

The slope formula is b1 = Σ(x − x̄)(y − ȳ) / Σ(x − x̄)². For the toy data the cross-products sum to 6.0000 and the squared x-deviations to 10.0000 (NB02's printed values). Centring on the means is what makes the formula so compact.

**[02:10]** So b1 = 0.6 and b0 = 2.2: the same line the bowl found. b1 is Cov(x, y) / Var(x).

> *On screen:* The result b1 = 0.6, b0 = 2.2 appears and the fitted line is drawn on the points.

b1 = 6 / 10 = 0.6 and b0 = 4 − 0.6·3 = 2.2, exactly the bottom of the bowl. Dividing numerator and denominator by n − 1 shows b1 = Cov(x, y) / Var(x): the slope is how much x and y move together, scaled by how much x moves on its own.

### Matrix form: works for any number of x's

**[02:17]** Add a column of 1s to x. Solving (XᵀX)b = Xᵀy gives [2.2, 0.6] again.

> *On screen:* A design matrix X with a column of 1s builds up, then (XᵀX)b = Xᵀy is solved to give [2.2, 0.6].

Stacking a column of ones (for the intercept) next to x gives X; the normal equations (XᵀX)b = Xᵀy solve all coefficients at once. In NB02, XᵀX = [[5, 15], [15, 55]] and Xᵀy = [20, 66], giving b = [2.2, 0.6] (Match: True). The same equation works unchanged for any number of predictors, but in code solve it with lstsq/QR rather than inverting XᵀX (Chapter 5).

### NB03: OLS from scratch, checked against sklearn

**[02:25]** Pure-Python OLS on the salary data gives b1 = 6.3636, the same as sklearn.

> *On screen:* A side-by-side panel shows the pure-Python result next to sklearn's: b0 = 32.0000, b1 = 6.3636 on the salary data.

NB03 implements OLS with nothing but loops and the formulas above, on salary vs years (1–10). It gets b0 = 32.0000 and b1 = 6.3636, matching sklearn's LinearRegression to 8 decimals, with R² = 0.994318. Writing it once by hand is the best way to know exactly what the library is doing.

**[02:30]** Residuals sum to about 0 (2.13e-14), as they always do with an intercept.

> *On screen:* The residuals of the from-scratch fit are summed and the total shows 2.13e-14.

Including an intercept forces Σ residuals = 0 (that was the b0 derivative condition), so the tiny 2.13e-14 is just floating-point rounding. NB03 also reports SSR = 19.0909 and RMSE = 1.3817; note that RMSE there divides by n (√(19.09/10)) while the error variance estimate σ² divides by n − 2 (two estimated coefficients).

### Key takeaways  `[02:35]`

- SSR as a function of the slope is a bowl
- OLS sits where the derivatives are zero
- b1 = Σ(x−x̄)(y−ȳ)/Σ(x−x̄)²,  b0 = ȳ − b1·x̄
- Matrix form (XᵀX)b = Xᵀy scales to many x's

---

## Chapter 3 — R²: What Does It Measure?

**Starts at 02:49** · length 01:08 · source `L03-r2-adjusted-r2` · hook: *"How much of the variation does the line actually explain?"*

**What you'll learn.** What R² actually measures: the share of y's variation the line explains, from the decomposition SS_tot = SS_reg + SS_res. Then why plain R² can be gamed by adding predictors and how adjusted R² penalises that. Source: NB04 (plus NB01's line for comparison). Prerequisites: Chapters 1–2.

### Start with no model at all: the mean

**[02:56]** Predicting ȳ for everyone leaves these gaps. Their squared sum is SS_tot.

> *On screen:* A horizontal mean line is drawn through an illustrative scatter and vertical gaps drop from every point to it.

The simplest possible 'model' predicts ȳ for everyone. Its squared gaps add up to SS_tot = Σ(y − ȳ)², the total variation in y. Every model is judged against this baseline. (The scatter shown is illustrative; the numbers on screen are NB04's.)

### Now fit the line

**[03:02]** Gaps from the points to the line: what the line still misses. That's SS_res.

> *On screen:* The fitted line appears and new, shorter gaps connect each point to the line.

SS_res = Σ(y − ŷ)² is what the line still fails to explain, the same SSR as Chapter 1. A useful line should make these gaps much smaller than the gaps to the mean.

**[03:06]** Gaps from the line to the mean: what the line explains. That's SS_reg.

> *On screen:* Gaps between the line and the mean line are highlighted at each x.

SS_reg = Σ(ŷ − ȳ)² is the part of the variation the line accounts for: how far its predictions move away from the flat mean. For OLS with an intercept the cross term vanishes, so the three pieces add up exactly.

### SS_tot = SS_reg + SS_res

**[03:11]** In NB04 the total 2518.55 splits exactly into 1987.59 explained + 530.96 left over.

> *On screen:* Two stacked bars build up: 1987.59 explained plus 530.96 residual equals the 2518.55 total.

NB04 (seed 42, 40 points, y = 3x + 5 + noise) prints SS_tot = 2518.55, SS_reg = 1987.59 and SS_res = 530.96, and 1987.59 + 530.96 = 2518.55. This decomposition is exact in-sample for OLS with an intercept; it is what gives R² its 'fraction explained' meaning.

**[03:16]** R² = 1 − SS_res / SS_tot = 0.7892: the line explains 78.9% of the variation in y.

> *On screen:* The ratio is computed on screen: R² = 1 − 530.96 / 2518.55 = 0.7892.

R² = 1 − SS_res/SS_tot = SS_reg/SS_tot = 0.7892, so the line explains 78.9% of the variation in y; the remaining 21.1% is scatter around the line. In simple regression R² also equals the squared correlation between x and y.

**[03:20]** For comparison, the NB01 study-hours line reaches R² = 0.9945: almost no scatter left.

> *On screen:* A comparison bar for the NB01 study-hours line rises to 0.9945.

The NB01 line (score = 45.20 + 4.93·hours) leaves almost no scatter, so R² = 0.9945. Higher R² means tighter points around the line, but whether 0.79 is 'good' depends entirely on the field: noisy social data rarely exceeds 0.3, physics experiments often exceed 0.99.

### What R² does NOT tell you

**[03:25]** R² measures fit, not truth. Check residual plots too, and judge it on held-out data.

> *On screen:* Three warning cards slide in: R² is not truth, check residual plots, judge on held-out data.

A curved relationship can still give a high R² with a straight line, so always inspect residuals (Chapter 6). R² says nothing about causation or whether coefficients are unbiased. And it is only guaranteed to lie between 0 and 1 in-sample for OLS with an intercept: on test data R² can be negative, as in Chapters 9–10.

### Adjusted R²: a penalty for extra predictors

**[03:30]** Plain R² never goes down when you add a predictor, even a useless one.

> *On screen:* A plain-R² bar creeps upward as useless predictors are added one by one.

Adding any predictor, even pure noise, can only lower SS_res on the training data, so R² never decreases. This makes R² useless for choosing how many predictors to keep. NB04 demonstrates it by adding pure-noise columns to a pure-noise target (seed 0, n = 60).

**[03:33]** With 24 noise predictors R² climbs to 0.392, but adjusted R² stays near zero: −0.024.

> *On screen:* Paired bars compare R² and adjusted R² at k = 1, 10 and 24 noise predictors.

Adjusted R² = 1 − (1 − R²)(n − 1)/(n − k − 1) charges a price for every predictor. In NB04: k = 1 gives R² 0.006 vs adjusted −0.011, k = 10 gives 0.251 vs 0.098, and k = 24 gives 0.392 vs −0.024. Plain R² 'explains' 39% of pure noise; adjusted R² correctly says nothing is explained.

**[03:38]** Compare models with different numbers of predictors using adjusted R², not R².

> *On screen:* A rule-of-thumb card appears: compare models with adjusted R², not R².

Adjusted R² can go down when a predictor adds less than it costs, so it is a fairer in-sample comparison between models of different size. Even better are cross-validated scores (Chapter 9) or AIC/BIC (Chapter 13). Adjusted R² can be negative, which simply means the model does worse than predicting the mean after the penalty.

### Key takeaways  `[03:43]`

- SS_tot = SS_reg + SS_res (NB04: 2518.55 = 1987.59 + 530.96)
- R² = share of variation explained (0.7892 here)
- High R² is not causation, and not a correct model
- Adjusted R² penalises predictors that add nothing

---

## Chapter 4 — Inference & Intervals

**Starts at 03:57** · length 01:22 · source `L04-inference-and-intervals` · hook: *"How sure are we about the slope, and about one prediction?"*

**What you'll learn.** How sure can we be about a fitted slope? Standard errors, the t-test, p-values and confidence intervals (NB05), then the difference between a confidence interval for the mean response and a prediction interval for one new observation (NB23, a notebook added to fill a gap). Prerequisites: Chapters 1–3. This is the chapter that answers 'how wrong could this forecast be?'.

### Another sample, another slope

**[04:03]** Each new sample of 40 points gives a slightly different slope.

> *On screen:* Repeated illustrative samples of 40 points each produce slightly different fitted lines, and their slopes stack into a histogram.

Our data is one random sample, so b1 is a random quantity: a different sample would give a different slope. NB05 uses n = 40 with true slope 2.5 and estimates b1 = 2.3792 from its sample. The histogram (illustrative) shows the sampling distribution of b1, centred on the true slope.

**[04:07]** The standard error, 0.2594, is how much b1 typically wobbles from sample to sample.

> *On screen:* The spread of the slope histogram is marked as the standard error, 0.2594.

SE(b1) = √(σ̂² / Σ(x − x̄)²), where σ̂² = SSR/(n − 2) = 19.0947 in NB05. It shrinks with less noise, more data, and more spread in x. SE is the yardstick for everything that follows: tests and intervals are 'estimate measured in standard errors'.

### Is the slope really non-zero? The t-test

**[04:14]** If the true slope were 0, t would almost always land inside ±2.02.

> *On screen:* A t-distribution curve with 38 degrees of freedom is drawn with shaded cut-offs at ±2.02.

Under the null hypothesis H0: true slope = 0, the statistic t = b1/SE(b1) follows a t-distribution with n − 2 = 38 degrees of freedom. 95% of that distribution lies within ±2.0244, so landing outside would happen only 5% of the time if H0 were true.

**[04:18]** Ours is 9.17, far in the tail: p = 3.55e-11. Reject H0, the slope is real.

> *On screen:* A marker for the observed t = 9.17 lands far out in the right tail, and p = 3.55e-11 appears.

t = 2.3792 / 0.2594 = 9.17: the slope is over nine standard errors away from zero. The p-value, the probability of a |t| this large if the true slope were 0, is 3.55e-11, so we reject H0. In simple regression the overall F statistic equals t² (84.14 in the NB05 summary).

### 95% confidence interval for the slope

**[04:25]** Estimate ± t* × SE gives the interval [1.854, 2.904].

> *On screen:* An interval bar grows outward from the estimate 2.3792 to [1.854, 2.904].

A 95% confidence interval is b1 ± t*·SE = 2.3792 ± 2.0244·0.2594 = [1.854, 2.904]. The same recipe gives the intercept interval [2.055, 8.472]. Reporting the interval is more informative than the p-value alone, because it shows the plausible size of the effect.

**[04:28]** 0 is outside the interval (so the slope is significant); the true 2.5 is inside.

> *On screen:* Markers for 0 and the true slope 2.5 are placed on the axis: 0 falls outside the bar, 2.5 inside.

If 0 is outside the 95% CI, the two-sided test at the 5% level rejects H0: the CI and the t-test always agree. Here the true value 2.5 is inside, as it should be most of the time. Always check practical size too: a significant slope can still be too small to matter.

**[04:33]** "95%" is about the method: in NB05, 191 of 200 simulated intervals caught the true slope.

> *On screen:* A row of 16 illustrative interval bars appears; most cross the true-slope line, a few miss it.

'95% confidence' describes the procedure, not one interval: if you repeated the study many times, about 95% of the intervals built this way would contain the true slope. NB05's simulation caught it in 191 of 200 intervals (95.5%). Any single interval either contains the truth or does not.

### Confidence interval vs prediction interval

**[04:39]** The confidence interval (blue) says where the AVERAGE y lies at each x.

> *On screen:* A narrow blue band is drawn around the NB23 fitted line, ŷ = 6.423 + 1.678x.

The confidence interval for the mean response at x0 is ŷ ± t*·se_fit, where se_fit = σ̂·√(1/n + (x0 − x̄)²/Σ(x − x̄)²). It answers 'where is the average y at this x?'. NB23 uses 30 points (seed 23) with σ̂ = 3.724.

**[04:42]** The prediction interval (orange) says where ONE new observation will land: much wider.

> *On screen:* A much wider orange band appears around the blue one.

A prediction interval for one new observation must also include that observation's own noise: se_pred = √(se_fit² + σ̂²). At x̄ = 4.915 the CI is only 2.79 wide but the PI is 15.51 wide, 5.6 times wider. More data shrinks the CI toward zero, but the PI never gets narrower than about 2·1.96·σ (11.76 in NB23).

**[04:46]** Both are narrowest at x̄ and widen as you move away from the data's centre.

> *On screen:* Both bands are seen pinching in at x̄ and flaring out toward the ends of the data.

The (x0 − x̄)² term makes both intervals narrowest at the centre of the data and wider toward the edges, because small errors in the slope are amplified far from the mean point. At x0 = 9 the CI is [18.983, 24.060] versus [13.276, 16.061] at x̄.

**[04:51]** Use the PI for a single forecast: the CI caught a new point only 46.7% of the time.

> *On screen:* A warning card shows the coverage numbers: the CI caught a new point only 46.7% of the time.

In NB23's 2,000-sample simulation at x0 = 9, the CI contained the true mean 95.1% of the time and the PI contained a new observation 95.7% of the time, both close to the promised 95%. Misusing the CI as a forecast range covered new points only 46.7% of the time. For 'what will this one house sell for?', always report the PI.

**[04:55]** Outside the data, the bands simply assume the line still holds.

> *On screen:* The bands are extended into a shaded 'no data here' region beyond x = 10.

Both intervals are computed from the fitted line, so beyond the data they silently assume the straight-line relationship continues. They grow a little wider, but that width only reflects sampling noise, not the risk that the true relationship bends.

**[04:58]** NB23 curved-truth test: at x0 = 15 the true mean 72.5 fell outside the PI [32.3, 44.8].

> *On screen:* A curved true-mean line rises steeply past x = 10 and leaves the prediction band behind.

In NB23's extrapolation test the truth is straight on [0, 10] and curves upward after 10. Inside the data the PIs contain the true mean, but at x0 = 15 the true mean 72.5 lies far outside the PI [32.3, 44.8], and at x0 = 20 the true 195.0 is far outside [43.2, 57.4]. Intervals cannot protect you from a wrong model.

### Key takeaways  `[05:04]`

- SE = how much a coefficient wobbles across samples
- t = b / SE; large |t| ⇒ small p (3.55e-11 in NB05)
- CI = estimate ± t* × SE ([1.854, 2.904] for b1)
- Prediction interval ≫ confidence interval (5.6× at x̄)

---

## Chapter 5 — Assumptions & Gauss–Markov

**Starts at 05:19** · length 01:28 · source `L05-assumptions-gauss-markov` · hook: *"When can you trust the fitted line?"*

**What you'll learn.** The LINE assumptions (Linearity, Independence, Normality, Equal variance), how to test each one, and what actually breaks when they fail (NB06, corrected). Then the theory that justifies least squares: the Gauss–Markov theorem, the Gaussian-MLE link, and how to solve OLS in a numerically stable way (NB24, newly added). Prerequisites: Chapters 1–4.

### LINE: four promises about the errors

**[05:26]** Every test below looks at the residuals, the leftovers after the fit.

> *On screen:* The word LINE builds letter by letter, each letter labelled with its assumption about the errors.

The four classic assumptions are Linearity, Independence, Normality and Equal variance (homoscedasticity). They are statements about the errors, which we can only see through the residuals, so every diagnostic in this chapter (and in Chapter 6) works on residuals.

### L — Linearity

**[05:32]** A U-shape means a straight line is the wrong model: the estimates are biased.

> *On screen:* An illustrative residual plot shows a clear U-shape around zero.

If the true relationship is curved (NB06 uses y = 0.5x² + noise), a straight line misses systematically: residuals are positive at both ends and negative in the middle. That is bias, not noise, so more data does not fix it. Remedies: add polynomial terms or transform variables (Chapters 9 and 13).

### I — Independence

**[05:39]** Correlated errors snake up and down. Neighbours share information.

> *On screen:* An illustrative residual series snakes up and down in long runs above and below zero.

Independence fails when one error predicts the next, typical for time-ordered data. NB06 simulates AR(1) errors with ρ = 0.85: residuals stay positive or negative for long stretches. Each new point then carries less new information than OLS assumes.

**[05:42]** DW near 2 means independent. Far below 2 means positive autocorrelation: SEs too small.

> *On screen:* Durbin–Watson values appear: 2.03 for independent errors, 0.45 for the autocorrelated case.

Durbin–Watson ≈ 2·(1 − lag-1 autocorrelation), so 2 means no autocorrelation and values well below 2 mean positive autocorrelation. NB06 measures 2.03 (independent) vs 0.45 (ρ = 0.85). The coefficients stay unbiased, but the usual SEs are too small and p-values too optimistic; use HAC (Newey–West) SEs or model the time structure (Chapters 12 and 14).

### N — Normality of residuals

**[05:47]** Shapiro–Wilk tests the shape of the residual histogram.

> *On screen:* Two illustrative residual histograms appear side by side, one bell-shaped and one right-skewed, with Shapiro–Wilk p-values.

Shapiro–Wilk tests whether residuals look normal. NB06 gets p = 0.7918 for normal errors (no evidence against normality) and p = 1.673e-09 for right-skewed errors (clearly non-normal); heavy-tailed errors give 1.829e-05. A Q-Q plot (Chapter 6) shows the same thing visually.

**[05:50]** Non-normal residuals mostly hurt exact small-sample p-values and CIs, not the estimates.

> *On screen:* A note card explains that non-normality mainly affects small-sample p-values and intervals.

OLS coefficients do not need normal errors to be unbiased or best linear unbiased. Normality is what makes t-tests and confidence intervals exact in small samples; with larger n the central limit theorem makes them approximately right anyway. Severe skew is often better handled by transforming y (Chapter 13).

### E — Equal variance (homoscedasticity)

**[05:55]** A funnel: the error spread changes with x.

> *On screen:* An illustrative residual funnel widens from left to right.

Equal variance means the error spread is the same at every x. In NB06's violated case the error SD is 0.4·x, so the scatter fans out. Breusch–Pagan tests this: p = 0.587 for constant variance vs p = 2.94e-05 for the funnel.

**[05:57]** Estimates stay unbiased, but the usual standard errors are wrong.

> *On screen:* A card notes that estimates stay unbiased but the classic standard errors become wrong.

Heteroscedasticity does not bias b0 or b1, but the textbook SE formula assumes one common σ², so SEs, p-values and CIs can be misleading. Fixes: robust (HC3) standard errors or weighted least squares, both shown in Chapter 12 (NB25).

### Gauss–Markov: when is OLS the best?

**[06:02]** Four conditions make OLS the lowest-variance linear unbiased estimator. Normality isn't one.

> *On screen:* Four condition cards appear for Gauss–Markov; a normality card is shown crossed out.

Gauss–Markov theorem: if the model is linear in its coefficients, the errors have mean zero given x (exogeneity), equal variance, and no autocorrelation, then OLS is BLUE, the Best (lowest-variance) Linear Unbiased Estimator. Normality is not required. The original NB06 text overstated this, and it was corrected.

### Checked by simulation: 10,000 samples (NB24)

**[06:07]** Both unbiased, but OLS varies 1.34x less, even with non-normal errors.

> *On screen:* Two histograms from 10,000 simulated samples compare the OLS slope with a two-group slope estimator; the OLS one is narrower.

NB24 simulates y = 1 + 2x with uniform (non-normal) errors. Both estimators are unbiased (means 1.9982 and 1.9978), but the OLS slope has variance 0.00843 vs 0.01127 for the two-group slope, 1.34 times smaller. That is Gauss–Markov in action, with no normality needed.

**[06:11]** Break equal variance and OLS loses: weighted least squares is 3.10x less variable.

> *On screen:* A second comparison shows the WLS histogram much narrower than OLS when the error variance grows with x.

With error SD = 0.3 + 0.6x, the equal-variance condition fails, and OLS is no longer best: weighted least squares (weights 1/σ²) has slope variance 0.01613 vs 0.04999 for OLS, 3.10 times smaller. Both remain unbiased. This is why diagnosing heteroscedasticity matters.

### Where normality matters: maximum likelihood

**[06:17]** With Gaussian noise, the likelihood peak is exactly the OLS line.

> *On screen:* Two equation cards appear: 'Gaussian errors, maximize likelihood' equals 'minimize SSR', with matching MLE and OLS coefficients.

If errors are Gaussian, the log-likelihood is a constant minus SSR/(2σ²), so maximising the likelihood is exactly minimising SSR. NB24 confirms numerically: BFGS on the negative log-likelihood gives b0 = 0.72929, b1 = 2.14691, identical to OLS. The MLE of σ² divides by n (4.06279), while the unbiased OLS estimate divides by n − 2 (4.27662).

**[06:21]** Normality is what makes the t-tests, p-values and CIs exact in small samples.

> *On screen:* A summary card links normality to exact t-tests, p-values and confidence intervals.

Normality earns its place in inference, not estimation: with Gaussian errors, (b1 − β1)/SE follows an exact t-distribution at any sample size, which is what Chapter 4's p-values and intervals rely on. Without it, those results are approximations that improve as n grows.

### Solve it safely: avoid inverting XᵀX

**[06:26]** Normal equations square the condition number. QR and SVD stay accurate far longer.

> *On screen:* Error bars for four solvers appear across polynomial degrees; the normal-equation bars explode first.

Forming XᵀX squares the condition number: cond(XᵀX) = cond(X)². In NB24's polynomial design at degree 9 (cond(X) = 6.2e+10), inv(XᵀX) gives an error of 3.8e+03 and solve(XᵀX) 4.1e+01, while QR gives 9.1e-07 and SVD/lstsq 3.6e-07. The maths is the same; only floating-point accuracy differs.

**[06:31]** In practice: np.linalg.lstsq or a QR solver, never inv().

> *On screen:* A code card recommends np.linalg.lstsq or a QR solver, with inv() crossed out.

In practice call np.linalg.lstsq (SVD-based), a QR solver, or a library such as sklearn/statsmodels, which already avoid explicit inversion. Never compute inv(XᵀX) @ Xᵀy for real problems. Scaling the features (Chapter 11) also reduces the condition number.

### Key takeaways  `[06:35]`

- LINE: check residuals for curve, snake, skew, funnel
- Gauss–Markov: OLS is BLUE without normality
- Unequal variance → WLS / robust SEs (3.10x here)
- Gaussian MLE = OLS; solve with QR/SVD

---

## Chapter 6 — Diagnostics & influence

**Starts at 06:48** · length 01:16 · source `L06-diagnostics-influence` · hook: *"Which points can bend your regression line?"*

**What you'll learn.** This chapter teaches how to tell a harmless outlier from an influential point that rewrites your model, and which four diagnostic plots to run after every fit. It uses the real data from NB07 (seed 42, 70 points on a trend plus one far-out point, obs 70). Prerequisites: residuals (Chapter 1) and the assumptions (Chapter 5). One badly placed point can change a slope by 25%, and you won't see it in R².

### 70 points on a trend, plus one far out in x

**[06:55]** Fit the 70 ordinary points: slope 2.717. One point (red) sits far above the trend.

> *On screen:* The 70 trend points appear on the axes with the fitted line drawn through them, and the red obs 60 sits well above the trend.

Obs 60 has an ordinary x value but a large positive residual: it is an outlier in y. With obs 70 left out, the line fitted to these points has slope 2.717 (intercept 2.872). Keep that number in mind, because it is the baseline every later comparison is made against.

**[07:01]** Now add obs 70 at x = 16, and drag it down to y = 15. The trend predicts about 44.

> *On screen:* The orange obs 70 drops in at x = 16, far to the right of all other points, and slides down to y = 15.

Obs 70 sits far outside the range of the other x values (most points have x below about 10). The trend line would predict about 44 there, but the point sits at 15, so it has both an unusual x and a huge residual. That combination is what makes a point dangerous.

**[07:05]** One point drags the whole line: slope 2.717 → 2.171.

> *On screen:* The regression line rotates downward toward obs 70 as it is dragged, and the slope label changes from 2.717 to 2.171.

OLS minimizes squared residuals, so a far-away point with a big residual gets enormous weight: rotating the line toward it reduces its huge squared error more than it costs everywhere else. A single point out of 71 cut the slope by about 20%. Points far from x̄ act like a long lever on the line.

**[07:08]** Remove the red y-outlier instead and the slope barely moves: 2.171 → 2.016.

> *On screen:* Obs 60 fades out instead, and the line barely moves; the slope label reads 2.016.

Removing the y-outlier obs 60 changes the slope only from 2.171 to 2.016, because it sits near the middle of the x range, where it can shift the line up or down but can't tilt it much. Its residual is large (studentized 5.54), yet its influence is moderate (Cook's D 0.493).

**[07:12]** Influence needs BOTH: a big residual and an unusual x (leverage).

> *On screen:* Two labels, 'big residual' and 'unusual x', combine into one 'influential' badge.

Influence is roughly residual size times leverage. A big residual at an ordinary x (obs 60) mostly shifts the intercept; an unusual x with a tiny residual is a 'good' leverage point that actually helps; only a big residual at an unusual x (obs 70) drags the slope. That is why you have to check both.

### Leverage and Cook's distance

**[07:17]** Obs 70 has 3.5x the leverage cut-off and Cook's D 3.572: it is influential.

> *On screen:* A table shows leverage and Cook's D for obs 60 and obs 70, next to the rules of thumb leverage > 4/n = 0.056 and Cook's D > 1.

Leverage h_ii is the diagonal of the hat matrix H = X(XᵀX)⁻¹Xᵀ and only depends on x: it measures how far a point sits from the centre of the x values. Obs 70 has leverage 0.194, about 3.5× the 4/n = 0.056 threshold. Its Cook's D of 3.572 is far above 1, while obs 60 has leverage 0.031 and Cook's D 0.493.

**[07:22]** Cook's D: how much ALL fitted values change if one point is removed.

> *On screen:* Cook's D bars rise for all 71 points; nearly all stay tiny while obs 70's bar towers over the rest.

Cook's distance measures how much all fitted values move, in standardized units, when one point is deleted. It combines residual and leverage in one number: roughly D_i ∝ (studentized residual)² × h_ii/(1 − h_ii). Values above 1 (or a stricter 4/n) are worth a closer look.

### The four plots to run after every fit

**[07:28]** 1. Residuals vs fitted: look for a curve (non-linearity) or a funnel.

> *On screen:* The first panel draws residuals against fitted values around a flat zero line.

If the model is right, residuals scatter evenly around zero with no shape. A curve means you missed a non-linear term (Chapter 9), and a funnel that widens means unequal variance (Chapters 5 and 12). Here the cloud is flat, and the two unusual points stand out above and below.

**[07:31]** 2. Normal Q-Q: points should follow the line. Ours peel off at both ends.

> *On screen:* The Normal Q-Q panel plots sorted residuals against theoretical normal quantiles, and the extreme points bend away from the diagonal.

On a Q-Q plot, normal residuals fall on the straight line. Our two outliers have studentized residuals of +5.54 and −5.44, far beyond what a normal distribution produces in 71 points, so the ends peel off. Heavy tails like this make t-based p-values and intervals less trustworthy.

**[07:34]** 3. Scale-location: √|standardized residual|. A rising trend means unequal variance.

> *On screen:* The scale-location panel plots √|standardized residual| against fitted values.

Taking the square root of the absolute residual turns spread into height, so a trend upward means the noise grows with the fitted value (heteroscedasticity). A flat band means the equal-variance assumption looks fine. The Breusch–Pagan test in Chapter 5 is the formal version of this plot.

**[07:38]** 4. Residuals vs leverage: danger lives in the far corners, like obs 70.

> *On screen:* The residuals-vs-leverage panel spreads points horizontally by leverage, and obs 70 sits alone in the far right corner.

This panel puts both ingredients of influence on one chart: leverage on the x-axis and standardized residual on the y-axis. Ordinary points crowd the left; danger lives in the top-right and bottom-right corners, where both are large. That is exactly where obs 70 lands.

**[07:41]** Every panel flags the same two points: red obs 60 and orange obs 70.

> *On screen:* Obs 60 (red) and obs 70 (orange) are highlighted in all four panels at once.

Diagnostics are meant to be read together: one plot can mislead, but a point flagged everywhere is a real story. Obs 60 is flagged mainly by its residual, and obs 70 by its leverage plus residual. Always check the actual rows behind flagged points before deciding anything.

**[07:46]** Don't just delete points: check the data, then consider robust regression.

> *On screen:* A short checklist appears: check the data first, then consider robust regression.

Deleting a point because it's inconvenient is a form of p-hacking. First ask whether it's a data-entry error or a different population. If the point is genuine, use a method that limits its pull, such as Huber or RANSAC regression (Chapter 12), or report results with and without it.

### Key takeaways  `[07:51]`

- Run the 4 plots after every fit
- Outlier in y + ordinary x: slope barely moves
- High leverage + big residual = influential
- obs 70: Cook's D 3.572, slope 2.717 → 2.171

---

## Chapter 7 — Multiple regression & categories

**Starts at 08:04** · length 01:24 · source `L07-multiple-regression-categorical` · hook: *"What does one coefficient mean when there are eight?"*

**What you'll learn.** This chapter extends the single line to many predictors and shows how to read each coefficient 'holding everything else fixed', using California Housing (NB08, 20,640 blocks, 8 predictors). It then shows how to put categories such as a city into a regression correctly with one-hot encoding, and why keeping every dummy breaks OLS (NB22). Prerequisites: the matrix form of OLS (Chapter 2) and inference (Chapter 4). Almost every real dataset has several predictors and at least one categorical column.

### From one x to many

**[08:10]** One slope per predictor. California Housing: 20,640 blocks, 8 predictors.

> *On screen:* The equation y = b0 + b1·x1 + … + b8·x8 builds up term by term next to a sketch of the design matrix.

Multiple regression fits one slope per predictor, all at the same time. California Housing (NB08) has 20,640 census blocks, 8 predictors such as median income, house age and location, and a target of median house value in units of $100k.

**[08:14]** The column of 1s carries the intercept. The normal equations just get bigger.

> *On screen:* A column of 1s appears at the left of the design matrix X, and the normal equations (XᵀX)b = Xᵀy appear below it.

The intercept is just the coefficient on a column of ones, so it fits into the same formula as every other coefficient. Chapter 2's normal equations work unchanged: XᵀX is now 9×9 instead of 2×2. The solution b = (XᵀX)⁻¹Xᵀy only exists when no column is a combination of the others, which becomes important later in this chapter.

### The fitted coefficients (statsmodels, NB08)

**[08:22]** Raw coefficients live in different units, so bar lengths are not importance.

> *On screen:* The 8 fitted coefficients appear as signed horizontal bars, some pointing left (negative) and some right.

The raw coefficients from statsmodels are, for example, MedInc 0.4367, AveBedrms 0.6451, Latitude −0.4213 and Population −3.976e-06. Each one is 'per one unit' of its own predictor, and the units differ (income in $10k, population in people), so a long bar doesn't mean an important feature. Standardize the predictors first if you want to compare sizes (NB08's coefficient plot is per 1 standard deviation of x).

**[08:26]** Population is the only one that isn't significant (p = 0.402).

> *On screen:* The Population bar is highlighted with its p-value of 0.402 while the others are marked significant.

With 20,640 rows, even small effects become statistically significant, so 7 of the 8 predictors have tiny p-values. Population is the exception: given the other seven, adding people to a block tells you almost nothing extra about price (p = 0.402). Statistical significance is not practical importance, especially with very large n.

### Ceteris paribus: holding everything else fixed

**[08:31]** b1 = 0.4367: one more unit of median income, same everything else, adds about $43.7k.

> *On screen:* Two identical-looking house cards differ only in median income, 3.5 vs 4.5, and the price difference +$43.7k appears.

Ceteris paribus means 'all else equal'. b1 = 0.4367 says: raise MedInc by one unit ($10k of income) while keeping house age, rooms, location and everything else fixed, and the predicted value goes up by 0.4367 × $100k ≈ $43.7k. This is different from the slope of a simple regression on income alone, which also absorbs the effects of correlated variables such as location.

**[08:36]** DW 0.885 warns of spatially correlated errors: the SEs here are optimistic.

> *On screen:* The summary statistics R² 0.606, F 3970.36 and Durbin–Watson 0.885 appear, with DW highlighted.

R² = 0.606 and a huge F-statistic say the predictors jointly explain a lot. But DW = 0.885 is well below 2, because the rows are ordered by location and neighbouring blocks have similar errors (spatial correlation). That breaks the 'no autocorrelation' assumption, so the printed standard errors are too small and the p-values too optimistic.

### Categories: house price by city A, B, C (NB22)

**[08:41]** Coding cities 1, 2, 3 forces an order and equal steps. The truth is B > C > A.

> *On screen:* City labels A, B, C turn into the numbers 1, 2, 3 with a single straight line through them, next to bars of the true city effects.

Label encoding forces the model to assume cities are ordered and evenly spaced, so it fits one slope of 28.36 per 'step'. The real effects are A = 0, B = +90, C = +40: not in order and not evenly spaced. Label encoding only reaches R² 0.8757.

### One-hot encoding, and the dummy-variable trap

**[08:48]** One 0/1 column per city: exactly one 1 per row.

> *On screen:* A one-hot matrix builds row by row with one column per city, each row containing exactly one 1.

One-hot encoding replaces the city column with three 0/1 indicator columns, one per city. Each house gets a 1 in its own city's column and 0 elsewhere. The model can then learn a separate shift for each city, with no order assumed.

**[08:52]** Keep all three and they add up to the intercept column: perfect collinearity.

> *On screen:* The three dummy columns are added together and their sum matches the column of 1s, row by row.

Every row has exactly one city, so A + B + C = 1 for every row, which is exactly the intercept column. One column is a perfect linear combination of others: perfect multicollinearity. In NB22 the design matrix has 5 columns but rank only 4.

**[08:56]** XᵀX can't be inverted: there is no single answer. That's the dummy trap.

> *On screen:* det(XᵀX) = 0 appears, and two different coefficient vectors produce identical predictions.

When the columns are linearly dependent, XᵀX is singular (its determinant is 0; NB22 prints cond(XᵀX) ≈ 2.5e18), so it can't be inverted. NB22 shows two coefficient sets, one with the intercept raised by 10 and each dummy lowered by 10, giving identical predictions (maximum difference 0.0). There are infinitely many 'best' fits, so no coefficient means anything. That's the dummy-variable trap.

**[09:00]** Fix: drop one dummy (drop_first). City A becomes the reference.

> *On screen:* The city A column is crossed out, leaving const, size, B and C, and the rank shows 4 of 4.

Dropping one dummy (pandas get_dummies(drop_first=True) or OneHotEncoder(drop='first')) restores full rank. The dropped city becomes the reference, absorbed into the intercept. Which city you drop changes the meaning of the coefficients, not the predictions: NB22 shows identical R² 0.966652 with A or C as the reference.

### Reading dummy coefficients: differences vs city A

**[09:05]** Each dummy is a price difference from the reference city, holding size fixed.

> *On screen:* Coefficient bars for B vs A (+89.24k) and C vs A (+38.24k) appear with their confidence intervals, and R² 0.9667 is compared with 0.8757.

Each dummy coefficient is the price difference from the reference city for a house of the same size: B costs 89.24k more than A (95% CI [84.05, 94.43]) and C costs 38.24k more (CI [32.05, 44.43]), close to the true +90 and +40. C vs B is the difference, −51.00k. One-hot encoding lifts R² from 0.8757 to 0.9667.

**[09:10]** In a pipeline, an unseen city gets all-zero dummies, so it's priced like city A.

> *On screen:* A pipeline box receives a house from an unseen city 'Z' and outputs all-zero dummies and the same price as city A.

In NB22's sklearn pipeline (ColumnTransformer + OneHotEncoder(drop='first', handle_unknown='ignore')), a category never seen in training gets all-zero dummies, so it's silently priced like the reference city: 349.9k for a 100 m² house, the same as city A. The pipeline scores test R² 0.9598. Be aware of this default: unknown categories are treated as the baseline, not flagged.

### Key takeaways  `[09:16]`

- Each slope: effect of x_j holding the others fixed
- MedInc +1 ($10k) → +$43.7k, ceteris paribus
- One-hot categories; never label-encode them
- Drop one dummy: all of them = intercept (rank 4 of 5)

---

## Chapter 8 — Multicollinearity

**Starts at 09:29** · length 01:15 · source `L08-multicollinearity` · hook: *"What happens when two predictors tell the same story?"*

**What you'll learn.** This chapter shows what happens when two predictors carry almost the same information: coefficients wobble, standard errors inflate, and interpretation breaks while predictions stay fine (NB09). It introduces the Variance Inflation Factor (VIF) and applies it to California Housing. Prerequisites: multiple regression and standard errors (Chapters 4 and 7). Correlated features are the norm in real data, so you need to know when a coefficient can be trusted.

### Two predictors, one story

**[09:36]** In the notebook, x2 = 0.97·x1 + a little noise. corr(x1, x2) = 0.976.

> *On screen:* A scatter of x2 against x1 shows the points lying almost on a straight line, with corr = 0.976 displayed.

NB09 builds x2 = 0.97·x1 plus a little noise (standard deviation 0.2) with seed 42 and n = 100. The two predictors have correlation 0.976, so knowing one tells you nearly everything about the other.

**[09:40]** The truth is y = 3·x1 + 2·x2 + noise. Can the model tell the two apart?

> *On screen:* The true model y = 3·x1 + 2·x2 + noise appears above the scatter.

Because the data are simulated, we know the right answer: b1 = 3 and b2 = 2. The question is whether OLS can split the credit correctly between two near-copies. Simulations like this are the only way to see estimation error directly, because with real data the truth is unknown.

### Alone vs together: the coefficients move

**[09:46]** Alone, each predictor soaks up the other's effect: about 5 instead of 3 or 2.

> *On screen:* Coefficient bars for x1 alone (5.111) and x2 alone (5.266) grow far past the true values of 3 and 2.

When only one predictor is in the model, it also picks up the effect of its missing twin: x1 alone gets 5.111 and x2 alone 5.266, roughly 3 + 2. This is omitted-variable bias (Chapter 13): the slope measures x1 plus everything correlated with it. Each single-predictor model still fits well (R² 0.9445 and 0.9322).

**[09:53]** Together the estimates land near the truth (3, 2)… but SE(b1) grows 4.4×: 0.125 → 0.551.

> *On screen:* With both predictors in the model, the bars shrink to 3.286 and 1.939 while their error bars grow from about ±0.125 to ±0.551.

Together, OLS lands close to the truth (3.286 and 1.939), but the standard error of b1 jumps from 0.125 to 0.551, about 4.4× larger. Both coefficients remain significant here (p = 4.09e-08 and 1.01e-03) because the signal is strong. With weaker effects or fewer rows, the same inflation can push p-values above 0.05 even though the variables matter.

**[09:58]** R² barely moves (0.9503). Predictions are fine; interpretation is what breaks.

> *On screen:* R² 0.9503 appears next to the single-predictor values 0.9445 and 0.9322.

Adding the second predictor barely changes R², because x2 adds little new information. Predictions for new data with the same correlation pattern are fine. What breaks is your ability to say how much each variable matters on its own.

### Why: the model can't decide who gets the credit

**[10:03]** The data pins down b1 + b2, not each one. The estimate slides along the valley.

> *On screen:* In a coefficient plane, a long, narrow valley lies along the b1 + b2 ≈ 5.2 line, and an estimate dot slides back and forth along it.

The data tightly pin down the sum b1 + b2 (≈ 3.286 + 1.939 = 5.2), but give very little information about how to split it, so many (b1, b2) pairs fit almost equally well. A new sample from the same process would land somewhere else along the valley. The wobble of the dot is illustrative, not real resampled estimates.

**[10:08]** Stronger correlation, wider valley of doubt: SE 0.12 → 0.18 → 0.45.

> *On screen:* A mini chart shows SE(b1) rising from 0.12 to 0.18 to 0.45 as the correlation increases from 0 to 0.7 to 0.97.

Standard-error inflation grows non-linearly with correlation: moderate correlation (r = 0.7) costs relatively little, but near-duplicates (r = 0.97) multiply the standard error several times. The variance of b_j scales with 1/(1 − R²_j), which explodes as R²_j → 1. These values come from NB09's SE-vs-correlation figure.

### Measure it: the Variance Inflation Factor

**[10:14]** Regress each predictor on the others. If they explain it well, its VIF explodes.

> *On screen:* A diagram regresses one predictor on all the others, producing R²_j and VIF = 1/(1 − R²_j); for the NB09 data, VIF = 21.47.

The VIF tells you how much a coefficient's variance is inflated by its correlation with the other predictors. If the others explain x_j with R²_j = 0.95, then VIF = 1/0.05 = 20. NB09's twin predictors both have VIF 21.47. Common rules: above 5 is moderate, above 10 is severe.

**[10:20]** California: nothing above 10, but rooms, bedrooms, latitude and longitude pass 5.

> *On screen:* Horizontal VIF bars for the 8 California predictors appear, with reference lines at 5 and 10.

California VIFs: Latitude 9.30, Longitude 8.96, AveRooms 8.34, AveBedrms 6.99, MedInc 2.50, HouseAge 1.24, Population 1.14, AveOccup 1.01. None exceed 10, but four are above 5: latitude and longitude move together along the coast, and rooms and bedrooms are closely linked. Read those four coefficients with extra caution.

**[10:25]** Fixes: drop or combine predictors, get more data, use Ridge, or use PCA first.

> *On screen:* A list of fixes appears: drop or combine, more data, Ridge, PCA.

If you need interpretable coefficients, drop one of the twins or combine them into a single feature (for example rooms per bedroom). More data shrinks all standard errors. Ridge (Chapter 10) stabilizes the estimates by shrinking them, and PCA replaces correlated predictors with uncorrelated components, at the cost of interpretability. If you only care about prediction, you may not need to fix anything.

### Key takeaways  `[10:32]`

- Correlated predictors share credit: estimates wobble
- SEs inflate (4.4× here); predictions stay fine
- VIF = 1/(1 − R²_j): > 5 moderate, > 10 severe
- Fix: drop/combine, more data, Ridge or PCA

---

## Chapter 9 — Polynomials, Interactions & CV

**Starts at 10:44** · length 01:24 · source `L09-polynomial-interactions-cv` · hook: *"How flexible should a 'linear' model be?"*

**What you'll learn.** This chapter shows how 'linear' regression fits curves (polynomial terms) and slopes that depend on another variable (interactions), and how cross-validation chooses the right flexibility. It uses NB10 (polynomial data with seed 0, n = 80; salary data with interactions) and NB14 (cross-validation and learning curves). Prerequisites: R² (Chapter 3) and multiple regression (Chapter 7). The bias–variance trade-off you see here drives every model-selection decision later on.

### Curves are still linear regression

**[10:51]** Degree 1: a straight line can't follow the bends. Underfit.

> *On screen:* The NB10 points appear (an S-shaped cubic cloud), and a straight degree-1 line is drawn through them.

The data come from y = 0.5x³ − x² + 2x + noise. A straight line can't follow the bends, so its errors are systematic: too high in some regions, too low in others. That's underfitting, or high bias: train R² 0.789, CV R² 0.714. The curves shown are fitted on all 80 points; the notebook's table uses a 75/25 split, so they look very similar but are not identical.

**[10:55]** Add x² as a new column. Still linear in the b's, so plain OLS fits it.

> *On screen:* A new column x² appears next to x in the design matrix, and the fitted curve bends.

Adding x² (and x³, …) creates new columns, but the model stays linear in the coefficients: y = b0 + b1·x + b2·x². So ordinary OLS fits it with the same normal equations. 'Linear' regression means linear in the parameters, not a straight line.

**[11:01]** Degree 3 matches the true shape.

> *On screen:* The curve morphs into the degree-3 fit, which follows the true S-shape closely.

Degree 3 matches the data-generating process, so it captures the signal without chasing noise: train R² 0.935, test R² 0.829. Usually you don't know the true degree, which is why the next steps compare degrees by cross-validation.

**[11:03]** Degree 10 bends to chase the noise, especially at the edges.

> *On screen:* The curve morphs into degree 10 and wiggles, especially near the left and right edges.

With 11 coefficients, the curve has enough freedom to follow random noise, and high-degree polynomials swing wildly at the edges of the data, where few points constrain them. Train R² goes up slightly (0.937), but test R² drops to 0.802. That is overfitting: high variance.

**[11:07]** Train R² keeps rising (0.937 at degree 10). CV R² peaks at degree 3: 0.891.

> *On screen:* Grouped bars of train, test and 5-fold CV R² appear for degrees 1, 2, 3 and 10, and the CV bar at degree 3 is circled (0.891).

Train R² can only go up as you add terms, so it can't choose the model. Shuffled 5-fold CV R² goes 0.714 → 0.845 → 0.891 → 0.872 and peaks at degree 3. Choose the degree with the best validation score, not the best training score.

**[11:12]** Underfit at degree 1, overfit at degree 10: that is the bias–variance trade-off.

> *On screen:* The bias–variance labels appear on the bar chart: underfit at degree 1, overfit at degree 10.

Expected test error = bias² + variance + irreducible noise. Simple models have high bias (they systematically miss the shape); flexible models have high variance (they change a lot from one sample to the next). The best model balances the two: here degree 3.

### K-fold cross-validation: every point gets tested once

**[11:18]** Split into 5 folds. Train on 4, test on the 5th, rotate, average the 5 scores.

> *On screen:* Five coloured fold blocks appear; one block at a time is marked 'test' while the other four train, and the test fold rotates.

K-fold cross-validation splits the data into K parts, trains on K − 1, tests on the remaining one, and repeats K times so every point is tested exactly once. The average of the K scores estimates out-of-sample performance more reliably than one train/test split, especially with small n.

**[11:24]** Trap: x is SORTED. Unshuffled folds are separate x-ranges, so CV tests extrapolation.

> *On screen:* The folds are shown over sorted x: each block covers a separate x-range, and a warning appears.

NB14's x values are sorted, so cross_val_score(cv=5) without shuffling made each fold a contiguous slice of x. Every test fold then lies outside the training range, so CV measured extrapolation and reported only 0.2813. This was a real bug in the original notebooks, now fixed.

**[11:30]** Shuffle, and every fold spans the whole x-range: 0.2813 → 0.7790. Same model.

> *On screen:* The points shuffle into mixed folds that each span the whole x-range, and the score jumps from 0.2813 to 0.7790.

With KFold(5, shuffle=True, random_state=0), every fold samples the whole x range, so the test points are within the region the model learned. The same degree-3 model now scores CV R² 0.7790. Shuffle whenever row order carries structure, except for time series, where you need time-ordered splits instead (Chapter 14).

### Learning curves: bias or variance?

**[11:36]** Score vs training size: low and close = too simple; a wide gap = too flexible.

> *On screen:* Two learning-curve sketches plot training and validation scores against training-set size: one pair low and close together, the other with a wide gap.

A learning curve shows how scores change as you add training data. If both curves are low and converge (high bias), more data won't help: you need a more flexible model. If there is a wide gap (high variance), more data or regularization will help. These curves are illustrative sketches; NB14 computes the real ones with learning_curve(shuffle=True).

### Interactions: the slope depends on another variable

**[11:43]** Without the interaction the lines must be parallel, and edu becomes 47.30 (truth 10).

> *On screen:* Salary-vs-experience lines for two education levels are drawn parallel, with edu = 47.30 displayed against the true 10.

Without an interaction term, the model forces the experience slope to be the same for both education groups, so the lines must be parallel. The true model has an interaction (3.5·exper·edu), so the misspecified model distorts other coefficients: edu becomes 47.30 instead of 10. It is absorbing the missing interaction (10.0028 + 3.5028 × 10.6478 = 47.30, the omitted-variable-bias formula in Chapter 13).

**[11:48]** Add exper × edu and the slopes differ: 1.96 vs 5.46 per year, matching the truth.

> *On screen:* An exper × edu column is added, and the two lines rotate to different slopes, 1.96 and 5.46.

With the interaction term, the experience slope depends on education: 1.9588 per year without a degree and 1.9588 + 3.5028 ≈ 5.46 with one, matching the true values 2 and 5.5. The edu coefficient returns to 10.0028. When the effect of one variable 'depends on' another, include their product as a feature.

### Key takeaways  `[11:55]`

- Polynomial terms are new columns: still OLS
- Train R² always rises; pick complexity by CV (degree 3 here)
- Shuffle folds when data is sorted: 0.2813 → 0.7790
- Interactions let one slope depend on another variable

---

## Chapter 10 — Ridge, Lasso & ElasticNet

**Starts at 12:09** · length 01:20 · source `L10-regularization` · hook: *"How do you stop a model from overfitting?"*

**What you'll learn.** This chapter shows how to control overfitting by penalizing large coefficients: Ridge (L2) shrinks every coefficient, Lasso (L1) can set some to exactly zero, and ElasticNet mixes the two (NB11, NB12, NB13). It explains geometrically why Lasso produces zeros, and why you must standardize first. Prerequisites: overfitting and cross-validation (Chapter 9) and multicollinearity (Chapter 8). Regularization is the default tool when you have many or correlated features.

### Ridge: make big coefficients pay

**[12:15]** Ridge adds a price on large coefficients. λ = 0 is plain OLS.

> *On screen:* The Ridge objective SSR + λ·Σb² appears, and the λ term is highlighted.

Ridge adds a penalty proportional to the sum of squared coefficients, so the fit must trade off a lower SSR against smaller coefficients. The closed form is b = (XᵀX + λI)⁻¹Xᵀy on centred data. The intercept is not penalized, and λ = 0 gives back plain OLS. Adding λI also makes XᵀX invertible even under perfect collinearity.

**[12:18]** A little λ helps a lot: test R² 0.552 → 0.777. Too much λ (1) and it underfits: 0.012.

> *On screen:* A table of test R² for the NB11 toy model fills in: 0.552 for OLS, 0.777 at λ = 1e-4, 0.666 at λ = 0.01, and 0.012 at λ = 1.

NB11 fits a degree-12 polynomial to 25 training points of a sine curve, a model built to overfit. Plain OLS reaches train R² 0.951 but test R² only 0.552. A tiny penalty (λ = 1e-4) lifts test R² to 0.777, and too much (λ = 1) flattens the model into underfitting (0.012). λ is a bias–variance dial, chosen by cross-validation.

### Ridge path: every coefficient shrinks, none hits zero

**[12:25]** California housing, 8 standardised features. Slide λ up: all 8 lines bend toward 0.

> *On screen:* A Ridge coefficient path for 8 standardized California features: as λ slides from 1e-3 to 1e5, all 8 lines bend toward zero.

Each line is one coefficient as a function of λ (log scale). Small λ leaves them near the OLS values; large λ pulls them all toward 0 together. RidgeCV chose λ = 38.2749 on all the data, and a properly held-out evaluation gives test R² 0.5941. The path is computed with sklearn on standardized California data.

**[12:29]** Even at λ = 100,000 they are small but not zero. Ridge shrinks; it never deletes.

> *On screen:* The path reaches λ = 100,000 and every line is close to, but not exactly, zero.

The L2 penalty's gradient (2λb) gets weaker as b approaches 0, so Ridge never pushes a coefficient all the way to zero. Ridge keeps every feature and spreads the weight among correlated ones. If you need a smaller set of features, you need L1.

### Why Lasso makes exact zeros: corners

**[12:36]** Ridge's circle is smooth, so the first contact is usually off-axis: both b's non-zero.

> *On screen:* A circular L2 constraint region meets an elliptical SSR contour at an off-axis point, labelled (0.979, 0.202).

Ridge's problem is equivalent to minimizing SSR inside a circle b1² + b2² ≤ t. The SSR contours (ellipses around the OLS solution) usually first touch a smooth circle at a point where both coefficients are non-zero. NB12 computes the contact point for its toy loss: (0.979, 0.202). The contours are schematic; the contact points are computed.

**[12:40]** Lasso's diamond has corners on the axes. Contact at a corner means b2 = 0 exactly.

> *On screen:* A diamond-shaped L1 region appears, and the contour touches it at the corner (1.000, 0.000) on the axis.

Lasso constrains |b1| + |b2| ≤ t, a diamond with sharp corners on the axes. Expanding ellipses are much more likely to hit a corner first, and a corner means one coefficient is exactly zero: NB12's computed solution is (1.000, 0.000). The L1 penalty's pull doesn't fade near zero, so coefficients can stop exactly at zero.

### Lasso path: coefficients snap to exactly 0

**[12:47]** Same 8 features. As α grows, coefficients hit 0 one by one and stay there.

> *On screen:* A Lasso coefficient path for the same 8 features: as α grows, lines drop to zero one by one, with a counter showing how many are still non-zero.

As α increases from 0.001 to 1, the number of non-zero coefficients goes 8 → 8 → 7 → 6 → 3 → 1 → 0. These counts come from an sklearn lasso_path run on standardized California data, not from the notebook output. Weak or redundant predictors leave first. Once a coefficient hits zero, it usually stays there.

**[12:56]** That is automatic feature selection. But LassoCV picked α = 0.0026 here, keeping 8 of 8.

> *On screen:* A marker at α = 0.0026 shows LassoCV's choice, with all 8 coefficients still non-zero.

LassoCV picked α = 0.002600 for California, small enough that all 8 features stay in the model. With 20,640 rows and only 8 features, every predictor carries some signal, so dropping one would hurt the CV score. Lasso is a feature-selection tool, but it only removes features when the data say they are worth removing.

### ElasticNet: a dial between Ridge and Lasso

**[13:02]** One dial mixes the two penalties. Useful when correlated features come in groups.

> *On screen:* The ElasticNet objective appears with an l1_ratio dial between Ridge and Lasso.

ElasticNet's penalty is α·[l1_ratio·Σ|b| + (1 − l1_ratio)·Σb²/2]: l1_ratio = 0 is Ridge, 1 is Lasso. The mix helps when correlated features come in groups: pure Lasso tends to pick one feature from a group at random, while the L2 part keeps the group together. sklearn also scales the SSR by 1/(2n), so α values are not comparable between Ridge and Lasso/ElasticNet.

**[13:07]** ElasticNetCV chose l1_ratio = 1.0 (pure Lasso), α = 0.475979, 13 of 20 non-zero.

> *On screen:* A results table shows Ridge, Lasso and ElasticNet non-zero counts and CV R², then ElasticNetCV's choice: l1_ratio 1.0, α = 0.475979, 13 of 20 non-zero.

NB13's data come from make_regression with 20 independent features, 5 of them informative. Ridge keeps 20/20 (CV R² 0.994), Lasso(0.1) 17/20 (0.995), ElasticNet(0.1, 0.5) 18/20 (0.992). ElasticNetCV chose l1_ratio = 1.0, pure Lasso, because these features are independent, so there are no correlated groups that need the L2 part.

**[13:11]** And always standardise first: the penalty compares coefficients across features.

> *On screen:* A warning card appears: standardize before penalizing.

The penalty adds up coefficients across features, but a coefficient's size depends on its feature's units: income in dollars vs in thousands would get very different penalties. StandardScaler puts every feature on the same scale, so the penalty treats them fairly; NB21 shows Ridge giving the same answer for income in any units after scaling. Do the scaling inside a pipeline, fitted on training data only (Chapter 14).

### Key takeaways  `[13:16]`

- Ridge (L2) shrinks every coefficient, none to zero
- Lasso (L1) corners give exact zeros: feature selection
- ElasticNet mixes both; pick α and l1_ratio by CV
- Standardise first; sklearn α scales differ by model

---

## Chapter 11 — Gradient Descent & Feature Scaling

**Starts at 13:29** · length 01:18 · source `L11-gradient-descent-scaling` · hook: *"Why did gradient descent refuse to converge?"*

**What you'll learn.** This chapter covers gradient descent (GD), the iterative alternative to the closed-form OLS solution, and why feature scaling decides whether it works. It draws on NB15 (corrected) and NB21. It builds on Chapter 2 (the SSR bowl and normal equations) and Chapter 10 (Ridge/Lasso). It matters because GD is how linear models are fitted on data too large for one matrix solve. It is also the algorithm behind every neural network, so a GD that never converges usually means an unscaled feature.

### Walk downhill on the error bowl

**[13:35]** Gradient descent: measure the slope, take a step downhill, repeat.

> *On screen:* A ball sits on the error bowl and takes repeated steps downhill, each step pointing against the local slope.

Each GD step applies b ← b − lr·∇SSR(b): it computes the gradient of the loss, which points uphill, and moves a small distance the other way. The learning rate lr sets the step length. Too small and it crawls; too big and it overshoots the bottom. For linear regression the bowl has a single minimum, so a well-tuned GD reaches exactly the OLS answer.

**[13:38]** OLS can be solved exactly in one step. GD is the iterative route that scales to huge data.

> *On screen:* A note contrasts the one-step normal-equation solve with GD's many small steps.

OLS has a closed form, b = (XᵀX)⁻¹Xᵀy, so why iterate? The matrix solve costs roughly O(n·p² + p³) and needs all the data in memory. GD only needs gradients, which can be computed on chunks of data. With millions of rows or features, the iterative route is the practical one.

### Salary data, raw x = 1…10: three learning rates

**[13:46]** Same data, same 6,000 epochs, three step sizes. Watch b0 travel toward 32.

> *On screen:* Three lanes start GD on the NB03 salary data (raw x = 1…10) with learning rates 0.001, 0.003 and 0.03, and b0 begins moving toward 32.

The target is the OLS answer from Chapter 2: b0 = 32.0, b1 = 6.3636. All three runs use the same data and the same 6,000 epochs (full passes over the data). Only the step size differs, so any difference in the result comes from the learning rate alone.

**[13:49]** 0.001 crawls, 0.003 lands on OLS, 0.03 blows up. (NB15 had the labels backwards.)

> *On screen:* The 0.001 lane stalls at b0 ≈ 29.55, the 0.003 lane lands on 32 (31.9842), and the 0.03 lane shoots off to infinity.

After 6,000 epochs, lr = 0.001 has only reached b0 = 29.55, b1 = 6.7156 (SSR 31.95 vs the optimal 19.09): not converged. lr = 0.003 reaches 31.9842 / 6.3659, essentially OLS. lr = 0.03 diverges. The original NB15 labelled 0.001 "good" and 0.003 "diverges", which was backwards; the corrected notebook now prints `Close? True` for 0.003.

### Why: raw x makes a long, narrow valley

**[13:56]** Raw x: one direction is steep, the other almost flat. The step size is set by the steep one.

> *On screen:* Elongated elliptical contours appear and a GD path zig-zags across the narrow valley while creeping slowly along it (illustrative contours).

With raw x, the Hessian of the loss has eigenvalues 0.42 and 78.58. Its condition number κ = 78.58/0.42 ≈ 187 means the bowl is 187 times steeper in one direction than the other. GD is only stable when lr < 2/λmax = 0.02545, so the steep direction caps the step size. In the flat direction, steps that small make almost no progress, which is why lr = 0.001 crawls.

**[14:03]** Standardise x (mean 0, sd 1) and the valley becomes a round bowl: κ drops from 187 to 1.

> *On screen:* The contours morph into concentric circles and the path heads straight to the centre, with κ shrinking from 187 to 1.

Standardising (subtracting the mean and dividing by the standard deviation) centres x, which removes the strong correlation between the intercept and slope directions. The result is a round bowl with κ = 1.0. Every direction now has the same curvature, so one learning rate suits them all and the gradient points straight at the minimum.

### Payoff: 22× fewer epochs

**[14:10]** To reach the OLS answer: 1,095 epochs on raw x versus 49 after standardising.

> *On screen:* Two epoch bars appear: 1,095 for raw x and 49 for standardised x.

In NB21, reaching the OLS solution takes 1,095 epochs on raw x but only 49 after standardising: about 22× fewer. This holds for any gradient-based optimiser, including SGD and Adam. Scaling inputs is the cheapest speed-up in machine learning.

**[14:14]** Fit on the scaled x, then convert back to original units. Same line, far less work.

> *On screen:* The scaled-x coefficients are converted back into original units, recovering the same line as OLS.

If z = (x − mean)/sd, a model ŷ = a0 + a1·z converts back as b1 = a1/sd and b0 = a0 − a1·mean/sd. NB21's back-transformed GD result matches OLS (b0 ≈ 32.0, b1 ≈ 6.36). Scaling changes the optimisation path, not the fitted line: predictions are identical.

### Batch, stochastic, mini-batch

**[14:20]** All three land within about 0.06 of OLS. Mini-batch is the deep-learning workhorse.

> *On screen:* Three paths, batch, stochastic and mini-batch, descend to nearly the same point, with update counts 50, 5,000 and 314.

Batch GD uses all rows for each step. Stochastic GD (SGD) uses one row at a time: noisy but cheap steps. Mini-batch uses small groups, here 32 rows. On NB21's 5,000-row example (true y = 4 + 3x), SGD after one epoch gives b0 = 4.0387, b1 = 3.0012. Mini-batch after 314 updates gives 3.9757 / 2.9426. All land close to OLS, and mini-batch is the default in deep learning because it balances noise against hardware efficiency.

### Scaling also changes Ridge and Lasso

**[14:26]** Change income's units and an unscaled Ridge gives a different answer.

> *On screen:* Income's units switch from thousands of dollars to dollars, and the unscaled Ridge coefficients change.

Ridge penalises λ·Σb². A coefficient's size depends on its feature's units: measuring income in dollars instead of $1000s shrinks its coefficient 1000×, which makes it almost free from the penalty. In NB21, Ridge with α = 5000 and no scaling gives [1.7562, 1.1853] with income in $1000s, but [0.00194, 1.177679] (1.9402 per $1000) with income in dollars. Same data, different model.

**[14:29]** Standardise first and the penalty no longer depends on units.

> *On screen:* A StandardScaler box slides in front of Ridge and both unit choices produce identical coefficients [1.1671, 0.5979].

After standardising, every feature is in standard-deviation units, so the penalty treats them all equally whatever the original units. NB21 gets [1.1671, 0.5979] for both unit choices. The rule: always scale before Ridge, Lasso, ElasticNet or GD. Put the scaler inside a Pipeline (Chapter 14) so it is learned from training data only.

### Key takeaways  `[14:34]`

- GD steps downhill: b ← b − lr·gradient
- Raw x: κ = 187, lr must stay < 0.0255, progress is slow
- Standardise: κ = 1, 1,095 → 49 epochs
- Mini-batch scales; scaling also fixes penalty units

---

## Chapter 12 — Beyond plain OLS

**Starts at 14:48** · length 01:34 · source `L12-beyond-ols` · hook: *"Outliers, fanning noise, and uncertainty: when least squares needs help"*

**What you'll learn.** This chapter covers four situations where plain least squares needs help: outliers (robust regression, NB16), changing spread (quantile regression, NB17), quantifying uncertainty (Bayesian regression, NB18) and uneven noise (heteroscedasticity fixes, NB25). It builds on the assumptions in Chapter 5 and the diagnostics in Chapter 6. Each section names the symptom, the tool and the evidence from the notebook.

### Outliers drag OLS (NB16)

**[14:55]** 60 clean points from y = 2x + 3 + noise. OLS nails the slope.

> *On screen:* Sixty blue points appear along a rising trend and an OLS line fits through them.

NB16 starts from clean data generated as y = 2x + 3 + noise (seed 42, n = 60). With well-behaved errors, OLS recovers the slope close to the true 2.0. This is the baseline before the trouble starts.

**[15:00]** Add 8 gross outliers (11.8% of the data)...

> *On screen:* Eight crosses appear far above and below the trend.

Eight gross outliers are added, 11.8% of the 68 points. They are placed away from the trend on purpose. Real data sets get such points from typos, sensor faults or mixed populations.

**[15:03]** ...and OLS gets dragged: squaring makes big residuals dominate.

> *On screen:* The red OLS line tilts away from the clean points, toward the outliers, and its slope drops to 1.1593.

OLS minimises squared residuals, so a point 10 units off counts 100 times more than a point 1 unit off. A few extreme points therefore dominate the fit. Here the slope collapses from about 2 to 1.1593. One bad point can move OLS arbitrarily far, which is why OLS is said to have zero breakdown point.

**[15:06]** Robust fits down-weight or ignore outliers and stay near the true slope 2.0.

> *On screen:* Huber, RANSAC and Theil–Sen lines appear close to the clean trend, with slopes 1.9144, 1.9937 and 1.8447 listed against the true 2.0.

Huber loss (ε = 1.35) is quadratic for small residuals and linear for large ones, so outliers count less. RANSAC repeatedly fits random subsets and keeps the fit with the most inliers, ignoring the rest. Theil–Sen takes the median of pairwise slopes. All three stay near 2.0 while OLS fell to 1.16. Robustness to points far out in x (leverage) varies by method, so still look at Chapter 6's diagnostics.

### Quantile regression: model the spread (NB17)

**[15:14]** Noise grows with x: y = 2x + 5 + N(0, 0.5x + 0.5).

> *On screen:* A scatter fans out to the right: points spread more as x grows.

NB17's data are y = 2x + 5 + N(0, 0.5x + 0.5) (seed 0, n = 200): the noise standard deviation grows with x. OLS still estimates the mean line correctly, but a single line hides the fact that uncertainty is much larger at high x.

**[15:20]** Fit the 10th, 50th and 90th percentiles instead of the mean: the lines fan out, like the data.

> *On screen:* Three lines for the 10th, 50th and 90th percentiles fan out with the data.

Quantile regression minimises an asymmetric absolute loss (the pinball loss) and estimates a conditional percentile instead of the mean. NB17 gets Q0.1 = 4.254 + 1.360x, Q0.5 = 5.260 + 1.817x and Q0.9 = 5.564 + 2.543x. In theory the slopes are 2 + 0.5·z_τ, which gives 1.36 / 2.00 / 2.64. Use it for prediction ranges, risk ("the slow 10%") and skewed outcomes. It needs no normality assumption.

### Bayesian: a distribution, not one number (NB18)

**[15:29]** With 3 points, the posterior for the slope is wide: we are unsure.

> *On screen:* A wide bell-shaped posterior for the slope appears above three data points.

Bayesian regression treats the coefficients as uncertain quantities with a prior, here N(0, 10I). The data update the prior into a posterior distribution. With only 3 points the posterior for b1 has sd 0.675: many slopes are still plausible. Instead of one number, you get a full description of what you know.

**[15:34]** Now add data: n = 10, then n = 40.

> *On screen:* More points arrive (n = 10, then n = 40) and the bell curve tightens each time.

Each new observation multiplies in more likelihood, so the posterior concentrates. Unlike a point estimate, the width tells you directly how much the data have taught you.

**[15:37]** More data, narrower posterior: sd 0.675 -> 0.396 -> 0.214 at n = 40.

> *On screen:* The posterior sd counter steps down 0.675 → 0.396 → 0.214 as the curve narrows around the true slope 2.

The posterior mean moves 2.03 → 2.47 → 2.07 and the sd shrinks 0.675 → 0.396 → 0.214. That is roughly 1/√n behaviour, the same rate as a classical standard error. With lots of data, the prior matters little and the Bayesian and OLS answers converge.

**[15:41]** Its most likely value (MAP) is exactly Ridge: NB18 prints Match: True.

> *On screen:* The MAP estimate and the Ridge coefficients appear side by side with "Match: True".

With a Gaussian prior N(0, τ²) and Gaussian noise σ², the posterior mode (MAP) is exactly Ridge with λ = σ²/τ². A tight prior (small τ²) is a strong penalty. NB18's demo prints identical coefficients [2.26981, −0.74375, 0.22371] for both. Regularisation is a prior belief that coefficients are small.

### Uneven noise: detect it, then fix it (NB25)

**[15:49]** The spread grows with x. Coefficients stay unbiased: 3.0411 + 1.9976x.

> *On screen:* A scatter whose spread widens with x appears, with a fitted line 3.0411 + 1.9976x (funnel outline is a sketch).

In NB25 the noise grows with x (heteroscedasticity). The OLS coefficients remain unbiased: the fitted line 3.0411 + 1.9976x is close to the truth. What breaks is the classic standard-error formula, which assumes one constant σ² for every point.

**[15:53]** Breusch-Pagan confirms it. The problem is the classic standard errors.

> *On screen:* A red box shows Breusch–Pagan LM = 23.21, p = 1.45e-06.

The Breusch–Pagan test regresses the squared residuals on x. If they rise with x, the variance is not constant. LM = 23.21 with p = 1.45e-06 rejects constant variance decisively (White's test agrees: p = 7.45e-06). Classic SEs, t-tests and CIs from Chapter 4 can't be trusted here.

**[15:58]** Fix 1: robust HC3 standard errors. Same coefficients; CIs now hit 95% (93.4% before).

> *On screen:* Coverage bars grow: classic SEs reach 93.4%, HC3 robust SEs reach 95.3%, against a dashed 95% target (axis starts at 90%).

HC3 "sandwich" standard errors estimate the variance from each point's own squared residual, so they need no constant-variance assumption. The coefficients don't change; only the SEs, p-values and CIs do. In NB25's one sample the HC3 slope SE was actually slightly smaller (0.0751 vs 0.0795): one sample can go either way. The evidence is the simulation: over 2,000 samples, classic 95% CIs covered the true slope only 93.4% of the time and HC3 CIs covered it 95.3%. In statsmodels: `fit(cov_type='HC3')`.

**[16:03]** Fix 2: weighted least squares. Same center, slope variance 2.64x smaller.

> *On screen:* Two bell curves of slope estimates appear, wider for OLS and narrower for WLS (normal shape assumed for the drawing).

Weighted least squares gives each point weight 1/σᵢ², trusting precise points more. That is the efficient (BLUE) estimator under heteroscedasticity, as Chapter 5's Gauss–Markov discussion says. Across NB25's simulated samples the slope SD falls from 0.0833 (OLS) to 0.0513 (WLS): 2.64× less variance. In practice σᵢ is unknown and must be estimated from a model of the residuals. For autocorrelated errors, the analogue is Newey–West (HAC) SEs, which NB25 shows are 1.90× larger than classic SEs.

### Key takeaways  `[16:09]`

- Outliers: robust fits stay near 2.0; OLS fell to 1.16
- Quantile regression models the spread, not just the mean
- Bayesian: posterior narrows with n; MAP = Ridge
- Uneven noise: HC3 for honest SEs, WLS for precision

---

## Chapter 13 — Transform, select, beware

**Starts at 16:23** · length 01:37 · source `L13-transforms-selection-pitfalls` · hook: *"When to log y, which model to keep, and the traps that fool regressions"*

**What you'll learn.** This chapter covers three practical skills: transforming a skewed target and interpreting the result (NB26), choosing between models with sound metrics (NB27), and recognising the classic traps of omitted variables, extrapolation and confounding (NB27). It builds on the diagnostics (Chapter 6), inference (Chapter 4) and interactions (Chapter 9). These are the mistakes that make a well-fitted regression give the wrong business answer.

### Skewed target? Model log(y) (NB26)

**[16:28]** price = exp(...) is right-skewed: residuals lean right and the spread fans out.

> *On screen:* A right-skewed residual histogram and a fanning residual plot appear for the price model.

NB26 generates prices as exp(linear predictor + noise), as with many money, count and size variables. A linear model on raw price leaves residuals that are right-skewed (skew 1.130) with spread growing with the fitted value (Breusch–Pagan p = 7.11e-07). That violates the N and E in LINE.

**[16:33]** Fit log(price) instead: symmetric residuals, normality and constant variance restored.

> *On screen:* The histogram becomes symmetric after fitting log(price), and the funnel flattens.

Modelling log(price) turns multiplicative effects into additive ones. The residual skew goes from 1.130 to −0.016 and Breusch–Pagan p rises to 0.345: no evidence of unequal variance. Box–Cox confirms the choice: its estimated λ = 0.0080 (95% CI [−0.174, 0.190]) includes 0, and λ = 0 is the log transform.

### Reading coefficients after a log

**[16:38]** Log coefficients are percentages; for big b use 100(e^b - 1), not b x 100.

> *On screen:* Coefficient-reading rules appear: log-level as a percentage, 100(e^b − 1), and log-log as an elasticity.

In a log-level model (log y on x), a one-unit change in x multiplies y by e^b, a change of 100(e^b − 1)%. For small b this is about 100·b: NB26 gets b = 0.00768 per m², so +0.771% per m². For larger b the shortcut fails: a dummy coefficient of 0.15 means +16.18%, not +15%. In a log-log model b is an elasticity: NB26 estimates −1.4938 (true −1.5), meaning +1% in x gives about −1.49% in y.

### Back to dollars: the smearing correction

**[16:44]** exp() of a predicted log is the median, not the mean: 6.8% too low on 100,000 houses.

> *On screen:* A bar shows plain exp(prediction) undershooting the true mean price by 6.8%.

The mean of log y is not the log of the mean, because exp() is convex (Jensen's inequality). exp(predicted log price) estimates the median price, which sits below the mean for right-skewed data. On 100,000 fresh houses, plain back-transformation came out 6.8% too low on average, a systematic bias in every forecast.

**[16:49]** Duan's smearing factor (mean of exp(residuals)) fixes it: -0.9%.

> *On screen:* A smearing factor of 1.0634 multiplies the predictions and the error bar shrinks to −0.9%.

Duan's smearing estimator multiplies exp(prediction) by the mean of exp(residuals) from the training fit, here 1.0634. It assumes nothing about the residual distribution. The bias falls from −6.8% to −0.9%. Use it whenever you need predicted means, such as total revenue, rather than typical values.

### RMSE punishes big misses, MAE doesn't (NB27)

**[16:54]** 100 errors of size 1: RMSE = MAE = 1.00.

> *On screen:* One hundred error bars of size 1 appear with RMSE = MAE = 1.00.

MAE is the average absolute error and RMSE the square root of the average squared error. When all errors are the same size they are equal: here both are 1.00.

**[16:55]** Make 5 of them size 10: RMSE jumps to 2.44, MAE only to 1.45.

> *On screen:* Five of the bars stretch to size 10, RMSE jumps to 2.44 and MAE only to 1.45.

Squaring makes RMSE sensitive to large misses, while MAE grows only in proportion. Choose RMSE when big errors are disproportionately costly, and MAE when every unit of error costs the same or outliers are noise. On California housing NB27 reports RMSE 0.7273 (about $73k) vs MAE 0.5351 (about $54k): a gap like that signals some large misses.

### AIC vs BIC: lower is better

**[17:04]** AIC picks all 5 (631.64); BIC's stronger penalty picks the true 3 (645.43).

> *On screen:* AIC and BIC bars appear for candidate models, AIC lowest at 5 variables (631.64), BIC lowest at the true 3 (645.43).

Both criteria trade fit against complexity: AIC = 2k − 2·logL and BIC = k·ln(n) − 2·logL, lower is better. BIC's penalty grows with n, so it prefers smaller models. Here it picks the true x1+x2+x3, while AIC keeps two extra variables. A nested F-test asks the same question directly: adding x4 and x5 gives F = 2.8121, p = 0.0634, which is not significant at 5%.

**[17:08]** Selected-then-tested p-values are too optimistic: validate on held-out data.

> *On screen:* A warning card appears over the stepwise results: the selected noise variable x4 is flagged.

Forward stepwise selection picks variables by repeatedly adding the one that most improves AIC. Then it reports p-values as if the model had been chosen in advance. That double-dipping inflates significance: in NB27 stepwise kept the noise variable x4, and on pure noise 2 of 6 selected variables came out "significant". Validate selections on held-out data or with cross-validation (Chapter 9).

### Omitted-variable bias

**[17:14]** Ability raises both education and wages. Leave it out...

> *On screen:* A causal diagram appears: ability points to both education and wage.

Omitted-variable bias happens when a left-out variable affects y and is also correlated with an included x. In NB27, ability raises both years of education and wages (true education effect 1.0 per year, ability effect 3.0).

**[17:16]** ...and education takes its credit: 2.2885 instead of the true 1.0.

> *On screen:* The ability node fades out and the education coefficient grows from 1.1255 to 2.2885.

Without ability in the model, education absorbs part of ability's effect. The bias formula is exact here: short coefficient = long coefficient + β_omitted·δ, where δ is the slope of ability on education. Numerically 1.1255 + 2.8749 × 0.4045 = 2.2885: more than double the true effect. Adding variables changes coefficients whenever predictors are correlated.

**[17:20]** Same algebra explains NB10: edu came out 47.30 when its true effect was 10.

> *On screen:* The same formula is applied to NB10's interaction model: 10.0028 + 3.5028 × 10.6478 = 47.3001.

In NB10 the model without the experience×education interaction reported an education effect of 47.30, while the true main effect is 10. The missing term behaves like an omitted variable: the identity 10.0028 + 3.5028 × 10.6478 = 47.3001 reproduces the misleading coefficient exactly. Misspecification and omitted variables are the same problem.

### Don't extrapolate

**[17:28]** On x in [0, 5] a straight line fits well: R2 = 0.8978.

> *On screen:* A straight line fits curved data well on x in [0, 5], with R² = 0.8978.

On a narrow range, many curves look straight, and a high R² inside the data range says nothing about the shape beyond it. NB27's true relationship bends, but the linear fit on [0, 5] reaches R² = 0.8978.

**[17:32]** At x = 15 it predicts 27.31; the truth is 9.99. Outside the data, all bets are off.

> *On screen:* The line is extended to x = 15, predicting 27.31 while the true curve gives 9.99.

Extrapolating assumes the fitted relationship holds where you have no data. Here the prediction is almost 3× the truth. Prediction intervals (Chapter 4) also widen beyond the data, but only under the model's own assumptions, so they can't warn you that the shape is wrong. Report the range of x the model was fitted on.

### Correlation is not causation

**[17:40]** Regress drownings on ice cream: hugely 'significant'.

> *On screen:* Drownings are regressed on ice-cream sales and a highly significant slope appears (p = 4.51e-54).

Ice-cream sales and drownings both rise in hot weather. A regression of one on the other finds a strong, "significant" association (slope 0.0310, p = 4.51e-54), but neither causes the other. A tiny p-value measures how surely an association exists, not why it exists.

**[17:43]** Add the confounder and the effect vanishes. Regression measures association.

> *On screen:* Temperature joins the model and the ice-cream slope collapses to −0.0023 with p = 0.6534.

Adjusting for the confounder (temperature) removes the spurious effect: the ice-cream slope becomes −0.0023 (p = 0.6534), while temperature carries the real effect (0.1083, true 0.10). Regression coefficients are causal only if every confounder is included and none of the controls is itself caused by the treatment. That needs domain knowledge or experiments, not a better R².

### Key takeaways  `[17:48]`

- Skewed y: log it; read b as 100(e^b - 1)%
- Back-transform with smearing, not plain exp()
- RMSE vs MAE, AIC vs BIC, F-test: then validate
- Omitted variables, extrapolation, confounders mislead

---

## Chapter 14 — Time series & production pipelines

**Starts at 18:00** · length 01:26 · source `L14-time-series-pipelines` · hook: *"Forecast with a regression, then ship it without leaking the test set"*

**What you'll learn.** This chapter shows linear regression in two real-world settings: forecasting a time series with engineered time features (NB19), and packaging a model so it can be trained, tuned and shipped without leakage (NB20). It builds on cross-validation (Chapter 9), scaling (Chapter 11) and diagnostics (Chapter 6). The common theme is honest evaluation: the test data must never influence training.

### Time itself becomes a feature (NB19)

**[18:07]** Ten years of monthly data: an upward trend plus a yearly cycle.

> *On screen:* A ten-year monthly series draws itself, rising with a regular yearly wave.

NB19 simulates 120 months with y = 10 + 0.3t + 5·sin(2πt/12) + noise (seed 0, noise sd 1.5): a trend plus a 12-month season. The trend line drawn on screen is the true generating trend, not a fitted one. Linear regression can model both components, as long as we build the right columns.

**[18:11]** Build columns from time: t for the trend, Fourier terms for the season, past values as lags.

> *On screen:* Feature columns build up next to the series: t, sin/cos Fourier terms, and lagged values.

Linear regression is linear in the coefficients, not in time, so any function of t can be a feature. A t column captures the trend. sin(2πkt/12) and cos(2πkt/12) pairs (Fourier terms) capture the yearly cycle with a few parameters. Lags y(t−1), y(t−2)… let the model use recent values. Lags must only look backward, or you are using the future to predict the present.

### Autocorrelation: detrend before you look

**[18:19]** On the raw series every lag looks huge (0.97, 0.75, 0.98): the trend swamps it.

> *On screen:* ACF bars at lags 1, 6 and 12 all stand tall on the raw series (0.97, 0.75, 0.98).

The autocorrelation function (ACF) measures how correlated the series is with itself k steps earlier. On a trending series, every lag looks highly correlated simply because both values sit on the same rising trend. The trend swamps any other structure, so reading seasonality off the raw ACF is misleading.

**[18:24]** Detrend first: the yearly cycle appears, negative at 6 months, positive at 12.

> *On screen:* After detrending, the bars become 0.74, −0.82 and 0.86: negative at 6 months, positive at 12.

Removing the trend first reveals the true dependence: lag 6 is strongly negative (half a cycle apart, opposite phase) and lag 12 strongly positive (a full cycle). That is the signature of a yearly season. After fitting, also check the residual ACF. In NB19 the largest residual autocorrelation is 0.233 against a ±0.200 band, with 1 of 12 lags outside, about what chance alone produces.

### Never shuffle: hold out the future

**[18:30]** Train on the first 96 months, test on the last 24, never a random shuffle.

> *On screen:* A wall splits the timeline: the first 96 months are training, the last 24 the test set.

Random K-fold would shuffle the months, so the model would be trained on the future and tested on the past. That inflates scores and is impossible in real forecasting. A time-ordered holdout, or a rolling-origin CV such as sklearn's TimeSeriesSplit, always trains on the past and evaluates on later data, exactly as the model will be used.

**[18:36]** In-sample R2 of 0.97 drops to about 0.77-0.80 on unseen months: that is the honest number.

> *On screen:* In-sample R² bars of about 0.97 shrink to 0.7701 and 0.7950 on the held-out future months.

In-sample, trend + Fourier reaches R² 0.9710 and adding lags 1–3 gives 0.9706. On the last 24 unseen months, R² falls to 0.7701 and 0.7950. The holdout numbers are the honest estimate of forecast quality, and the in-sample figure overstates it badly. Here the lags help slightly out of sample, even though they add nothing in sample.

### Pipelines keep preprocessing honest (NB20)

**[18:46]** Every step learns its numbers (medians, means, scales) from the training rows only.

> *On screen:* A pipeline of boxes appears, imputer → scaler → model, each learning its parameters from the training rows only.

Preprocessing steps have parameters too: the imputer learns medians, the scaler learns means and SDs. In an sklearn Pipeline, `fit` learns every step's parameters on the training data, and `predict` applies the same frozen parameters to new data. During cross-validation, each fold refits the whole pipeline, so nothing from the validation fold leaks in.

**[18:52]** Fitting them on all the data lets test information leak into training.

> *On screen:* A red leakage arrow crosses the train/test wall when preprocessing is fitted on all the data.

Fitting the imputer or scaler before splitting lets statistics computed from test rows shape the training data: data leakage. Results then look better than they will be in production. NB20 injects 3% missing values into California housing (3,846 in train, 979 in test) to show the setup.

**[18:56]** Small for scaling, huge for feature selection: noise looked like R2 0.363.

> *On screen:* Two CV bars compare feature selection before CV (R² 0.363) and inside a pipeline (R² −0.285) on pure noise.

For simple steps the leak is small: preprocessing before the split gave test R² 0.5349 vs 0.5350 with the pipeline. For feature selection it is huge. With 2,000 pure-noise features and a noise target, selecting features on all data before CV produced a fake CV R² of 0.363. Done correctly inside the pipeline, CV R² was −0.285, the truthful "no signal". Any step that looks at y must live inside the pipeline.

### Tune with GridSearchCV, then save the whole pipeline

**[19:03]** The grid is flat until alpha ~ 85, then falls: best alpha 37.28, test R2 0.5347.

> *On screen:* A GridSearchCV curve stays flat up to α ≈ 85 then falls, with the best α = 37.2759 marked (curve shape between grid points is sketched).

GridSearchCV refits the full pipeline for every hyperparameter value and fold, then picks the best CV score. Here Ridge's CV R² is 0.5576–0.5577 for every α up to about 85, then drops to 0.5461 at α = 1000. The chosen α = 37.2759 is one point on a plateau, not a sharp optimum. The untouched test set gives R² 0.5347, consistent with CV.

**[19:08]** Save the fitted pipeline as one file: imputer, scaler and model travel together.

> *On screen:* The whole fitted pipeline collapses into a single best_pipeline.pkl file.

Saving the pipeline with joblib stores the imputer's medians, the scaler's statistics and the model coefficients together, so production applies exactly the training-time transformations. NB20 reloads it and gets test RMSE 0.7789 (about $78k) and a prediction of $201k for the median house. The corrected NB20 saves next to the notebook (`best_pipeline.pkl`) instead of a hard-coded Windows path. Version the file along with the library versions it was built with.

### Key takeaways  `[19:14]`

- Time series: t, Fourier terms and lags as features
- Detrend before reading the ACF
- Hold out the future; never shuffle time
- Put every fitted step inside the Pipeline, then save it
