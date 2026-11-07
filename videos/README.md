# Animated explainer videos

Hand-drawn animated explainers, rendered frame by frame with [Excalidraw](https://excalidraw.com). Every full-length video has chapter markers (in VLC: *Playback → Chapter*), and a companion guide that explains each scene at its timestamp.

| Course | Full video | Length | Guide | Editable drawings |
|---|---|---|---|---|
| **Linear Regression** (this repo's notebooks NB01–NB27) | [Linear-Regression-Full-Course.mp4](linear-regression/Linear-Regression-Full-Course.mp4) | 00:19:27 | [GUIDE.md](linear-regression/GUIDE.md) | [.excalidraw](linear-regression/Linear-Regression-Full-Course.excalidraw) |
| **Embeddings** (multimodal search, Gemini Embedding 2 + Qdrant) | [Embeddings-Full-Course.mp4](embeddings/Embeddings-Full-Course.mp4) | 00:12:26 | [GUIDE.md](embeddings/GUIDE.md) | [.excalidraw](embeddings/Embeddings-Full-Course.excalidraw) |
| **Vector Search** (embeddings, HNSW, IVF, BM25, hybrid, RAG) | [Search-Full-Course.mp4](vector-search/Search-Full-Course.mp4) | 00:16:13 | [GUIDE.md](vector-search/GUIDE.md) | [.excalidraw](vector-search/Search-Full-Course.excalidraw) |

Each folder also holds the individual chapter videos (`L01-…mp4`, `E01-…mp4`, `01-…mp4`) and a storyboard for each one. To edit a drawing, open the `.excalidraw` file at excalidraw.com with *Menu → Open*; every scene is a named frame you can edit or export as PNG/SVG.

[VIDEO_STRUCTURE.md](VIDEO_STRUCTURE.md) reviews how the Embeddings and Vector Search chapters are ordered.

## Linear Regression chapters

| # | Chapter | Notebooks |
|---|---|---|
| 1 | Fitting a line: residuals & SSR | NB01 |
| 2 | Deriving the OLS formula | NB02, NB03 |
| 3 | R² and adjusted R² | NB04 |
| 4 | Inference: t, p, confidence vs prediction intervals | NB05, NB23 |
| 5 | Assumptions & Gauss–Markov | NB06, NB24 |
| 6 | Diagnostics & influence | NB07 |
| 7 | Multiple regression & categorical encoding | NB08, NB22 |
| 8 | Multicollinearity & VIF | NB09 |
| 9 | Polynomials, interactions & cross-validation | NB10, NB14 |
| 10 | Ridge, Lasso & ElasticNet | NB11–NB13 |
| 11 | Gradient descent & feature scaling | NB15, NB21 |
| 12 | Beyond OLS: robust, quantile, Bayesian, heteroscedasticity | NB16–NB18, NB25 |
| 13 | Transforms, model selection & pitfalls | NB26, NB27 |
| 14 | Time series & production pipelines | NB19, NB20 |
