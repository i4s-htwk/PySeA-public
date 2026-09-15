import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace

from backend.QTI_Paket.AssessmentItem import AssessmentItem
from backend.stores import StoreVariants
from backend.utils import Response, ExcelResponse, Selection, Matching


def make_assessment_item():
    item = object.__new__(AssessmentItem)
    item.root = ET.Element("assessmentItem")
    item.max_score = 0
    return item


class TestAssessmentItem(unittest.TestCase):

    def test_response_declaration_creates_float_declaration_for_normal_response(self):
        item = make_assessment_item()

        responses = [
            Response(id="RESPONSE_1", value="42")
        ]

        item.response_declaration(responses)

        declaration = item.root.find("responseDeclaration")

        self.assertIsNotNone(declaration)
        self.assertEqual(declaration.attrib["identifier"], "RESPONSE_1")
        self.assertEqual(declaration.attrib["cardinality"], "single")
        self.assertEqual(declaration.attrib["baseType"], "float")

        value = declaration.find("./correctResponse/value")
        self.assertIsNotNone(value)
        self.assertEqual(value.text, "42")

    def test_response_declaration_creates_identifier_declaration_for_selection(self):
        item = make_assessment_item()

        selection = Selection(
            id="SELECTION",
            type="singleChoice",
            correct=["Bild_1"],
            incorrect=["Bild_2"]
        )

        item.response_declaration([selection])

        declaration = item.root.find("responseDeclaration")

        self.assertIsNotNone(declaration)
        self.assertEqual(declaration.attrib["identifier"], "SELECTION")
        self.assertEqual(declaration.attrib["cardinality"], "single")
        self.assertEqual(declaration.attrib["baseType"], "identifier")

        value = declaration.find("./correctResponse/value")
        self.assertIsNotNone(value)
        self.assertEqual(value.text, "Bild_1")

    def test_response_declaration_uses_multiple_cardinality_for_multiple_correct_selection(self):
        item = make_assessment_item()

        selection = Selection(
            id="SELECTION",
            type="multipleChoice",
            correct=["Bild_1", "Bild_2"],
            incorrect=["Bild_3"]
        )

        item.response_declaration([selection])

        declaration = item.root.find("responseDeclaration")

        self.assertEqual(declaration.attrib["cardinality"], "multiple")
        self.assertEqual(declaration.attrib["baseType"], "identifier")

        values = [
            value.text
            for value in declaration.findall("./correctResponse/value")
        ]

        self.assertEqual(values, ["Bild_1", "Bild_2"])

    def test_response_declaration_creates_directed_pair_declaration_for_matching(self):
        item = make_assessment_item()

        matching = Matching()
        matching.add_pair("Quellelement 1", "Zielelement 1")
        matching.add_pair("Quellelement 2", "Zielelement 2")

        item.response_declaration([matching])

        declaration = item.root.find("responseDeclaration")

        self.assertIsNotNone(declaration)
        self.assertEqual(declaration.attrib["identifier"], "RESPONSE_1")
        self.assertEqual(declaration.attrib["cardinality"], "multiple")
        self.assertEqual(declaration.attrib["baseType"], "directedPair")

        values = [
            value.text
            for value in declaration.findall("./correctResponse/value")
        ]

        self.assertEqual(values, ["ID_1 IDT_1", "ID_2 IDT_2"])

    def test_get_point_distribution_respects_priority_order(self):
        item = make_assessment_item()

        matching = Matching()
        matching.add_pair("Quellelement 1", "Zielelement 1")
        matching.add_pair("Quellelement 2", "Zielelement 2")

        test_cases = [
            {
                "name": "task_points_have_highest_priority_for_normal_response",
                "task_distribution": {
                    "task": "12",
                    "gap": "4"
                },
                "answer": Response(
                    id="RESPONSE_1",
                    value="10",
                    points="2.5"
                ),
                "global_distribution": {
                    "gap": "1",
                    "selection": "3",
                    "matching": "5"
                },
                "len_responses": 4,
                "expected_gap": "3.0",
                "expected_selection": "12",
                "expected_matching": "12"
            },
            {
                "name": "task_points_define_selection_points",
                "task_distribution": {
                    "task": "6",
                    "gap": None
                },
                "answer": Selection(
                    id="SELECTION",
                    correct=["A"],
                    incorrect=["B"]
                ),
                "global_distribution": {
                    "gap": "1",
                    "selection": "3",
                    "matching": "5"
                },
                "len_responses": 1,
                "expected_gap": "6.0",
                "expected_selection": "6",
                "expected_matching": "6"
            },
            {
                "name": "task_points_define_matching_points",
                "task_distribution": {
                    "task": "8",
                    "gap": None
                },
                "answer": matching,
                "global_distribution": {
                    "gap": "1",
                    "selection": "3",
                    "matching": "5"
                },
                "len_responses": 1,
                "expected_gap": "8.0",
                "expected_selection": "8",
                "expected_matching": "8"
            },
            {
                "name": "answer_points_are_used_for_normal_response_if_task_points_are_not_set",
                "task_distribution": {
                    "task": None,
                    "gap": "4"
                },
                "answer": Response(
                    id="RESPONSE_1",
                    value="10",
                    points="2.5"
                ),
                "global_distribution": {
                    "gap": "1",
                    "selection": "3",
                    "matching": "5"
                },
                "len_responses": 4,
                "expected_gap": "2.5",
                "expected_selection": "3",
                "expected_matching": "5"
            },
            {
                "name": "task_gap_is_used_for_normal_response_if_no_task_points_and_no_answer_points_are_set",
                "task_distribution": {
                    "task": None,
                    "gap": "4"
                },
                "answer": Response(
                    id="RESPONSE_1",
                    value="10",
                    points=None
                ),
                "global_distribution": {
                    "gap": "1",
                    "selection": "3",
                    "matching": "5"
                },
                "len_responses": 4,
                "expected_gap": "4",
                "expected_selection": "3",
                "expected_matching": "5"
            },
            {
                "name": "global_gap_is_used_for_normal_response_if_no_more_specific_points_are_set",
                "task_distribution": {
                    "task": None,
                    "gap": None
                },
                "answer": Response(
                    id="RESPONSE_1",
                    value="10",
                    points=None
                ),
                "global_distribution": {
                    "gap": "1",
                    "selection": "3",
                    "matching": "5"
                },
                "len_responses": 4,
                "expected_gap": "1",
                "expected_selection": "3",
                "expected_matching": "5"
            },
            {
                "name": "selection_uses_global_selection_points_if_no_task_points_are_set",
                "task_distribution": {
                    "task": None,
                    "gap": None
                },
                "answer": Selection(
                    id="SELECTION",
                    correct=["A"],
                    incorrect=["B"]
                ),
                "global_distribution": {
                    "gap": "1",
                    "selection": "3",
                    "matching": "5"
                },
                "len_responses": 1,
                "expected_gap": "1",
                "expected_selection": "3",
                "expected_matching": "5"
            },
            {
                "name": "matching_uses_global_matching_points_if_no_task_points_are_set",
                "task_distribution": {
                    "task": None,
                    "gap": None
                },
                "answer": matching,
                "global_distribution": {
                    "gap": "1",
                    "selection": "3",
                    "matching": "5"
                },
                "len_responses": 1,
                "expected_gap": "1",
                "expected_selection": "3",
                "expected_matching": "5"
            }
        ]

        for case in test_cases:
            with self.subTest(case["name"]):
                task = SimpleNamespace(
                    point_distribution=case["task_distribution"]
                )

                point_gap, point_selection, point_matching = item.get_point_distribution(
                    answer=case["answer"],
                    task=task,
                    point_distribution=case["global_distribution"],
                    len_responses=case["len_responses"]
                )

                self.assertEqual(point_gap, case["expected_gap"])
                self.assertEqual(point_selection, case["expected_selection"])
                self.assertEqual(point_matching, case["expected_matching"])

    def test_outcome_declaration_creates_global_score_outcomes(self):
        item = make_assessment_item()

        task = SimpleNamespace(
            point_distribution={
                "task": None,
                "gap": None,
                "selection": None,
                "matching": None
            }
        )

        responses = [
            Response(id="RESPONSE_1", value="10"),
            Response(id="RESPONSE_2", value="20")
        ]

        used_content = ["RESPONSE_1", "RESPONSE_2"]

        returned_gap = item.outcome_declaration(
            task=task,
            responses=responses,
            used_content=used_content,
            point_distribution={
                "gap": "1.5",
                "selection": "4",
                "matching": "5"
            }
        )

        self.assertEqual(returned_gap, "1.5")
        self.assertEqual(item.max_score, 3.0)

        score = item.root.find("./outcomeDeclaration[@identifier='SCORE']")
        minscore = item.root.find("./outcomeDeclaration[@identifier='MINSCORE']")
        maxscore = item.root.find("./outcomeDeclaration[@identifier='MAXSCORE']")
        feedback_basic = item.root.find("./outcomeDeclaration[@identifier='FEEDBACKBASIC']")
        feedback_modal = item.root.find("./outcomeDeclaration[@identifier='FEEDBACKMODAL']")

        self.assertIsNotNone(score)
        self.assertIsNotNone(minscore)
        self.assertIsNotNone(maxscore)
        self.assertIsNotNone(feedback_basic)
        self.assertIsNotNone(feedback_modal)

        maxscore_value = maxscore.find("./defaultValue/value")
        self.assertEqual(maxscore_value.text, "3.0")

    def test_template_declaration_adds_variant_declaration_when_variants_are_used(self):
        item = make_assessment_item()

        task = SimpleNamespace(
            variant_dependent_images=[],
            local_variables_used=[],
            excel_variables=[],
        )
        v = StoreVariants()
        v.use_variants = True
        item.template_declaration(
            excel_responses=None,
            used_content=[],
            point_deduction_is_used=False,
            variants=v,
            task=task,
            selection=None,
            images = []
        )

        declaration = item.root.find("./templateDeclaration[@identifier='Variante']")

        self.assertIsNotNone(declaration)
        self.assertEqual(declaration.attrib["cardinality"], "single")
        self.assertEqual(declaration.attrib["baseType"], "integer")

    def test_template_declaration_only_adds_used_excel_responses(self):
        item = make_assessment_item()

        excel_responses = SimpleNamespace(
            answer_acc_from_excel=True,
            responses=[
                ExcelResponse(id="EXCEL_RESPONSE_1", cell="A1"),
                ExcelResponse(id="EXCEL_RESPONSE_2", cell="B1")
            ]
        )

        task = SimpleNamespace(
            variant_dependent_images=[],
            local_variables_used=[],
            excel_variables = [],
        )

        item.template_declaration(
            excel_responses=excel_responses,
            used_content=["EXCEL_RESPONSE_1"],
            point_deduction_is_used=False,
            variants=StoreVariants(),
            task=task,
            selection=None,
            images = []
        )

        declarations = item.root.findall("templateDeclaration")
        identifiers = [declaration.attrib["identifier"] for declaration in declarations]

        self.assertIn("VARIABLE_EXCEL_RESPONSE_1", identifiers)
        self.assertIn("VARIABLE_ACC_EXCEL_RESPONSE_1", identifiers)

        self.assertNotIn("VARIABLE_EXCEL_RESPONSE_2", identifiers)
        self.assertNotIn("VARIABLE_ACC_EXCEL_RESPONSE_2", identifiers)

    def test_template_declaration_adds_point_deduction_variable(self):
        item = make_assessment_item()

        task = SimpleNamespace(
            variant_dependent_images=[],
            local_variables_used=[],
            excel_variables=[],
        )

        item.template_declaration(
            excel_responses=None,
            used_content=[],
            point_deduction_is_used=True,
            variants= StoreVariants(),
            task=task,
            selection=None,
            images = []
        )

        declaration = item.root.find("./templateDeclaration[@identifier='mindestpunktzahl']")

        self.assertIsNotNone(declaration)
        self.assertEqual(declaration.attrib["baseType"], "float")

    def test_template_declaration_adds_local_variables(self):
        item = make_assessment_item()

        task = SimpleNamespace(
            variant_dependent_images=[],
            local_variables_used=[
                ("A", "2*x", "x"),
                ("B", "3*y", "y")
            ],
            excel_variables=[],
        )

        item.template_declaration(
            excel_responses=None,
            used_content=[],
            point_deduction_is_used=False,
            variants= StoreVariants(),
            task=task,
            selection=None,
            images = []
        )

        identifiers = [
            declaration.attrib["identifier"]
            for declaration in item.root.findall("templateDeclaration")
        ]

        self.assertIn("A", identifiers)
        self.assertIn("x", identifiers)
        self.assertIn("B", identifiers)
        self.assertIn("y", identifiers)

    def test_set_template_value_creates_maxima_custom_operator(self):
        item = make_assessment_item()

        template_processing = ET.SubElement(item.root, "templateProcessing")

        item.set_template_value(
            template_processing=template_processing,
            identifier="A",
            maxima_code="float($(1) + 1);",
            variables=["x"]
        )

        set_template_value = template_processing.find("setTemplateValue")
        self.assertIsNotNone(set_template_value)
        self.assertEqual(set_template_value.attrib["identifier"], "A")

        custom_operator = set_template_value.find("customOperator")
        self.assertIsNotNone(custom_operator)
        self.assertEqual(custom_operator.attrib["definition"], "MAXIMA")
        self.assertEqual(custom_operator.attrib["value"], "float($(1) + 1);")

        variable = custom_operator.find("variable")
        self.assertEqual(variable.attrib["identifier"], "x")

    def test_style_sheet_adds_redtick_css_file(self):
        item = make_assessment_item()

        task = SimpleNamespace(id="task11")

        item.style_sheet(task)

        stylesheet = item.root.find("stylesheet")

        self.assertIsNotNone(stylesheet)
        self.assertEqual(stylesheet.attrib["type"], "text/css")
        self.assertEqual(
            stylesheet.attrib["href"],
            "files/task11/redtick-display-none.css"
        )

    def test_clear_content_removes_unused_responses_but_keeps_selection(self):
        item = make_assessment_item()

        responses = [
            Response(id="RESPONSE_1", value="10"),
            Response(id="RESPONSE_2", value="20"),
            Selection(id="SELECTION", correct=["A"], incorrect=["B"])
        ]

        tables = [
            SimpleNamespace(id="TABLE_1"),
            SimpleNamespace(id="TABLE_2")
        ]

        item.clear_content(
            used_content=["RESPONSE_1", "TABLE_2"],
            responses=responses,
            tables=tables
        )

        self.assertEqual(
            [response.id for response in responses],
            ["RESPONSE_1", "SELECTION"]
        )

        self.assertEqual(
            [table.id for table in tables],
            ["TABLE_2"]
        )


if __name__ == "__main__":
    unittest.main()