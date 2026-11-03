"""Regression tests for source-symbol references in conformance evidence."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_fixture_catalog import evidence_references, evidence_symbol_declared


class EvidenceReferenceTests(unittest.TestCase):
    def test_extracts_path_and_terminal_symbol(self):
        refs = list(evidence_references(
            "`ronin/solver.py::internal::solve` and `tests/test_core.py`"
        ))
        self.assertEqual(
            refs,
            [("ronin/solver.py", "internal::solve"), ("tests/test_core.py", None)],
        )

    def test_accepts_python_and_rust_function_declarations(self):
        self.assertTrue(evidence_symbol_declared("def k_min(value):\n    return value\n", "k_min"))
        self.assertTrue(evidence_symbol_declared(
            "async def load_project(path):\n    pass\n", "load_project"
        ))
        self.assertTrue(evidence_symbol_declared(
            "    pub(crate) fn shared_check() {\n    }\n", "shared_check"
        ))
        self.assertTrue(evidence_symbol_declared(
            "    fn nested_check() {\n    }\n", "module::nested_check"
        ))

    def test_rejects_mentions_comments_and_prefix_matches(self):
        source = (
            "# def missing_symbol():\n"
            "message = 'fn missing_symbol()'\n"
            "def missing_symbol_extra():\n    pass\n"
        )
        self.assertFalse(evidence_symbol_declared(source, "missing_symbol"))

    def test_rejects_empty_symbol(self):
        self.assertFalse(evidence_symbol_declared("def present():\n    pass\n", ""))


if __name__ == "__main__":
    unittest.main()
