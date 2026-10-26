"""Re-run semantic examples against the real corpus; save evidence, not assertions of perfection."""
import json
import re

from storage import ROOT
from study import StudyHelper, STOPWORDS

TESTS = [
    {
        "query": "Why does seeing a rash not guarantee a particular diagnosis?",
        "expected_id": "wasserman-v2-p27-g1-1-1aaa8ab76cb7",
        "expected_concept": "Conditional probability: spots versus measles",
    },
    {
        "query": "Why can an association reverse direction after pooling subpopulations?",
        "expected_id": "wasserman-v2-p276-g1-0-f7e3a41735d6",
        "expected_concept": "Simpson's paradox",
    },
]


def words(text):
    return set(re.findall(r"[a-z]+", text.lower())) - STOPWORDS


def verify():
    helper = StudyHelper()
    evidence = []
    for test in TESTS:
        result = helper.collection.query(
            query_texts=[test["query"]], n_results=5, where={"kind": "textbook"},
            include=["documents", "metadatas", "distances"])
        ids = result["ids"][0]
        rank = ids.index(test["expected_id"])+1 if test["expected_id"] in ids else None
        row = {**test, "rank_in_top_five": rank, "raw": result}
        if rank:
            text = result["documents"][0][rank-1]
            row["non_stopword_overlap"] = sorted(words(test["query"]) & words(text))
            row["appears_in_study_guide"] = test["expected_id"] in [m.id for m in helper.retrieve(test["query"], "textbook")]
        evidence.append(row)
        print(test["expected_concept"], "rank:", rank,
              "non-stopword overlap:", row.get("non_stopword_overlap"),
              "in guide:", row.get("appears_in_study_guide"))
    unrelated = ["Where can I buy concert tickets for tonight?",
                 "How can I get a refund for a broken laptop?", "Suggest a movie for tonight."]
    for query in unrelated:
        matches = helper.retrieve(query, "textbook")
        evidence.append({"unrelated_query": query, "accepted_results": len(matches)})
        print("Unrelated query accepted results:", len(matches), query)
    path = ROOT / "data" / "semantic-verification.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2))
    print("Evidence saved to", path)
    return evidence


if __name__ == "__main__":
    verify()
