"""Download, extract, index, and inspect a real textbook corpus in small stages."""
import argparse
import hashlib
import json
import re
import time
import unicodedata
from urllib.request import urlopen

import pymupdf

from storage import ROOT, full_tokenizer, open_collection, split_to_fit

URL = "https://www.stat.cmu.edu/~brian/valerie/617-2022/0%20-%20books/2004%20-%20wasserman%20-%20all%20of%20statistics.pdf"
DATA = ROOT / "data"
PDF = DATA / "all-of-statistics.pdf"
CHUNKS = DATA / "passages-v2.jsonl"


def download():
    DATA.mkdir(exist_ok=True)
    if PDF.exists():
        print(f"Already downloaded: {PDF}")
        return
    temporary = PDF.with_suffix(".download")
    try:
        with urlopen(URL, timeout=60) as response, temporary.open("wb") as output:
            while block := response.read(1024 * 1024):
                output.write(block)
        with pymupdf.open(temporary) as doc:
            if len(doc) < 400:
                raise ValueError("Unexpected textbook download; check source.")
        temporary.replace(PDF)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Downloaded: {PDF}")


def clean(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"([a-z])-\n([a-z])", r"\1\2", text)
    return " ".join(text.split())


def extract():
    if not PDF.exists():
        raise SystemExit("Run: python textbook.py download")
    _, embedding = open_collection()
    tokenizer = full_tokenizer(embedding)
    records = []
    chapter, section = "", ""
    with pymupdf.open(PDF) as doc:
        for index, page in enumerate(doc):
            blocks = page.get_text("blocks", sort=True)
            # Chapter openers contain printer marks, chapter number, and title.
            if blocks:
                match = re.search(r"Printer: Opaque this\s+(\d+)\s+(.+)", blocks[0][4], re.S)
                if match:
                    number = int(match[1])
                    if number > 16:
                        break
                    chapter = f"{number}. {clean(match[2])}"
                    section = chapter
            if not chapter:
                continue  # Skip front matter and contents.
            groups = []
            for block_index, block in enumerate(blocks):
                raw = block[4]
                # Remove running headers and printer/chapter title blocks.
                if block[1] < 110 or "Printer: Opaque this" in raw:
                    continue
                text = clean(raw)
                if (re.match(r"^\d+\.\d+\s+[A-Z]", text)
                        and len(text.split()) < 16
                        and not re.search(r"\b(Theorem|Example|Remark|Lemma|Definition|Proof|Exercise)\b", text)
                        and not re.search(r"[.!?]", re.sub(r"^\d+\.\d+", "", text))):
                    section = text
                    continue
                # Keep substantive prose, not isolated equations, tables or figure labels.
                words = re.findall(r"\b[A-Za-z]{3,}\b", text)
                letter_ratio = sum(c.isalpha() for c in text) / max(1, len(text))
                if len(words) < 8 or letter_ratio < 0.60 or text.startswith("FIGURE"):
                    continue
                # Keep shorter explanatory paragraphs; they were lost in v1.
                # Combine only neighboring retained blocks from the same section/page.
                if groups and groups[-1][0] == section:
                    groups[-1][1].append(text)
                else:
                    groups.append((section, [text]))
            for group_index, (heading, paragraphs) in enumerate(groups):
                prefix = f"{chapter} | {heading}\n"
                prefix_tokens = len(tokenizer.encode(prefix).ids)
                for part, passage in enumerate(split_to_fit(" ".join(paragraphs), tokenizer,
                                                            budget=228-prefix_tokens)):
                    if len(re.findall(r"\b[A-Za-z]{3,}\b", passage)) < 15:
                        continue
                    document = prefix + passage
                    digest = hashlib.sha256(document.encode()).hexdigest()[:12]
                    records.append({
                        "id": f"wasserman-v2-p{index+1}-g{group_index}-{part}-{digest}",
                        "document": document,
                        "metadata": {
                            "source": "Wasserman, All of Statistics (2004)",
                            "kind": "textbook", "chapter": chapter,
                            "section": heading, "pdf_page": index + 1,
                            "book_page": index + 1 - 17,
                            "tokens": len(tokenizer.encode(document).ids),
                        },
                    })
    if len(records) < 300:
        raise ValueError(f"Only {len(records)} passages; inspect extraction before indexing.")
    DATA.mkdir(exist_ok=True)
    CHUNKS.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
    print(f"Extracted {len(records)} context-bearing passages from chapters 1-16.")
    print(f"Largest passage: {max(r['metadata']['tokens'] for r in records)} tokens.")
    print("Equations may be imperfect: consult the original PDF using page references.")


def load(limit):
    if not CHUNKS.exists():
        raise SystemExit("Run: python textbook.py extract")
    records = [json.loads(line) for line in CHUNKS.read_text().splitlines()]
    if limit:
        # Spread a small trial batch across the whole selected corpus.
        count = min(limit, len(records))
        records = [records[i * len(records) // count] for i in range(count)]
    collection, _ = open_collection()
    existing = set(collection.get(include=[])["ids"])
    refreshed = [r for r in records if r["id"] in existing]
    if refreshed:
        collection.update(ids=[r["id"] for r in refreshed],
                          metadatas=[r["metadata"] for r in refreshed])
    pending = [r for r in records if r["id"] not in existing]
    start = time.perf_counter()
    for offset in range(0, len(pending), 50):
        batch = pending[offset:offset + 50]
        collection.add(ids=[r["id"] for r in batch],
                       documents=[r["document"] for r in batch],
                       metadatas=[r["metadata"] for r in batch])
        print(f"Embedded {min(offset+50, len(pending))}/{len(pending)} new passages", flush=True)
    elapsed = time.perf_counter() - start
    report = {"new_passages": len(pending), "seconds": round(elapsed, 2),
              "total_stored": collection.count()}
    (DATA / "last_load.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


def search(query, raw=False):
    collection, embedding = open_collection()
    if not query.strip():
        raise SystemExit("Please enter a question.")
    if len(full_tokenizer(embedding).encode(query).ids) > 256:
        raise SystemExit("Please shorten the question to fewer than 256 tokens.")
    if not collection.count():
        raise SystemExit("No textbook passages yet. Run the load command first.")
    result = collection.query(query_texts=[query], n_results=min(5, collection.count()),
                              include=["documents", "metadatas", "distances"])
    if raw:
        print(json.dumps(result, indent=2))
        return
    print("\nClosest passages (not a verified answer; lower cosine distance is closer):")
    for rank, (text, metadata, distance) in enumerate(zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]), 1):
        print(f"\n{rank}. {metadata['chapter']} | book p. {metadata['book_page']} "
              f"(PDF p. {metadata['pdf_page']}) | distance {distance:.3f}")
        print(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("download", "extract"):
        commands.add_parser(name)
    load_parser = commands.add_parser("load")
    load_parser.add_argument("--limit", type=int, default=0, help="0 means all passages")
    query_parser = commands.add_parser("search")
    query_parser.add_argument("query")
    query_parser.add_argument("--raw", action="store_true")
    args = parser.parse_args()
    if args.command == "download":
        download()
    elif args.command == "extract":
        extract()
    elif args.command == "load":
        if args.limit < 0:
            parser.error("--limit must be nonnegative")
        load(args.limit)
    else:
        search(args.query, args.raw)
