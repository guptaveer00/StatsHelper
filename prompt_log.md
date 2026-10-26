# Stats Helper prompt log

## Tools and authorship

Development started October 26, 2026 in the Codex desktop app. Codex assisted
with planning, source inspection, and initial environment/persistence setup.
The exact underlying model identifier has not been verified. Python, pip,
Git, and ChromaDB are the initial development tools. No work-hour total is
claimed. This log is incomplete and must grow with actual development.

## Important project-specific user prompts (verbatim)

The conversation began with the student's prior-project context and the full
assignment text. Those long messages are not reproduced here; they were supplied
before implementation. Their omission does not mean they were not used.

> i like the study helper

> use this stats textbook:
> [https://www.stat.cmu.edu/\~brian/valerie/617-2022/0%20-%20books/2004%20-%20wasserman%20-%20all%20of%20statistics.pdf](https://www.stat.cmu.edu/~brian/valerie/617-2022/0%20-%20books/2004%20-%20wasserman%20-%20all%20of%20statistics.pdf)

> call it Stats Helper

> ok

The final "ok" followed the assistant's proposal to create a fresh local
repository, save two proposed search tests, and run a Chroma persistence test.

## Actual development record

- Inspected the linked PDF through web tools; it has 459 PDF pages and extractable
  text. Equation extraction quality still needs local inspection.
- Proposed two semantic queries in design_notes.md before writing code. Neither
  is yet a verified retrieval success.
- Created a separate StatsHelper folder and virtual environment under
  Documents/Codex. Existing portfolio files were not edited.
- Consulted Chroma's current Python reference for PersistentClient. An initially
  attempted documentation URL returned 404; the reference page was found next.
- Installed ChromaDB 1.5.9 in the isolated environment after retrying a blocked
  network download. Downloaded its free local embedding model into the project.
- Ran smoke_test.py in two separate processes: first count went from 0 to 1;
  second count remained 1 before and after the duplicate check. Disk persistence
  is verified for this synthetic test item. The textbook is not indexed yet.
- Added a README with clearly labeled AI setup instructions and placeholders for
  the student's required writing. No completed-app claims or hours were invented.

README's required personal sections must be written by the student. Do not
present this AI-maintained record as personal writing or evidence of 4.5 hours.

## Project location change

User prompt (verbatim):

> nah can u svae this in a flder on my desktop then we can commit to github when finish

Moved the complete project to `/Users/veergupta/Desktop/StatsHelper`, updated
virtual environment paths, and reran the persistence test successfully (count 1
before and after). No commit, GitHub remote, push, or deployment was created.

## Textbook download and indexing stage

Important user prompts (verbatim):

> what next

> idk how to this all of this, can u just downlaod and uplaod the pdf here and u do it?

Codex downloaded the user-selected PDF directly into the Desktop project's
ignored data directory. The student did not need to upload a copy to chat.
Codex implemented storage.py and textbook.py for staged download, extraction,
batch indexing, and search, consulting current Chroma and PyMuPDF docs.
A pypdf extraction experiment reported missing font support; PyMuPDF's text
blocks were used instead, and a rendered bootstrap page was visually compared
with extracted prose. Mathematical notation remains imperfect and is explicitly
not treated as a reliable formula transcription.

An actual AI implementation error: the first heading detector mistook short
numbered theorems/definitions for section headings. Inspection exposed the
incorrect metadata. The detector was corrected to exclude those labels and
sentence punctuation; existing metadata was refreshed without re-embedding.

Extracted 313 prose passages from chapters 1–16, each at most 230 model tokens.
The 50-item embedding trial took 0.69 seconds; the remaining 263 took 4.16
seconds. A separate process reopened all 313 records. No time spent by the
student is inferred from machine execution time.

Both originally proposed semantic test queries failed to retrieve the intended
sections in the top five. Additional diagnostic rephrasings and an unrelated
concert-ticket query were tried; full results are saved locally in
`data/retrieval_checks.json`. No assignment-query success is claimed. The app
still needs retrieval improvement, runtime note entry, and useful study output.
A sandboxed search initially failed because Chroma needs write access even when
searching; rerunning with authorized Desktop access succeeded. No push or commit.

## Interactive app and retrieval improvement

User prompt (verbatim):

> okay next continue

Codex rechecked local files, Git status, and remotes before editing. The repository
still had no remote, so there were no remote changes to fetch. No Git commit,
push, portfolio edit, or deployment was performed.

Retrieval investigation showed that the v1 extractor dropped short explanatory
blocks and kept useful section context only in metadata. Codex retained shorter
prose blocks, grouped neighboring retained blocks by page and section, and
embedded section/chapter context with the real content. The new study_v2 index
has 397 passages; the original 313-passage collection and diagnostics remain
local. Maximum actual textbook input is 226 tokens. The 50-item trial took 0.67
seconds, and the remaining 347 took 3.88 seconds; these are computation times,
not hours the student worked.

The original two proposed queries still did not reliably retrieve the intended
sections. Codex evaluated additional realistic phrasings and saved the raw local
diagnostics. The final repeatable examples are:

- "Why does seeing a rash not guarantee a particular diagnosis?" — conditional
  probability, PDF page 27, rank 1, distance approximately 0.707.
- "Why can an association reverse direction after pooling subpopulations?" —
  Simpson's paradox, PDF page 276, rank 3, distance approximately 0.708.

Both target items have zero overlapping non-stopword literal query words and
appear in the three-source reading guide. This is a literal-word check, not a
claim that all stems or semantic families differ. The second source needs the
following PDF page for its numeric example. A provisional cosine cutoff of 0.75
rejects three recorded unrelated requests; results at or above 0.65 are labeled
weak. Neither setting guarantees relevance.

Codex implemented app.py and study.py: an interactive menu, runtime note addition
with UUIDs and token-aware chunking, scope filtering, reading guides with source
references, source-sentence selection using local embeddings, cloze recall
practice with self-assessed scores, and Markdown guide saving. No generative
language model or external API is used. The source passages and explanations
can still have extraction artifacts, so the UI directs users to original pages.

Five integration tests passed (four initially, followed by the new menu test):
immediate add/search, guide/card generation, saved guide contents, metadata
scope filtering, long notes, unique IDs, input validation, note retrieval in a
fresh Python process, and the menu add/search/practice/status/save/quit flow.
Tests use temporary databases, not the user's library. The semantic verification
script recorded both target ranks and rejected concert-ticket, laptop-refund,
and movie requests. The Desktop launcher was made executable and checked with
zsh's syntax checker; Finder launch itself was not UI-tested.

The README was rewritten to match the implemented app. All AI-authored technical
notes are labeled below the student's four still-empty required personal
sections. The student must actually use the app and write those sections in
personal words. This log records real prompts and work; it does not establish
4.5 hours, invent student contributions, or replace the student's learning.

## Final technical verification

User prompt (verbatim):

> i dont have time to check all this, can u just check for me

Codex rechecked the actual project and ran all five integration tests again;
all passed. Real-corpus checks again placed conditional probability first and
Simpson's paradox third, with no important literal word overlaps in the target
items. The three unrelated diagnostic queries were rejected by the cutoff.

To test the instructions as another GitHub user would, Codex copied only the
13 publishable source/documentation files to a separate scratch folder, with
no existing environment, model cache, PDF, or database. A new Python 3.13 virtual
environment installed requirements.txt successfully; pip check reported no
broken requirements. The documented download/extract/50-item trial/full-load
sequence independently downloaded the PDF and model, rebuilt 397 passages,
reproduced both semantic examples, and passed all five integration tests.
The scratch install was on the same Mac; cross-platform support is not claimed.

The actual Desktop .command launcher was run in a terminal. Library status
reported 397 textbook passages and zero user notes; quitting and closing the
launcher completed successfully. Finder double-click behavior was not UI-tested.
No synthetic test notes were inserted into the user's real library.

The Git-eligible file list excluded data, database, virtual environment, and
model cache directories. A basic scan of those files found no common API-token
or private-key patterns; this is not a claim of comprehensive security auditing.
The README now reflects the verified fresh setup. No application defects were
found in these checks, so no functional code change was needed.

Still outstanding for submission: the student's required personal README
writing, honest work-time/process evidence, a demo video, GitHub publication,
a portfolio repository link, and submission. Technical checks do not establish
student authorship or replace those requirements. No GitHub upload or commit was
made in this step.

## GitHub publication

User prompt (verbatim):

> push to github pls

Codex rechecked the repository's actual files, status, and remotes. There was no
existing commit or remote. Using the existing macOS credential helper without
printing credentials, Codex created a new public repository at
https://github.com/guptaveer00/StatsHelper. The helper initially failed when
queried with an explicitly assumed username; allowing its stored username
worked. GitHub confirmed the authenticated account was guptaveer00 before the
repository was created. No credentials were written into project files.

The README was updated with the public source link, clone/ZIP instructions,
and an accurate explanation that GitHub distributes the code rather than
running a hosted app. The required personal sections remain clearly marked as
unfinished. Source files are being committed and pushed on main; the textbook,
private notes/database, model cache, and environment are excluded. This is the
first real local commit, not a fabricated history of incremental commits.
