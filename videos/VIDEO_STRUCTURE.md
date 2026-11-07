# Video Series — Structure & Sequence Review

How the videos are ordered, whether each one builds only on earlier ideas, where content repeats, and what is missing.

**How this was checked.** The scene list for every video was extracted from its rendered `.excalidraw` storyboard: each step's caption plus the section heading on screen. So this review describes what actually appears on screen, not what was planned. The full scene-by-scene list is in the [Appendix](#appendix--scene-by-scene-outline-from-the-rendered-storyboards).

| Series | Source folder | Videos | Total length | Output |
|---|---|---|---|---|
| A. Vector Search | `video/Search_vector/` | 12 | ≈ 16.5 min | `output/01…12-*.mp4` and `.excalidraw` |
| B. Embeddings (multimodal) | `video/embedding/` | 9 + intro | ≈ 12.4 min | `output/embedding/E01…E09-*.mp4`, `Embeddings-Full-Course.mp4` |

---

## 1. Structure inside each video ✅ consistent

All 21 videos follow the same 5-part template from `lib/kit.js`:

| # | Part | What it does |
|---|---|---|
| 1 | **Title card** | Series label, title, and the hook question (`titleCard`) |
| 2 | **Problem / intuition** | Why the topic matters, shown with a small concrete example |
| 3 | **Mechanism, step by step** | Numbered sections (`heading`) with one caption per step (`say`), each paired with an animation |
| 4 | **Numbers & trade-offs** | Real or worked values, plus the knob or trade-off to tune |
| 5 | **Key takeaways** | 3–4 bullet recap (`outro`) |

Checks run on every storyboard:

| Check | Result |
|---|---|
| Every video starts with a Title frame | ✅ 21 / 21 |
| Every video ends with a Key takeaways frame | ✅ 21 / 21 |
| Steps are numbered in order where the topic is a process | ✅ e.g. "Step 1 → Step 2 → Step 3" in 01, 05, 11, 12 |
| One idea per caption, captions short enough to read | ✅ (8–13 steps per video) |
| Length per video | 60–104 s. Longest is 10 Hybrid (104 s); shortest is 09 (60 s) |

---

## 2. Series A — Vector Search: sequence check

### Order and dependencies

| # | Video | Length | Builds on | Introduces (used later by) |
|---|---|---|---|---|
| 01 | What is an embedding? | 84 s | — | vectors, dimensions, embedding model (→ all) |
| 02 | Measuring similarity | 82 s | 01 | cosine / dot / L2, normalization (→ 03, 04, 05, 10, 12) |
| 03 | Exact k-NN vs Approximate | 69 s | 01, 02 | k-NN, brute force, ANN, recall vs speed (→ 04, 05, 06) |
| 04 | HNSW | 72 s | 03 | graph layers, M, ef_search, ef_construction (→ 06) |
| 05 | IVF | 93 s | 03, 04 | clusters, nlist, nprobe |
| 06 | Quantization | 71 s | 03, 04 | FP16/INT8/binary, rescoring, storage tiers |
| 07 | Keyword search: TF-IDF & BM25 | 77 s | — | inverted index, TF, IDF, BM25 (→ 08, 09, 10) |
| 08 | Sparse encoding | 67 s | 07 | sparse vectors, term expansion (→ 10) |
| 09 | Why one method isn't enough | 60 s | 01, 07, 08 | failure modes of each method (→ 10, 11) |
| 10 | Hybrid search | 104 s | 07, 08, 09 | normalization, weighted sum, harmonic mean, RRF |
| 11 | Filtered vector search | 93 s | 03, 09 | pre- vs post-filtering |
| 12 | RAG with Bedrock | 87 s | 01, 02, 03 | chunk → embed → retrieve → generate |

**Verdict: ✅ the order is correct.** Every video only relies on ideas taught in an earlier one. The series moves through four blocks:

1. **Dense foundations** (01–02)
2. **Finding neighbours fast** (03–06)
3. **Keyword side** (07–08)
4. **Combining and applying** (09–12)

09 is placed right before 10 deliberately: it gives the reason ("each method misses different things") for the solution in 10.

### Issues found

| Severity | Issue | Where | Suggestion |
|---|---|---|---|
| Medium | **IVF re-teaches basics.** 05 opens with "Embeddings turn text into vectors" and a brute-force scene, which repeats 01 and 03. It was made first, as a standalone demo. | 05, first 3 steps (~20 s) | Keep it for standalone viewing. For a joined course, trim to one recap step: "recall from 03: brute force is slow". |
| Low | **"Recall" is never defined.** It is first used in 03 ("gives up a few percent of recall") and reused in 04, 05 and 06. | 03 | Add one caption to 03: "Recall = how many of the true top-K we actually found." |
| Low | **"$500 ≈ $5000" appears twice** (09 and 11). | 09, 11 | Fine as reinforcement. 11 could say "as we saw in 09…". |
| Low | **No evaluation video.** NDCG@10 appears only as illustrative bars in 09. Recall@K and MRR are never taught. | — | Possible 13th video: "Measuring search quality (Recall@K, NDCG, MRR)". |
| Info | **Two passes appear twice.** 06 (binary search, then FP32 rescoring) and Series B E03 (dim 256, then dim 1024) are the same "cheap pass, then precise pass" pattern. | 06 ↔ E03 | Could be cross-referenced in captions. |

---

## 3. Series B — Embeddings (multimodal project): sequence check

The current order (also the order of `Embeddings-Full-Course.mp4`):

| # | Chapter (course time) | Length | Builds on | Introduces |
|---|---|---|---|---|
| — | Introduction (00:00) | 12 s | — | Agenda of the 9 chapters |
| E01 | One space for every modality (00:12) | 90 s | — | Shared vector space, interleaved parts, architecture, input limits, stub-image caveat |
| E02 | Matryoshka embeddings (01:42) | 93 s | E01 | 8 nested sizes, prefix + rescale, latency and throughput |
| E03 | Two-stage retrieval (03:15) | 93 s | E02 | Named vectors dim_256 + dim_1024, top-100 → top-10 |
| E04 | One space, many languages (04:48) | 65 s | E01 | The 4×4 heatmap (0.765–0.872) |
| E05 | Anatomy of a Qdrant point (05:53) | 93 s | E01, E02 | ID, named vectors, payload, indexes, filters, uuid4 duplicates |
| E06 | Score thresholds (07:26) | 78 s | E05 | score_threshold sweep 44 → 26 → 2 → 0 |
| E07 | RAG retrieval (08:44) | 77 s | E05, E06 | KB retrieval, duplicate slots, retrieval-only scope |
| E08 | Recommendations (10:01) | 62 s | E05 | Seed self-match, exclude the seed, duplicate slots |
| E09 | 6 production lessons (11:03) | 83 s | all | IDs, retries, concurrency, local truncation, real test data, secrets |

**Verdict: ✅ mostly correct, with one dependency out of order.**

### Issues found

| Severity | Issue | Where | Suggestion |
|---|---|---|---|
| Medium | **Named vectors are used before they are explained.** E03 relies on Qdrant named vectors (`dim_256` + `dim_1024` on the same point) and gives a one-step explanation. The full explanation (point = ID + named vectors + payload) only comes later, in E05. | E03 → E05 | **Recommended order: E01 → E02 → E05 → E03 → E04 → E06 → E07 → E08 → E09.** E05 then becomes the storage foundation that E03, E06, E07 and E08 build on. |
| Medium | **The duplicate-ID problem is explained 4 times:** E05 (cause and fix), E07 ("got the same document twice"), E08 ("4 slots held only 2 products"), E09 (lesson 1). | E05, E07, E08, E09 | Keep the full explanation in E05 and the lesson in E09. In E07 and E08, shorten to one callback step: "the duplicate problem from E05 strikes again". |
| Low | **The 1×1 stub image caveat appears 3 times** (E01, E05, E09). | E01, E05, E09 | Acceptable: each video stands alone. In the course, E05's mention could be a callback. |
| Low | **Cosine similarity is assumed, not taught.** E01, E04 and E07 use cosine scores without explaining them. | Series B overall | Watch Series A 01–02 first, or add one sentence to the intro: "cosine score: 1 = same meaning, 0 = unrelated". |
| Info | **RAG is covered in both series.** A12 shows the full pipeline including the LLM answer. B-E07 is retrieval only and says so on screen ("next step, not built here"). | A12 ↔ B-E07 | Consistent, no contradiction. B-E07 can point to A12 for the generation step. |

### Accuracy cross-check between the series ✅ no contradictions

| Topic | Series A says | Series B says | Consistent? |
|---|---|---|---|
| Vector sizes | 384 / 768 / 1,024 (Titan v2) | 128–3,072, project default 756 (Gemini Embedding 2) | ✅ Different models, both labelled |
| Similarity metric | Cosine for text | Qdrant collection uses COSINE | ✅ |
| Numbers in embeddings | "$500 ≈ $5000": use filters | Payload fields plus filters (E05) | ✅ |
| Thresholds | — | Calibrate on your own data (E06) | ✅ |
| Facts source | Corrected numbers from the doc review | Measured values only (`videos-embedding/FACTS.md`) | ✅ |

---

## 4. Recommended viewing path

The order for a learner who knows nothing yet:

1. **A01 → A02** (what vectors are, how similarity is scored)
2. **A03 → A04 → A05 → A06** (how search stays fast)
3. **A07 → A08 → A09 → A10 → A11** (keyword side, hybrid, filters)
4. **A12** (RAG end to end)
5. **Series B in the recommended order:** E01 → E02 → E05 → E03 → E04 → E06 → E07 → E08 → E09

---

## 5. Applying the fixes

| Fix | Effort | How |
|---|---|---|
| Re-order Series B course to E01, E02, E05, E03, … | 1 command (no re-render) | `node build-course.mjs Embeddings-Full-Course "Embeddings, explained — the full course" E00-intro.mp4 E01-*.mp4 E02-*.mp4 E05-*.mp4 E03-*.mp4 E04-*.mp4 E06-*.mp4 E07-*.mp4 E08-*.mp4 E09-*.mp4`. Also update the agenda numbering in `videos-course/E00-intro.js` and re-render the intro (12 s). |
| Add a "Recall = …" caption to A03 | Small script edit + re-render (~2 min) | `videos/03-exact-vs-ann.js` |
| Trim A05's recap, or the duplicate callbacks in E07/E08 | Script edits + re-render | `videos/05-ivf.js`, `videos-embedding/E07-*.js`, `E08-*.js` |
| Add one cosine sentence to the course intro | Edit + re-render intro | `videos-course/E00-intro.js` |
| Build a single long Series A video | 1 command | `node build-course.mjs Search-Full-Course "Vector search, explained" ../output/[0-9]*.mp4` |

---

## 6. Commands to build the full-length videos

Run these in a terminal. Do not put `run` in front of them; it is not a command.

**A. Vector Search, one long video (about 16 min)**
```bash
cd /workshop/excalidraw/video/_studio
node build-course.mjs Search-Full-Course "Vector search, explained" ../output/[0-9]*.mp4
```
Output: `output/Search-Full-Course.mp4` (with chapters) and `output/Search-Full-Course.excalidraw`

**B. Embeddings, one long video in the recommended order (about 12.4 min)**
```bash
cd /workshop/excalidraw/video/output/embedding
node ../../_studio/build-course.mjs Embeddings-Full-Course "Embeddings, explained — the full course" \
  E00-intro.mp4 E01-*.mp4 E02-*.mp4 E05-*.mp4 E03-*.mp4 E04-*.mp4 E06-*.mp4 E07-*.mp4 E08-*.mp4 E09-*.mp4
```
This overwrites the current `Embeddings-Full-Course.mp4`, which is in the original order. If you also want the intro's agenda to match, change the chapter order in `_studio/videos-course/E00-intro.js`, re-render the intro, then run the command above again:
```bash
cd /workshop/excalidraw/video/_studio
node render.mjs videos-course/E00-intro.js --out=/workshop/excalidraw/video/output/embedding
```

**If you edit a chapter script**, re-render it first, then run the build command again:
```bash
cd /workshop/excalidraw/video/_studio
node render.mjs videos/05-ivf.js                                                              # Series A chapter
node render.mjs videos-embedding/E03-two-stage-retrieval.js --out=../output/embedding         # Series B chapter
```

## Appendix — scene-by-scene outline (from the rendered storyboards)

Each bullet is one animation step, in playback order. Long captions are cut off at about 85 characters by the frame-name limit.


### Series A — Vector Search
#### `01-embeddings` — What is an embedding?
- *Title card*
- Describe a house with numbers, and it becomes a vector.
- Each number is one dimension. This house vector has 4.
- Plot them as points. Closer points mean more similar houses.
- A 5-bed, $1M house would land right next to House 1.
- An embedding model turns any sentence into a vector of numbers.
- Step 1 — tokenize: split the text into tokens, each with an ID.
- Step 2 — a transformer lets every token look at the others: self-attention.
- Now each token has its own vector, informed by its context.
- Step 3 — pooling averages them into ONE vector for the whole sentence.
- Every output has the same length: 384, 768, or 1,024 numbers (Titan v2).
- No single dimension means "animal-ness" — meaning is spread across all of them.
- Words scattered randomly… the model places similar meanings together.
- No shared words, yet the two phrases land side by side. That's semantic search.
- **Key takeaways**

#### `02-distance-metrics` — Measuring similarity
- *Title card*
- A = [3, 4] and B = [6, 8]: same direction, but B is twice as long.
- Euclidean distance measures how far apart the tips are: 5 units.
- Manhattan walks the city blocks: 3 across + 4 up = 7.
- Chebyshev keeps only the biggest step — like a chess king: 4.
- Cosine looks only at the angle between vectors: 1 = same direction, 0 = unrelated.
- A and B point the same way, so cosine = 1.0 — a perfect match, despite different leng
- That's why cosine is great for text: a short and a long article on one topic still ma
- Same direction, but longer vectors score higher. Magnitude counts.
- Divide each vector by its length: both land on the unit circle at [0.6, 0.8].
- After normalizing, dot product equals cosine — and it's cheaper to compute.
- Use the metric your embedding model was trained with — for most text models, cosine.
- **Key takeaways**

#### `03-exact-vs-ann` — Exact k-NN vs Approximate
- *Title card*
- Given a query vector, k-NN returns the K closest ones. Here K = 3.
- Brute force computes the distance to every single vector.
- The answer is guaranteed exact… but the cost grows with every vector you add.
- At a million vectors, that's 0.5 to 5 seconds per query. Too slow for search.
- ANN indexes (HNSW, IVF…) jump straight to the right neighbourhood.
- Only 20 distance checks instead of 140 — and the same answer.
- "Approximate": usually right, but it may occasionally miss a true neighbour.
- ANN gives up a few percent of recall for a 10 to 100 times speedup.
- Exact search is the right call when the data is small or every result must be found.
- **Key takeaways**

#### `04-hnsw` — HNSW: highways for vectors
- *Title card*
- HNSW stacks graphs: few long-range links on top, every vector at the bottom.
- Each new vector rolls a random top layer. Higher layers are exponentially rarer.
- Each node connects to its nearest neighbours (default M = 16; we draw 3–4).
- Begin at the entry point on the top layer.
- Hop to whichever neighbour is closer to the query. Big jumps first.
- No closer neighbour? Drop down a layer and keep refining.
- At the bottom, keep a list of the ef_search best candidates — here 5.
- Return the top K = 3, after touching only 13 of 34 nodes.
- In a real index (1M vectors), that's a few hundred distance checks instead of a milli
- Bigger ef_search → higher recall, slower queries. Start at 100 and measure.
- ef_construction shapes the graph once; ef_search is the one you tune per query.
- **Key takeaways**

#### `05-ivf` — IVF: the Inverted File Index
- *Title card*
- Embeddings turn text into vectors. Similar meaning → nearby points.
- Brute force checks every vector. Fine for 100… painful for 100 million.
- HNSW is the most popular fix. But IVF is another cool idea…
- Drop k random centroids. Each vector joins its nearest centroid.
- Move each centroid to the middle of its group. Repeat.
- Converged: 6 clusters. In real indexes this is nlist — often 1,024 or more.
- Each vector is filed in its centroid's list — like a library shelf.
- Compare the query with just 6 centroids — not every vector.
- nprobe = 1: open only the closest list.
- Scanned 18 of 109 vectors and got a top 3. Fast!
- But the true nearest neighbour sits just across the border — in a list we never opene
- nprobe = 2: open the two closest lists.
- Now the real nearest neighbour is found — after scanning 37 of 109.
- Higher nprobe → better recall, more work. Lower → faster, may miss.
- Query 1,024 centroids + 8 lists instead of a million vectors.
- IVF needs a training step (k-means) before indexing — e.g. the Faiss engine in OpenSe
- **Key takeaways**

#### `06-quantization` — Quantization: cheaper vectors
- *Title card*
- Each dimension is a 32-bit float. That adds up fast.
- One million of them: about 3 GB of RAM, just for the vectors.
- 16-bit floats keep almost all the precision.
- Store one byte per number instead of four.
- 3,072 MB → 96 MB. But a bare sign bit loses detail…
- Step 1: search the tiny binary codes — rough but blazing fast.
- Step 2: re-score just those few with the original FP32 vectors.
- Cheap first pass, accurate second pass: the best of both.
- Hot data in memory; huge, cold collections on disk or S3.
- Minimal-cost preset: disk mode + 32× binary + HNSW m = 16, ef_construction = 300.
- **Key takeaways**

#### `07-keyword-bm25` — Keyword search: TF-IDF & BM25
- *Title card*
- Like the index at the back of a book: every word points to its pages.
- Look up only the query's words. D1 has both terms → it ranks first.
- Term frequency: apple is 2 of the 3 words.
- Inverse document frequency: the fewer docs contain it, the higher it scores.
- "the" is everywhere, so it is almost worthless for ranking.
- Multiply them: frequent here AND rare overall = relevant.
- Two knobs: k1 controls TF saturation, b controls length normalisation.
- Plain TF keeps growing: keyword stuffing would win.
- BM25 bends the curve: it levels off near k1 + 1.
- The same count in a twice-as-long document is worth less.
- Great for exact tokens — and fully explainable.
- But no shared word means no match: synonyms are invisible.
- **Key takeaways**

#### `08-sparse-encoding` — Sparse encoding
- *Title card*
- Imagine a row with a slot for every word the model knows.
- Almost every slot is zero — only ~1% light up.
- So we store only the non-zero entries: a small {term: weight} dictionary.
- The model adds related terms with weights — learned synonyms, still just keywords.
- Only terms that appear on both sides count.
- A dot product over a handful of terms: tiny and fast.
- Both say 'apple' — but the expanded terms tip it toward the brand.
- Keyword speed and explainability, with some semantic smarts.
- **Key takeaways**

#### `09-why-one-method-fails` — Why one method isn't enough
- *Title card*
- Same meaning, zero overlapping words → BM25 scores it 0.
- Semantic search sees they're neighbours in meaning space.
- Error codes look nearly identical to an embedding — it may return the wrong one.
- Numbers blur: embed('$500') ≈ embed('$5000') — 10× apart in price!
- Negation is weak: 'not' barely moves the vector.
- One word, two meanings — you need context or filters to decide.
- Each method misses different things — so combining them wins.
- That's why production search goes hybrid — keyword + semantic together.
- **Key takeaways**

#### `10-hybrid-search` — Hybrid Search: Fusing Scores
- *Title card*
- Run keyword and semantic search in parallel on the same query.
- But look: 12.7 vs 0.78. The scores live on totally different scales.
- Each engine scores on its own ruler: BM25 is unbounded, cosine stays within 0–1.
- Add them raw and the biggest scale wins: BM25 decides almost everything.
- Raw scores from one engine: [0.12, 0.82, 0.45, 0.03, 0.67].
- After: [0.11, 1, 0.53, 0, 0.81]. Every list now spans exactly 0 → 1.
- Normalized scores, each multiplied by a weight: 0.3, 0.3 and 0.4.
- Add the weighted parts: 0.3·0.8 + 0.3·0.6 + 0.4·0.9 = 0.78.
- The engines disagree: sparse thinks this document is barely relevant.
- Harmonic gives 0.24 instead of 0.60: one weak signal drags the result down.
- Throw away the scores, keep only positions. Each list votes 1 / (60 + rank).
- Doc A is #1 and #3: 1/61 + 1/63 ≈ 0.0323, the top fused result.
- No normalization needed, which makes RRF a very robust default.
- Shopping: keyword-heavy, so 'iPhone 15 Pro' matches exactly. 0.4 / 0.3 / 0.3.
- Support questions: meaning-heavy, so dense gets 0.5. Measure and tune.
- **Key takeaways**

#### `11-filtering` — Filtered Vector Search
- *Title card*
- 'laptop' is meaning, so it goes in the vector. '$500' is a hard rule: a filter.
- So which comes first: the nearest-neighbour search, or the filter?
- Step 1: find the 10 nearest neighbours, ignoring price completely.
- Step 2: apply the filter. Most neighbours cost too much: only 2 of 10 survive.
- With a very strict filter, post-filtering can return nothing at all.
- Step 1: the filter narrows 90 vectors to 27 candidates that fit the budget.
- Step 2: search only inside the survivors. You always get a full top 10, if it exists.
- And when the filter is very selective, there is far less to search: faster too.
- Rule of thumb: the stricter the filter, the more you want pre-filtering.
- Put the filter inside the knn clause, so the engine filters while it searches.
- A bool filter wrapped around knn acts like post-filtering. Qdrant: use query_filter.
- Embeddings blur numbers: '$500' and '$5000' land almost on top of each other.
- Store prices, ratings and dates as fields, and filter on them exactly.
- **Key takeaways**

#### `12-rag-bedrock` — RAG: Search That Answers
- *Title card*
- Split the PDF into small chunks: 35 pages become 38 searchable pieces.
- An embedding model turns each chunk into a 1,024-dimension vector.
- The vectors, plus text and page numbers, go into the vector database.
- The question gets embedded by the same model, then searched in Qdrant.
- Mixing models breaks it: vectors from different models aren't comparable.
- Cosine search finds the 5 chunks closest in meaning to the question.
- Instructions + the 5 chunks with their page numbers + the question.
- Claude writes the answer from the context only, and points to the pages.
- Answers grounded in your own documents, with sources you can check.
- Overlap keeps ideas from being cut in half at a chunk border.
- And re-index everything if you ever switch embedding models.
- **Key takeaways**


### Series B — Embeddings
#### `E01-multimodal-shared-space` — One space for every modality
- *Title card*
- Text, images, audio, video and PDFs all go into ONE model: gemini-embedding-2-preview
- Everything lands in the SAME space. Meaning decides the position, not the file type.
- The idea: a text query lands by the beach cluster, next to an image and a video.
- No separate image pipeline: one cosine search in Qdrant covers every modality.
- One request carries both parts, in order: the image first, then its caption.
- The model returns a single vector that describes the image and its caption together.
- One entry point, three parts: embed (Vertex AI), store (Qdrant), search (engine).
- At search time the engine embeds the query, then asks Qdrant for the nearest points.
- MultimodalSearchAPI validates content against these limits before embedding it.
- Matching text: 0.6859. The stub image: only 0.3236, even with an image-only filter.
- No image or interleaved point reached the top 10. One pixel carries no meaning.
- The design supports cross-modal search — prove it with real images, not stubs.
- **Key takeaways**

#### `E02-matryoshka` — Matryoshka embeddings
- *Title card*
- Gemini Embedding 2 can return 8 sizes: 128 up to 3,072 numbers per vector.
- Like nesting dolls: the small vector is the beginning of the big one.
- The numbers shrink as the vector grows, but the signs stay −, +, − in every row.
- The ratio stays ≈ 0.65 at every size: all five vectors point in the same direction.
- The measured outputs match this: keep the first d numbers, rescale to length 1.
- Length 1.00 at all 8 sizes. Spread over more numbers, each number gets smaller.
- Each call took about 440–660 ms, whatever the size. The network round-trip dominates.
- ≈ 1.9 docs/sec at every size: embed_batch makes one API call per item, in turn.
- Today, asking for two sizes costs two API calls — one per dimension.
- Because the sizes are nested, one 3,072-d call could be cut down locally instead.
- Small vectors for fast scans, big ones for precision. Two-stage uses both.
- **Key takeaways**

#### `E03-two-stage-retrieval` — Two-stage retrieval
- *Title card*
- Each point stores the same item at two sizes: named vectors dim_256 and dim_1024.
- Both sit on the SAME point, so stage 2 can fetch the candidates by their IDs.
- 10,000 CVs get a quick 5-minute phone screen. 50 make the shortlist.
- Only those 50 get the full 1-hour interview.
- Stage 1: embed the query at 256 dims, search dim_256, keep the top-100 (the default).
- Stage 2 compares only the 100 candidates at 1,024 dims and returns the top-10.
- The demo used smaller numbers: 256 → top-20 candidates, then 1024 → top-5.
- On 54 points two-stage was the SLOWEST: 2,348 ms vs 1,154 ms at dim 256.
- Why: it embeds the query twice and searches twice. With 54 points, nothing is saved.
- At scale, stage 1 discards almost everything; only 100 points get the 1024-d check.
- Note: this project measured speed only — check accuracy on your own data.
- **Key takeaways**

#### `E04-multilingual` — One space, many languages
- *Title card*
- The Eiffel Tower, written in English, Spanish, French and Japanese.
- Each sentence goes through the same model: gemini-embedding-2-preview.
- Same meaning lands in the same neighbourhood, whatever the language.
- Query in each language, score each document with cosine similarity.
- Every one of the 16 pairs scores between 0.765 and 0.872.
- Even the weakest cross-language pair, French to Japanese, is 0.765.
- For English, Spanish and French queries, the same-language document scores highest.
- Surprise: for the Japanese query, the English document edges out the Japanese one.
- Cross-language scores stay close to same-language scores: meaning carries over.
- The old way: translate everything into one language first.
- With a shared space: embed the query, search everything, done.
- **Key takeaways**

#### `E05-qdrant-payload-filters` — Anatomy of a Qdrant point
- *Title card*
- Every stored embedding is a point. It starts with an ID.
- The collection defines 8 named vectors: dim_128 up to dim_3072.
- A point fills only the sizes it was embedded at. Two-stage docs: dim_256 + dim_1024.
- This knowledge-base doc was embedded once, at the project default: dim_756.
- The payload carries metadata: type, source, time, size, model.
- Four payload fields get an index: three KEYWORD, one DATETIME.
- Content of every modality lives in the same collection.
- Filter on modality: content_type MatchAny ["text"] keeps only text.
- Add language MatchAny ["es","fr"] and the conditions combine.
- Timestamp ranges and source IDs work the same way.
- Text only: five matches, all around 0.51 to 0.55.
- Image only: one match at 0.3236.
- No surprise: a 1×1-pixel stub image carries no meaning. Use real images.
- Each store call makes a new random uuid4, so re-running the demo stores everything ag
- The collection holds 54 points, each item twice, so top-2 is one doc repeated.
- Fix: derive the ID from source_id with uuid5. Same doc, same ID: upsert overwrites.
- **Key takeaways**

#### `E06-score-thresholds` — Score thresholds
- *Title card*
- One query, 44 results. Where do their scores fall?
- 18 between 0.3 and 0.4, 24 between 0.4 and 0.5, and just 2 above 0.6.
- The best match, about 0.686, is the golden-retriever sentence. It is stored twice.
- Qdrant drops every result scoring below score_threshold.
- 0.0 to 0.3: all 44 stay. At 0.4: 26 left.
- At 0.5 and 0.6: only 2 survive.
- From 0.7 up: nothing at all.
- Same query, ten thresholds: 44, 44, 44, 44, 26, 2, 2, 0, 0, 0.
- Lower keeps more but lets weak matches in. Higher is stricter, until nothing is left.
- The README suggests 0.0 for discovery and 0.5+ to keep weak context out of RAG.
- But scores depend on the model, the data and the query, so calibrate.
- A fixed 0.7 would keep the RAG answers but return nothing for the beach query.
- **Key takeaways**

#### `E07-rag-knowledge-base` — RAG retrieval: find the right doc
- *Title card*
- 6 policy documents, each embedded at dim 756 and stored in Qdrant.
- Closest vector: the parental-leave policy, cosine score 0.8381.
- Deployment question → kb-infra-001 (two approvals + CI), score 0.8477.
- Rate-limit question → kb-product-001, score 0.8528. No keywords needed.
- Asked for 2 results, got the same document twice.
- Each run stored new points with random IDs, so every document exists twice.
- Duplicates waste result slots: your top 2 should be 2 different docs.
- The demo asked Qdrant to drop anything scoring below 0.4.
- All three right answers scored about 0.84, far above the cut-off.
- This project does the retrieval. Handing the docs to an LLM is the next stage.
- **Key takeaways**

#### `E08-recommendations` — Recommendations: more like this
- *Title card*
- Each product is just a line of text, embedded at dim 756. No category field.
- Headphones and earbuds land close together; mouse and keyboard sit apart.
- Search with the seed's own text: 'Sony WH-1000XM5 wireless noise-cancelling headphone
- Bose 0.776, Galaxy Buds2 0.720: the nearest neighbours are other audio gear.
- Rank 1 is always the seed (score 1.000): identical text, identical vector.
- Every product was stored twice, so 4 slots held only 2 products.
- A real match got pushed out. Unique IDs per product fix this.
- The grouping came only from the meaning of the product text.
- **Key takeaways**

#### `E09-production-lessons` — 6 production lessons
- *Title card*
- Re-running the demo doubled every document. Deterministic IDs make writes idempotent.
- Up to 3 attempts, waiting 1 s then 2 s, for rate limits, timeouts and API errors.
- Retrying a bad credential never helps, so it stops immediately.
- Items are embedded sequentially: about 1.9 documents per second (dims 128 to 1024).
- Network round-trips dominate, so concurrency is the real speed-up.
- Smaller Matryoshka vectors are a rescaled prefix of the big one, so truncate locally.
- One blank pixel carries no meaning, so cross-modal search was never really tested.
- Mocks make tests fast and free, but they can't tell you if results are relevant.
- Example env files are committed, so keep only placeholders there and rotate any leake
- **Key takeaways**
