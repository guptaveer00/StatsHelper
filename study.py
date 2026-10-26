"""Semantic retrieval, persistent notes, and source-based active-recall guides."""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
from uuid import uuid4

import numpy as np

from storage import ROOT, full_tokenizer, open_collection, split_to_fit

# Conservative exploratory cutoff, calibrated against the bundled diagnostics.
# A distance is not a confidence percentage; this is not a universal boundary.
MAX_DISTANCE = 0.75
WEAK_DISTANCE = 0.65
STOPWORDS = set("""a an the and or but if then than this that those these there
their they we you your our its it is are was were be been being to of in on
for from by with without as at not no can could should would will do does
have has had such which what when where why how all any each some many much
more most very also only other into about because example consider suppose
called given using use used let since however therefore hence means
""".split())


@dataclass
class Match:
    id: str
    text: str
    metadata: dict
    distance: float


@dataclass
class Card:
    prompt: str
    answer: str
    source: str


@dataclass
class Guide:
    query: str
    matches: list
    key_sentences: list
    cards: list
    scope: str


def source_label(match):
    m = match.metadata
    if m["kind"] == "textbook":
        return f"{m['section']} — book p. {m['book_page']} (PDF p. {m['pdf_page']})"
    return f"Your note: {m['title']} — {m['created_at'][:10]}"


def body_text(text):
    return text.split("\n", 1)[-1]


def sentences(text):
    candidates = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", body_text(text))
    good = []
    for sentence in candidates:
        sentence = re.sub(r"^\d+(?:\.\d+)?\s+(?:Example|Definition|Remark)\.\s*", "", sentence)
        words = sentence.split()
        # Do not turn equation fragments or truncated sentences into flashcards.
        if not (8 <= len(words) <= 55) or not sentence.endswith((".", "!", "?")):
            continue
        if re.search(r"[=<>∫∑θσβµμˆ]|/brace|\b[A-Z]\d", sentence):
            continue
        if sum(c.isalpha() or c.isspace() for c in sentence) / len(sentence) < 0.89:
            continue
        good.append(sentence)
    return good


def make_card(sentence, match):
    words = re.findall(r"\b[A-Za-z][A-Za-z'-]{3,}\b", sentence)
    usable = [w for w in words if w.lower() not in STOPWORDS]
    if not usable:
        return None
    title_words = set(re.findall(r"[a-z]+", match.metadata.get("section", "").lower()))
    # Prefer a concept from the section title; otherwise a substantial source word.
    answer = max(usable, key=lambda w: (w.lower() in title_words, len(w)))
    masked = re.sub(r"\b" + re.escape(answer) + r"\b", "________", sentence, flags=re.I)
    return Card(masked, answer, source_label(match))


class StudyHelper:
    def __init__(self, collection=None, embedding=None):
        if collection is None:
            collection, embedding = open_collection()
        self.collection = collection
        self.embedding = embedding
        self.tokenizer = full_tokenizer(embedding)

    def add_note(self, title, text):
        title, text = title.strip(), text.strip()
        if not title or not text:
            raise ValueError("A title and note text are both required.")
        if len(title) > 100:
            raise ValueError("Keep the title under 101 characters.")
        if len(text) > 30000:
            raise ValueError("Please add at most 30,000 characters per note.")
        prefix = f"Your note: {title}\n"
        prefix_tokens = len(self.tokenizer.encode(prefix).ids)
        if prefix_tokens > 80:
            raise ValueError("Please use a shorter title.")
        parts = list(split_to_fit(text, self.tokenizer, 228-prefix_tokens))
        group = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        docs = [prefix + part for part in parts]
        if any(len(self.tokenizer.encode(doc).ids) > 230 for doc in docs):
            raise ValueError("Could not safely split this note; please use shorter words.")
        ids = [f"note-{group}-{i}" for i in range(len(parts))]
        self.collection.add(
            ids=ids, documents=docs,
            metadatas=[{"kind": "note", "source": "User-added note", "title": title,
                        "note_group": group, "part": i+1, "parts": len(parts),
                        "created_at": now, "tokens": len(self.tokenizer.encode(doc).ids)}
                       for i, doc in enumerate(docs)],
        )
        return ids

    def retrieve(self, query, scope="all"):
        query = query.strip()
        if not query:
            raise ValueError("Type a question first.")
        if len(self.tokenizer.encode(query).ids) > 256:
            raise ValueError("Please shorten your question to at most 256 model tokens.")
        if scope not in ("all", "textbook", "notes"):
            raise ValueError("Choose all, textbook, or notes.")
        if not self.collection.count():
            return []
        kwargs = {} if scope == "all" else {"where": {"kind": "note" if scope == "notes" else "textbook"}}
        result = self.collection.query(
            query_texts=[query], n_results=min(15, self.collection.count()),
            include=["documents", "metadatas", "distances"], **kwargs,
        )
        matches, seen = [], set()
        for id_, text, metadata, distance in zip(
                result["ids"][0], result["documents"][0],
                result["metadatas"][0], result["distances"][0]):
            if distance > MAX_DISTANCE:
                continue
            # One result per textbook page or note avoids repetitive reading plans.
            key = (metadata["kind"], metadata.get("pdf_page", metadata.get("note_group")))
            if key in seen:
                continue
            seen.add(key)
            matches.append(Match(id_, text, metadata, float(distance)))
            if len(matches) == 3:
                break
        return matches

    def make_guide(self, query, scope="all"):
        matches = self.retrieve(query, scope)
        key_sentences, cards = [], []
        for match in matches:
            options = sentences(match.text)
            selected = None
            if options:
                vectors = np.asarray(self.embedding([query] + options), dtype=float)
                norms = np.linalg.norm(vectors, axis=1, keepdims=True)
                vectors = vectors / np.maximum(norms, 1e-12)
                index = int(np.argmax(vectors[1:] @ vectors[0]))
                selected = options[index]
                card = make_card(selected, match)
                if card:
                    cards.append(card)
            key_sentences.append(selected)
        return Guide(query.strip(), matches, key_sentences, cards, scope)

    def status(self):
        result = self.collection.get(include=["metadatas"])
        metadatas = result["metadatas"]
        notes = [m for m in metadatas if m["kind"] == "note"]
        return {"textbook_passages": sum(m["kind"] == "textbook" for m in metadatas),
                "notes": len({m["note_group"] for m in notes}), "note_chunks": len(notes)}


def guide_markdown(guide):
    lines = ["# Stats Helper study guide", "", f"Question: {guide.query}",
             f"Search: {guide.scope}", "",
             "Source-based reading and recall, not a generated explanation. Check formulas in the PDF.", ""]
    if not guide.matches:
        lines.append("No close matches under the current exploratory cutoff. Try a more specific statistics question.")
        return "\n".join(lines) + "\n"
    lines += ["## Read in this order", ""]
    for index, (match, sentence) in enumerate(zip(guide.matches, guide.key_sentences), 1):
        lines += [f"### {index}. {source_label(match)}", "",
                  f"Cosine distance: {match.distance:.3f} (lower is closer; not a confidence percentage).", ""]
        if match.distance >= WEAK_DISTANCE:
            lines += ["Possible starting point: match is weak. Check whether it addresses your question.", ""]
        if sentence:
            lines += ["Key sentence from source:", "", f"> {sentence}", ""]
        else:
            lines += ["No clean complete sentence found for a flashcard. Read the original source.", ""]
        lines += ["Retrieved passage (text extraction may contain broken notation):", "", body_text(match.text), ""]
        if match.metadata["kind"] == "textbook":
            page = match.metadata["pdf_page"]
            lines += [f"[Open original page]({(ROOT / 'data' / 'all-of-statistics.pdf').as_uri()}#page={page})", ""]
        lines += ["After reading: explain how this passage helps answer your question, and name one assumption or limitation.", ""]
    lines += ["## Recall practice", "", "Fill each blank before checking its answer.", ""]
    for i, card in enumerate(guide.cards, 1):
        lines += [f"{i}. {card.prompt}", f"   Source: {card.source}", "",
                  f"   Answer: {card.answer}", ""]
    if not guide.cards:
        lines.append("No reliable text-based recall cards could be made from these passages.")
    return "\n".join(lines) + "\n"


def save_guide(guide, directory=None):
    directory = Path(directory) if directory else ROOT / "data" / "guides"
    directory.mkdir(parents=True, exist_ok=True)
    filename = datetime.now(timezone.utc).strftime("study-%Y%m%d-%H%M%S-%f.md")
    path = directory / filename
    path.write_text(guide_markdown(guide), encoding="utf-8")
    return path
