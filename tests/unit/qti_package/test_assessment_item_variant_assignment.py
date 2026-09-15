import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace

from backend.QTI_Paket.AssessmentItemVariantAssignment import AssessmentItemVariantAssignment
from backend.utils.Variants.ManualAssignment import ManualAssignment
from backend.utils.Variants.VariableDependentAssignment.VariableDependentAssignment import VariableDependentAssignment
from backend.utils.Variants.StudentIdToVariantAssignment import StudentIdToVariantAssignment


def make_variant_assignment_item():
    item = object.__new__(AssessmentItemVariantAssignment)
    item.root = ET.Element("assessmentItem")
    return item


class TestAssessmentItemVariantAssignment(unittest.TestCase):

    def test_outcome_declaration_creates_response_and_global_outcomes(self):
        item = make_variant_assignment_item()

        responses = [
            SimpleNamespace(id="RESPONSE")
        ]

        item.outcome_declaration(responses)

        identifiers = [
            declaration.attrib["identifier"]
            for declaration in item.root.findall("outcomeDeclaration")
        ]

        self.assertIn("SCORE_RESPONSE", identifiers)
        self.assertIn("MINSCORE_RESPONSE", identifiers)
        self.assertIn("MAXSCORE_RESPONSE", identifiers)

        self.assertIn("SCORE", identifiers)
        self.assertIn("MINSCORE", identifiers)
        self.assertIn("MAXSCORE", identifiers)
        self.assertIn("FEEDBACKBASIC", identifiers)
        self.assertIn("FEEDBACKMODAL", identifiers)

        maxscore_response = item.root.find(
            "./outcomeDeclaration[@identifier='MAXSCORE_RESPONSE']/defaultValue/value"
        )

        self.assertIsNotNone(maxscore_response)
        self.assertEqual(maxscore_response.text, "1")

    def test_template_declaration_for_manual_assignment_only_declares_variante(self):
        item = make_variant_assignment_item()

        variant_assignment = ManualAssignment()
        item.template_declaration(variant_assignment)

        declarations = item.root.findall("templateDeclaration")

        self.assertEqual(len(declarations), 1)
        self.assertEqual(declarations[0].attrib["identifier"], "Variante")
        self.assertEqual(declarations[0].attrib["baseType"], "float")

    def test_template_processing_before_for_manual_assignment_sets_correct_response_to_variante(self):
        item = make_variant_assignment_item()

        variant_assignment = ManualAssignment()
        item.template_processing_before(variant_assignment)

        set_correct_response = item.root.find(
            "./templateProcessing/setCorrectResponse[@identifier='RESPONSE']"
        )

        self.assertIsNotNone(set_correct_response)

        variable = set_correct_response.find("variable")

        self.assertIsNotNone(variable)
        self.assertEqual(variable.attrib["identifier"], "Variante")

    def test_template_processing_after_for_manual_assignment_checks_response_range(self):
        item = make_variant_assignment_item()

        variant_assignment = ManualAssignment()
        variant_assignment.get_count_variants = lambda: 4

        response_processing = ET.SubElement(item.root, "responseProcessing")

        item.template_processing_after(response_processing, variant_assignment)

        response_condition = response_processing.find("responseCondition")
        self.assertIsNotNone(response_condition)

        gte = response_condition.find("./responseIf/and/gte")
        lte = response_condition.find("./responseIf/and/lte")

        self.assertIsNotNone(gte)
        self.assertIsNotNone(lte)

        lower_bound = gte.find("baseValue")
        upper_bound = lte.find("baseValue")

        self.assertEqual(lower_bound.text, "1")
        self.assertEqual(upper_bound.text, "4")

        set_template_value = response_condition.find(
            "./responseIf/setTemplateValue[@identifier='Variante']"
        )

        self.assertIsNotNone(set_template_value)

    def test_set_template_value_creates_maxima_custom_operator(self):
        item = make_variant_assignment_item()

        response_processing = ET.Element("responseProcessing")

        item.set_template_value(
            response_processing=response_processing,
            identifier="Variante",
            maxima_code="$(1)+1",
            variables=["RESPONSE"]
        )

        set_template_value = response_processing.find("setTemplateValue")

        self.assertIsNotNone(set_template_value)
        self.assertEqual(set_template_value.attrib["identifier"], "Variante")

        custom_operator = set_template_value.find("customOperator")

        self.assertIsNotNone(custom_operator)
        self.assertEqual(custom_operator.attrib["definition"], "MAXIMA")
        self.assertEqual(custom_operator.attrib["value"], "$(1)+1")

        variable = custom_operator.find("variable")

        self.assertIsNotNone(variable)
        self.assertEqual(variable.attrib["identifier"], "RESPONSE")

    def test_template_declaration_for_variable_dependent_assignment_declares_variables(self):
        item = make_variant_assignment_item()

        variable = SimpleNamespace(
            id="VARIANT_ID",
            variables=["a", "b"]
        )

        variant_assignment = object.__new__(VariableDependentAssignment)
        variant_assignment.list_variables = [variable]

        item.template_declaration(variant_assignment)

        identifiers = [
            declaration.attrib["identifier"]
            for declaration in item.root.findall("templateDeclaration")
        ]

        self.assertIn("Variante", identifiers)
        self.assertIn("RESPONSE_TO_STRING", identifiers)
        self.assertIn("IS_INTEGER", identifiers)
        self.assertIn("RESPONSE_TO_STRING_AUTOMATISCH", identifiers)
        self.assertIn("Matr_Nr_automatisch", identifiers)

        self.assertIn("VARIANT_ID", identifiers)
        self.assertIn("a", identifiers)
        self.assertIn("b", identifiers)

    def test_template_declaration_for_student_id_assignment_declares_helper_variables(self):
        item = make_variant_assignment_item()

        variant_assignment = object.__new__(StudentIdToVariantAssignment)

        item.template_declaration(variant_assignment)

        identifiers = [
            declaration.attrib["identifier"]
            for declaration in item.root.findall("templateDeclaration")
        ]

        self.assertIn("Variante", identifiers)
        self.assertIn("RESPONSE_TO_STRING", identifiers)
        self.assertIn("IS_INTEGER", identifiers)
        self.assertIn("RESPONSE_TO_STRING_AUTOMATISCH", identifiers)
        self.assertIn("Matr_Nr_automatisch", identifiers)

if __name__ == "__main__":
    unittest.main()