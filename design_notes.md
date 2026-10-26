# Stats Helper — planning before code

Source: Larry Wasserman, All of Statistics, user-selected CMU-hosted PDF:
https://www.stat.cmu.edu/~brian/valerie/617-2022/0%20-%20books/2004%20-%20wasserman%20-%20all%20of%20statistics.pdf

One item: a short textbook passage or user-added note, with source, chapter,
and page metadata where available. Chunk size must be checked against the
embedding model's token limit. Equations need extraction checks.

Useful output: assemble a source-linked reading guide from related passages,
with a reading order and self-check prompts. Generation method is undecided.

## Proposed semantic tests — NOT verified results

1. "Can I recycle the observations I already collected to figure out how shaky my answer is?"
   Target: bootstrap material.
2. "How can a trend flip when I combine separate groups?"
   Target: Simpson's paradox material.

Before claiming either passes, run it against real indexed passages, record
the actual item and rank, and check for important overlapping words.
These examples were proposed by AI, not written by the student.

## Next stages

1. Confirm Chroma imports and disk persistence with a tiny smoke test.
2. Inspect extracted textbook passages and choose chunk boundaries.
3. Time 50 real passages before embedding a larger subset.
4. Inspect retrieval distances, including unrelated queries.
5. Build runtime note addition and useful study output.

This is a new standalone project, separate from the portfolio repository.

## Implemented outcome after retrieval experiments

The two initial queries above remain failed attempts. The app now uses a new
397-item study_v2 index with chapter/section context embedded alongside prose.
A rash/diagnosis query retrieves conditional probability first; an association
reversal/pooling query retrieves Simpson's paradox third. Exact wording, IDs,
distances, and evidence are in verify_semantics.py and the README's labeled
AI notes. These examples were proposed by AI, not written by the student.

Useful output is an extractive reading guide plus source-grounded cloze recall
cards, practice with self-assessment, and saved Markdown with original-page
links. No language model is used. The menu also adds persistent notes at runtime.
Five integration tests and real-corpus diagnostic checks passed; weak matches
and broken mathematical extraction remain explicit limitations.
