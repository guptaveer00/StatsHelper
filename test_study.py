"""Integration tests use a temporary database, never the user's notes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
import io

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

from storage import ROOT
from study import StudyHelper, guide_markdown, save_guide


class StudyFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="stats-helper-test-")
        cls.database = Path(cls.temporary.name) / "store"
        cls.embedding = ONNXMiniLM_L6_V2()
        cls.embedding.DOWNLOAD_PATH = ROOT / ".model_cache" / cls.embedding.MODEL_NAME
        cls.client = chromadb.PersistentClient(
            path=str(cls.database), settings=Settings(anonymized_telemetry=False))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.collection = self.client.create_collection(
            name="test_" + self._testMethodName,
            embedding_function=self.embedding,
            configuration={"hnsw": {"space": "cosine"}})
        self.helper = StudyHelper(self.collection, self.embedding)

    def test_add_search_guide_and_save(self):
        ids = self.helper.add_note("Rain survey", "People carry umbrellas when it rains. Umbrellas do not cause wet pavements; rain explains both observations.")
        matches = self.helper.retrieve("Do umbrellas cause wet pavements?", "notes")
        self.assertEqual(matches[0].id, ids[0])
        self.assertEqual(self.helper.retrieve("Do umbrellas cause wet pavements?", "textbook"), [])
        guide = self.helper.make_guide("Do umbrellas cause wet pavements?", "notes")
        self.assertTrue(guide.cards)
        self.assertIn(guide.cards[0].answer.lower(), guide.key_sentences[0].lower())
        self.assertIn("________", guide.cards[0].prompt)
        path = save_guide(guide, Path(self.temporary.name) / "guides")
        self.assertEqual(path.read_text(), guide_markdown(guide))
        self.assertEqual(self.helper.status()["notes"], 1)

    def test_long_note_and_unique_ids(self):
        text = "Random assignment helps distinguish a treatment effect from selection bias. " * 80
        first = self.helper.add_note("Experiment notes", text)
        second = self.helper.add_note("Experiment notes", "Control groups provide a comparison for the treated subjects.")
        self.assertGreater(len(first), 1)
        self.assertFalse(set(first) & set(second))
        result = self.collection.get(ids=first, include=["documents"])
        self.assertTrue(all(len(self.helper.tokenizer.encode(d).ids) <= 230 for d in result["documents"]))
        self.assertEqual(self.helper.status()["notes"], 2)

    def test_validation_and_empty_library(self):
        self.assertEqual(self.helper.retrieve("What is uncertainty?"), [])
        for title, text in (("", "some text"), ("title", " "), ("x"*101, "text"), ("title", "x"*30001)):
            with self.assertRaises(ValueError):
                self.helper.add_note(title, text)
        for query in (" ", "probability "*300):
            with self.assertRaises(ValueError):
                self.helper.retrieve(query)

    def test_menu_add_search_practice_save_quit(self):
        from app import menu
        answers = iter([
            "2", "Rain demo", "Umbrellas do not cause wet pavements because rain explains both observations.", ".",
            "1", "Do umbrellas cause wet pavements?", "n", "3", "", "y", "4", "5", "0",
        ])
        output = io.StringIO()
        directory = Path(self.temporary.name) / "menu-guides"
        with patch("builtins.input", side_effect=lambda *args: next(answers)), \
                patch("app.save_guide", side_effect=lambda guide: save_guide(guide, directory)), \
                redirect_stdout(output):
            menu(self.helper)
        self.assertIn("Saved in 1 searchable chunk", output.getvalue())
        self.assertIn("1/1 recalled", output.getvalue())
        self.assertIn("Your notes: 1", output.getvalue())
        self.assertEqual(len(list(directory.glob("*.md"))), 1)

    def test_persistence_in_new_process(self):
        ids = self.helper.add_note("Sampling note", "Drawing individuals at random helps avoid selection bias when conducting a survey.")
        code = '''
import json,sys,chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from storage import ROOT
from study import StudyHelper
e=ONNXMiniLM_L6_V2()
e.DOWNLOAD_PATH=ROOT / '.model_cache' / e.MODEL_NAME
c=chromadb.PersistentClient(path=sys.argv[1],settings=Settings(anonymized_telemetry=False))
h=StudyHelper(c.get_collection(sys.argv[2],embedding_function=e),e)
print(json.dumps([m.id for m in h.retrieve('Drawing individuals at random helps avoid selection bias','notes')]))
'''
        run = subprocess.run([sys.executable, "-c", code, str(self.database), self.collection.name],
                             cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertIn(ids[0], json.loads(run.stdout))


if __name__ == "__main__":
    unittest.main()
