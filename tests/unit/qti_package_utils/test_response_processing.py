import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace

import backend.QTI_Paket.utils.ResponseProcessing as response_processing_module
from backend.utils import Response, ExcelResponse


class TestResponseProcessingResponse(unittest.TestCase):

    def test_creates_response_condition(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_response(
            response_processing_tag=root,
            response_id="RESPONSE_1",
            equal_attribs={"toleranceMode": "exact"},
        )

        condition = root.find("responseCondition")

        self.assertIsNotNone(condition)

    def test_creates_equal_with_given_attributes(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_response(
            response_processing_tag=root,
            response_id="RESPONSE_1",
            equal_attribs={
                "toleranceMode": "absolute",
                "tolerance": "0.1",
            },
        )

        equal = root.find("./responseCondition/responseIf/equal")

        self.assertIsNotNone(equal)
        self.assertEqual(
            equal.attrib["toleranceMode"],
            "absolute",
        )
        self.assertEqual(
            equal.attrib["tolerance"],
            "0.1",
        )

    def test_equal_references_response_and_correct_value(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_response(
            response_processing_tag=root,
            response_id="RESPONSE_42",
            equal_attribs={"toleranceMode": "exact"},
        )

        variable = root.find(
            "./responseCondition/responseIf/equal/"
            "variable[@identifier='RESPONSE_42']"
        )
        correct = root.find(
            "./responseCondition/responseIf/equal/"
            "correct[@identifier='RESPONSE_42']"
        )

        self.assertIsNotNone(variable)
        self.assertIsNotNone(correct)

    def test_sets_response_score_to_response_maxscore(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_response(
            response_processing_tag=root,
            response_id="RESPONSE_1",
            equal_attribs={"toleranceMode": "exact"},
        )

        score_variable = root.find(
            "./responseCondition/responseIf/"
            "setOutcomeValue[@identifier='SCORE_RESPONSE_1']/"
            "variable[@identifier='MAXSCORE_RESPONSE_1']"
        )

        self.assertIsNotNone(score_variable)


class TestResponseProcessingScoreBounds(unittest.TestCase):

    def test_creates_two_score_conditions(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_score_bounds(
            root
        )

        conditions = root.findall("responseCondition")

        self.assertEqual(len(conditions), 2)

    def test_first_condition_checks_score_below_minimum(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_score_bounds(
            root
        )

        less_than = root.find(
            "./responseCondition[1]/responseIf/lt"
        )

        self.assertIsNotNone(less_than)

        identifiers = [
            variable.attrib["identifier"]
            for variable in less_than.findall("variable")
        ]

        self.assertEqual(
            identifiers,
            ["SCORE", "MINSCORE"],
        )

    def test_first_condition_sets_score_to_minimum(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_score_bounds(
            root
        )

        minimum = root.find(
            "./responseCondition[1]/responseIf/"
            "setOutcomeValue[@identifier='SCORE']/"
            "variable[@identifier='MINSCORE']"
        )

        self.assertIsNotNone(minimum)

    def test_second_condition_checks_score_above_maximum(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_score_bounds(
            root
        )

        greater_than = root.find(
            "./responseCondition[2]/responseIf/gt"
        )

        self.assertIsNotNone(greater_than)

        identifiers = [
            variable.attrib["identifier"]
            for variable in greater_than.findall("variable")
        ]

        self.assertEqual(
            identifiers,
            ["SCORE", "MAXSCORE"],
        )

    def test_second_condition_sets_score_to_maximum(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_score_bounds(
            root
        )

        maximum = root.find(
            "./responseCondition[2]/responseIf/"
            "setOutcomeValue[@identifier='SCORE']/"
            "variable[@identifier='MAXSCORE']"
        )

        self.assertIsNotNone(maximum)


class TestResponseProcessingFeedback(unittest.TestCase):

    def test_creates_basic_feedback_condition_without_modal_feedback(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_feedback(
            response_processing_tag=root,
            feedback=None,
            max_score=5,
        )

        conditions = root.findall("responseCondition")

        self.assertEqual(len(conditions), 1)

    def test_sets_basic_feedback_to_incorrect_when_score_is_lower(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_feedback(
            response_processing_tag=root,
            feedback=None,
            max_score=5,
        )

        less_than = root.find(
            "./responseCondition/responseIf/lt"
        )

        identifiers = [
            variable.attrib["identifier"]
            for variable in less_than.findall("variable")
        ]

        self.assertEqual(
            identifiers,
            ["SCORE", "MAXSCORE"],
        )

        incorrect = root.find(
            "./responseCondition/responseIf/"
            "setOutcomeValue[@identifier='FEEDBACKBASIC']/"
            "baseValue[@baseType='identifier']"
        )

        self.assertIsNotNone(incorrect)
        self.assertEqual(incorrect.text, "incorrect")

    def test_sets_basic_feedback_to_correct_in_response_else(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_feedback(
            response_processing_tag=root,
            feedback=None,
            max_score=5,
        )

        correct = root.find(
            "./responseCondition/responseElse/"
            "setOutcomeValue[@identifier='FEEDBACKBASIC']/"
            "baseValue[@baseType='identifier']"
        )

        self.assertIsNotNone(correct)
        self.assertEqual(correct.text, "correct")

    def test_creates_correct_modal_feedback_condition(self):
        root = ET.Element("responseProcessing")

        feedback = {
            "feedback_correct": SimpleNamespace(
                id="FEEDBACK_CORRECT",
                type="correct",
                condition=None,
            ),
            "feedback_incorrect": [],
        }

        response_processing_module.response_processing_feedback(
            response_processing_tag=root,
            feedback=feedback,
            max_score=5,
        )

        feedback_value = root.find(
            ".//setOutcomeValue[@identifier='FEEDBACKMODAL']/"
            "multiple/baseValue[@baseType='identifier']"
        )

        self.assertIsNotNone(feedback_value)
        self.assertEqual(
            feedback_value.text,
            "FEEDBACK_CORRECT",
        )

    def test_creates_all_incorrect_modal_feedback_conditions(self):
        root = ET.Element("responseProcessing")

        feedback = {
            "feedback_correct": SimpleNamespace(
                id="FEEDBACK_CORRECT",
                type="correct",
                condition=None,
            ),
            "feedback_incorrect": [
                SimpleNamespace(
                    id="FEEDBACK_INCORRECT_1",
                    type="incorrect",
                    condition=1,
                ),
                SimpleNamespace(
                    id="FEEDBACK_INCORRECT_2",
                    type="incorrect",
                    condition=2,
                ),
            ],
        }

        response_processing_module.response_processing_feedback(
            response_processing_tag=root,
            feedback=feedback,
            max_score=5,
        )

        feedback_ids = [
            value.text
            for value in root.findall(
                ".//setOutcomeValue"
                "[@identifier='FEEDBACKMODAL']/"
                "multiple/baseValue"
                "[@baseType='identifier']"
            )
        ]

        self.assertEqual(
            feedback_ids,
            [
                "FEEDBACK_CORRECT",
                "FEEDBACK_INCORRECT_1",
                "FEEDBACK_INCORRECT_2",
            ],
        )


class TestFeedbackTagCorrect(unittest.TestCase):

    def test_correct_feedback_checks_score_equal_to_maxscore(self):
        root = ET.Element("responseProcessing")

        feedback = SimpleNamespace(
            id="FEEDBACK_CORRECT",
            type="correct",
            condition=None,
        )

        response_processing_module.feedback_tag(
            response_processing_tag=root,
            feedback=feedback,
            max_score=5,
        )

        equal = root.find(
            "./responseCondition/responseIf/and/equal"
        )

        self.assertIsNotNone(equal)
        self.assertEqual(
            equal.attrib["toleranceMode"],
            "exact",
        )

        variable = equal.find(
            "./variable[@identifier='SCORE']"
        )
        value = equal.find(
            "./baseValue[@baseType='float']"
        )

        self.assertIsNotNone(variable)
        self.assertIsNotNone(value)
        self.assertEqual(value.text, "5")

    def test_correct_feedback_with_point_deduction_checks_minimum_score(self):
        root = ET.Element("responseProcessing")

        feedback = SimpleNamespace(
            id="FEEDBACK_CORRECT",
            type="correct",
            condition=None,
        )

        point_deduction = SimpleNamespace(
            is_used=True
        )

        response_processing_module.feedback_tag(
            response_processing_tag=root,
            feedback=feedback,
            point_deduction=point_deduction,
            max_score=5,
        )

        greater_than = root.find(
            "./responseCondition/responseIf/and/gt"
        )

        self.assertIsNotNone(greater_than)

        variable = greater_than.find(
            "./variable[@identifier='mindestpunktzahl']"
        )
        value = greater_than.find(
            "./baseValue[@baseType='float']"
        )

        self.assertIsNotNone(variable)
        self.assertEqual(value.text, "0")

    def test_correct_feedback_adds_modal_feedback_id(self):
        root = ET.Element("responseProcessing")

        feedback = SimpleNamespace(
            id="FEEDBACK_CORRECT",
            type="correct",
            condition=None,
        )

        response_processing_module.feedback_tag(
            response_processing_tag=root,
            feedback=feedback,
            max_score=5,
        )

        feedback_value = root.find(
            "./responseCondition/responseIf/"
            "setOutcomeValue[@identifier='FEEDBACKMODAL']/"
            "multiple/baseValue[@baseType='identifier']"
        )

        self.assertIsNotNone(feedback_value)
        self.assertEqual(
            feedback_value.text,
            "FEEDBACK_CORRECT",
        )

    def test_modal_feedback_keeps_existing_feedback_values(self):
        root = ET.Element("responseProcessing")

        feedback = SimpleNamespace(
            id="FEEDBACK_CORRECT",
            type="correct",
            condition=None,
        )

        response_processing_module.feedback_tag(
            response_processing_tag=root,
            feedback=feedback,
            max_score=5,
        )

        existing_feedback = root.find(
            "./responseCondition/responseIf/"
            "setOutcomeValue[@identifier='FEEDBACKMODAL']/"
            "multiple/variable[@identifier='FEEDBACKMODAL']"
        )

        self.assertIsNotNone(existing_feedback)


class TestFeedbackTagIncorrect(unittest.TestCase):

    def test_incorrect_feedback_checks_score_less_than_maxscore(self):
        root = ET.Element("responseProcessing")

        feedback = SimpleNamespace(
            id="FEEDBACK_INCORRECT",
            type="incorrect",
            condition=None,
        )

        response_processing_module.feedback_tag(
            response_processing_tag=root,
            feedback=feedback,
            i=1,
            max_score=5,
        )

        less_than = root.find(
            "./responseCondition/responseIf/and/lt"
        )

        self.assertIsNotNone(less_than)

        variable = less_than.find(
            "./variable[@identifier='SCORE']"
        )
        value = less_than.find(
            "./baseValue[@baseType='float']"
        )

        self.assertIsNotNone(variable)
        self.assertEqual(value.text, "5")

    def test_incorrect_feedback_with_point_deduction_checks_zero_minimum_score(self):
        root = ET.Element("responseProcessing")

        feedback = SimpleNamespace(
            id="FEEDBACK_INCORRECT",
            type="incorrect",
            condition=None,
        )

        point_deduction = SimpleNamespace(
            is_used=True
        )

        response_processing_module.feedback_tag(
            response_processing_tag=root,
            feedback=feedback,
            point_deduction=point_deduction,
            i=1,
            max_score=5,
        )

        equal = root.find(
            "./responseCondition/responseIf/and/equal"
        )

        self.assertIsNotNone(equal)
        self.assertEqual(
            equal.attrib["toleranceMode"],
            "exact",
        )

        variable = equal.find(
            "./variable[@identifier='mindestpunktzahl']"
        )
        value = equal.find(
            "./baseValue[@baseType='float']"
        )

        self.assertIsNotNone(variable)
        self.assertEqual(value.text, "0")

    def test_integer_attempt_condition_creates_lower_bound(self):
        root = ET.Element("responseProcessing")

        feedback = SimpleNamespace(
            id="FEEDBACK_ATTEMPT",
            type="incorrect",
            condition=2,
        )

        response_processing_module.feedback_tag(
            response_processing_tag=root,
            feedback=feedback,
            i=0,
            max_score=5,
        )

        greater_equal = root.find(
            "./responseCondition/responseIf/and/gte"
        )

        self.assertIsNotNone(greater_equal)

        variable = greater_equal.find(
            "./variable[@identifier='numAttempts']"
        )
        value = greater_equal.find(
            "./baseValue[@baseType='integer']"
        )

        self.assertIsNotNone(variable)
        self.assertEqual(value.text, "1")

    def test_attempt_range_creates_lower_and_upper_bounds(self):
        root = ET.Element("responseProcessing")

        feedback = SimpleNamespace(
            id="FEEDBACK_RANGE",
            type="incorrect",
            condition=[2, 4],
        )

        response_processing_module.feedback_tag(
            response_processing_tag=root,
            feedback=feedback,
            i=0,
            max_score=5,
        )

        greater_equal = root.find(
            "./responseCondition/responseIf/and/gte"
        )
        less_equal = root.find(
            "./responseCondition/responseIf/and/lte"
        )

        self.assertIsNotNone(greater_equal)
        self.assertIsNotNone(less_equal)

        lower_value = greater_equal.find(
            "./baseValue[@baseType='integer']"
        )
        upper_value = less_equal.find(
            "./baseValue[@baseType='integer']"
        )

        self.assertEqual(lower_value.text, "1")
        self.assertEqual(upper_value.text, "3")

    def test_response_condition_checks_zero_response_score(self):
        root = ET.Element("responseProcessing")

        response = Response(
            id="RESPONSE_1",
            value="12",
        )

        feedback = SimpleNamespace(
            id="FEEDBACK_RESPONSE",
            type="incorrect",
            condition=response,
        )

        response_processing_module.feedback_tag(
            response_processing_tag=root,
            feedback=feedback,
            i=0,
            max_score=5,
        )

        equal = root.find(
            "./responseCondition/responseIf/and/equal"
        )

        self.assertIsNotNone(equal)
        self.assertEqual(
            equal.attrib["toleranceMode"],
            "exact",
        )

        variable = equal.find(
            "./variable[@identifier='SCORE_RESPONSE_1']"
        )
        value = equal.find(
            "./baseValue[@baseType='float']"
        )

        self.assertIsNotNone(variable)
        self.assertEqual(value.text, "0")

    def test_excel_response_condition_checks_zero_response_score(self):
        root = ET.Element("responseProcessing")

        response = ExcelResponse(
            id="EXCEL_RESPONSE_1",
            cell="C3",
        )

        feedback = SimpleNamespace(
            id="FEEDBACK_EXCEL_RESPONSE",
            type="incorrect",
            condition=response,
        )

        response_processing_module.feedback_tag(
            response_processing_tag=root,
            feedback=feedback,
            i=0,
            max_score=5,
        )

        variable = root.find(
            "./responseCondition/responseIf/and/equal/"
            "variable[@identifier='SCORE_EXCEL_RESPONSE_1']"
        )

        self.assertIsNotNone(variable)

    def test_incorrect_feedback_adds_modal_feedback_identifier(self):
        root = ET.Element("responseProcessing")

        feedback = SimpleNamespace(
            id="FEEDBACK_INCORRECT",
            type="incorrect",
            condition=1,
        )

        response_processing_module.feedback_tag(
            response_processing_tag=root,
            feedback=feedback,
            i=0,
            max_score=5,
        )

        feedback_value = root.find(
            "./responseCondition/responseIf/"
            "setOutcomeValue[@identifier='FEEDBACKMODAL']/"
            "multiple/baseValue[@baseType='identifier']"
        )

        self.assertIsNotNone(feedback_value)
        self.assertEqual(
            feedback_value.text,
            "FEEDBACK_INCORRECT",
        )


class TestResponseProcessingGeneratedXml(unittest.TestCase):

    def test_generated_response_processing_is_valid_xml(self):
        root = ET.Element("responseProcessing")

        response_processing_module.response_processing_response(
            response_processing_tag=root,
            response_id="RESPONSE_1",
            equal_attribs={"toleranceMode": "exact"},
        )

        response_processing_module.response_processing_score_bounds(
            root
        )

        feedback = {
            "feedback_correct": SimpleNamespace(
                id="FEEDBACK_CORRECT",
                type="correct",
                condition=None,
            ),
            "feedback_incorrect": [
                SimpleNamespace(
                    id="FEEDBACK_INCORRECT",
                    type="incorrect",
                    condition=1,
                )
            ],
        }

        response_processing_module.response_processing_feedback(
            response_processing_tag=root,
            feedback=feedback,
            max_score=5,
        )

        xml_text = ET.tostring(
            root,
            encoding="unicode",
        )

        parsed_root = ET.fromstring(xml_text)

        self.assertEqual(
            parsed_root.tag,
            "responseProcessing",
        )


if __name__ == "__main__":
    unittest.main()