# Embeddings — Full Course Guide

Total length: **12:26**

**Video:** [`Embeddings-Full-Course.mp4`](Embeddings-Full-Course.mp4), 1920×1080, 30 fps, with chapter markers. In VLC use *Playback → Chapter*.
**Editable drawings:** [`Embeddings-Full-Course.excalidraw`](Embeddings-Full-Course.excalidraw). Open it at excalidraw.com with *Menu → Open*.
**Source project:** `video/embedding/embeddings/multimodal/multimodal-search-vertex-qdrant/`. It uses Gemini Embedding 2 (`gemini-embedding-2-preview`) and Qdrant.

### How to use this guide
- Each **[mm:ss]** line is the on-screen caption, with its exact time in the full video.
- *On screen* describes the animation; the paragraph under it explains the idea in depth.
- Chapter order follows the dependencies:
  1. The shared space (Ch 1) and its sizes (Ch 2)
  2. How a vector is stored in Qdrant (Ch 3), which two-stage retrieval (Ch 4), thresholds (Ch 6), RAG (Ch 7) and recommendations (Ch 8) all build on
  3. The engineering lessons, collected at the end (Ch 9)
- **Prerequisite:** cosine similarity (1 = same meaning, 0 = unrelated). It's covered in the Vector Search course, Chapter 2.

> **Accuracy note.** Every score and timing comes from the project's own runs (`demo_output.txt`, `charts.png`). Where the README disagrees with the measured output, the measurement is used. For example, no image reached the top 10 in cross-modal search, because the demo image is a 1×1-pixel stub. 2-D point layouts are labelled *sketch/illustrative*: real vectors have 128–3,072 dimensions.

## Chapters

| Starts | Chapter | Length | Source video |
|---|---|---|---|
| 00:00 | [Introduction](#introduction) | 00:13 | `E00-intro` |
| 00:13 | [Chapter 1 — One space for every modality](#chapter-1--one-space-for-every-modality) | 01:30 | `E01-multimodal-shared-space` |
| 01:43 | [Chapter 2 — Matryoshka embeddings](#chapter-2--matryoshka-embeddings) | 01:33 | `E02-matryoshka` |
| 03:16 | [Chapter 3 — Anatomy of a Qdrant point](#chapter-3--anatomy-of-a-qdrant-point) | 01:33 | `E05-qdrant-payload-filters` |
| 04:49 | [Chapter 4 — Two-stage retrieval](#chapter-4--two-stage-retrieval) | 01:33 | `E03-two-stage-retrieval` |
| 06:22 | [Chapter 5 — One space, many languages](#chapter-5--one-space-many-languages) | 01:04 | `E04-multilingual` |
| 07:27 | [Chapter 6 — Score thresholds](#chapter-6--score-thresholds) | 01:17 | `E06-score-thresholds` |
| 08:45 | [Chapter 7 — RAG retrieval: find the right doc](#chapter-7--rag-retrieval-find-the-right-doc) | 01:16 | `E07-rag-knowledge-base` |
| 10:02 | [Chapter 8 — Recommendations: more like this](#chapter-8--recommendations-more-like-this) | 01:01 | `E08-recommendations` |
| 11:04 | [Chapter 9 — 6 production lessons](#chapter-9--6-production-lessons) | 01:22 | `E09-production-lessons` |

---

## Introduction

**Starts at 00:00** · length 00:13 · source `E00-intro` · hook: *"Gemini Embedding 2 + Qdrant, with real measured results"*

**What you'll learn.** A 13-second opener. It shows the nine chapters of the course in the order they play, and sets up the one idea you need going in: a **cosine score** is close to 1 when two items mean the same thing and close to 0 when they are unrelated. Every score and timing in the course comes from the project's own runs (`demo_output.txt`, `charts.png`), not from the README's descriptions.

### What we'll cover

**[00:07]** Cosine score: 1 = same meaning, 0 = unrelated. All scores come from the project's own runs.

> *On screen:* The agenda appears item by item: nine numbered blue circles, each with its chapter title typed beside it, then the caption at the bottom.

Cosine similarity compares the *direction* of two vectors: 1.0 means they point exactly the same way, around 0 means unrelated. Every search in this project uses cosine, because the Qdrant collection is created with `Distance.COSINE`. Scores are only meaningful relative to each other and to the model you used; a score from one model can't be compared with a score from another.


---

## Chapter 1 — One space for every modality

**Starts at 00:13** · length 01:30 · source `E01-multimodal-shared-space` · hook: *"How can a text query find an image?"*

**What you'll learn.** This chapter shows the core idea of the project: one model, `gemini-embedding-2-preview`, puts text, images, audio, video, PDFs and *interleaved* content (several parts in one request) into **one shared vector space**. It also walks through how the code is wired (`api.py` → `embedding_service.py`, `vector_store.py`, `search_engine.py`) and the input limits from `content_processor.py`. It ends by checking what the demo actually proved. No prerequisites.

### Six content types, one model

**[00:19]** Text, images, audio, video and PDFs all go into ONE model: gemini-embedding-2-preview.

> *On screen:* Six coloured boxes (text, image, audio, video, PDF, interleaved) appear on the left, and arrows draw from each into one yellow model box.

`embedding_service.py` has one method per modality (`embed_text`, `embed_image`, `embed_audio`, `embed_video`, `embed_pdf`, `embed_interleaved`). All of them call the same API, `client.models.embed_content(model="gemini-embedding-2-preview", ...)`, with an `output_dimensionality`. Non-text content is sent as raw bytes with its MIME type (`types.Part.from_bytes`).

**[00:25]** Everything lands in the SAME space. Meaning decides the position, not the file type.

> *On screen:* Small coloured points fly out of the model into a dashed "shared vector space" panel and settle into topic clusters (this 2-D layout is illustrative).

Because every modality comes out of the same model, a vector for a photo and a vector for a sentence are directly comparable: they live in one coordinate system. Points cluster by **topic**, not by file type. Real vectors have hundreds or thousands of dimensions; the 2-D picture is only a sketch.

### Cross-modal search

**[00:33]** The idea: a text query lands by the beach cluster, next to an image and a video.

> *On screen:* A red text-query marker drops into the space and lands next to the beach cluster, beside an image point and a video point.

This is the *idea* of cross-modal search: a text query such as "dog playing on beach" is embedded into the same space, so its nearest neighbours can be of any modality. The marker's position is illustrative, not a measured result; the end of this chapter checks what the demo really returned.

**[00:38]** No separate image pipeline: one cosine search in Qdrant covers every modality.

> *On screen:* Arrows from the query reach points of several modalities while the caption explains that one search covers them all.

In the code, a cross-modal search is just one Qdrant `query_points` call with cosine distance. Restricting it to certain modalities is a payload filter (`content_type` MatchAny), not a separate index or pipeline. `search_engine.py` exposes this as `search_cross_modal(query, target_modalities=[...])`.

### Interleaved: image + caption → ONE vector

**[00:45]** One request carries both parts, in order: the image first, then its caption.

> *On screen:* An image part and a caption part slide into a single request box, in order (image first, then text).

An *interleaved* item (`content_type="interleaved"`) carries an ordered list of `InterleavedPart`s. `embed_interleaved` turns them into one `contents=[...]` request: text parts as strings, media parts as `Part.from_bytes`. The order is kept so the model can relate the caption to the image.

**[00:49]** The model returns a single vector that describes the image and its caption together.

> *On screen:* The request box sends one arrow to a single vector bar labelled `response.embeddings[0]`.

Even with several parts, the API returns **one** embedding, `response.embeddings[0].values`, describing the combined content. That is useful for product listings (photo plus description) indexed as a single item. The demo stored one such item, with a caption like "Wireless noise-cancelling headphones, 30h battery."

### How the project is wired

**[00:57]** One entry point, three parts: embed (Vertex AI), store (Qdrant), search (engine).

> *On screen:* The architecture diagram draws itself: MultimodalSearchAPI on top, with arrows down to EmbeddingService, VectorStore and SearchEngine.

`api.py` (`MultimodalSearchAPI`) is the single entry point and wires three components together. `EmbeddingService` talks to Vertex AI. `VectorStore` wraps the Qdrant client (named vectors, payload, cosine). `SearchEngine` orchestrates single-stage, two-stage, cross-modal and multilingual search.

**[01:01]** At search time the engine embeds the query, then asks Qdrant for the nearest points.

> *On screen:* Arrows labelled "embed query" and `query_points` light up between SearchEngine, EmbeddingService and VectorStore.

Every search runs in two steps. First the query (any modality) is embedded at the chosen dimension, which is a network call to Vertex AI. Then Qdrant is asked for the nearest points using the matching named vector (`using="dim_756"` by default). Both steps add latency, which matters for the timings in chapters 2 and 4.

### Input limits (content_processor.py)

**[01:08]** MultimodalSearchAPI validates content against these limits before embedding it.

> *On screen:* A table of six limits fades in: text 8,192 tokens, audio 80 s, video 120 s, PDF 6 pages, 6 images per batch, PNG/JPEG images.

`content_processor.py` validates items before embedding, so oversize content fails fast with a clear error (`SIZE_EXCEEDED`) instead of an API failure. The text check uses an *estimated* token count. Long documents therefore need chunking before they are embedded.

### Honest check: what did the demo show?

**[01:14]** Matching text: 0.6859. The stub image: only 0.3236, even with an image-only filter.

> *On screen:* Measured score bars grow: the matching text at 0.6859, other text around 0.45, and a short bar for the stub image at 0.3236.

For the query "dog playing on beach", the closest point was the golden-retriever sentence (0.6859). Unrelated knowledge-base text scored about 0.44–0.47. The only image in the collection reached 0.3236, and only when the search was restricted to images. The demo image is a **1×1-pixel stub JPEG**.

**[01:18]** No image or interleaved point reached the top 10. One pixel carries no meaning.

> *On screen:* The image bar is crossed out while the caption notes that no image or interleaved point reached the top 10.

In the measured cross-modal chart, all top-10 results were text. A single pixel carries no visual content, so the model can't place it near "dog on a beach". This is a limit of the *test data*, not of the design.

**[01:23]** The design supports cross-modal search — prove it with real images, not stubs.

> *On screen:* A final card summarises: the architecture supports cross-modal search, but it needs real images to prove it.

The README's claim that images "score competitively" isn't supported by the measured output. To actually validate cross-modal retrieval, index real photos (for example several beach and non-beach images) and check that text queries rank the right images first. Measure before you trust it.

### Key takeaways  `[01:28]`

- One model maps text, image, audio, video and PDF into one space
- Meaning decides the position, so text can find images
- Interleaved parts (image + caption) become ONE vector
- Validate inputs; test cross-modal with real images

---

## Chapter 2 — Matryoshka embeddings

**Starts at 01:43** · length 01:33 · source `E02-matryoshka` · hook: *"Can one embedding come in eight sizes?"*

**What you'll learn.** Gemini Embedding 2 can return vectors of 8 sizes, from 128 to 3,072 numbers. This chapter uses the project's measured output to show that they are **nested**: a small vector looks like the start of the big one, rescaled to length 1. That lets you trade precision for speed and memory. It also covers what size does *not* change (API latency, throughput), and an inefficiency in `embedding_service.py`. It builds on chapter 1.

### Eight sizes, nested like dolls

**[01:50]** Gemini Embedding 2 can return 8 sizes: 128 up to 3,072 numbers per vector.

> *On screen:* Eight bars of increasing length appear, labelled 128, 256, 512, 756, 1024, 1536, 2048, 3072, with 756 marked as the project default.

`EmbeddingService.VALID_DIMENSIONS = [128, 256, 512, 756, 1024, 1536, 2048, 3072]`; any other value raises an `INVALID_DIMENSION` error. The project's default is **756** (`DEFAULT_DIMENSION`). It's passed to the API as `output_dimensionality`.

**[01:54]** Like nesting dolls: the small vector is the beginning of the big one.

> *On screen:* The bars stack inside each other like nesting dolls, the short ones sitting at the left start of the long ones.

Matryoshka-style models are trained so that the *first* numbers of the vector carry the most important information. A short vector is then useful on its own, and you can pick the size per use case without a separate model.

### Measured: same text, five sizes

**[02:01]** The numbers shrink as the vector grows, but the signs stay −, +, − in every row.

> *On screen:* A table types in the measured first three values at 128 / 256 / 756 / 1024 / 3072 dims, with the signs −, +, − highlighted in every row.

Measured for "A golden retriever playing fetch on a sunny beach.": 128 → [-0.0837, 0.0082, -0.0544], 3072 → [-0.0214, 0.0021, -0.0139]. The values shrink as the size grows, but the pattern (negative, small positive, negative) stays the same.

**[02:08]** The ratio stays ≈ 0.65 at every size: all five vectors point in the same direction.

> *On screen:* A ratio column (third value ÷ first value) fills in: 0.650, 0.650, 0.652, 0.652, 0.650.

If the small vectors were unrelated to the big one, these ratios would jump around. Instead they are essentially constant, which means that within these first numbers all five vectors point in the **same direction** and differ only by an overall scale. (This is based on 3 values per size, so it's strong evidence, not proof.)

### Cut the prefix, rescale to length 1

**[02:15]** The measured outputs match this: keep the first d numbers, rescale to length 1.

> *On screen:* A long bar is cut after its first d cells, and the piece is rescaled with a "÷ length" step.

The pattern fits *truncate, then renormalise*: keep the first d numbers, then divide by their length so the vector has length 1. Renormalising after truncation matters because cosine and dot-product scores assume consistent lengths.

**[02:22]** Length 1.00 at all 8 sizes. Spread over more numbers, each number gets smaller.

> *On screen:* Norm bars at all 8 sizes rise to exactly 1.00.

The project measured the L2 norm (length) at every size and got **1.00** each time: every vector is unit length. That explains the shrinking values: a fixed length of 1 shared across 3,072 numbers leaves each number smaller than when it's shared across 128.

### Does a smaller size make the API faster?

**[02:29]** Each call took about 440–660 ms, whatever the size. The network round-trip dominates.

> *On screen:* A latency band from about 440 to 660 ms is drawn across all sizes, with no upward trend.

The measured time per API call was about 440–660 ms regardless of dimension. A smaller vector does **not** make the embedding call faster, because the network round-trip to Vertex AI dominates. The benefit of small sizes comes later, in storage and search.

**[02:35]** ≈ 1.9 docs/sec at every size: embed_batch makes one API call per item, in turn.

> *On screen:* Throughput bars at 128 / 256 / 512 / 756 / 1024 are almost equal: 1.95, 1.91, 1.87, 1.90, 1.84 docs/sec.

Batch throughput was about 1.9 documents per second at every size. `embed_batch` loops over the items **sequentially**, one API call each, so throughput is bounded by round-trip latency. Concurrency, not a smaller dimension, would speed this up.

### Two sizes = two calls?

**[02:42]** Today, asking for two sizes costs two API calls — one per dimension.

> *On screen:* Two separate arrows go from one item to the API: one call for 256 and another for 1024.

`embed_with_multiple_dimensions(item, [256, 1024])` returns `{dim: self._embed_item(content, dim)}`: **one API call per dimension**. Storing an item for two-stage search therefore costs two network calls, contrary to the README's "single model call" description.

**[02:48]** Because the sizes are nested, one 3,072-d call could be cut down locally instead.

> *On screen:* One 3,072-d call is drawn, then cut locally into shorter prefixes (marked as an idea, not in the code).

Because the sizes are nested, you could call the API once at the largest size you need and derive the smaller vectors locally: truncate and renormalise, with no extra network calls. This is a suggested improvement, not something the project does. Check that local truncation gives the same results as the API on your data before switching.

### Which size when? (README guidance)

**[02:55]** Small vectors for fast scans, big ones for precision. Two-stage uses both.

> *On screen:* A guidance card maps sizes to uses: 128/256 fast scans, 512/756 balanced, 1024/1536 re-ranking, 2048/3072 maximum precision.

The README's guidance: small vectors for cheap first-stage retrieval and low memory, large ones where precision matters most. Storage grows linearly; as float32, a 128-d vector is 512 bytes, 756-d is 3,024 bytes and 3,072-d is 12,288 bytes. Chapter 4 (two-stage retrieval) combines a small and a large size.

### Key takeaways  `[03:00]`

- 8 sizes from one model: 128 → 3,072 (project default 756)
- Smaller = the first d numbers, rescaled to length 1
- Measured norm 1.00 at every size; latency ≈ flat
- One call per size today — local truncation could save calls

---

## Chapter 3 — Anatomy of a Qdrant point

**Starts at 03:16** · length 01:33 · source `E05-qdrant-payload-filters` · hook: *"What does the database actually store for each embedding?"*

**What you'll learn.** This chapter opens up a single Qdrant **point**: an ID, a set of named vectors and a payload. It then shows how payload indexes and filters narrow a search. It builds on chapter 1 (one shared space) and chapter 2 (Matryoshka sizes), and the next chapters reuse its ideas: named vectors in two-stage retrieval, scores and thresholds, and the duplicate-ID problem. Source: `src/multimodal_search/vector_store.py` (`initialize_collection`, `store_embedding`, `_build_payload`, `_build_filter`) and the measured runs in `demo_output.txt`.

### One point = id + named vectors + payload

**[03:22]** Every stored embedding is a point. It starts with an ID.

> *On screen:* A point card draws in with an `id` field at the top.

In Qdrant every stored item is a **point**. A point has a unique ID, one or more vectors, and an optional JSON payload. In this project the ID is a random `uuid4` generated in `vector_store.py` each time something is stored, which matters later in this chapter.

**[03:27]** The collection defines 8 named vectors: dim_128 up to dim_3072.

> *On screen:* Eight empty slots labelled dim_128 to dim_3072 appear inside the point card.

`initialize_collection` creates the collection with **named vectors**: one vector slot per supported Matryoshka size (128, 256, 512, 756, 1024, 1536, 2048, 3072), all using COSINE distance. Named vectors let a single point hold the same item at several sizes. Each search chooses a size with `using="dim_256"`, `"dim_1024"` and so on.

**[03:30]** A point fills only the sizes it was embedded at. Two-stage docs: dim_256 + dim_1024.

> *On screen:* The dim_256 and dim_1024 slots fill in while the others stay empty.

A point doesn't have to fill every slot. Content stored for two-stage retrieval (chapter 4) carries exactly two vectors, `dim_256` and `dim_1024`, on the same point. That is what lets stage 2 re-rank the stage-1 candidates by ID without re-fetching anything.

**[03:35]** This knowledge-base doc was embedded once, at the project default: dim_756.

> *On screen:* The card switches to the knowledge-base doc kb-infra-002, where only dim_756 is filled.

Most demo content, including the knowledge-base documents, was embedded once at the project's default size of 756 and stored under `dim_756`. The vector name always matches the size it holds (`dim_<dimension>`). A query must be embedded at the same size to search that slot.

**[03:41]** The payload carries metadata: type, source, time, size, model.

> *On screen:* Payload fields type in one by one below the vectors.

The payload built by `_build_payload` stores `content_type`, `source_id`, `timestamp` (ISO 8601), `dimension` and `model_version`. Optional fields are `language`, `duration`, `page_count` and `custom_metadata`. The payload doesn't affect similarity at all, but it's what you filter on and what you show users.

### Payload indexes make filters fast

**[03:48]** Four payload fields get an index: three KEYWORD, one DATETIME.

> *On screen:* Four index badges appear next to content_type, source_id, timestamp and language.

Qdrant can filter on any payload field, but an index makes it fast. The project creates KEYWORD indexes on `content_type`, `source_id` and `language`, and a DATETIME index on `timestamp`. Without an index, a filter has to check each candidate's payload one by one.

**[03:52]** Content of every modality lives in the same collection.

> *On screen:* A mixed set of text, image and other items appears as small cards in one collection box.

Because every modality is embedded into the same vector space (chapter 1), all of them live in one collection, `multimodal_embeddings`. The `content_type` field records what each point is, so a search can include or exclude modalities.

**[03:55]** Filter on modality: content_type MatchAny ["text"] keeps only text.

> *On screen:* Every card that isn't text fades out.

`_build_filter` turns `content_types=["text"]` into a `FieldCondition` with `MatchAny`. Only points whose `content_type` is in the list are considered. The filter is passed into `query_points`, so Qdrant applies it while it searches rather than afterwards.

**[03:59]** Add language MatchAny ["es","fr"] and the conditions combine.

> *On screen:* A second condition is added and only the Spanish and French text cards stay visible.

Conditions in the same filter combine with AND: the point must be text **and** its `language` must be `es` or `fr`. `MatchAny` means "any of these values", so each condition can accept several values.

**[04:02]** Timestamp ranges and source IDs work the same way.

> *On screen:* Timestamp-range and source-ID filter chips slide in.

Timestamps use a `Range` condition with `gte`/`lte` on the DATETIME index, for example "content stored this week". Source IDs use `MatchAny` like modality. There's also a special `_point_ids` key that becomes a `HasIdCondition`, which two-stage retrieval uses to restrict stage 2 to the stage-1 candidates.

### Measured: modality filter demo

**[04:06]** Text only: five matches, all around 0.51 to 0.55.

> *On screen:* Five bars grow to between 0.51 and 0.55, labelled with their source IDs.

These are the measured results of the text-only filter for the query "ocean beach sunset": kb-infra-002 0.5496, kb-product-001 0.5243, kb-infra-001 0.5231, ml-en-001 0.5194, kb-hr-002 0.5087. The scores are close together and modest, because none of the stored texts is really about a beach at sunset. The filter worked, but the collection simply had no strong match.

**[04:09]** Image only: one match at 0.3236.

> *On screen:* One short bar grows to 0.3236 for demo-image-001.

With an image-only filter the single image point scored **0.3236**, well below the text results. On its own this number tells you little about cross-modal quality, as the next step explains.

**[04:12]** No surprise: a 1×1-pixel stub image carries no meaning. Use real images.

> *On screen:* The image card zooms in to show a single pixel.

The demo image is a hard-coded 1×1-pixel stub JPEG (`STUB_JPEG` in `demo.py`), so the model had almost nothing to embed. The low score is expected, and it does not show that text-to-image search fails. To evaluate cross-modal search you need real images.

### Pitfall: random IDs create duplicates

**[04:17]** Each store call makes a new random uuid4, so re-running the demo stores everything again.

> *On screen:* The same document card is stored twice, with two different random IDs.

`store_embedding` creates a fresh `uuid4()` whenever no ID is supplied. Running the demo again therefore inserts a second copy of every item instead of updating the first. Qdrant's upsert only overwrites when the ID is the same.

**[04:22]** The collection holds 54 points, each item twice, so top-2 is one doc repeated.

> *On screen:* A results list shows rank 1 and rank 2 holding the same document.

The live collection has 54 points, and the demo items appear twice. So when the demo asks for the top 2, both slots go to identical copies with identical scores; the RAG demo returned `kb-hr-001` twice. You'll see this symptom again in chapters 6, 7 and 8.

**[04:27]** Fix: derive the ID from source_id with uuid5. Same doc, same ID: upsert overwrites.

> *On screen:* The duplicate cards merge into one as a uuid5(source_id) label appears.

A deterministic ID fixes it: for example `uuid.uuid5(NAMESPACE, source_id)` always gives the same UUID for the same `source_id`, so re-indexing overwrites the existing point. This makes writes **idempotent**. This is a suggested fix; the current code still uses `uuid4`.

### Key takeaways  `[04:34]`

- A point = id + named vectors + payload
- Points fill only the vector sizes they were embedded at
- Indexed payload fields let you filter by modality, language, time
- Use deterministic IDs (uuid5 of source_id) to avoid duplicates

---

## Chapter 4 — Two-stage retrieval

**Starts at 04:49** · length 01:33 · source `E03-two-stage-retrieval` · hook: *"Scan fast with 256 dims, then re-rank with 1024?"*

**What you'll learn.** Two-stage retrieval does a cheap first pass with small vectors, then re-ranks a short list with large ones. The project stores both sizes on the **same Qdrant point** as named vectors (`dim_256`, `dim_1024`), so **watch chapter 3 (Anatomy of a Qdrant point) first**. This chapter explains the pipeline in `search_engine.py`, shows the measured latencies, and explains why it was *slower* on this tiny 54-point demo.

### One Qdrant point, two named vectors

**[04:57]** Each point stores the same item at two sizes: named vectors dim_256 and dim_1024.

> *On screen:* A Qdrant point card appears with two vector slots, `dim_256` and `dim_1024`, filled for the same item, plus its payload fields.

Named vectors let one Qdrant point hold several vectors under different names. The collection is created with all 8 sizes (`dim_128` … `dim_3072`). A two-stage document fills `dim_256` and `dim_1024` via `store_embedding_with_named_vectors`. Chapter 3 covers point anatomy in detail.

**[05:02]** Both sit on the SAME point, so stage 2 can fetch the candidates by their IDs.

> *On screen:* An arrow from the stage-1 list points back to the same point IDs used in stage 2.

Because both sizes live on the same point, stage 1's results are just a list of **point IDs**. Stage 2 can re-score exactly those points with their 1024-d vectors, without looking anything up elsewhere.

### The README's analogy: hiring

**[05:09]** 10,000 CVs get a quick 5-minute phone screen. 50 make the shortlist.

> *On screen:* A pile of CV cards shrinks to a shortlist of 50 after a quick "phone screen" step.

The README's analogy: screening 10,000 CVs with a 5-minute call is cheap per candidate and good enough to discard most of them. The 256-d search plays this role: fast and approximate.

**[05:13]** Only those 50 get the full 1-hour interview.

> *On screen:* Only the shortlisted cards move on to an "interview" box, and a mapping card shows phone screen = 256, interview = 1024.

The expensive 1-hour interview (the 1024-d comparison) is spent only on the shortlist. Each candidate goes through two steps, yet the total cost is lower than interviewing everyone.

### Stage 1: fast scan with dim_256

**[05:21]** Stage 1: embed the query at 256 dims, search dim_256, keep the top-100 (the default).

> *On screen:* In an illustrative field of points, the query's 100 nearest neighbours light up blue.

`search_two_stage` first embeds the query at 256 dims, then calls `search_with_named_vector(vector_name="dim_256", limit=first_stage_limit)`. The default `DEFAULT_FIRST_STAGE_LIMIT` is 100 candidates, and the same optional modality filter applies.

### Stage 2: re-rank only those, with dim_1024

**[05:30]** Stage 2 compares only the 100 candidates at 1,024 dims and returns the top-10.

> *On screen:* The 100 candidates are re-ordered by their 1024-d scores (illustrative), and the top 10 are circled.

Stage 2 embeds the query again at 1024 dims and searches `dim_1024`, restricted to the candidate IDs through a `_point_ids` custom filter that becomes a Qdrant `HasIdCondition`. The final limit defaults to 10. The re-ordering on screen is illustrative; the project has no stage-1 vs stage-2 ranking data.

**[05:34]** The demo used smaller numbers: 256 → top-20 candidates, then 1024 → top-5.

> *On screen:* The numbers on the diagram change to the demo's settings: 20 candidates, then the top 5.

`demo.py` and `visualize.py` call it with `first_stage_config=StageConfig(dimension=256, limit=20)` and `second_stage_config=StageConfig(dimension=1024, limit=5)`. The demo query "attention mechanism transformers" returned a document at 0.8861, listed twice because of the duplicate-ID issue from chapter 3.

### Measured on 54 points

**[05:42]** On 54 points two-stage was the SLOWEST: 2,348 ms vs 1,154 ms at dim 256.

> *On screen:* Three measured latency bars grow: single dim 256 at 1,154 ms, single dim 1024 at 1,620 ms, two-stage at 2,348 ms.

These are averages of 3 runs on the 54-point collection, *including* the embedding calls. On such a small collection, two-stage was the slowest of the three.

**[05:48]** Why: it embeds the query twice and searches twice. With 54 points, nothing is saved.

> *On screen:* The two-stage bar splits into its parts: two embedding calls and two Qdrant searches.

Two-stage makes **two** Vertex AI calls (one per dimension) and **two** Qdrant queries. With only 54 points, scanning everything at 1024-d is already cheap, so the extra round-trips are pure overhead. Embedding once at 1024 and truncating locally to 256 would remove one call (see chapter 2).

### Where it pays off: big collections

**[05:56]** At scale, stage 1 discards almost everything; only 100 points get the 1024-d check.

> *On screen:* A huge illustrative collection is pruned to a sliver by stage 1, and only that sliver goes to the 1024-d check.

At millions of points the picture flips. Stage 1 compares against small 256-d vectors and keeps only 100 candidates, so the expensive 1024-d comparison runs on a tiny fraction of the data. This is the README's reasoning; the project didn't benchmark a large collection.

**[06:01]** Note: this project measured speed only — check accuracy on your own data.

> *On screen:* A note card appears: this project measured speed only.

The project never measured *accuracy* (for example recall@10 of two-stage vs single-stage 1024). Before adopting two-stage, compare its top-k against a full 1024-d search on your own queries. Tune the candidate count (100 by default) until quality matches.

### Key takeaways  `[06:07]`

- Store dim_256 and dim_1024 as named vectors on one point
- Stage 1: dim_256 → top-100 · Stage 2: dim_1024 → top-10
- On 54 points it was slower: 2,348 ms vs 1,154 ms
- It pays off on large collections, not tiny ones

---

## Chapter 5 — One space, many languages

**Starts at 06:22** · length 01:04 · source `E04-multilingual` · hook: *"Can a Spanish query find an English document?"*

**What you'll learn.** The same sentence about the Eiffel Tower, in English, Spanish, French and Japanese, is embedded and compared all-against-all. The measured 4×4 cosine heatmap shows meaning carrying across languages with no translation step. It builds on chapter 1 (the shared vector space).

### Same meaning, four languages

**[06:28]** The Eiffel Tower, written in English, Spanish, French and Japanese.

> *On screen:* Four language tags (EN, ES, FR, JA) appear, each with its Eiffel Tower sentence typed beside it.

The sentences are: "The Eiffel Tower is a famous landmark in Paris." / "La Torre Eiffel es un famoso monumento en París." / "La Tour Eiffel est un monument célèbre à Paris." / "エッフェル塔はパリにある有名なランドマークです。" They mean the same thing; only the language differs.

**[06:32]** Each sentence goes through the same model: gemini-embedding-2-preview.

> *On screen:* Coloured arrows draw from each sentence into one yellow "Gemini Embedding 2" box.

There is no per-language model and no translation. Every sentence is embedded by the same `gemini-embedding-2-preview` call at the project's default 756 dimensions. The README says the model supports more than 100 languages in one space.

**[06:35]** Same meaning lands in the same neighbourhood, whatever the language.

> *On screen:* Four points settle close together inside a dashed circle labelled as a sketch of the shared space.

If the model works, the same meaning should land in the same neighbourhood whatever the language. The circle is illustrative; the next scenes show the measured similarities.

### Measured: query language × document language

**[06:40]** Query in each language, score each document with cosine similarity.

> *On screen:* An empty 4×4 grid appears, with query languages as rows and document languages as columns.

Each cell is the cosine similarity between a query in one language and a document in another. The grid covers all 16 combinations, including same-language pairs on the diagonal.

**[06:44]** Every one of the 16 pairs scores between 0.765 and 0.872.

> *On screen:* The heatmap fills cell by cell with the measured values, coloured by score.

Measured rows (query → EN, ES, FR, JA): EN 0.832 / 0.772 / 0.778 / 0.798; ES 0.812 / 0.872 / 0.822 / 0.782; FR 0.781 / 0.814 / 0.842 / 0.765; JA 0.829 / 0.795 / 0.818 / 0.813. Every pair falls between 0.765 and 0.872.

**[06:48]** Even the weakest cross-language pair, French to Japanese, is 0.765.

> *On screen:* The lowest cell, FR query → JA document at 0.765, is circled.

Even the weakest cross-language pair is well above the unrelated-text scores seen in chapter 1, which were about 0.44–0.47. (Those came from a different query, so treat this as a rough sense of scale.) This is also lower than the README's claim of "0.8+" for all cross-language scores.

**[06:52]** For English, Spanish and French queries, the same-language document scores highest.

> *On screen:* The diagonal cells for EN, ES and FR are highlighted as the highest in their rows.

For English (0.832), Spanish (0.872) and French (0.842) queries, the document in the same language scored highest. Same-language matching is easiest, because the wording overlaps as well as the meaning.

**[06:56]** Surprise: for the Japanese query, the English document edges out the Japanese one.

> *On screen:* In the JA row, the EN cell (0.829) is highlighted above the JA cell (0.813).

For the Japanese query, the English document scored slightly higher than the Japanese one. So the README's statement that the diagonal is always highest doesn't hold exactly. The gap is small (0.016); the point is that all four are strong matches.

**[07:00]** Cross-language scores stay close to same-language scores: meaning carries over.

> *On screen:* A summary bracket spans the whole grid, comparing cross-language scores with same-language ones.

Across the grid, cross-language scores sit close to same-language scores. A query in any of these languages retrieves the Eiffel Tower document in every language, without knowing which language it was written in.

### No translation step

**[07:05]** The old way: translate everything into one language first.

> *On screen:* A "translate first" pipeline is drawn (query → translate → search) and then crossed out.

The traditional approach translates queries or documents into one pivot language, which adds latency, cost and translation errors. In practice, pick one threshold per model and check it per language, since scores vary slightly by language pair.

**[07:08]** With a shared space: embed the query, search everything, done.

> *On screen:* A short pipeline replaces it: embed the query, then search everything.

With a shared multilingual space, indexing and querying both use the same embedding call. Optional payload filters (`language` MatchAny, covered in chapter 3) restrict results to certain languages when you want that.

### Key takeaways  `[07:13]`

- One model maps every language into one vector space
- All 16 Eiffel Tower pairs scored 0.765 – 0.872
- Own language wins for EN, ES, FR; JA query slightly preferred EN
- No translation layer needed

---

## Chapter 6 — Score thresholds

**Starts at 07:27** · length 01:17 · source `E06-score-thresholds` · hook: *"How similar is similar enough?"*

**What you'll learn.** Every Qdrant result comes with a cosine score. This chapter asks how high a score has to be before a result counts as a match. It uses the measured threshold sweep from `visualize.py` (query "dog playing on beach", limit 50) to show how quickly results disappear as the cut-off rises. Prerequisite: cosine similarity (1 = same meaning, 0 = unrelated) and the duplicate points from chapter 3. Choosing a threshold is the main precision/recall knob in RAG and search, and it has to be calibrated on your own data.

### Every result comes with a cosine score

**[07:34]** One query, 44 results. Where do their scores fall?

> *On screen:* A 0-to-1 score axis is drawn and 44 result dots drop onto it.

The query "dog playing on beach" (limit 50) returned 44 results. Each result's cosine score is shown as a dot on the axis. The point of this view is the shape of the distribution: where the bulk sits and how few results are actually strong matches.

**[07:36]** 18 between 0.3 and 0.4, 24 between 0.4 and 0.5, and just 2 above 0.6.

> *On screen:* The dots group into bands, with counts labelled above each band.

The counts per band are derived from the measured sweep; where each dot sits inside its band is illustrative. Most results sit between 0.3 and 0.5, which is weak background similarity, and only two clear 0.6. That gap is what a threshold takes advantage of.

**[07:41]** The best match, about 0.686, is the golden-retriever sentence. It is stored twice.

> *On screen:* The highest dot is highlighted and labelled with the golden-retriever sentence.

The best match, at about 0.686, is the stored text "A golden retriever playing fetch on a sunny beach.", the obvious answer to a query about a dog on a beach. It appears twice because of the duplicate IDs from chapter 3.

### Slide the threshold, watch results vanish

**[07:46]** Qdrant drops every result scoring below score_threshold.

> *On screen:* A threshold slider appears below the axis.

`score_threshold` is passed straight to Qdrant's `query_points`. Any point scoring below it is dropped before the results come back. It doesn't change the order of results, only how many you get.

**[07:51]** 0.0 to 0.3: all 44 stay. At 0.4: 26 left.

> *On screen:* The slider moves right and the dots below it fade out while a counter updates.

From 0.0 to 0.3 nothing is removed, because every one of the 44 results scores at least 0.3. At 0.4 the 18 results in the 0.3–0.4 band disappear, leaving 26.

**[07:54]** At 0.5 and 0.6: only 2 survive.

> *On screen:* The slider passes 0.5 and only two dots remain.

Between 0.5 and 0.6 the large 0.4–0.5 band is gone and only the two copies of the golden-retriever sentence (about 0.686) survive. A threshold here keeps only the genuinely relevant result.

**[07:58]** From 0.7 up: nothing at all.

> *On screen:* The slider passes 0.7 and the last dots disappear; the counter reads 0.

The best score for this query is below 0.7, so every threshold from 0.7 upwards returns nothing. The right result existed, but the threshold was set too high.

### Measured sweep (limit 50)

**[08:04]** Same query, ten thresholds: 44, 44, 44, 44, 26, 2, 2, 0, 0, 0.

> *On screen:* A table and bar chart of all ten measured counts build up.

Measured (limit 50): thresholds 0.0, 0.1, 0.2 and 0.3 → 44 results; 0.4 → 26; 0.5 → 2; 0.6 → 2; 0.7, 0.8 and 0.9 → 0. The steep drop between 0.3 and 0.5 is typical: most results are background noise, and there are only a few real matches.

### The trade-off

**[08:10]** Lower keeps more but lets weak matches in. Higher is stricter, until nothing is left.

> *On screen:* A see-saw tilts between "more results" and "only confident results".

A low threshold favours **recall**: you miss nothing, but weak, irrelevant results come back too. A high threshold favours **precision**: what you get is relevant, but go too high and you get nothing at all.

### So which threshold?

**[08:16]** The README suggests 0.0 for discovery and 0.5+ to keep weak context out of RAG.

> *On screen:* Two boxes appear: "broad discovery: 0.0" and "RAG context: 0.5+".

The project README advises no threshold for exploratory search, and 0.5 or higher for RAG, so that weak context doesn't reach the LLM and encourage made-up answers. That's a sensible starting point, not a universal rule.

**[08:21]** But scores depend on the model, the data and the query, so calibrate.

> *On screen:* A "calibrate" note is stamped next to the two boxes.

Cosine scores depend on the model, the content and even the type of query, so a number that works for one setup can fail for another. Calibrate on your own data: run real queries, mark which results are relevant, and choose the threshold that keeps them.

**[08:24]** A fixed 0.7 would keep the RAG answers but return nothing for the beach query.

> *On screen:* The RAG scores (about 0.84) and the beach query's best score (0.686) are placed either side of a 0.7 line.

The RAG questions in chapter 7 scored about 0.84, so a 0.7 threshold would keep them. The beach query's best match is only 0.686, so the same 0.7 would return nothing. One fixed threshold can't suit both kinds of query, which is why calibration matters.

### Key takeaways  `[08:31]`

- score_threshold drops results below a cosine score
- Measured: 44 → 26 → 2 → 0 as the threshold rises
- Low = more recall, high = more precision
- Pick thresholds per use case, calibrated on your data

---

## Chapter 7 — RAG retrieval: find the right doc

**Starts at 08:45** · length 01:16 · source `E07-rag-knowledge-base` · hook: *"How does a question find the one policy that answers it?"*

**What you'll learn.** This chapter covers the **retrieval half of RAG**, using the six-document company knowledge base from `demo.py` (section 11). It shows questions with no shared keywords still finding the right policy through meaning alone, with the measured cosine scores. It also shows two real-world problems: duplicate result slots (see chapter 3) and choosing a score threshold (chapter 6). The project stops at retrieval: passing the retrieved documents to an LLM is not implemented.

### A tiny company knowledge base

**[08:51]** 6 policy documents, each embedded at dim 756 and stored in Qdrant.

> *On screen:* Six policy cards (HR, infra, product) appear inside a Qdrant box.

The knowledge base has six short policies: parental leave, a learning budget, deployment approvals, database backups, API rate limits and webhook retries. Each was embedded at dim 756 and stored as its own point with a `source_id` such as `kb-hr-001`.

### Ask a question → embed it → nearest doc

**[08:59]** Closest vector: the parental-leave policy, cosine score 0.8381.

> *On screen:* The question "How much parental leave do employees get?" flows through Gemini Embedding 2 and an arrow lights up the parental-leave card.

The question is embedded with the same model and size as the documents. Qdrant returns the nearest vector by cosine similarity: `kb-hr-001`, "16 weeks of paid leave for primary caregivers", scoring **0.8381**. The question and the document share few words; the match comes from meaning.

**[09:04]** Deployment question → kb-infra-001 (two approvals + CI), score 0.8477.

> *On screen:* A second question lights up the deployment-policy card.

"What is the deployment approval process?" retrieves `kb-infra-001`, "All production deployments require two approvals and a passing CI pipeline", at **0.8477**. The question says "approval process" and the document describes what is required; the embedding treats them as the same idea.

**[09:10]** Rate-limit question → kb-product-001, score 0.8528. No keywords needed.

> *On screen:* A third question lights up the API rate-limit card.

"What are the API rate limits?" retrieves `kb-product-001`, "1,000 requests per minute per API key", at **0.8528**. (The README calls this document `kb-api-001`; the code and the measured output use `kb-product-001`.)

### Wait: the top 2 were the same doc

**[09:17]** Asked for 2 results, got the same document twice.

> *On screen:* The result panel shows rank 1 and rank 2 holding the same parental-leave card.

The demo asked for the top 2 results, but both slots contained the same document at the same score. This is the duplicate-ID problem from chapter 3.

**[09:21]** Each run stored new points with random IDs, so every document exists twice.

> *On screen:* Two identical copies of each policy card appear side by side in the collection.

Because each run stored new points with random `uuid4` IDs, every policy exists twice. Qdrant isn't wrong here: it really does hold two equally similar points.

**[09:26]** Duplicates waste result slots: your top 2 should be 2 different docs.

> *On screen:* The duplicate slot is crossed out and a different document takes its place.

In RAG, every result slot is context you could give the LLM. A duplicate wastes that slot, and the second most relevant document never gets retrieved. Deterministic IDs (chapter 3), or deduplicating by `source_id` after the search, fix this.

### Score threshold: keep only confident matches

**[09:32]** The demo asked Qdrant to drop anything scoring below 0.4.

> *On screen:* A threshold line is drawn at 0.4 on a score axis.

The demo's RAG search used `score_threshold=0.4` (`visualize.py` used 0.3). Anything below the line isn't returned, so a question with no good answer in the knowledge base returns nothing instead of a weak, misleading match.

**[09:35]** All three right answers scored about 0.84, far above the cut-off.

> *On screen:* The three answer scores land at about 0.84, well to the right of the line.

All three correct documents scored between 0.838 and 0.853, far above 0.4, so the threshold doesn't hurt recall here. A gap that clear is what you want to see when you calibrate (chapter 6).

### Retrieval is half of RAG

**[09:42]** This project does the retrieval. Handing the docs to an LLM is the next stage.

> *On screen:* A pipeline is drawn: question → retrieve (solid) → prompt → LLM answer (dashed, labelled next step).

Retrieval-augmented generation has two halves: find relevant context, then have an LLM write an answer using only that context. This project implements and measures the first half. The prompt-building and LLM steps are drawn dashed because they're not in this codebase; they would be the next thing to build.

### Key takeaways  `[09:48]`

- Question and docs are embedded with the same model
- Nearest vector = most relevant doc (scores ≈ 0.84)
- Unique, deterministic IDs prevent duplicate results
- Threshold + LLM step turn retrieval into full RAG

---

## Chapter 8 — Recommendations: more like this

**Starts at 10:02** · length 01:01 · source `E08-recommendations` · hook: *"Can a model know headphones and earbuds belong together, with no categories?"*

**What you'll learn.** The same nearest-neighbour search becomes a "more like this" recommender. This chapter embeds a six-product catalogue from `demo.py` (section 12) as plain text, queries with one product as the seed, and reads off the measured similarities. It needs only the basics from chapters 1 and 3. The lessons are practical: exclude the seed, deduplicate IDs, and notice that no category labels were needed.

### A 6-product catalogue, text only

**[10:07]** Each product is just a line of text, embedded at dim 756. No category field.

> *On screen:* Six product lines type in as a plain-text catalogue.

The catalogue is Sony WH-1000XM5, Bose QuietComfort 45, Apple AirPods Pro 2nd gen, Samsung Galaxy Buds2 Pro, Logitech MX Master 3 mouse and Apple Magic Keyboard. Each line was embedded at dim 756. The payload has no category or price field, only the text's meaning.

### Similar meaning → nearby vectors

**[10:15]** Headphones and earbuds land close together; mouse and keyboard sit apart.

> *On screen:* The products drift onto a 2-D map: audio gear clusters on one side, mouse and keyboard on the other.

The map is **illustrative**; the real vectors have 756 dimensions. It shows what the scores imply: headphones and earbuds are close to each other in meaning, and the computer accessories sit further away.

### Seed: Sony WH-1000XM5

**[10:20]** Search with the seed's own text: 'Sony WH-1000XM5 wireless noise-cancelling headphones'.

> *On screen:* The Sony card is picked up and used as the search query.

The recommender is ordinary nearest-neighbour search where the query is an existing item's own text: "Sony WH-1000XM5 wireless noise-cancelling headphones". The nearest products are its recommendations.

**[10:25]** Bose 0.776, Galaxy Buds2 0.720: the nearest neighbours are other audio gear.

> *On screen:* Score bars grow for Bose (0.776) and Galaxy Buds2 (0.720).

Measured scores: Bose QuietComfort 45 at **0.776** and Samsung Galaxy Buds2 Pro at **0.720**, both audio products. The mouse and keyboard rank lower; the project doesn't record their exact scores.

### Lesson 1: drop the seed itself

**[10:29]** Rank 1 is always the seed (score 1.000): identical text, identical vector.

> *On screen:* The seed's own bar at 1.000 is highlighted, then crossed out.

The top result is always the seed itself, at a score of 1.000, because identical text produces an identical vector. A recommender must filter it out, for example by excluding the seed's `source_id`, or it will recommend the item the user is already looking at.

### Lesson 2: duplicates steal result slots

**[10:38]** Every product was stored twice, so 4 slots held only 2 products.

> *On screen:* Four result slots fill with Sony, Sony, Bose, Bose.

With `limit=4` and a 0.5 threshold, the demo returned only Sony and Bose, each twice, because every product was stored twice (the duplicate-ID problem from chapter 3).

**[10:42]** A real match got pushed out. Unique IDs per product fix this.

> *On screen:* Galaxy Buds2 is pushed out of the list, then returns once the duplicates are removed.

Galaxy Buds2 (0.720) clears the 0.5 threshold, but the duplicates filled all four slots first, so a genuine recommendation was lost. With unique IDs per product, the four slots would hold four different products.

### Lesson 3: no category labels needed

**[10:47]** The grouping came only from the meaning of the product text.

> *On screen:* A "no labels" badge appears over the audio cluster.

Nobody told the system which products are audio devices. The grouping comes purely from the meaning of the product descriptions. That makes embedding-based recommendations work on day one for a new catalogue, before any user behaviour data exists.

### Key takeaways  `[10:52]`

- Recommend = search with the seed item's embedding
- Exclude the seed: it always scores 1.000
- Duplicate points crowd out real matches
- Similar products cluster without any labels

---

## Chapter 9 — 6 production lessons

**Starts at 11:04** · length 01:22 · source `E09-production-lessons` · hook: *"What this multimodal search project teaches about running embeddings for real"*

**What you'll learn.** The closing chapter collects six engineering lessons visible in this codebase. Each is tied to a specific file: `vector_store.py` (IDs), `embedding_service.py` (retries, batching, multi-dimension calls), `demo.py` / `visualize.py` (the stub image), and `tests/` (mocked unit tests). Some of these turn up as symptoms in earlier chapters, such as duplicate results and slow two-stage queries. Here each one is named, with a fix. The fixes are suggestions; none of them is implemented in the project yet.

### 1. Random IDs create duplicates

**[11:12]** Re-running the demo doubled every document. Deterministic IDs make writes idempotent.

> *On screen:* Two copies of a document merge into one as a uuid4 label is replaced by uuid5(source_id).

Lesson 1 sums up the problem behind chapters 3, 7 and 8: random `uuid4` IDs mean every re-run inserts a second copy. Deriving the ID from `source_id` (for example `uuid5`) makes re-indexing **idempotent**: running it twice gives the same result as running it once.

### 2. Retry with exponential backoff

**[11:19]** Up to 3 attempts, waiting 1 s then 2 s, for rate limits, timeouts and API errors.

> *On screen:* A retry timeline draws three attempts with 1 s and 2 s gaps between them.

`_execute_with_retry` in `embedding_service.py` makes up to 3 attempts, sleeping `1.0 × 2^attempt` seconds between them (1 s, then 2 s). It retries rate-limit (`ResourceExhausted`), timeout (`DeadlineExceeded`) and generic API errors, which are often temporary.

**[11:22]** Retrying a bad credential never helps, so it stops immediately.

> *On screen:* An auth-error attempt stops at once with a red X.

`Unauthenticated` and `PermissionDenied` are raised immediately as `AUTH_FAILED`. Retrying a wrong key or missing permission can never succeed, so failing fast gives a clear error instead of a slow one.

### 3. 'Batch' is really a loop

**[11:31]** Items are embedded sequentially: about 1.9 documents per second (dims 128 to 1024).

> *On screen:* Documents pass through the API one at a time in a single lane, with a ≈1.9 docs/sec counter.

`embed_batch` is a sequential loop that makes one API call per item. The measured throughput was about 1.84–1.95 documents per second at every size from 128 to 1024. In other words, the time goes on waiting for the network, not on computing the vector.

**[11:36]** Network round-trips dominate, so concurrency is the real speed-up.

> *On screen:* The single lane splits into several parallel lanes.

Since each call is mostly network wait, sending requests concurrently (within your API quota) is the real speed-up. Choosing a smaller dimension barely changes throughput. This is general advice; the current code doesn't do it.

### 4. One call per dimension: avoidable

**[11:44]** Smaller Matryoshka vectors are a rescaled prefix of the big one, so truncate locally.

> *On screen:* Two separate API calls (256 and 1024) are replaced by one call followed by a local cut and rescale.

`embed_with_multiple_dimensions` makes one API call per size. The measured outputs are consistent with each smaller vector being the first d numbers of the larger one, rescaled to length 1 (chapter 2). So one large call followed by local truncation and renormalization could replace several calls. Check that the results match on your data first.

### 5. Test with real data

**[11:53]** One blank pixel carries no meaning, so cross-modal search was never really tested.

> *On screen:* The stub image enlarges to a single blank pixel next to its 0.3236 score.

Every image test in the demo used the same 1×1-pixel stub JPEG. That proved the API path works, but it never tested whether a text query actually finds a relevant image. Representative real data is needed before trusting any quality result.

### 6. Unit tests and secrets

**[12:03]** Mocks make tests fast and free, but they can't tell you if results are relevant.

> *On screen:* A "76 passed" test badge appears beside a mocked-client box.

The 76 unit tests mock the Gemini client, so they're fast, free and deterministic. They check validation, retry logic and request structure. They cannot check relevance; that needs an evaluation set with real embeddings.

**[12:07]** Example env files are committed, so keep only placeholders there and rotate any leaked key.

> *On screen:* An example env file appears with placeholder values and a "rotate keys" note.

Example env files get committed to git, so they should only ever hold placeholders such as `your-api-key`. If a real key was ever committed, assume it's exposed: rotate it, then remove it from the file and from history. This is general good practice.

### Key takeaways  `[12:14]`

- Deterministic IDs: re-runs overwrite, never duplicate
- Retry transient errors with backoff; fail fast on auth
- Parallelize calls; truncate Matryoshka vectors locally
- Test with real data, and keep secrets out of git
