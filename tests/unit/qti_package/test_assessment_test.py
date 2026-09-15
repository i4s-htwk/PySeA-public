import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace

from backend.QTI_Paket.AssessmentTest import AssessmentTest


def make_assessment_test():
    assessment_test = object.__new__(AssessmentTest)
    assessment_test.root = ET.Element("assessmentTest")
    return assessment_test


def task(
    task_id,
    global_variables_used=None,
    variant_dependent_tables=None
):
    return SimpleNamespace(
        id=task_id,
        global_variables_used=global_variables_used or [],
        variant_dependent_tables=variant_dependent_tables or []
    )


def section(
    section_id="section1",
    title="Section 1",
    list_tasks=None,
    excel_variables=None,
    local_variables_used=None
):
    return SimpleNamespace(
        id=section_id,
        title=title,
        list_tasks=list_tasks or [],
        excel_variables=excel_variables,
        local_variables_used=local_variables_used or [],
        images_used=[],
        variant_dependent_images=[],
        global_variables_used=[]
    )


class DummyItemBody:
    def __init__(self, text_by_id=None):
        self.text_by_id = text_by_id or {}

    def get_item(self, item_id):
        return self.text_by_id.get(item_id, "")


class DummyTables:
    def create_tables(self, section_obj, task_obj):
        return []


class TestAssessmentTest(unittest.TestCase):

    def test_outcome_declaration_creates_score_pass_and_pass_score(self):
        assessment_test = make_assessment_test()

        assessment_test.outcome_declaration(
            pass_score_pertentage=50,
            max_score=20,
            navigation_mode="nonlinear"
        )

        identifiers = [
            declaration.attrib["identifier"]
            for declaration in assessment_test.root.findall("outcomeDeclaration")
        ]

        self.assertIn("SCORE", identifiers)
        self.assertIn("MINSCORE", identifiers)
        self.assertIn("PASS", identifiers)
        self.assertIn("PASS_SCORE", identifiers)
        self.assertIn("MAXSCORE", identifiers)
        self.assertIn("FEEDBACKMODAL", identifiers)

        pass_score = assessment_test.root.find(
            "./outcomeDeclaration[@identifier='PASS_SCORE']/defaultValue/value"
        )

        self.assertIsNotNone(pass_score)
        self.assertEqual(pass_score.text, "10.0")

        pass_declaration = assessment_test.root.find(
            "./outcomeDeclaration[@identifier='PASS']"
        )

        self.assertEqual(pass_declaration.attrib["baseType"], "boolean")

    def test_outcome_declaration_does_not_create_maxscore_for_test_path_control(self):
        assessment_test = make_assessment_test()

        assessment_test.outcome_declaration(
            pass_score_pertentage=50,
            max_score=20,
            navigation_mode="test_path_control"
        )

        maxscore = assessment_test.root.find(
            "./outcomeDeclaration[@identifier='MAXSCORE']"
        )

        self.assertIsNone(maxscore)

    def test_template_declaration_does_nothing_when_variants_are_disabled(self):
        assessment_test = make_assessment_test()

        variants = SimpleNamespace(
            use_variants=False
        )

        assessment_test.template_declaration(
            variants=variants,
            teststructure=[
                section()
            ]
        )

        declarations = assessment_test.root.findall("templateDeclaration")

        self.assertEqual(declarations, [])

    def test_template_declaration_creates_variant_and_student_id_variables(self):
        assessment_test = make_assessment_test()

        variants = SimpleNamespace(
            use_variants=True,
            list_variants=[1, 2, 3]
        )

        assessment_test.template_declaration(
            variants=variants,
            teststructure=[
                section()
            ]
        )

        identifiers = [
            declaration.attrib["identifier"]
            for declaration in assessment_test.root.findall("templateDeclaration")
        ]

        self.assertIn("Variante", identifiers)
        self.assertIn("Matr_Nr_automatisch", identifiers)

        variante = assessment_test.root.find(
            "./templateDeclaration[@identifier='Variante']"
        )

        self.assertEqual(variante.attrib["baseType"], "integer")

    def test_template_declaration_adds_global_variables_used_by_tasks(self):
        assessment_test = make_assessment_test()

        variants = SimpleNamespace(
            use_variants=True,
            list_variants=[1, 2, 3]
        )

        teststructure = [
            section(
                list_tasks=[
                    task("task11", global_variables_used=["a", "b"]),
                    task("task12", global_variables_used=["c"])
                ]
            )
        ]

        assessment_test.template_declaration(
            variants=variants,
            teststructure=teststructure
        )

        identifiers = [
            declaration.attrib["identifier"]
            for declaration in assessment_test.root.findall("templateDeclaration")
        ]

        self.assertIn("a", identifiers)
        self.assertIn("b", identifiers)
        self.assertIn("c", identifiers)

    def test_template_declaration_adds_local_variables_from_sections(self):
        assessment_test = make_assessment_test()

        variants = SimpleNamespace(
            use_variants=True,
            list_variants=[1, 2, 3]
        )

        teststructure = [
            section(
                local_variables_used=[
                    ("LOCAL_VARIABLE_1_0", "$(1)+5", "x"),
                    ("LOCAL_VARIABLE_1_1", "$(1)*2", "y")
                ]
            )
        ]

        assessment_test.template_declaration(
            variants=variants,
            teststructure=teststructure
        )

        identifiers = [
            declaration.attrib["identifier"]
            for declaration in assessment_test.root.findall("templateDeclaration")
        ]

        self.assertIn("LOCAL_VARIABLE_1_0", identifiers)
        self.assertIn("x", identifiers)
        self.assertIn("LOCAL_VARIABLE_1_1", identifiers)
        self.assertIn("y", identifiers)

    def test_add_editordata_adds_json_stylesheet_reference(self):
        assessment_test = make_assessment_test()

        assessment_test.add_editordata()

        stylesheet = assessment_test.root.find("stylesheet")

        self.assertIsNotNone(stylesheet)
        self.assertEqual(stylesheet.attrib["type"], "application/json")
        self.assertEqual(
            stylesheet.attrib["href"],
            "files/assessmenttest/editordata.json"
        )

    def test_test_part_creates_testpart_section_and_item_refs(self):
        assessment_test = make_assessment_test()

        advanced_settings = SimpleNamespace(
            navigation_mode="nonlinear",
            keep_responses=False
        )

        teststructure = [
            section(
                section_id="section1",
                title="Erste Sektion",
                list_tasks=[
                    task("task11"),
                    task("task12")
                ]
            )
        ]

        variants = SimpleNamespace(
            use_variants=False,
            assignment=None
        )

        assessment_test.test_part(
            advanced_settings=advanced_settings,
            test_struktur=teststructure,
            bilder=[],
            item_body=DummyItemBody({"section1": "Einleitungstext"}),
            variants=variants,
            tables=DummyTables()
        )

        test_part = assessment_test.root.find("testPart")

        self.assertIsNotNone(test_part)
        self.assertEqual(test_part.attrib["identifier"], "testpart")
        self.assertEqual(test_part.attrib["navigationMode"], "nonlinear")
        self.assertEqual(test_part.attrib["data-testcontrol"], "false")
        self.assertEqual(test_part.attrib["submissionMode"], "individual")

        assessment_section = test_part.find("assessmentSection")

        self.assertIsNotNone(assessment_section)
        self.assertEqual(assessment_section.attrib["identifier"], "section1")
        self.assertEqual(assessment_section.attrib["title"], "Erste Sektion")

        item_refs = assessment_section.findall("assessmentItemRef")

        self.assertEqual(len(item_refs), 2)

        self.assertEqual(item_refs[0].attrib["identifier"], "task11")
        self.assertEqual(item_refs[0].attrib["href"], "task11.xml")

        self.assertEqual(item_refs[1].attrib["identifier"], "task12")
        self.assertEqual(item_refs[1].attrib["href"], "task12.xml")

    def test_test_part_maps_test_path_control_to_linear_navigation(self):
        assessment_test = make_assessment_test()

        advanced_settings = SimpleNamespace(
            navigation_mode="test_path_control",
            keep_responses=False
        )

        teststructure = [
            section(
                section_id="section1",
                title="Erste Sektion",
                list_tasks=[
                    task("task11")
                ]
            )
        ]

        variants = SimpleNamespace(
            use_variants=False,
            assignment=None
        )

        assessment_test.test_part(
            advanced_settings=advanced_settings,
            test_struktur=teststructure,
            bilder=[],
            item_body=DummyItemBody({"section1": ""}),
            variants=variants,
            tables=DummyTables()
        )

        test_part = assessment_test.root.find("testPart")

        self.assertEqual(test_part.attrib["navigationMode"], "linear")
        self.assertEqual(test_part.attrib["data-testcontrol"], "true")

    def test_test_part_adds_keep_responses_session_controls(self):
        assessment_test = make_assessment_test()

        advanced_settings = SimpleNamespace(
            navigation_mode="nonlinear",
            keep_responses=True
        )

        teststructure = [
            section(
                section_id="section1",
                title="Erste Sektion",
                list_tasks=[
                    task("task11")
                ]
            )
        ]

        variants = SimpleNamespace(
            use_variants=False,
            assignment=None
        )

        assessment_test.test_part(
            advanced_settings=advanced_settings,
            test_struktur=teststructure,
            bilder=[],
            item_body=DummyItemBody({"section1": ""}),
            variants=variants,
            tables=DummyTables()
        )

        test_part = assessment_test.root.find("testPart")
        test_part_session_control = test_part.find("itemSessionControl")

        self.assertIsNotNone(test_part_session_control)
        self.assertEqual(
            test_part_session_control.attrib["data-features"],
            "keepResponses"
        )

        assessment_section = test_part.find("assessmentSection")
        section_session_control = assessment_section.find("itemSessionControl")

        self.assertIsNotNone(section_session_control)
        self.assertEqual(
            section_session_control.attrib["data-features"],
            "keepResponses"
        )

        item_ref = assessment_section.find("assessmentItemRef")
        item_ref_session_control = item_ref.find("itemSessionControl")

        self.assertIsNotNone(item_ref_session_control)
        self.assertEqual(
            item_ref_session_control.attrib["data-features"],
            "keepResponses"
        )

    def test_test_part_adds_template_defaults_and_precondition_for_variant_tasks(self):
        assessment_test = make_assessment_test()

        advanced_settings = SimpleNamespace(
            navigation_mode="nonlinear",
            keep_responses=False
        )

        teststructure = [
            section(
                section_id="section1",
                title="Erste Sektion",
                list_tasks=[
                    task(
                        "task11",
                        global_variables_used=["a"]
                    ),
                    task("task_variant_assignment")
                ]
            )
        ]

        variants = SimpleNamespace(
            use_variants=True,
            task_id="task_variant_assignment",
            assignment=None
        )

        assessment_test.test_part(
            advanced_settings=advanced_settings,
            test_struktur=teststructure,
            bilder=[],
            item_body=DummyItemBody({"section1": ""}),
            variants=variants,
            tables=DummyTables()
        )

        task11_ref = assessment_test.root.find(
            ".//assessmentItemRef[@identifier='task11']"
        )

        self.assertIsNotNone(task11_ref)

        variante_template_default = task11_ref.find(
            "./templateDefault[@templateIdentifier='Variante']"
        )
        variable_a_template_default = task11_ref.find(
            "./templateDefault[@templateIdentifier='a']"
        )

        self.assertIsNotNone(variante_template_default)
        self.assertIsNotNone(variable_a_template_default)

        precondition = task11_ref.find("preCondition")
        self.assertIsNotNone(precondition)

        equal = precondition.find("equal")
        self.assertIsNotNone(equal)

        score_variable = equal.find("./variable[@identifier='task_variant_assignment.SCORE']")
        score_base_value = equal.find("./baseValue[@baseType='float']")

        self.assertIsNotNone(score_variable)
        self.assertIsNotNone(score_base_value)
        self.assertEqual(score_base_value.text, "1")

    def test_test_part_adds_student_id_template_default_for_variant_assignment_task(self):
        assessment_test = make_assessment_test()

        advanced_settings = SimpleNamespace(
            navigation_mode="nonlinear",
            keep_responses=False
        )

        teststructure = [
            section(
                section_id="section1",
                title="Erste Sektion",
                list_tasks=[
                    task("task_variant_assignment")
                ]
            )
        ]

        variants = SimpleNamespace(
            use_variants=True,
            task_id="task_variant_assignment",
            assignment=None
        )

        assessment_test.test_part(
            advanced_settings=advanced_settings,
            test_struktur=teststructure,
            bilder=[],
            item_body=DummyItemBody({"section1": ""}),
            variants=variants,
            tables=DummyTables()
        )

        variant_assignment_ref = assessment_test.root.find(
            ".//assessmentItemRef[@identifier='task_variant_assignment']"
        )

        template_default = variant_assignment_ref.find(
            "./templateDefault[@templateIdentifier='Matr_Nr_automatisch']"
        )

        self.assertIsNotNone(template_default)

        variable = template_default.find(
            "./variable[@identifier='Matr_Nr_automatisch']"
        )

        self.assertIsNotNone(variable)

    def test_outcome_processing_sums_scores_and_sets_pass(self):
        assessment_test = make_assessment_test()

        variants = SimpleNamespace(
            use_variants=False
        )

        feedback = {
            "feedback_correct": SimpleNamespace(id="feedback_correct"),
            "feedback_incorrect": SimpleNamespace(id="feedback_incorrect")
        }

        assessment_test.outcome_processing(
            variants=variants,
            feedback=feedback,
            test_structure=[]
        )

        outcome_processing = assessment_test.root.find("outcomeProcessing")

        self.assertIsNotNone(outcome_processing)

        score_sum = outcome_processing.find(
            "./setOutcomeValue[@identifier='SCORE']/sum/testVariables[@variableIdentifier='SCORE']"
        )

        self.assertIsNotNone(score_sum)

        pass_true = outcome_processing.find(
            "./outcomeCondition/outcomeIf/setOutcomeValue[@identifier='PASS']/baseValue[@baseType='boolean']"
        )

        self.assertIsNotNone(pass_true)
        self.assertEqual(pass_true.text, "true")

    def test_outcome_processing_adds_feedback_modal_outcomes(self):
        assessment_test = make_assessment_test()

        variants = SimpleNamespace(
            use_variants=False
        )

        feedback = {
            "feedback_correct": SimpleNamespace(id="feedback_correct"),
            "feedback_incorrect": SimpleNamespace(id="feedback_incorrect")
        }

        assessment_test.outcome_processing(
            variants=variants,
            feedback=feedback,
            test_structure=[]
        )

        feedback_values = [
            value.text
            for value in assessment_test.root.findall(
                ".//setOutcomeValue[@identifier='FEEDBACKMODAL']/multiple/baseValue"
            )
        ]

        self.assertIn("feedback_correct", feedback_values)
        self.assertIn("feedback_incorrect", feedback_values)

    def test_outcome_processing_with_variants_sets_variant_and_global_variables(self):
        assessment_test = make_assessment_test()

        variants = SimpleNamespace(
            use_variants=True,
            task_id="task_variant_assignment"
        )

        feedback = {
            "feedback_correct": SimpleNamespace(id="feedback_correct"),
            "feedback_incorrect": SimpleNamespace(id="feedback_incorrect")
        }

        teststructure = [
            section(
                list_tasks=[
                    task("task11", global_variables_used=["a", "b"])
                ],
                local_variables_used=[
                    ("LOCAL_VARIABLE_1_0", "$(1)+5", "x")
                ]
            )
        ]

        assessment_test.outcome_processing(
            variants=variants,
            feedback=feedback,
            test_structure=teststructure
        )

        variante_value = assessment_test.root.find(
            "./outcomeProcessing/setTemplateValue[@identifier='Variante']/variable[@identifier='task_variant_assignment.Variante']"
        )

        variable_a = assessment_test.root.find(
            "./outcomeProcessing/setTemplateValue[@identifier='a']/variable[@identifier='task_variant_assignment.a']"
        )

        variable_b = assessment_test.root.find(
            "./outcomeProcessing/setTemplateValue[@identifier='b']/variable[@identifier='task_variant_assignment.b']"
        )

        local_source_variable = assessment_test.root.find(
            "./outcomeProcessing/setTemplateValue[@identifier='x']/variable[@identifier='task_variant_assignment.x']"
        )

        local_variable = assessment_test.root.find(
            "./outcomeProcessing/setTemplateValue[@identifier='LOCAL_VARIABLE_1_0']/customOperator[@definition='MAXIMA']"
        )

        self.assertIsNotNone(variante_value)
        self.assertIsNotNone(variable_a)
        self.assertIsNotNone(variable_b)
        self.assertIsNotNone(local_source_variable)
        self.assertIsNotNone(local_variable)
        self.assertEqual(local_variable.attrib["value"], "$(1)+5")


if __name__ == "__main__":
    unittest.main()