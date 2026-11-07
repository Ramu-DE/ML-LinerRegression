# Vector Search — Full Course Guide

Total length: **16:13**

**Video:** [`Search-Full-Course.mp4`](Search-Full-Course.mp4), 1920×1080, 30 fps, with chapter markers. In VLC use *Playback → Chapter*.
**Editable drawings:** [`Search-Full-Course.excalidraw`](Search-Full-Course.excalidraw). Open it at excalidraw.com with *Menu → Open*. Every scene below is one named frame there.
**Source material:** `video/Search_vector/` (guides, code and slide deck).

### How to use this guide
- Each **[mm:ss]** line is the on-screen caption, with its exact time in the full video.
- *On screen* describes the animation at that moment, so you can follow along or rebuild it.
- The paragraph under it explains the idea in more depth than the caption has room for.
- The course has four blocks:
  1. **Dense foundations** (Ch 1–2)
  2. **Finding neighbours fast** (Ch 3–6)
  3. **Keyword search** (Ch 7–8)
  4. **Combining and applying** (Ch 9–12)

  Each chapter only uses ideas from earlier chapters.

> **Accuracy note.** Some numbers in the original docs were wrong; this course uses the corrected values (for example, harmonic mean (0.8, 0.1, 0.9) ≈ 0.24, not 0.16). The docs don't explain IVF's nlist/nprobe, the BM25 formula or RRF, so those parts come from general knowledge. Bars marked *illustrative* show the shape of a result, not a measurement.

## Chapters

| Starts | Chapter | Length | Source video |
|---|---|---|---|
| 00:00 | [Introduction](#introduction) | 00:12 | `A00-intro` |
| 00:12 | [Chapter 1 — What is an embedding?](#chapter-1--what-is-an-embedding) | 01:24 | `01-embeddings` |
| 01:36 | [Chapter 2 — Measuring similarity](#chapter-2--measuring-similarity) | 01:22 | `02-distance-metrics` |
| 02:59 | [Chapter 3 — Exact k-NN vs Approximate](#chapter-3--exact-k-nn-vs-approximate) | 01:09 | `03-exact-vs-ann` |
| 04:08 | [Chapter 4 — HNSW: highways for vectors](#chapter-4--hnsw-highways-for-vectors) | 01:12 | `04-hnsw` |
| 05:20 | [Chapter 5 — IVF: the Inverted File Index](#chapter-5--ivf-the-inverted-file-index) | 01:33 | `05-ivf` |
| 06:53 | [Chapter 6 — Quantization: cheaper vectors](#chapter-6--quantization-cheaper-vectors) | 01:11 | `06-quantization` |
| 08:05 | [Chapter 7 — Keyword search: TF-IDF & BM25](#chapter-7--keyword-search-tf-idf--bm25) | 01:17 | `07-keyword-bm25` |
| 09:22 | [Chapter 8 — Sparse encoding](#chapter-8--sparse-encoding) | 01:07 | `08-sparse-encoding` |
| 10:29 | [Chapter 9 — Why one method isn't enough](#chapter-9--why-one-method-isnt-enough) | 00:59 | `09-why-one-method-fails` |
| 11:29 | [Chapter 10 — Hybrid Search: Fusing Scores](#chapter-10--hybrid-search-fusing-scores) | 01:44 | `10-hybrid-search` |
| 13:13 | [Chapter 11 — Filtered Vector Search](#chapter-11--filtered-vector-search) | 01:32 | `11-filtering` |
| 14:46 | [Chapter 12 — RAG: Search That Answers](#chapter-12--rag-search-that-answers) | 01:27 | `12-rag-bedrock` |

---

## Introduction

**Starts at 00:00** · length 00:12 · source `A00-intro` · hook: *"From embeddings to HNSW, BM25, hybrid search and RAG"*

**What you'll learn.** This 12-second opener lays out the route through the whole course. It needs no background. The 12 chapters form four blocks: what dense vectors are (1–2), how to search them fast (3–6), keyword-based search (7–8), and how to combine everything into a real system (9–12). Each block builds on the one before it, so watching in order works best.

### What we'll cover

**[00:07]** Four blocks: dense vectors, fast search, keyword search, then combining it all.

> *On screen:* The two-column agenda pops in one numbered circle at a time while each chapter title types out beside it.

The order follows dependencies. Chapters 1–2 define vectors and similarity. 3–6 make nearest-neighbour search fast and cheap. 7–8 cover the keyword side. 9–12 explain why neither side is enough alone, and how hybrid search, filters and RAG combine them.


---

## Chapter 1 — What is an embedding?

**Starts at 00:12** · length 01:24 · source `01-embeddings` · hook: *"How can a computer tell "cheap phone" and "affordable smartphone" mean the same thing?"*

**What you'll learn.** This chapter explains what an embedding is: a list of numbers that places a thing (a house, a sentence) as a point in space, so that similar things end up close together. It is the foundation for every later chapter and needs no background. By the end you'll know how a text model turns a sentence into one fixed-length vector, and why that makes search by meaning possible.

### A vector is just a list of numbers

**[00:18]** Describe a house with numbers, and it becomes a vector.

> *On screen:* A house sketch draws in and an arrow writes its vector [5 bed, 4 bath, 854 sqm, $1.1M] in blue.

A vector is just an ordered list of numbers, where each position always means the same thing. Once a house is written this way, a computer can compare it with other houses by arithmetic instead of by reading descriptions. That is the core idea behind every embedding.

**[00:22]** Each number is one dimension. This house vector has 4.

> *On screen:* A second house appears with its own vector [4 bed, 3 bath, 335 sqm, $530K] in green.

Each position in the list is called a dimension, so these house vectors are 4-dimensional. Both houses use the same four positions in the same order. That shared layout is what makes them comparable: position 1 is always bedrooms, position 4 always price.

### Vectors are points in space

**[00:29]** Plot them as points. Closer points mean more similar houses.

> *On screen:* Axes for bedrooms and price draw in, the two houses drop onto the plot as points, and a dashed red line marks the distance between them.

Using two of the dimensions as coordinates turns each vector into a point. The straight-line distance between points becomes a similarity measure: small distance means similar houses. Real embeddings work the same way, just with hundreds of dimensions instead of two.

**[00:33]** A 5-bed, $1M house would land right next to House 1.

> *On screen:* A third house slides across the plot and settles right beside House 1.

A 5-bed house priced around $1M lands next to House 1 (5 bed, $1.1M) because its numbers are close. Nobody wrote a rule saying 'these are alike'; closeness falls out of the numbers. This is the property search relies on: find the points nearest to a query point.

### Text → vector with an embedding model

**[00:37]** An embedding model turns any sentence into a vector of numbers.

> *On screen:* A sentence card feeds an arrow into an 'embedding model' box, and a vector [0.234, -0.567, 0.891, …] types out on the right.

Text has no obvious numbers, so an embedding model learns them. It is a neural network trained so that sentences with similar meaning get similar vectors. The individual values (0.234, -0.567, …) mean nothing alone; only their pattern, compared with other vectors, carries meaning.

**[00:41]** Step 1 — tokenize: split the text into tokens, each with an ID.

> *On screen:* The sentence splits into six token chips (The, cat, sat, on, the, mat), each with a numeric ID underneath.

The model first breaks text into tokens from a fixed vocabulary and maps each to an integer ID. The two 'the's get the same ID (1996 here) because they are the same token. Long or rare words may be split into several sub-word tokens.

**[00:45]** Step 2 — a transformer lets every token look at the others: self-attention.

> *On screen:* Curved red arrows draw from 'cat' to other tokens, showing self-attention.

In a transformer, every token looks at every other token and decides how much each one matters for its own meaning. That is how 'bank' can mean a river bank or a money bank depending on the words around it. Attention is repeated over many layers.

**[00:50]** Now each token has its own vector, informed by its context.

> *On screen:* Small coloured vector bars appear under every token.

After the attention layers, each token has its own vector, and that vector now reflects the whole sentence, not just the word alone. The 'cat' vector here already 'knows' the cat sat on a mat. But search needs one vector per sentence, not six.

**[00:55]** Step 3 — pooling averages them into ONE vector for the whole sentence.

> *On screen:* The token bars slide to the centre, merge and turn orange, labelled 'one sentence vector'.

Pooling combines the token vectors into one, often by averaging them (mean pooling) or by using a special summary token. The result is a single fixed-length vector for the entire sentence, which is what gets stored and searched.

### Fixed size: hundreds of dimensions

**[01:00]** Every output has the same length: 384, 768, or 1,024 numbers (Titan v2).

> *On screen:* Three bars grow to different lengths: MiniLM 384, mpnet 768 and Titan v2 1,024 dimensions.

Every model has a fixed output size: a sentence of 3 words and one of 300 words both come out at the same length. Larger vectors can hold more nuance but cost more memory and compute. Amazon Titan Text Embeddings v2 outputs 1,024 dimensions by default (256 and 512 are also available).

**[01:05]** No single dimension means "animal-ness" — meaning is spread across all of them.

> *On screen:* The dimension bars stay on screen while the caption makes the point about meaning.

It is tempting to think 'dimension 42 = animal-ness', but single dimensions are generally not interpretable. Meaning is spread across many dimensions at once. That is why you compare whole vectors (Chapter 2) rather than reading individual numbers.

### Similar meaning → nearby vectors

**[01:10]** Words scattered randomly… the model places similar meanings together.

> *On screen:* Scattered words fly from random positions into topic clusters (animals together, vehicles together).

Before training, positions would be random. A trained model places related words and sentences near each other: dog, cat and bird form one group; car, bike and plane another. The drawing is a 2-D sketch of what happens in hundreds of dimensions.

**[01:18]** No shared words, yet the two phrases land side by side. That's semantic search.

> *On screen:* Two phrase cards, 'cheap phone' and 'affordable smartphone', glide together and land side by side.

These phrases share no words, so keyword search would see no match at all. An embedding model places them almost on top of each other because they mean the same thing. Finding results by meaning rather than exact words is called semantic search.

### Key takeaways  `[01:24]`

- A vector is a list of numbers describing something
- Embedding models: tokenize → attention → pooling
- Fixed size: 384 / 768 / 1,024 dimensions
- Similar meaning ends up close together

---

## Chapter 2 — Measuring similarity

**Starts at 01:36** · length 01:22 · source `02-distance-metrics` · hook: *"Similar because they point the same way… or because they're close together?"*

**What you'll learn.** Once things are vectors, we need a way to say how similar two of them are. This chapter compares Euclidean (L2), Manhattan, Chebyshev, cosine and dot product on one worked example, A = [3, 4] and B = [6, 8]. It builds on Chapter 1. Picking the wrong metric quietly ruins search quality, so this is worth getting right.

### Two vectors

**[01:44]** A = [3, 4] and B = [6, 8]: same direction, but B is twice as long.

> *On screen:* A grid draws in, then a blue arrow A = [3, 4] and a green arrow B = [6, 8] grow from the origin.

A and B point in exactly the same direction, but B is twice as long (length 10 vs 5). This one pair is a good test case: metrics that care about length will call them different, while metrics that only look at direction will call them identical.

### Euclidean (L2): the straight-line gap

**[01:50]** Euclidean distance measures how far apart the tips are: 5 units.

> *On screen:* A red two-headed arrow appears beside the vectors, labelled 5, while the formula √((6−3)² + (8−4)²) = 5 types out.

Euclidean (L2) distance is the ordinary straight-line distance: subtract coordinates, square, add, take the square root. Here √(9 + 16) = 5. It is a distance, so smaller means more similar, and it is sensitive to vector length. A short and a long vector on the same line are still 5 apart.

### Bonus: Manhattan & Chebyshev

**[01:54]** Manhattan walks the city blocks: 3 across + 4 up = 7.

> *On screen:* An orange staircase path walks 3 across and 4 up, and 'Manhattan = |6−3| + |8−4| = 7' types out.

Manhattan (L1) distance adds up the absolute differences in each dimension, like walking city blocks where you can't cut diagonally. Here 3 + 4 = 7. It is less sensitive to one large difference than L2, because differences are not squared.

**[01:58]** Chebyshev keeps only the biggest step — like a chess king: 4.

> *On screen:* A violet line appears, 'Chebyshev = max(3, 4) = 4' types out.

Chebyshev distance keeps only the single largest per-dimension difference, here 4. Think of a chess king, which can move diagonally, so the number of moves equals the biggest gap. It is rarely used for text embeddings but useful when one bad dimension should dominate.

### Cosine similarity: only the angle

**[02:04]** Cosine looks only at the angle between vectors: 1 = same direction, 0 = unrelated.

> *On screen:* A violet vector C = [7, 2] appears with an angle arc of about 37° to A, and cos θ = 29 / (5 × 7.28) = 0.80 types out.

Cosine similarity is the cosine of the angle between two vectors: A·C divided by the product of their lengths. A·C = 3×7 + 4×2 = 29, ‖A‖ = 5, ‖C‖ ≈ 7.28, so cos ≈ 0.80. It ranges from −1 (opposite) through 0 (unrelated) to 1 (same direction), and ignores length entirely.

**[02:10]** A and B point the same way, so cosine = 1.0 — a perfect match, despite different lengths.

> *On screen:* Vector C rotates onto A's direction, the arc fades, and the formula updates to cos(A, B) = 50 / (5 × 10) = 1.0.

For A and B: A·B = 3×6 + 4×8 = 50 and ‖A‖ × ‖B‖ = 5 × 10 = 50, so cosine = 1.0, a perfect match, even though L2 says they are 5 apart. This is the key difference: cosine measures direction only, L2 measures position.

**[02:16]** That's why cosine is great for text: a short and a long article on one topic still match.

> *On screen:* A note types out: short article [5, 1, 0] vs long article [50, 10, 0] → cos = 1.0.

For text, direction reflects what a document is about, while length can reflect how long it is or how often words repeat. A short and a long article on the same topic should match, and cosine makes them match (both point the same way). That is why cosine is the default for text.

### Dot product: direction × magnitude

**[02:23]** Same direction, but longer vectors score higher. Magnitude counts.

> *On screen:* A·B = 3×6 + 4×8 = 50 types out, and bars grow for A·A = 25, A·B = 50 and B·B = 100.

The dot product multiplies matching dimensions and adds them up, so it grows with both direction and length. B·B (100) beats A·B (50) even though all three pairs point the same way. That is useful when magnitude carries meaning, such as popularity in recommendations, but surprising if you expected pure similarity.

### Normalize to length 1

**[02:29]** Divide each vector by its length: both land on the unit circle at [0.6, 0.8].

> *On screen:* The camera zooms into the unit circle while A and B both shrink onto the same point [0.6, 0.8].

Normalizing means dividing a vector by its length so it becomes length 1. A = [3, 4] / 5 = [0.6, 0.8], and B = [6, 8] / 10 = [0.6, 0.8]: the same point. After normalizing, every vector sits on the unit circle (or sphere), and only direction remains.

**[02:34]** After normalizing, dot product equals cosine — and it's cheaper to compute.

> *On screen:* 'dot product = cosine' types out in red beside the normalized vectors.

When both vectors have length 1, the cosine formula's denominator is 1 × 1, so cosine equals the plain dot product. Many vector databases store normalized vectors and use the cheaper dot product. Ranking by L2 distance gives the same order too, since ‖a − b‖² = 2 − 2·cos for unit vectors.

### Rule of thumb

**[02:40]** Use the metric your embedding model was trained with — for most text models, cosine.

> *On screen:* Three cards pop in: Cosine (text & semantic search), Dot product (recommendations), Euclidean (measurements, images, sensor data).

These are rules of thumb, not laws. The most important rule: use the metric the embedding model was trained for, which is stated on its model card. Using L2 on vectors trained for cosine, or skipping normalization when the model expects it, can quietly reduce search quality.

### Key takeaways  `[02:46]`

- Euclidean = straight-line gap (A to B: 5)
- Cosine = angle only (A and B: 1.0)
- Dot product = angle × length (A·B = 50)
- Normalize → dot product equals cosine

---

## Chapter 3 — Exact k-NN vs Approximate

**Starts at 02:59** · length 01:09 · source `03-exact-vs-ann` · hook: *"Comparing your query to a million vectors, one by one: how slow is that?"*

**What you'll learn.** This chapter explains k-nearest-neighbour (k-NN) search: finding the K vectors closest to a query. It then shows why comparing against every vector (exact search) is too slow at scale, and how approximate nearest neighbour (ANN) indexes trade a little accuracy for a lot of speed. It builds on Chapters 1–2 and sets up HNSW, IVF and quantization (Chapters 4–6).

### k-NN: find the K most similar vectors

**[03:06]** Given a query vector, k-NN returns the K closest ones. Here K = 3.

> *On screen:* A scatter of 140 points appears with a red query marker, and its three nearest neighbours are circled.

k-NN (k-nearest neighbours) search returns the K stored vectors most similar to a query, here K = 3. 'Most similar' uses the metric from Chapter 2, usually cosine for text. In search, K is simply how many results you want back, for example the top 10.

### Exact k-NN: compare with every vector

**[03:10]** Brute force computes the distance to every single vector.

> *On screen:* Thin red lines shoot from the query to every point while a counter climbs to 'comparisons: 140'.

Exact (brute-force) k-NN computes the distance from the query to every stored vector, then keeps the K best. It is simple and needs no index. But it does one full distance calculation per stored vector, every single query.

**[03:14]** The answer is guaranteed exact… but the cost grows with every vector you add.

> *On screen:* '100% correct top 3' appears in green next to the finished scan.

Because every vector was checked, the result is guaranteed to be the true top 3: nothing can be missed. The cost is linear: double the vectors, double the work. That is fine for thousands of vectors and painful for millions.

**[03:20]** At a million vectors, that's 0.5 to 5 seconds per query. Too slow for search.

> *On screen:* '1,000,000 vectors × 768 dims = O(N × D) work per query' types out and a clock hand spins, then '0.5 – 5 s per query' appears.

The work grows with N (number of vectors) times D (dimensions): one million vectors × 768 dimensions is about 768 million multiply-adds per query. Depending on hardware, that lands roughly between half a second and several seconds. Interactive search usually needs answers in milliseconds.

### Approximate NN: check a smart subset

**[03:27]** ANN indexes (HNSW, IVF…) jump straight to the right neighbourhood.

> *On screen:* All points fade to grey, then orange arrows hop from a far entry point toward the query, lighting up the points they visit.

An ANN (approximate nearest neighbour) index is a data structure built ahead of time so a query can jump to the right region instead of scanning everything. HNSW uses a graph to hop (Chapter 4); IVF uses clusters (Chapter 5). Either way, most of the collection is never touched.

**[03:32]** Only 20 distance checks instead of 140 — and the same answer.

> *On screen:* A short burst of red lines checks only the nearby points, and 'checked 20 of 140 / same top 3 (this time)' appears.

Here the index needed only 20 distance calculations instead of 140, and still found the same top 3. On real data the savings are far bigger: often a few hundred checks instead of a million. Note the wording 'this time': there is no guarantee.

**[03:36]** "Approximate": usually right, but it may occasionally miss a true neighbour.

> *On screen:* The ANN result stays on screen while the caption explains 'approximate'.

Approximate means the index can occasionally miss one of the true nearest neighbours, for example one just outside the region it explored. This is measured as recall: the fraction of the true top-K that the search actually returned. Recall@10 = 0.95 means 95% of the real top 10 were found.

### The trade-off

**[03:43]** ANN gives up a few percent of recall for a 10 to 100 times speedup.

> *On screen:* Recall bars (Exact 100%, ANN 95–99%) and latency bars (0.5–5 s vs milliseconds) grow, then a box reads 'give up 1–5% recall → get 10–100× speed'.

This is the core trade-off of vector search. A few percent of recall is usually invisible to users, while the speed-up is what makes search usable at scale. Index settings (ef_search in HNSW, nprobe in IVF) let you move along this curve. These numbers are typical ranges, not guarantees.

### When exact k-NN still wins

**[03:49]** Exact search is the right call when the data is small or every result must be found.

> *On screen:* Three cards appear: Small data, Recall must be 100%, Very strict filters.

Exact search still wins in three cases. With a few thousand vectors, brute force is already fast. Audits, legal or deduplication work can't accept misses. And when a filter leaves only a handful of candidates, scanning them directly is cheaper than using an index (see Chapter 11).

### Key takeaways  `[03:55]`

- Exact k-NN compares the query with every vector
- Cost grows as O(N × D): seconds at 1M vectors
- ANN checks a smart subset: milliseconds
- Trade 1–5% recall for 10–100× speed

---

## Chapter 4 — HNSW: highways for vectors

**Starts at 04:08** · length 01:12 · source `04-hnsw` · hook: *"How do you find the nearest neighbour without looking at everyone?"*

**What you'll learn.** HNSW (Hierarchical Navigable Small World) is the most widely used ANN index. This chapter builds a real 34-node, 3-layer HNSW graph and searches it step by step: greedy hops on the top layer, dropping down layers, then a beam search at the bottom. It builds on Chapter 3 and explains the three settings you'll actually tune: M, ef_construction and ef_search.

### A graph with layers

**[04:14]** HNSW stacks graphs: few long-range links on top, every vector at the bottom.

> *On screen:* Three stacked bands draw in (Layer 2 highways, Layer 1, Layer 0 every vector), with an 'interstates → main roads → local streets' analogy beside them.

HNSW is a stack of graphs. The bottom layer contains every vector, linked to its close neighbours. Each higher layer contains fewer vectors with longer-range links, like a road network: interstates for big jumps, local streets for the final approach.

**[04:19]** Each new vector rolls a random top layer. Higher layers are exponentially rarer.

> *On screen:* Nodes appear in Layer 0, copies rise into higher layers, and counters show 34, 10 and 3 nodes.

When a vector is inserted, it draws a random top layer, with the probability shrinking exponentially for each layer up. So most nodes live only at the bottom, and very few reach the top. In this tiny real example, all 34 nodes are in layer 0, 10 in layer 1 and 3 in layer 2.

### Each node links to M neighbours

**[04:24]** Each node connects to its nearest neighbours (default M = 16; we draw 3–4).

> *On screen:* Grey edges draw between each node and its nearest neighbours on every layer.

Each node is connected to up to M neighbours per layer (twice that on layer 0 in common implementations). The default is M = 16; the drawing uses 3–4 links so it stays readable. A larger M gives better recall but uses more memory and makes indexing slower.

### Search: start at the top, go greedy

**[04:30]** Begin at the entry point on the top layer.

> *On screen:* A red query marker appears, and the top-layer entry point is labelled.

Every search starts at a single fixed entry point on the top layer. Because the top layer is sparse, each link there crosses a large part of the space, so the search can get close to the query in just a few hops.

**[04:33]** Hop to whichever neighbour is closer to the query. Big jumps first.

> *On screen:* Orange arrows hop across the top layer, each time moving to the neighbour closest to the query.

This is greedy search: look at the current node's neighbours, move to whichever is closer to the query, and repeat. On the top layer, each hop covers a big distance, quickly reaching the right region.

**[04:35]** No closer neighbour? Drop down a layer and keep refining.

> *On screen:* When no neighbour is closer, a dashed arrow drops to Layer 1 and the hopping continues with shorter steps.

When greedy search can't improve on a layer, it has found a local best there. It drops to the same node on the layer below, which has more nodes and shorter links, and continues refining. This repeats until it reaches layer 0.

### Layer 0: beam search with ef_search

**[04:41]** At the bottom, keep a list of the ef_search best candidates — here 5.

> *On screen:* On Layer 0, evaluated nodes light up and the 5 best so far turn green, next to the note 'ef_search = 5'.

On the bottom layer, HNSW switches from one greedy path to a beam search: it keeps a list of the ef_search best candidates found so far and keeps expanding them. A wider list means it explores more and is less likely to miss a neighbour. Here ef_search = 5 so it's visible; in practice it's often 100 or more, and must be at least K.

**[04:46]** Return the top K = 3, after touching only 13 of 34 nodes.

> *On screen:* The three best nodes get circled, and 'visited 13 of 34 → return top K = 3' appears.

The search returns the top K = 3 from its candidate list, after evaluating only 13 of the 34 nodes. The other 21 were never compared to the query. That fraction shrinks dramatically as the collection grows.

**[04:50]** In a real index (1M vectors), that's a few hundred distance checks instead of a million.

> *On screen:* The result stays on screen while the caption gives the real-scale picture.

Because the layers give roughly logarithmic navigation, a well-built HNSW index over a million vectors typically needs only hundreds to a few thousand distance calculations per query, instead of a million. That is the difference between milliseconds and seconds.

### ef_search: the recall ↔ latency knob

**[04:56]** Bigger ef_search → higher recall, slower queries. Start at 100 and measure.

> *On screen:* Bars grow for ef = 50 / 100 / 200: recall 92% / 96% / 99%, latency 10 / 20 / 40 ms, with a note that the numbers are illustrative.

ef_search is a per-query setting: raising it explores more candidates, which raises recall and latency together. The numbers here are illustrative; the real curve depends on your data, M and hardware. A practical approach is to start around 100, then measure recall@K against exact search and adjust.

### The three knobs (this project's config)

**[05:02]** ef_construction shapes the graph once; ef_search is the one you tune per query.

> *On screen:* Three cards pop in: M = 16, ef_construction = 256, ef_search = 100 (this project's config.py).

M and ef_construction are fixed when the index is built: ef_construction is the candidate-list size used while inserting, so higher values build a better graph more slowly. Changing either means rebuilding. ef_search can change on every query, so it is the knob you tune day to day. Rule: ef_search ≥ K.

### Key takeaways  `[05:08]`

- HNSW = layered graph: sparse highways on top
- Greedy hops down the layers toward the query
- Layer 0 beam search keeps ef_search candidates
- M, ef_construction, ef_search trade recall vs speed

---

## Chapter 5 — IVF: the Inverted File Index

**Starts at 05:20** · length 01:33 · source `05-ivf` · hook: *"How do you search high-dimensional data for similarity?"*

**What you'll learn.** IVF (Inverted File index) is a second ANN idea. It clusters the vectors with k-means, then searches only the clusters closest to the query. It builds on Chapters 3–4; the first three scenes are a short recap of embeddings and brute force, so it also works on its own. Watch for the 'missed neighbour' scene: it shows exactly why the nprobe setting matters.

### Every document = a vector = a point

**[05:26]** Embeddings turn text into vectors. Similar meaning → nearby points.

> *On screen:* About 110 grey points pop into a dashed frame, with a note that real vectors have 384–1,536 dimensions.

Recap from Chapter 1: each document is a vector, drawn here as a point in 2-D so you can see it. Similar documents are close together, and they naturally form groups. IVF uses exactly those groups.

### Brute force: compare with everything

**[05:33]** Brute force checks every vector. Fine for 100… painful for 100 million.

> *On screen:* A red query appears and thin lines shoot to every point, next to '1 query × 100,000,000 vectors × 768 dims = way too slow'.

Recap from Chapter 3: brute force compares the query with every vector. At 100 million vectors that is far too much work for one query. We need an index that skips most of the data.

**[05:37]** HNSW is the most popular fix. But IVF is another cool idea…

> *On screen:* The brute-force lines fade away.

HNSW (Chapter 4) is the most widely used ANN index, but it's not the only design. IVF takes a different approach: instead of a graph to navigate, it divides the space into regions and searches only the regions closest to the query.

### Step 1: cluster the space (k-means)

**[05:42]** Drop k random centroids. Each vector joins its nearest centroid.

> *On screen:* Six grey diamond centroids pop in at rough positions, then every point takes the colour of its nearest centroid.

This is k-means clustering, the training step of IVF. Start with k centroids (cluster centres), then assign every vector to its nearest one. The first assignment is rough because the starting centroids are only guesses.

**[05:44]** Move each centroid to the middle of its group. Repeat.

> *On screen:* Each centroid slides to the middle of its coloured group, the points recolour, and this repeats a few times.

Each centroid moves to the average position of the points assigned to it, then points are reassigned to whichever centroid is now nearest. Repeating these two steps makes the clusters settle. This is exactly the k-means algorithm.

**[05:51]** Converged: 6 clusters. In real indexes this is nlist — often 1,024 or more.

> *On screen:* The clusters settle and labels C1–C6 appear above the centroids.

The centroids have stopped moving: the clustering has converged. The number of clusters is the IVF setting nlist. Real indexes use hundreds to thousands, often around √N; here it's 6 so you can see it.

### Step 2: an inverted list per centroid

**[05:56]** Each vector is filed in its centroid's list — like a library shelf.

> *On screen:* Dashed ellipses outline each cluster, and an 'inverted list' panel lists C1 → [v1, v2, v3, …] 18 for every cluster.

Each vector is stored in the list of its nearest centroid. This is the 'inverted file': a lookup from centroid to the vectors filed under it, like books on library shelves by topic. Here the lists hold 17–19 vectors each.

### Step 3: query → nearest centroids only

**[06:01]** Compare the query with just 6 centroids — not every vector.

> *On screen:* A red query appears and dashed arrows draw to all 6 centroids.

At query time, IVF first compares the query with the centroids only, which is 6 comparisons here (1,024 for a real index), not every vector. That ranks the clusters by how promising they are.

**[06:04]** nprobe = 1: open only the closest list.

> *On screen:* All but the nearest cluster fade to grey, along with their lists.

nprobe is how many of the closest lists to open and scan. With nprobe = 1, only the single nearest cluster's vectors are compared with the query. Everything else is skipped.

**[06:07]** Scanned 18 of 109 vectors and got a top 3. Fast!

> *On screen:* Lines scan the 18 vectors in the open cluster, and the top 3 get red circles.

Only 18 of the 109 vectors were compared, so the search is much cheaper than brute force. The top 3 found are the best within that one cluster.

**[06:10]** But the true nearest neighbour sits just across the border — in a list we never opened.

> *On screen:* An orange dashed ring marks a green point just across the cluster border, labelled 'missed!'.

The query sits near the edge of its cluster, and its true nearest neighbour belongs to the neighbouring cluster, which wasn't opened. This is the main weakness of IVF: neighbours across a border are invisible unless you open that list too.

### nprobe: the recall ↔ speed knob

**[06:16]** nprobe = 2: open the two closest lists.

> *On screen:* A second dashed arrow draws to the next-nearest centroid and its cluster lights up again.

Raising nprobe to 2 opens the two closest lists. The extra cluster costs another batch of comparisons, but it covers the area just across the border, where missed neighbours tend to be.

**[06:20]** Now the real nearest neighbour is found — after scanning 37 of 109.

> *On screen:* Scan lines sweep both clusters and the top-3 circles update to include the border point.

Now the true nearest neighbour is found, after scanning 37 of 109 vectors. That is still about a third of the data, and the savings grow enormously on large collections.

**[06:24]** Higher nprobe → better recall, more work. Lower → faster, may miss.

> *On screen:* The nprobe = 2 result stays on screen while the caption states the trade-off.

nprobe is IVF's main recall-versus-speed knob, much like ef_search in HNSW. Higher nprobe scans more lists, so recall goes up but each query costs more. The right value is found by measuring recall against exact search on your own data.

### At real scale

**[06:29]** Query 1,024 centroids + 8 lists instead of a million vectors.

> *On screen:* Two boxes appear: '1,000,000 vectors, nlist = 1,024 lists (~1,000 vectors each)' → 'nprobe = 8 → scan ≈ 8,000 vectors, < 1% of the data'.

At real scale, a query compares itself with 1,024 centroids, then scans 8 lists of about 1,000 vectors each, roughly 9,000 comparisons instead of 1,000,000. Each list holds about N / nlist vectors, so work per query is about nlist + nprobe × N / nlist.

**[06:34]** IVF needs a training step (k-means) before indexing — e.g. the Faiss engine in OpenSearch.

> *On screen:* A yellow box adds 'IVF-PQ bonus: also compress each vector into a short code → far less memory'.

IVF has to be trained (k-means) on a sample of your data before vectors can be added, unlike HNSW. In OpenSearch this is done with the Faiss engine. IVF-PQ adds product quantization, which stores each vector as a short code to cut memory sharply at some cost in precision (see Chapter 6).

### Key takeaways  `[06:40]`

- IVF clusters vectors with k-means (nlist centroids)
- Each vector lives in its centroid's inverted list
- A query scans only the nprobe closest lists
- nprobe trades recall for speed — border points can be missed

---

## Chapter 6 — Quantization: cheaper vectors

**Starts at 06:53** · length 01:11 · source `06-quantization` · hook: *"1 million vectors take 3 GB of RAM. Can we get that to 96 MB?"*

**What you'll learn.** Vectors take a lot of memory: a million 768-number vectors need about 3 GB in FP32. This chapter shrinks them step by step (FP16 → INT8 → binary), then shows how a two-pass search (search the binary codes, then re-score with full precision) recovers the lost accuracy. It finishes with storage tiers for cost control. It builds on Chapters 3–4.

### FP32: every number costs 4 bytes

**[07:00]** Each dimension is a 32-bit float. That adds up fast.

> *On screen:* A row of 8 violet number cells (the first 8 of 768) appears, with '768 numbers × 4 bytes = 3,072 bytes per vector' below.

By default, each dimension is stored as a 32-bit float (FP32), which takes 4 bytes. A 768-dimension embedding therefore takes 3,072 bytes. That sounds tiny, but it is multiplied by every document you store.

**[07:04]** One million of them: about 3 GB of RAM, just for the vectors.

> *On screen:* An FP32 bar labelled '3,072 MB' fills the chart 'RAM for 1,000,000 vectors'.

One million vectors × 3,072 bytes ≈ 3 GB, for the raw vectors alone. HNSW graph links come on top of that. Fast vector search wants all of this in RAM, so memory quickly becomes the main cost.

### FP16: half the bytes

**[07:10]** 16-bit floats keep almost all the precision.

> *On screen:* The cells turn blue, the text changes to '× 2 bytes = 1,536 bytes', and an FP16 bar shrinks to half: '1,536 MB, < 0.5% recall loss'.

FP16 (half precision) stores each number in 2 bytes. Embedding values are small and don't need full float precision, so search quality barely changes. The docs cite under 0.5% recall loss for half the memory.

### INT8: squeeze [-1, 1] into [-128, 127]

**[07:16]** Store one byte per number instead of four.

> *On screen:* The cells change to whole numbers (0.234 → 30, -0.789 → -100) and an INT8 bar shrinks to a quarter: '768 MB, ≈ 1% recall loss'.

INT8 maps each value from the range [-1, 1] to a whole number in [-128, 127] (here round(value × 127)) and stores it in 1 byte, 4× smaller than FP32. Rounding loses a little detail: about 1% recall in the docs' figures. Real systems often calibrate the range from your data instead of assuming [-1, 1].

### Binary: just one bit per number

**[07:22]** 3,072 MB → 96 MB. But a bare sign bit loses detail…

> *On screen:* The cells flip to 1s and 0s (value ≥ 0 → 1, < 0 → 0) and the Binary bar shrinks to a sliver: '96 MB, 32× smaller!'.

Binary quantization keeps only the sign of each number: 1 bit instead of 32, so 768 dimensions fit in 96 bytes and a million vectors fit in 96 MB. But a sign bit throws away how big each value was, so binary search alone ranks results more roughly.

### Binary search + full-precision rescoring

**[07:28]** Step 1: search the tiny binary codes — rough but blazing fast.

> *On screen:* A grid of binary codes appears and a fast scan picks out a handful of candidates, labelled 'Hamming distance: super cheap'.

With binary codes, distance is the Hamming distance: count the bits that differ. Computers do this very quickly with a few CPU instructions. This pass is rough but fast, so it is used only to find candidates, not the final answer.

**[07:31]** Step 2: re-score just those few with the original FP32 vectors.

> *On screen:* The candidates move into an 'oversample' group of 'top k × 5 = 15', then into 'rescore FP32'.

Oversampling asks the rough pass for more candidates than needed: 5 × k, so 15 for k = 3. Those few are then re-scored with their original full-precision vectors, which can sit on disk because only 15 are fetched. This undoes most of the ranking errors from the binary pass.

**[07:35]** Cheap first pass, accurate second pass: the best of both.

> *On screen:* The 'final top k = 3' appears, and a box reads '≈ 97% less memory, < 2% recall loss'.

This two-pass design keeps only the compact binary codes in RAM and uses full precision for a tiny number of candidates. Per the docs: about 97% less memory with under 2% recall loss. It's the same 'cheap first pass, precise second pass' idea as two-stage retrieval in the Embeddings course.

### Storage tiers: pick your price point

**[07:39]** Hot data in memory; huge, cold collections on disk or S3.

> *On screen:* Three staircase cards appear: In-memory HNSW $$$, Disk-based $$ (binary in RAM, full vectors on disk, 32× less RAM), S3 Vectors $.

Storage tiers trade speed for cost. In-memory HNSW is fastest and most expensive. Disk-based mode (OpenSearch 2.17+) keeps binary codes in RAM and full vectors on disk for rescoring, using about 32× less RAM. Object storage such as S3 Vectors is cheapest and slowest, suited to huge, rarely queried collections.

**[07:43]** Minimal-cost preset: disk mode + 32× binary + HNSW m = 16, ef_construction = 300.

> *On screen:* The tiers stay on screen while the minimal-cost preset caption appears.

The slide deck's minimal-cost preset combines disk mode, 32× binary compression and HNSW with m = 16 and ef_construction = 300. As always, validate recall on your own queries before and after switching. Compression that is invisible on one dataset can hurt on another.

### Key takeaways  `[07:49]`

- FP32 → FP16 → INT8 → binary: 4 → 2 → 1 → 1/8 bytes
- 1M × 768 dims: 3,072 MB → 96 MB
- Binary search + FP32 rescoring keeps recall high
- Tiers: RAM ($$$) → disk ($$) → S3 Vectors ($)

---

## Chapter 7 — Keyword search: TF-IDF & BM25

**Starts at 08:05** · length 01:17 · source `07-keyword-bm25` · hook: *"Before AI, how did search engines rank documents?"*

**What you'll learn.** This chapter shows how classic keyword search ranks documents, before any AI is involved: the inverted index, TF, IDF, TF-IDF and then BM25, the ranking function behind OpenSearch's default text search. It needs no earlier chapter. It matters because keyword search is still the best tool for exact tokens (codes, SKUs, names), and it is one half of the hybrid search covered in Chapter 10.

### The inverted index: term → documents

**[08:11]** Like the index at the back of a book: every word points to its pages.

> *On screen:* Three movie documents appear on the left, a dashed "index once" arrow draws across, and the term table builds row by row: matrix → [D1], sci-fi → [D1, D5], action → [D1, D3], space → [D5].

An inverted index flips the data around. Instead of storing "document → words", it stores "word → list of documents" (a posting list). It is built once at indexing time, so a search never has to read the documents themselves. It only reads the posting lists of the words in the query.

**[08:18]** Look up only the query's words. D1 has both terms → it ranks first.

> *On screen:* A query box "sci-fi action" appears and red arrows highlight just the sci-fi and action rows of the term table.

At query time the engine fetches the posting lists for the query terms and combines them. D1 is in both lists (sci-fi and action), D5 and D3 are each in only one, so D1 ranks first. This is why keyword search takes milliseconds even on millions of documents: the work depends on the query's words, not on the size of the collection.

### TF: how often does the term appear here?

**[08:25]** Term frequency: apple is 2 of the 3 words.

> *On screen:* The document "apple apple orange" appears word by word, and the formula TF(apple) = 2 / 3 = 0.667 is typed out in red.

Term frequency (TF) measures how much a document is about a word: the more often the word appears, the more relevant the document probably is. Here "apple" is 2 of 3 words, so TF = 0.667. Raw TF has a weakness that BM25 fixes later: repeating a word 100 times would keep raising the score.

### IDF: rare words carry more signal

**[08:30]** Inverse document frequency: the fewer docs contain it, the higher it scores.

> *On screen:* A grid of 100 document cells fades in, the 20 cells that contain "apple" turn red, and the label IDF = log(100/20) = 0.699 appears.

Inverse document frequency (IDF) rewards rare words. A word found in only a few documents is a strong clue about which document you want. With 100 documents and 20 containing "apple", IDF = log10(100/20) = log10(5) = 0.699. The guides use base-10 logs; BM25 implementations use a slightly different smoothed IDF, but the idea is the same.

**[08:34]** "the" is everywhere, so it is almost worthless for ranking.

> *On screen:* The grid greys out except two cells, and a second label shows "the": in 98 docs, IDF = log(100/98) = 0.009.

"the" appears in 98 of 100 documents, so it tells you almost nothing: log10(100/98) ≈ 0.009, close to zero. That is how IDF automatically down-weights stop words without needing a list of them. A word that appears in every document gets an IDF of exactly 0.

**[08:38]** Multiply them: frequent here AND rare overall = relevant.

> *On screen:* The TF and IDF values come together into one line: TF-IDF = 0.667 × 0.699 = 0.466.

TF-IDF multiplies the two signals: a term scores high only if it is frequent in this document AND rare across the collection. 0.667 × 0.699 = 0.466 for "apple" here. A document's score for a query is the sum of TF-IDF over the query's terms.

### BM25: TF-IDF, refined

**[08:45]** Two knobs: k1 controls TF saturation, b controls length normalisation.

> *On screen:* The BM25 formula is typed out piece by piece: score(q, d) = Σ IDF(t) · tf·(k1+1) / (tf + k1·(1 − b + b·|d|/avgdl)), then two boxes explain k1 = 1.2 and b = 0.75.

BM25 keeps the TF × IDF idea but adds two knobs. k1 (default 1.2) controls how quickly extra repeats stop helping. b (default 0.75) controls how much long documents are penalised, by comparing the document length |d| with the average length avgdl. With b = 0 length is ignored; with b = 1 it is fully normalised. BM25 scores are unbounded: they are not limited to 0–1, which matters in Chapter 10.

### TF saturation: the 10th 'apple' adds little

**[08:51]** Plain TF keeps growing: keyword stuffing would win.

> *On screen:* A plot draws a grey dashed line labelled "raw TF: grows forever", rising straight up as tf increases.

With raw TF, a document that repeats "apple" 50 times scores 25 times higher than one that says it twice. That rewards keyword stuffing rather than relevance. A good ranking function should treat the 1st and 2nd mention as important and the 20th as almost irrelevant.

**[08:53]** BM25 bends the curve: it levels off near k1 + 1.

> *On screen:* A blue BM25 curve sweeps across the same plot and flattens toward a dashed ceiling labelled k1 + 1 = 2.2.

In BM25 the TF part is tf·(k1+1) / (tf + k1·…), which can never exceed k1 + 1. With k1 = 1.2 the ceiling is 2.2. For an average-length document, tf = 1 gives 1.0, tf = 2 gives about 1.38, and tf = 10 gives about 1.96: the 10th mention adds very little. This is called TF saturation.

**[08:56]** The same count in a twice-as-long document is worth less.

> *On screen:* A second, orange curve for a document twice the average length draws in below the blue one.

This is the b parameter at work. For a document twice as long as average, the denominator grows, so the same count of "apple" is worth less: the word is a smaller share of a longer text. With b = 0.75 and tf = 1, the score drops from 1.0 to about 0.71. Long documents no longer win just because they contain more words.

### Fast and exact… but blind to meaning

**[09:01]** Great for exact tokens — and fully explainable.

> *On screen:* A query box ERR-4032 links to a document containing ERR-4032 with a match tick, and the note "exact codes, SKUs, names like 'iPhone 15 Pro' · ~1–5 ms" appears.

Keyword search is excellent when the user types the exact token that appears in the document: error codes, product SKUs, part numbers, names. It is fast (milliseconds) and explainable: you can see exactly which terms matched and why the score is what it is. Embeddings often blur such tokens (Chapter 9).

**[09:03]** But no shared word means no match: synonyms are invisible.

> *On screen:* A second pair shows "car" next to a document about a vehicle, joined by a red "no match" line: different words, same meaning.

The weakness: BM25 only counts shared words. A query for "car" scores 0 against a document that only says "vehicle" or "automobile", even though the meaning is identical. Sparse encoding (next chapter) and dense embeddings (Chapters 1–2) both exist to fix exactly this.

### Key takeaways  `[09:08]`

- Inverted index: each term → list of documents
- TF-IDF: frequent in this doc × rare overall
- BM25: TF saturates (k1 = 1.2), long docs penalised (b = 0.75)
- Exact and fast, but no synonyms or concepts

---

## Chapter 8 — Sparse encoding

**Starts at 09:22** · length 01:07 · source `08-sparse-encoding` · hook: *"Can keyword search learn synonyms and stay as fast as BM25?"*

**What you'll learn.** This chapter explains neural sparse encoding: keyword-style vectors whose term weights and extra related terms are predicted by a model. It builds on Chapter 7 (inverted index, term weights). It matters because it adds some meaning (synonyms) to keyword search while keeping its speed, low memory and explainability.

### A sparse vector: one slot per word

**[09:28]** Imagine a row with a slot for every word the model knows.

> *On screen:* A long row of tiny cells draws from "a" to "zebra", labelled "… 30,522 slots (the BERT vocabulary) …".

A sparse vector has one slot per word (token) in the model's vocabulary. For BERT-based models that is 30,522 slots. The value in each slot is how important that word is for the text. Compare this with a dense embedding, which has a few hundred to a few thousand slots that are all non-zero and have no direct word meaning.

**[09:32]** Almost every slot is zero — only ~1% light up.

> *On screen:* A handful of cells light up along the row while the rest stay empty.

For any one sentence, only a tiny fraction of the vocabulary is relevant, so roughly 1% of slots or fewer are non-zero. Storing all 30,522 numbers would waste space on zeros, which is why these vectors are called sparse.

**[09:36]** So we store only the non-zero entries: a small {term: weight} dictionary.

> *On screen:* The lit cells lift out of the row and fly between two large braces, forming a {term: weight} dictionary.

Instead of the full row we keep only the non-zero entries, for example {apple: 0.85, expensive: 0.72, phone: 0.68}. This is exactly the shape a search engine's inverted index already uses: term → (document, weight). So sparse vectors can be stored and searched with the same machinery as BM25.

### The neural trick: expansion

**[09:45]** The model adds related terms with weights — learned synonyms, still just keywords.

> *On screen:* The word "car" flows into a "neural sparse model (BERT-based)" box, and weighted bars come out: car 0.92, then dashed bars for automobile 0.8, vehicle 0.6 and driving 0.35.

The neural model does two things: it re-weights the words that are in the text, and it expands the text with related words that are not (dashed bars). A document about a "car" also gets entries for "automobile" and "vehicle", so a query using those words now matches. Real models (e.g. SPLADE-style or OpenSearch neural sparse models) learn these weights from data. Note: this project's own encoder is a hand-written synonym dictionary, not a learned model.

### Scoring: multiply the shared terms

**[09:52]** Only terms that appear on both sides count.

> *On screen:* Query terms (apple 0.85, expensive 0.72, phone 0.68) appear on the left and document terms on the right; green lines connect only the shared terms.

Scoring only looks at terms present in both the query and the document. "phone" in the query has no partner in the document, so it contributes nothing. Document terms that the query doesn't mention (products, price) also contribute nothing.

**[09:56]** A dot product over a handful of terms: tiny and fast.

> *On screen:* The products 0.85 × 0.78 = 0.663 and 0.72 × 0.54 = 0.389 appear on the connecting lines, and a green box sums them: score = 1.052.

The score is a dot product over the overlapping terms: Σ query_weight × doc_weight = 0.85×0.78 + 0.72×0.54 = 0.663 + 0.389 = 1.052. Because only a handful of terms overlap, this is a few multiplications, not hundreds or thousands as with dense vectors. Like BM25, the score is not limited to 0–1.

### Example: "apple headphones"

**[10:03]** Both say 'apple' — but the expanded terms tip it toward the brand.

> *On screen:* Two documents for the query "apple headphones" get score bars: Doc 1 "Apple products are expensive" grows to 7.45, Doc 2 "An apple a day keeps the doctor away" to 5.56.

Both documents contain the literal word "apple", so plain keyword matching can't tell them apart well. The model's expansion of "apple headphones" includes brand and electronics terms, which overlap with the first document but not the fruit one. That pushes Doc 1 ahead (7.45 vs 5.56, the example from the slide deck).

### Why it is cheap

**[10:11]** Keyword speed and explainability, with some semantic smarts.

> *On screen:* Four boxes appear: stored in the same Lucene inverted index as BM25; ≈ 10× smaller than dense vectors with no extra RAM for an HNSW graph; document-only mode; explainable matches.

Sparse vectors reuse the existing inverted index, so there is no separate vector graph to keep in memory. In document-only mode the model runs only at index time and the query is just tokenized, so queries stay as cheap as BM25. You can also inspect which terms matched. The "≈10× smaller than dense" figure is OpenSearch's claim from the slide deck; actual savings depend on the model and data.

### Key takeaways  `[10:15]`

- Sparse vector = {term: weight}, ~1% of 30,522 slots
- A neural model expands text with related terms
- Score = Σ query weight × doc weight on shared terms
- Runs on the inverted index: small, fast, explainable

---

## Chapter 9 — Why one method isn't enough

**Starts at 10:29** · length 00:59 · source `09-why-one-method-fails` · hook: *"Why does 'heart attack' miss 'myocardial infarction'?"*

**What you'll learn.** This chapter collects the typical failure cases of keyword search and of dense (semantic) search side by side. It builds on Chapters 1–2 (embeddings, similarity) and 7–8 (keyword and sparse search). It is the motivation for Chapter 10: each method fails on different queries, so combining them covers more.

### Keyword search: blind to synonyms

**[10:36]** Same meaning, zero overlapping words → BM25 scores it 0.

> *On screen:* Boxes for "heart attack" and "myocardial infarction" appear with a red line between them labelled "keyword match: 0 shared words".

These two phrases mean the same thing but share no word, so BM25 gives the document a score of exactly 0 for that query. This is the vocabulary mismatch problem, and it is very common in medical, legal and technical text where experts and users use different words.

**[10:39]** Semantic search sees they're neighbours in meaning space.

> *On screen:* Below, an "embedding space" area appears and the two phrases land as dots right next to each other.

An embedding model has learned from huge amounts of text that both phrases appear in the same contexts, so it places their vectors close together. Cosine similarity between them is high, and semantic search finds the document. This is the main strength of dense search.

### Semantic search: blurry on details

**[10:45]** Error codes look nearly identical to an embedding — it may return the wrong one.

> *On screen:* In an embedding-space sketch, ERR-4031, ERR-4032 and ERR-4033 sit almost on top of each other; on the right, keyword search returns ERR-4032 while dense search returns ERR-4031 ?!

To an embedding model, error codes that differ by one digit look almost identical: same format, same context. The nearest vector can easily be the wrong code. Keyword search treats "ERR-4032" as an exact token and finds it immediately. Any search over codes, SKUs or IDs needs an exact-match component.

**[10:49]** Numbers blur: embed('$500') ≈ embed('$5000') — 10× apart in price!

> *On screen:* Two dots labelled $500 and $5000 are drawn almost overlapping.

Embeddings capture what a text is about, not precise quantities. "$500" and "$5000" both mean "a price", so their vectors are close, even though one is ten times the other. Numbers, prices, dates and ratings should be stored as structured fields and filtered exactly (Chapter 11), not left to the vector.

**[10:53]** Negation is weak: 'not' barely moves the vector.

> *On screen:* Dots for "good movie" and "not a good movie" sit close together, labelled ≈ 0.85 similar.

One small word like "not" flips the meaning but changes the vector very little, because most of the words and the topic are the same. The 0.85 value is illustrative, but the effect is real: negation is a known weak spot of embeddings. Keyword search is no better here, it would match both.

### Both struggle with ambiguity

**[10:57]** One word, two meanings — you need context or filters to decide.

> *On screen:* A "python" box branches with two arrows to "the snake" and "the language", with a note: same for "Matrix", the movie or the math?

Ambiguous words trip up both methods. Keyword search matches every "python" document. A single embedding of the one-word query can't know which meaning you want. The fix is more context: a longer query, user context, or a filter (category = programming).

### Each method alone vs. combined

**[11:05]** Each method misses different things — so combining them wins.

> *On screen:* Four bars grow for NDCG@10 (labelled illustrative): keyword 0.72, sparse 0.74, dense 0.85, hybrid 0.91, and the hybrid bar is emphasised.

NDCG@10 is a ranking quality metric: it rewards putting the most relevant documents near the top of the first 10 results (1.0 = perfect). These four numbers are illustrative values from the project docs, not a measured benchmark. The pattern they show is typical in published evaluations: combining methods beats each one alone, because their errors don't overlap.

### Who handles what?

**[11:13]** That's why production search goes hybrid — keyword + semantic together.

> *On screen:* A "Who handles what?" table fills in row by row with ticks and crosses for Keyword, Semantic and Hybrid: synonyms/paraphrase, exact codes/SKUs/names, concepts ('things to do when bored'), and fast & explainable.

Keyword search wins on exact codes and is fast and explainable; semantic search wins on synonyms, paraphrases and concept queries such as "things to do when bored", where no keyword matches. Hybrid gets a tick in every row except speed and explainability, where it is only partial, since it runs two searches. Precise numbers are a separate problem for both, solved with filters (Chapter 11). Because the failure cases differ, production systems run both searches and merge the results, the topic of the next chapter.

### Key takeaways  `[11:18]`

- Keyword misses synonyms and concepts
- Semantic blurs exact codes, numbers and negation
- Ambiguous words need context or filters
- Hybrid search combines their strengths

---

## Chapter 10 — Hybrid Search: Fusing Scores

**Starts at 11:29** · length 01:44 · source `10-hybrid-search` · hook: *"BM25 says 12.7, cosine says 0.78. How do you add apples and oranges?"*

**What you'll learn.** This chapter shows how to merge keyword and semantic results into one ranking: why raw scores can't simply be added, how min-max normalization and weights fix it, why the harmonic mean penalises disagreement, and how Reciprocal Rank Fusion (RRF) avoids scores altogether. It builds on Chapters 7–9. It matters because almost every production search system today is hybrid.

### One query, two searches

**[11:36]** Run keyword and semantic search in parallel on the same query.

> *On screen:* The query "wireless noise cancelling headphones" splits with arrows into two lanes: Keyword (BM25) and Semantic (k-NN), each producing its own result list.

Hybrid search runs both searches for the same query, usually in parallel, so the total latency is close to the slower of the two rather than their sum. Each search returns its own ranked list with its own scores. The hard part is the next step: merging two lists into one.

**[11:39]** But look: 12.7 vs 0.78. The scores live on totally different scales.

> *On screen:* Each lane fills with three results: keyword gives Doc A 12.7, Doc C 8.1, Doc B 3.4; semantic gives Doc D 0.81, Doc B 0.78, Doc A 0.61, and the 12.7 and 0.78 boxes pulse.

The numbers are not comparable. Doc A's BM25 score of 12.7 is not "16 times better" than Doc B's cosine of 0.78; they are measured on completely different scales. Notice also that the two lists disagree: Doc A is #1 for keyword but #3 for semantic, and Doc D only appears in the semantic list. Merging them needs a common scale, or a method that ignores the raw values.

### Problem: apples + oranges

**[11:44]** Each engine scores on its own ruler: BM25 is unbounded, cosine stays within 0–1.

> *On screen:* Three rulers draw out, BM25 (0 to unbounded, ≈25), neural sparse (0 to ≈5) and dense cosine (0 to 1); a marker slides along each to 12.7, 3.45 and 0.78.

BM25 has no upper limit; its range depends on the query length and the collection. Neural sparse scores are also unbounded dot products. Cosine similarity is bounded between -1 and 1, and in practice text embeddings mostly land between 0 and 1. Each engine speaks a different unit.

**[11:51]** Add them raw and the biggest scale wins: BM25 decides almost everything.

> *On screen:* A stacked "naive sum" bar builds from the three raw scores: 12.7 + 3.45 + 0.78 = 16.93, with the note "cosine's vote: under 5%".

If you just add raw scores, the engine with the biggest numbers dominates: 0.78 / 16.93 is under 5%, so the semantic search barely affects the final ranking. The search behaves almost exactly like keyword-only search. This is a common bug in home-grown hybrid search (for example, a plain bool/should query that adds scores).

### Fix 1: min-max normalize each list

**[11:58]** Raw scores from one engine: [0.12, 0.82, 0.45, 0.03, 0.67].

> *On screen:* The formula norm = (s − min) / (max − min) is typed out and five raw score bars appear: 0.12, 0.82, 0.45, 0.03, 0.67, with min and max marked.

Min-max normalization rescales each result list separately so its lowest score becomes 0 and its highest becomes 1. Here min = 0.03 and max = 0.82, so the range is 0.79. It is applied per list, per query, so each engine's scores end up on the same 0–1 scale.

**[12:02]** After: [0.11, 1, 0.53, 0, 0.81]. Every list now spans exactly 0 → 1.

> *On screen:* The bars resize to [0.11, 1, 0.53, 0, 0.81].

Worked through: (0.12 − 0.03)/0.79 = 0.11, (0.82 − 0.03)/0.79 = 1, (0.45 − 0.03)/0.79 = 0.53, (0.03 − 0.03)/0.79 = 0, (0.67 − 0.03)/0.79 = 0.81. The order is unchanged; only the scale changes. One pitfall: min-max always stretches to 0–1, even when every result in the list is weak, so a poor list can look as confident as a good one. OpenSearch also offers L2 normalization as an alternative.

### Fix 2: combine with weights

**[12:09]** Normalized scores, each multiplied by a weight: 0.3, 0.3 and 0.4.

> *On screen:* Three normalized score bars (keyword 0.8, sparse 0.6, dense 0.9) appear, each with its weight 0.3, 0.3 and 0.4.

Once all scores are on 0–1, you can decide how much each engine should count. The weights should add up to 1 so the result also stays on 0–1. Here dense gets 0.4 and each keyword-style engine 0.3.

**[12:14]** Add the weighted parts: 0.3·0.8 + 0.3·0.6 + 0.4·0.9 = 0.78.

> *On screen:* The weighted parts slide into one stacked bar: hybrid = 0.24 + 0.18 + 0.36 = 0.78.

The weighted arithmetic mean: 0.3·0.8 + 0.3·0.6 + 0.4·0.9 = 0.24 + 0.18 + 0.36 = 0.78. This is the most common combination method and the default in OpenSearch's normalization processor. Its weakness: a document that one engine loves and another hates can still score well.

### Harmonic mean punishes disagreement

**[12:20]** The engines disagree: sparse thinks this document is barely relevant.

> *On screen:* A new example shows three scores where sparse is very low: keyword 0.8, sparse 0.1, dense 0.9.

Sometimes the engines disagree strongly. A score of 0.1 from one engine is a warning that this document may not really match. Whether you want that warning to count depends on the use case.

**[12:26]** Harmonic gives 0.24 instead of 0.60: one weak signal drags the result down.

> *On screen:* Two bars compare the results: arithmetic 0.60 and harmonic 3 / (1/0.8 + 1/0.1 + 1/0.9) ≈ 0.24.

The plain arithmetic mean is (0.8 + 0.1 + 0.9)/3 = 0.60. The harmonic mean is 3 / (1.25 + 10 + 1.11) = 3 / 12.36 ≈ 0.24: the low score dominates. Use the harmonic mean when you only want documents that all engines agree on. (The project guide states 0.16 for this example, which is a calculation error; 0.24 is correct. The geometric mean would be ≈ 0.42.)

### Or skip scores: Reciprocal Rank Fusion

**[12:33]** Throw away the scores, keep only positions. Each list votes 1 / (60 + rank).

> *On screen:* Two rank lists appear, Keyword (#1 Doc A, #2 Doc C, #3 Doc B) and Semantic (#1 Doc D, #2 Doc B, #3 Doc A), next to the formula RRF(d) = Σ 1 / (60 + rank).

Reciprocal Rank Fusion ignores the scores completely and uses only each document's position in each list. Each list gives a document 1/(k + rank) points, with k = 60 as the usual constant, and the points are summed across lists. Because ranks are always 1, 2, 3…, there is nothing to normalize.

**[12:40]** Doc A is #1 and #3: 1/61 + 1/63 ≈ 0.0323, the top fused result.

> *On screen:* Doc A is highlighted in both lists, arrows carry its two votes to a fused list, and the fused ranking builds up with Doc A on top.

Doc A: 1/(60+1) + 1/(60+3) = 0.01639 + 0.01587 ≈ 0.0323. Doc B, ranked #3 and #2: 1/63 + 1/62 ≈ 0.0320. Doc D, only in one list at #1: 1/61 ≈ 0.0164. Appearing high in both lists beats being #1 in just one.

**[12:44]** No normalization needed, which makes RRF a very robust default.

> *On screen:* A note appears: "k = 60 softens the gap between top ranks · built into OpenSearch 2.19+".

The constant k controls how much the top positions dominate. With k = 60, rank 1 (1/61) is worth only slightly more than rank 5 (1/65), so a document has to do well in several lists to win. RRF is robust because it doesn't care that BM25 scores are unbounded. OpenSearch supports it from version 2.19. The trade-off: it throws away how much better the #1 result was than #2.

### Tune the weights to the use case

**[12:49]** Shopping: keyword-heavy, so 'iPhone 15 Pro' matches exactly. 0.4 / 0.3 / 0.3.

> *On screen:* Three weight sliders (keyword, sparse, dense) slide to the e-commerce preset 0.4 / 0.3 / 0.3.

For shopping, users often type exact product names and model numbers, so keyword gets the largest weight (0.4). These presets are starting points from the project docs, not universal truths.

**[12:54]** Support questions: meaning-heavy, so dense gets 0.5. Measure and tune.

> *On screen:* The sliders move to the customer-support preset 0.2 / 0.3 / 0.5, with a note about OpenSearch's hybrid query and normalization processor.

Support questions are usually phrased in the user's own words ("my app keeps logging me out"), so meaning matters most and dense gets 0.5. In OpenSearch this is configured with a hybrid query plus a search pipeline whose normalization-processor picks min_max or l2 and then an arithmetic, geometric or harmonic mean with weights. The right weights come from evaluating on real queries with metrics like NDCG.

### Key takeaways  `[13:00]`

- Run keyword + semantic search in parallel
- Raw scores use different scales: normalize first
- Min-max, then a weighted (or harmonic) mean
- RRF fuses ranks instead: Σ 1 / (60 + rank)

---

## Chapter 11 — Filtered Vector Search

**Starts at 13:13** · length 01:32 · source `11-filtering` · hook: *""Sci-fi rated above 8": filter first, or search first?"*

**What you'll learn.** This chapter covers combining vector search with hard constraints such as price, rating or date: post-filtering (search, then filter) versus pre-filtering (filter, then search), and how to write efficient filters in OpenSearch and Qdrant. It builds on Chapter 3 (k-NN) and Chapter 9 (numbers blur in embeddings). It matters because almost every real query mixes meaning with rules.

### Real queries = meaning + constraints

**[13:20]** 'laptop' is meaning, so it goes in the vector. '$500' is a hard rule: a filter.

> *On screen:* The query "laptop under $500" splits into two boxes: "meaning → vector [0.12, -0.40, 0.88, …]" and "constraint → filter price ≤ 500".

A good search system separates the fuzzy part of a query from the exact part. "laptop" is about meaning, so it belongs in the embedding. "under $500" is a hard rule that must hold for every result, so it belongs in a structured filter on a price field. Asking an embedding to respect a price would not work reliably (Chapter 9).

**[13:25]** So which comes first: the nearest-neighbour search, or the filter?

> *On screen:* The two boxes stay on screen with a question between them: which runs first?

There are two orders: run k-NN first and then drop the results that break the rule (post-filtering), or restrict the candidates first and run k-NN only inside them (pre-filtering). Both return results that satisfy the filter, but they differ a lot in how many results you get and how much work is done.

### Post-filtering: search first, filter after

**[13:31]** Step 1: find the 10 nearest neighbours, ignoring price completely.

> *On screen:* A scatter of laptop dots appears around a red query point, and a ring captures the 10 nearest dots, with step 1 "k-NN: top 10 nearest" on the right.

Post-filtering starts with an ordinary vector search: find the top 10 by similarity, ignoring price completely. This is simple, and any vector index can do it.

**[13:36]** Step 2: apply the filter. Most neighbours cost too much: only 2 of 10 survive.

> *On screen:* Most dots inside the ring get × marks for costing over $500; the box reads "asked for 10, got only 2".

Now the filter removes every result above $500. Only 2 of the 10 nearest laptops are cheap enough, so the user gets 2 results even though many more cheap laptops exist further away. Post-filtering returns fewer than k results whenever the filter is selective. A common workaround is to fetch many more results (e.g. 100) before filtering, which costs extra work.

**[13:41]** With a very strict filter, post-filtering can return nothing at all.

> *On screen:* A dashed box appears: strict filter (e.g. rating ≥ 9) → 0 results!

With a very strict filter, it is quite possible that none of the top-k nearest neighbours pass, and the user sees an empty page. With contradictory filters (rating ≥ 9 AND rating ≤ 7) the result is always empty, whatever the order.

### Pre-filtering: filter first, then k-NN

**[13:46]** Step 1: the filter narrows 90 vectors to 27 candidates that fit the budget.

> *On screen:* The scatter resets: dots over budget fade out, leaving the 27 cheap ones bright, with step 1 "keep price ≤ $500".

Pre-filtering applies the rule first. Of the 90 vectors in this sketch, 27 fit the budget. Only these 27 are candidates for the similarity search.

**[13:54]** Step 2: search only inside the survivors. You always get a full top 10, if it exists.

> *On screen:* Lines reach from the query to its nearest surviving dots, and the box reads "asked for 10, got 10".

The k-NN search now runs only among the valid candidates, so if at least 10 matching laptops exist, you get a full top 10. Every result is both relevant and within budget.

**[14:00]** And when the filter is very selective, there is far less to search: faster too.

> *On screen:* The pre-filter result stays on screen, highlighting how few vectors remain to be searched.

When the filter removes most of the collection, there is far less to search, so pre-filtering can also be faster. Real engines do this efficiently inside the index: for example, they skip non-matching nodes while walking the HNSW graph, or switch to exact search when very few candidates are left.

### Which one when?

**[14:06]** Rule of thumb: the stricter the filter, the more you want pre-filtering.

> *On screen:* Two comparison cards appear: post-filter (simple to bolt on, fine for loose filters, can return fewer than k or nothing) and pre-filter (always k results if they exist, best for selective filters, less work per query, needs engine support).

Post-filtering is fine when the filter keeps most documents (e.g. "in stock" when 95% are in stock). Pre-filtering, or filtering during search, is what you want when the filter is selective. Most modern vector databases support it natively.

### In OpenSearch: put the filter inside knn

**[14:13]** Put the filter inside the knn clause, so the engine filters while it searches.

> *On screen:* An OpenSearch query is typed out with the filter block inside "knn" highlighted in green: "filter inside knn = efficient filtering (Lucene / Faiss engines)".

In OpenSearch, efficient filtering means putting the filter clause inside the knn query itself (supported with the Lucene and Faiss engines). The engine then applies the filter while it searches, so you get k results that all match. The project README shows a different structure, so this is worth checking in your own queries.

**[14:18]** A bool filter wrapped around knn acts like post-filtering. Qdrant: use query_filter.

> *On screen:* A red note appears: "bool filter outside knn ≈ post-filtering".

If you wrap a knn query inside a bool query and put the filter next to it, OpenSearch first finds the k nearest neighbours and then filters them, which behaves like post-filtering and can return fewer than k results. Qdrant handles this natively: pass the condition as query_filter in the search request and it filters during the search.

### Keep numbers out of the embedding

**[14:23]** Embeddings blur numbers: '$500' and '$5000' land almost on top of each other.

> *On screen:* Boxes embed("$500") and embed("$5000") appear with a big red ≈ between them.

This repeats the lesson from Chapter 9: embedding models do not preserve the size of numbers. A filter like "under $500" can never be enforced by vector similarity alone.

**[14:28]** Store prices, ratings and dates as fields, and filter on them exactly.

> *On screen:* A document card for The Matrix builds up: a violet "vector: plot & meaning" bar, then four teal field rows: genre sci-fi, rating 8.7, year 1999, price $9.99.

Store the text meaning in the vector and every number, date or category as a structured field next to it. Then index those fields (keyword, numeric, datetime) so filters are fast, and use exact filters for the hard rules. This works the same way in OpenSearch (fields in the document) and Qdrant (payload).

### Key takeaways  `[14:33]`

- Queries mix meaning (vector) with rules (filters)
- Post-filter: k-NN first, may return fewer than k
- Pre-filter: narrow first, then k-NN: full, fast results
- OpenSearch: put the filter inside the knn clause

---

## Chapter 12 — RAG: Search That Answers

**Starts at 14:46** · length 01:27 · source `12-rag-bedrock` · hook: *"How does a chatbot answer questions about a 35-page PDF it has never seen?"*

**What you'll learn.** This chapter puts everything together into Retrieval-Augmented Generation (RAG): chunk a PDF, embed the chunks, store them in a vector database, retrieve the best chunks for a question, and let Claude answer from them with page citations. It builds on Chapters 1–3 (embeddings, cosine, k-NN). It matters because RAG is how chatbots answer questions about your own documents without retraining the model.

### Step 1: chop the document into chunks

**[14:54]** Split the PDF into small chunks: 35 pages become 38 searchable pieces.

> *On screen:* NVIDIA.pdf (35 pages) appears and splits into a grid of chunk cards, labelled "38 chunks, ~500 chars each".

Embedding models and prompts work best with focused pieces of text, so the PDF is cut into chunks. In this project ingest_pdf.py turns the 35-page NVIDIA PDF into 38 chunks of about 500 characters each. Note: the code accepts an overlap parameter but never uses it, so these chunks don't actually overlap (see the pitfall at the end).

### Step 2: embed every chunk, store the vectors

**[15:01]** An embedding model turns each chunk into a 1,024-dimension vector.

> *On screen:* Copies of the chunks flow into a "Titan Text Embeddings v2" box, vector chips like [0.021, -0.113, 0.087, …] come out, labelled "1,024 numbers each".

Each chunk is sent to Amazon Titan Text Embeddings v2 on Bedrock, which returns a 1,024-dimension vector (v2 can also output 256 or 512). Chunks about similar topics get vectors that point in similar directions. This happens once, at indexing time.

**[15:06]** The vectors, plus text and page numbers, go into the vector database.

> *On screen:* The vector chips drop into a Qdrant cylinder together with their text and page numbers.

The vector database stores each vector with a payload: the chunk text, the source file and the page number. The text is needed later to build the prompt, and the page number to cite sources. The project uses a Qdrant collection with cosine distance.

### Step 3: embed the question the same way

**[15:13]** The question gets embedded by the same model, then searched in Qdrant.

> *On screen:* The question "What drove data center growth?" flows through the same Titan v2 box (labelled "same model!") into a query vector that points at Qdrant.

At question time, the question is embedded with exactly the same model and settings as the chunks. The resulting vector is sent to Qdrant, which finds the stored vectors closest to it. Only this one embedding call happens per question; the documents were embedded earlier.

**[15:17]** Mixing models breaks it: vectors from different models aren't comparable.

> *On screen:* The query path stays on screen with the red "same model!" label under the second Titan v2 box.

Vectors from different embedding models live in different spaces: their dimensions mean different things and may not even have the same length. Comparing a Titan v2 query vector with chunks embedded by another model gives meaningless similarity scores. Always use one model for documents and queries.

### Step 4: retrieve the top 5 chunks

**[15:25]** Cosine search finds the 5 chunks closest in meaning to the question.

> *On screen:* Five chunk cards (pages 4, 12, 7, 21, 15 with scores 0.82 down to 0.69) slide out of the Qdrant cylinder along dashed lines.

Qdrant returns the top k = 5 chunks by cosine similarity, each with its score and payload. The page numbers and scores shown are illustrative. Five chunks is a balance: enough context to answer, small enough to keep the prompt focused and cheap.

### Step 5: pack them into a prompt

**[15:32]** Instructions + the 5 chunks with their page numbers + the question.

> *On screen:* A prompt card fills line by line: "Answer ONLY from the context. Cite the page for each fact.", then [Source 1 – Page 4] … through [Source 5 – Page 15], then the question; the chunk cards slide into it.

The retrieved chunks are pasted into a prompt template with clear labels such as [Source 1 – Page 4], followed by the user's question. The instructions tell the model to use only this context and to cite pages. Labelling each chunk is what makes citations possible.

### Step 6: Claude answers, with citations

**[15:41]** Claude writes the answer from the context only, and points to the pages.

> *On screen:* The prompt flows into a "Claude on Amazon Bedrock" box, and a green answer card appears ("Growth was driven mainly by …") ending with [Source 1 · page 4] and [Source 2 · page 12].

Claude (Sonnet 4.6 via Amazon Bedrock in this project) reads the context and writes an answer grounded in it, pointing to the pages it used. The model was never trained on this PDF; everything it knows about the document comes from the five retrieved chunks.

**[15:45]** Answers grounded in your own documents, with sources you can check.

> *On screen:* The prompt, the Claude box and the cited answer card stay on screen together as the takeaway for the pipeline.

This is the core value of RAG: answers based on your own, current documents, with sources a reader can check. If retrieval returns the wrong chunks, the answer will be wrong too, so retrieval quality (chunking, embeddings, hybrid search, filters) matters as much as the LLM.

### Pitfalls to avoid

**[15:51]** Overlap keeps ideas from being cut in half at a chunk border.

> *On screen:* Three pitfall cards appear: chunk size 256–512 tokens with 10–20% overlap; one embedding model for docs AND queries; tell Claude to say "I don't know" if the context lacks the answer.

Chunks that are too small lose context, chunks that are too large dilute it; 256–512 tokens is a common starting range. An overlap of 10–20% between neighbouring chunks keeps a sentence or idea from being split across a border where neither half makes sense. Instructing the model to admit when the context lacks the answer reduces made-up answers.

**[15:55]** And re-index everything if you ever switch embedding models.

> *On screen:* The note "Model A vectors ≠ Model B vectors" pops up under the pitfall cards.

If you switch to a new embedding model, every stored document must be re-embedded and re-indexed; old and new vectors can't be mixed in one search. Plan for this when choosing a model, and record the model name with each vector (the embedding project in Series B stores model_version in every payload).

### Key takeaways  `[16:00]`

- Chunk → embed (Titan v2, 1,024 dims) → store in Qdrant
- Embed the question with the same model
- Retrieve the top-5 chunks by cosine similarity
- Claude answers from that context, citing pages
