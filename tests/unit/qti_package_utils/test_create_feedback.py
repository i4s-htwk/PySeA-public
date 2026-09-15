import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
from unittest.mock import patch

import backend.QTI_Paket.utils.Feedback as feedback_module
from backend.utils.Variants.VariableDependentAssignment.VariableDependentAssignment import (
    VariableDependentAssignment,
)


class TestCreateFeedback(unittest.TestCase):

    def setUp(self):
        self.root = ET.Element("assessmentItem")

    @staticmethod
    def make_feedback(
        feedback_id="FEEDBACK_1",
        value="Feedbacktext",
        feedback_type="correct",
    ):
        return SimpleNamespace(
            id=feedback_id,
            value=value,
            type=feedback_type,
        )

    def test_create_feedback_does_nothing_when_feedback_is_none(self):
        feedback_module.create_feedback(
            root_tag=self.root,
            feedback=None,
            feedback_titles=[None, None],
            images=[],
        )

        self.assertEqual(list(self.root), [])

    def test_create_feedback_creates_modal_feedback_for_item(self):
        feedback = {
            "feedback_correct": self.make_feedback(
                feedback_id="CORRECT_1",
                value="Das war richtig.",
            ),
            "feedback_incorrect": self.make_feedback(
                feedback_id="INCORRECT_1",
                value="Das war falsch.",
                feedback_type="incorrect",
            ),
        }

        with patch.object(feedback_module, "append_text"):
            feedback_module.create_feedback(
                root_tag=self.root,
                feedback=feedback,
                feedback_titles=["Richtig", "Falsch"],
                images=[],
                item=SimpleNamespace(),
            )

        feedback_tags = self.root.findall("modalFeedback")

        self.assertEqual(len(feedback_tags), 2)

        correct_tag = feedback_tags[0]
        self.assertEqual(correct_tag.attrib["identifier"], "CORRECT_1")
        self.assertEqual(
            correct_tag.attrib["outcomeIdentifier"],
            "FEEDBACKMODAL",
        )
        self.assertEqual(correct_tag.attrib["showHide"], "show")
        self.assertEqual(correct_tag.attrib["title"], "Richtig")

        incorrect_tag = feedback_tags[1]
        self.assertEqual(incorrect_tag.attrib["identifier"], "INCORRECT_1")
        self.assertEqual(incorrect_tag.attrib["title"], "Falsch")

    def test_create_feedback_creates_test_feedback_without_item(self):
        feedback = {
            "feedback_correct": self.make_feedback(
                feedback_id="CORRECT_1",
            ),
            "feedback_incorrect": self.make_feedback(
                feedback_id="INCORRECT_1",
                feedback_type="incorrect",
            ),
        }

        with patch.object(feedback_module, "append_text"):
            feedback_module.create_feedback(
                root_tag=self.root,
                feedback=feedback,
                feedback_titles=[None, None],
                images=[],
                item=None,
            )

        feedback_tags = self.root.findall("testFeedback")

        self.assertEqual(len(feedback_tags), 2)

        for tag in feedback_tags:
            self.assertEqual(tag.attrib["access"], "atEnd")
            self.assertEqual(
                tag.attrib["outcomeIdentifier"],
                "FEEDBACKMODAL",
            )
            self.assertEqual(tag.attrib["showHide"], "show")

    def test_create_feedback_accepts_multiple_incorrect_feedback_entries(self):
        feedback = {
            "feedback_correct": self.make_feedback(
                feedback_id="CORRECT_1",
            ),
            "feedback_incorrect": [
                self.make_feedback(
                    feedback_id="INCORRECT_1",
                    feedback_type="incorrect",
                ),
                self.make_feedback(
                    feedback_id="INCORRECT_2",
                    feedback_type="incorrect",
                ),
            ],
        }

        with patch.object(feedback_module, "append_text"):
            feedback_module.create_feedback(
                root_tag=self.root,
                feedback=feedback,
                feedback_titles=[None, None],
                images=[],
                item=SimpleNamespace(),
            )

        identifiers = [
            tag.attrib["identifier"]
            for tag in self.root.findall("modalFeedback")
        ]

        self.assertEqual(
            identifiers,
            ["CORRECT_1", "INCORRECT_1", "INCORRECT_2"],
        )

    def test_create_feedback_creates_one_paragraph_per_line(self):
        feedback = {
            "feedback_correct": self.make_feedback(
                value="Erste Zeile\nZweite Zeile\n",
            ),
            "feedback_incorrect": self.make_feedback(
                feedback_id="INCORRECT_1",
                value="Falsch",
                feedback_type="incorrect",
            ),
        }

        with patch.object(feedback_module, "append_text"):
            feedback_module.create_feedback(
                root_tag=self.root,
                feedback=feedback,
                feedback_titles=[None, None],
                images=[],
                item=SimpleNamespace(),
            )

        correct_feedback = self.root.find(
            "./modalFeedback[@identifier='FEEDBACK_1']"
        )

        paragraphs = correct_feedback.findall("p")

        self.assertEqual(len(paragraphs), 2)

    def test_create_feedback_passes_latex_block_to_append_text(self):
        feedback = {
            "feedback_correct": self.make_feedback(
                value="Formel: $$a+b$$ Ende",
            ),
            "feedback_incorrect": self.make_feedback(
                feedback_id="INCORRECT_1",
                feedback_type="incorrect",
            ),
        }

        with patch.object(
            feedback_module,
            "append_text",
        ) as append_text_mock:
            feedback_module.create_feedback(
                root_tag=self.root,
                feedback=feedback,
                feedback_titles=[None, None],
                images=[],
                item=SimpleNamespace(),
            )

        passed_texts = [
            call.args[1]
            for call in append_text_mock.call_args_list
        ]

        self.assertIn("$$a+b$$", passed_texts)

    def test_create_feedback_inserts_normal_image(self):
        feedback = {
            "feedback_correct": self.make_feedback(
                value="Lösung: {BILD_1}",
            ),
            "feedback_incorrect": self.make_feedback(
                feedback_id="INCORRECT_1",
                feedback_type="incorrect",
            ),
        }

        item = SimpleNamespace()

        with (
            patch.object(feedback_module, "append_text"),
            patch.object(
                feedback_module,
                "insert_image",
            ) as insert_image_mock,
        ):
            feedback_module.create_feedback(
                root_tag=self.root,
                feedback=feedback,
                feedback_titles=[None, None],
                images=[],
                item=item,
            )

        insert_image_mock.assert_called_once()

        args = insert_image_mock.call_args.args
        self.assertEqual(args[0], "BILD_1")
        self.assertIs(args[2], item)

    def test_create_feedback_inserts_variant_dependent_image(self):
        feedback = {
            "feedback_correct": self.make_feedback(
                value="Lösung: {V_BILD_1}",
            ),
            "feedback_incorrect": self.make_feedback(
                feedback_id="INCORRECT_1",
                feedback_type="incorrect",
            ),
        }

        item = SimpleNamespace()

        with (
            patch.object(feedback_module, "append_text"),
            patch.object(
                feedback_module,
                "insert_v_image",
            ) as insert_v_image_mock,
        ):
            feedback_module.create_feedback(
                root_tag=self.root,
                feedback=feedback,
                feedback_titles=[None, None],
                images=[],
                item=item,
            )

        insert_v_image_mock.assert_called_once()

        args = insert_v_image_mock.call_args.args
        self.assertEqual(args[0], "V_BILD_1")
        self.assertIs(args[3], item)

    def test_create_feedback_inserts_score_printed_variable(self):
        feedback = {
            "feedback_correct": self.make_feedback(
                value="Erreicht: {SCORE} von {MAXSCORE}",
            ),
            "feedback_incorrect": self.make_feedback(
                feedback_id="INCORRECT_1",
                feedback_type="incorrect",
            ),
        }

        with patch.object(feedback_module, "append_text"):
            feedback_module.create_feedback(
                root_tag=self.root,
                feedback=feedback,
                feedback_titles=[None, None],
                images=[],
                item=SimpleNamespace(),
            )

        correct_feedback = self.root.find(
            "./modalFeedback[@identifier='FEEDBACK_1']"
        )

        identifiers = [
            element.attrib["identifier"]
            for element in correct_feedback.findall(".//printedVariable")
        ]

        self.assertEqual(identifiers, ["SCORE", "MAXSCORE"])

    def test_create_feedback_inserts_variable_dependent_assignment_variable(self):
        feedback = {
            "feedback_correct": self.make_feedback(
                value="Der Wert ist {a}.",
            ),
            "feedback_incorrect": self.make_feedback(
                feedback_id="INCORRECT_1",
                feedback_type="incorrect",
            ),
        }

        variant_assignment = object.__new__(
            VariableDependentAssignment
        )
        variant_assignment.get_variable_name = lambda name: name

        with patch.object(feedback_module, "append_text"):
            feedback_module.create_feedback(
                root_tag=self.root,
                feedback=feedback,
                feedback_titles=[None, None],
                images=[],
                item=SimpleNamespace(),
                variant_assignment=variant_assignment,
            )

        printed_variable = self.root.find(
            ".//modalFeedback[@identifier='FEEDBACK_1']"
            "//printedVariable[@identifier='a']"
        )

        self.assertIsNotNone(printed_variable)

    def test_unknown_placeholder_is_kept_as_text(self):
        feedback = {
            "feedback_correct": self.make_feedback(
                value="Unbekannt: {UNKNOWN}",
            ),
            "feedback_incorrect": self.make_feedback(
                feedback_id="INCORRECT_1",
                feedback_type="incorrect",
            ),
        }

        with patch.object(
            feedback_module,
            "append_text",
        ) as append_text_mock:
            feedback_module.create_feedback(
                root_tag=self.root,
                feedback=feedback,
                feedback_titles=[None, None],
                images=[],
                item=SimpleNamespace(),
            )

        passed_texts = [
            call.args[1]
            for call in append_text_mock.call_args_list
        ]

        self.assertIn("{UNKNOWN}", passed_texts)


if __name__ == "__main__":
    unittest.main()