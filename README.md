# Stats Helper

Local command-line study helper. Public source: https://github.com/guptaveer00/StatsHelper

This README is still a draft until the student writes the four required personal sections below.

## Student-written sections — complete these in your own words

1. **Purpose and motivation:** What does your app do, and why did you choose it?
2. **Your data:** Explain the source, what one item is, chunking, actual count,
   and metadata. Inspect the code and facts below before writing.
3. **Adding and searching:** Explain the real user flow after trying it yourself.
4. **Two semantic examples:** Run the verified examples below and explain the
   retrieved items and why keyword matching misses them, in your own words.

## AI-generated technical notes

Everything below this heading was written by Codex. It is reference material,
not the student's personal writing. Codex implemented the Python code, proposed
and evaluated search examples, debugged extraction, and ran tests. The student
chose the study-helper direction, textbook, project name, and Desktop location.
See the separate `prompt_log.md` for actual prompts and development history.
No work-hour total or student code contribution is inferred.

### Start the app

On the already-configured development Mac, double-click **Start Stats Helper.command**
in the StatsHelper folder on the Desktop. Alternatively:

```sh
cd /Users/veergupta/Desktop/StatsHelper
source .venv/bin/activate
python app.py
```

For another machine, use Python 3.13 (tested; other versions not verified).
Download this repository with GitHub’s Code → Download ZIP button and open a
terminal in the extracted folder. Alternatively, if Git is installed:

```sh
git clone https://github.com/guptaveer00/StatsHelper.git
cd StatsHelper
```

Then install dependencies and build the local database:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python textbook.py download
python textbook.py extract
python textbook.py load --limit 50
python textbook.py load
python app.py
```

The install can be large. The free local all-MiniLM-L6-v2 ONNX embedding model
also downloads about 79 MB on first use, into `.model_cache/`. After installation,
model download, and textbook indexing, normal operation needs no network, paid
service, language-model API, or API key. ChromaDB is pinned to 1.5.9 and PyMuPDF
to 2.0 in `requirements.txt`.

### Menu and useful output

1. **Make a study guide:** ask a question and choose all sources, the textbook,
   or your notes. Semantic retrieval selects up to three distinct source pages
   or notes. The guide extracts a complete relevant sentence, shows original
   passages and page references, and prepares fill-in-the-blank recall cards.
2. **Add a note:** enter a title, paste text, and finish with a single period (`.`)
   on its own line. A blank title cancels. Notes are embedded immediately, use
   unique UUID-based IDs, and persist on disk. Long notes are split safely.
3. **Practice last guide:** recall the missing source word before revealing it,
   then mark whether you remembered it. The app reports your self-assessed score.
4. **Library status:** see textbook passages, logical notes, and note chunks.
5. **Save last guide:** write Markdown to `data/guides/`, including original-PDF
   page links and recall answers. The last guide itself is only held in memory
   unless saved; notes and indexed textbook passages persist automatically.
0. **Quit.**

The guide is an extractive reading-and-recall tool, not a generative tutor.
A local embedding comparison chooses a sentence from each retrieved passage;
cloze answers are words taken from those sentences. No language model writes
new statistical claims. This turns retrieval into a study session rather than
just a list of raw results. You still need to check context and formulas.

One-query mode is also available:

```sh
python app.py --query "Why does seeing a rash not guarantee a particular diagnosis?" --scope textbook --save
```

### Corpus and source

Larry Wasserman, *All of Statistics*, Springer, 2004. User-selected source:
https://www.stat.cmu.edu/~brian/valerie/617-2022/0%20-%20books/2004%20-%20wasserman%20-%20all%20of%20statistics.pdf

The PDF has 459 pages. The current index contains **397 context-bearing text
passages from chapters 1–16**, not the entire book. The download is stored in
`data/all-of-statistics.pdf` and is not committed. Rebuild with the download,
extract, and load commands above; no personal data is needed to try the app.

One textbook item consists of section/chapter context plus a short group of
prose blocks from one PDF page. The extractor normalizes ligatures and
line-break hyphenation, ignores front matter and running headers, and retains
blocks with at least eight alphabetic words of length three or more and a
60% letter ratio. Figure captions and many isolated formula/table blocks are
excluded. Neighboring retained blocks in the same page/section are combined,
then split at word boundaries with a budget below 230 model tokens including
titles. The actual model tokenizer measures lengths with truncation disabled.
The largest current textbook item has 226 tokens; short fragments with fewer
than 15 alphabetic words of length three or more are skipped.

Metadata records source, type (`textbook` or `note`), chapter, section, PDF page,
printed book page, and token count. Notes instead include title, UUID group,
UTC creation timestamp, chunk number, total chunks, and token count. Note titles
and body text are both embedded, so the real content is searchable.

**Extraction limitations:** this is a prose subset. Mathematical symbols and
equations can be garbled, missing, or incomplete. Blocks joined around skipped
formulas may omit context; word-boundary splitting can leave sentence fragments.
The app avoids using incomplete or formula-heavy sentences for recall cards.
Consult the linked original PDF page for notation and the surrounding context.

The original 313-passage experiment and `textbook_v1` collection are retained
locally for development history. The app and loader now consistently use the
separate **`study_v2`** collection. `smoke_test.py` uses its own test collection.
These older collections do not contribute to the app's displayed corpus count.

### Two verified meaning-based searches

These examples were proposed and verified by AI. The student must try them and
write the required explanation personally in the first four sections above.
They replace the two initial design-note queries, which failed and remain
recorded honestly as failed attempts.

**Query 1:** “Why does seeing a rash not guarantee a particular diagnosis?”

- Retrieves **Conditional Probability**, printed book page 10 / PDF page 27,
  at rank **1**, cosine distance about **0.707**.
- The relevant passage contrasts spots given measles with measles given spots,
  then discusses reversing conditional probabilities and the prosecutor's fallacy.
- The query's important terms, such as “rash,” “guarantee,” and “diagnosis,” are
  absent from that stored item. Exact matching those terms would miss it.
- Stable ID: `wasserman-v2-p27-g1-1-1aaa8ab76cb7`.

**Query 2:** “Why can an association reverse direction after pooling subpopulations?”

- Retrieves **Simpson's Paradox**, printed book page 259 / PDF page 276,
  at rank **3**, cosine distance about **0.708**, after two related causal-inference
  passages. It is included in the three-source study guide.
- The relevant passage introduces the paradox and its counterfactual/graphical
  context. Continue to the next PDF page for the numerical example.
- The target item contains none of “association,” “reverse,” “direction,”
  “pooling,” or “subpopulations.” It instead uses the concept name and different
  statistical language. Exact keyword matching those query terms would miss it.
- Stable ID: `wasserman-v2-p276-g1-0-f7e3a41735d6`.

Reproduce and inspect the evidence:

```sh
python verify_semantics.py
```

This saves ranked documents, distances, exact IDs, and a basic non-stopword
word-overlap check to `data/semantic-verification.json`. That check compares
literal words, not stems, and does not prove semantic understanding by itself;
inspect the actual passage too. Neither example is claimed to work for every
possible paraphrase. The original bootstrap query still does not work reliably.

### Relevance and persistence

ChromaDB `PersistentClient` stores embeddings and metadata in `chroma_store/`.
Paths are anchored to the source files, so changing the shell's working directory
does not create a new database. Loading the same textbook again checks stable
IDs and skips already-indexed documents; metadata is refreshed.

The collection uses cosine distance: lower is closer. A provisional cutoff of
**0.75** rejects distant candidates, and matches at or above **0.65** are labeled
weak. These are empirical settings for this corpus/model, not confidence
percentages or a guarantee of relevance. Concert-ticket, laptop-refund, and
movie requests all returned zero accepted results during the recorded checks.
Some weak in-domain results are still irrelevant. Refine the question or inspect
the source rather than trusting the ranking as an answer. Scope filtering
combines exact metadata with semantic retrieval; it does not replace vectors.

The first improved 50-passage batch embedded in 0.67 seconds, and the remaining
347 took 3.88 seconds on the development machine. This is machine runtime, not
student time worked.

### Tests and a demo flow

```sh
python -m unittest -v test_study
python verify_semantics.py
```

Five integration tests cover immediate note retrieval, guide/recall generation,
Markdown saving, source filtering, long-note token limits, unique IDs, invalid
inputs, persistence in a separate Python process, and the interactive menu flow.
Test notes live in temporary databases and are not added to the user's library.

Suggested demo sequence (not a record of student work):

1. Open the app and show library status.
2. Add a short note of your own. Search for it using notes-only scope.
3. Run one verified textbook query above with textbook scope; show the relevant
   source and page, then practice a recall card and save the guide.
4. Quit and reopen; show that your note is still available.

A fresh source-only copy was installed into a new Python 3.13 virtual environment
with only requirements.txt. It independently downloaded the PDF and model, rebuilt
all 397 passages, passed all five tests, and reproduced both semantic examples.
The actual .command launcher was also executed in a terminal: library status
showed 397 passages and quitting completed successfully. Finder double-click
launch itself has not been exercised through UI automation. Other operating
systems have not been tested.

### Repository and privacy

`data/`, `chroma_store/`, `.model_cache/`, `.venv/`, and `.env` are Git-ignored.
This keeps the downloaded textbook, databases, private notes, generated study
guides, and model binaries out of Git. Do not force-add these directories.
The public GitHub repository distributes source code and setup instructions;
it does not host a running web app. No paid service or deployment is used.
The portfolio is separate and has not been edited.

### How the code fits together

- `storage.py`: one persistent collection, one consistent embedding model, and
  token-aware text splitting.
- `textbook.py`: repeatable textbook download, extraction, batched load, and raw
  search diagnostics (`search "question" --raw`).
- `study.py`: note ingestion, semantic retrieval, reading/recall guide generation,
  source references, status, and Markdown export.
- `app.py`: the interactive menu and one-query command-line mode.
- `verify_semantics.py`: repeatable checks against actual textbook records.
- `test_study.py`: temporary-database integration tests.

Chroma's query result contains an outer list for each query. This app submits
one question at a time, so `result['documents'][0]`, `result['metadatas'][0]`,
`result['ids'][0]`, and `result['distances'][0]` are parallel lists for that
question. The code zips those lists into ranked matches.

References consulted:

- Chroma Python client: https://docs.trychroma.com/reference/python
- Chroma collections: https://docs.trychroma.com/reference/python/collection
- PyMuPDF text extraction: https://pymupdf.readthedocs.io/en/latest/recipes-text.html
- Sentence embedding similarities: https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html
