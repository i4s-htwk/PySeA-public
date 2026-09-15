import xml.etree.ElementTree as ET

from .utils import *
from ..utils.Variants.ManualAssignment import ManualAssignment
from ..utils.Variants.VariableDependentAssignment.VariableDependentAssignment import VariableDependentAssignment
from ..utils.Variants.StudentIdToVariantAssignment import StudentIdToVariantAssignment


class AssessmentItemVariantAssignment:

    def __init__(self, task, images, item_body, responses, feedback, variants, temp_dir):
        if isinstance(variants.assignment, VariableDependentAssignment):
            variants.assignment.update_variants()

        self.root = ET.Element("assessmentItem", attrib={
            "xmlns": "http://www.imsglobal.org/xsd/imsqti_v2p1",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1p1.xsd http://www.w3.org/1998/Math/MathML http://www.w3.org/Math/XMLSchema/mathml2/mathml2.xsd",
            "identifier": task.id,
            "title": task.title,
            "adaptive": "false",
            "timeDependent": "false"})

        self.response_declaration(responses)
        self.outcome_declaration(responses)
        self.template_declaration(variants.assignment)
        self.template_processing_before(variants.assignment)
        item_body_tag = ET.SubElement(self.root, "itemBody")
        create_item_body(item_body_tag, task, item_body, images, None, None, None, variants.assignment)
        self.response_processing(responses, feedback, variants.assignment)
        create_feedback(self.root, feedback, [None, None], images, item=task, variant_assignment=variants.assignment)

        self.file_path = write_xml_document(self.root, str(task.id) + ".xml", temp_dir)

    def response_declaration (self, responses):
        for antwort in responses:
            ET.SubElement(self.root, "responseDeclaration",{"identifier": antwort.id, "cardinality": "single", "baseType": "integer"})

    def outcome_declaration(self, responses):
        for antwort in responses:
            outcome_data = [
                {"identifier": "SCORE_"+antwort.id, "default": "0"},
                {"identifier": "MINSCORE_"+antwort.id, "default": "0"},
                {"identifier": "MAXSCORE_"+antwort.id, "default": "1"}]
            for outcome in outcome_data:
                outcome_declaration = ET.SubElement(self.root, "outcomeDeclaration",{"identifier": outcome["identifier"], "cardinality": "single", "baseType": "float"})
                default_value = ET.SubElement(outcome_declaration, "defaultValue")
                ET.SubElement(default_value, "value").text = outcome["default"]

        outcome_data = [
            {"identifier": "SCORE", "cardinality":"single", "baseType": "float", "default": "0"},
            {"identifier": "MINSCORE","cardinality":"single", "baseType": "float", "default": "0", "view": "testConstructor"},
            {"identifier": "MAXSCORE", "cardinality":"single","baseType": "float", "default": "1"},
            {"identifier": "FEEDBACKBASIC","cardinality":"single", "baseType": "identifier", "default": "empty"},
            {"identifier": "FEEDBACKMODAL", "cardinality":"multiple","baseType": "identifier", "default": "empty", "view": "testConstructor"}]
        for outcome in outcome_data:
            outcome_declaration = ET.SubElement(self.root, "outcomeDeclaration",{"identifier": outcome["identifier"], "cardinality": outcome["cardinality"], "baseType": outcome["baseType"]})
            if "view" in outcome:
                outcome_declaration.set("view", outcome["view"])
            default_value = ET.SubElement(outcome_declaration, "defaultValue")
            ET.SubElement(default_value, "value").text = outcome["default"]

    def template_declaration(self, variant_assignment):
        list_variables = [("Variante", "float")]
        if isinstance(variant_assignment, VariableDependentAssignment) or isinstance(variant_assignment, StudentIdToVariantAssignment):
            list_variables += [("RESPONSE_TO_STRING", "string"), ("IS_INTEGER", "integer"),
                               ("RESPONSE_TO_STRING_AUTOMATISCH", "string"), ("Matr_Nr_automatisch", "string")]
        if isinstance(variant_assignment, VariableDependentAssignment) :
            for variable in variant_assignment.list_variables:
                list_variables.append((variable.id,"float"))
                for v in variable.variables:
                    list_variables.append((v, "float"))
        for variable in list_variables:
            ET.SubElement(self.root, "templateDeclaration", {"identifier":variable[0], "cardinality":"single", "baseType":variable[1]})

    def template_processing_before(self, variant_assignment):
        if isinstance(variant_assignment, VariableDependentAssignment) or isinstance(variant_assignment, StudentIdToVariantAssignment):
            template_processing = ET.SubElement(self.root, "templateProcessing")
            set_template_value = ET.SubElement(template_processing, "setTemplateValue", {"identifier": "IS_INTEGER"})
            ET.SubElement(set_template_value, "baseValue", {"baseType": "integer"}).text = "0"
            set_template_value = ET.SubElement(template_processing, "setTemplateValue", {"identifier": "RESPONSE_TO_STRING_AUTOMATISCH"})
            custom_operator = ET.SubElement(set_template_value, "customOperator",{"definition":"MAXIMA", "value":'charlist("$(1)")'})
            ET.SubElement(custom_operator, "variable", {"identifier":"Matr_Nr_automatisch"})
            set_correct_response = ET.SubElement(template_processing, "setCorrectResponse", {"identifier": "RESPONSE"})
            ET.SubElement(set_correct_response, "variable", {"identifier": "IS_INTEGER"})
        elif isinstance(variant_assignment, ManualAssignment):
            template_processing = ET.SubElement(self.root, "templateProcessing")
            set_correct_response = ET.SubElement(template_processing, "setCorrectResponse", {"identifier": "RESPONSE"})
            ET.SubElement(set_correct_response, "variable", {"identifier": "Variante"})

    def set_template_value(self,response_processing, identifier, maxima_code, variables):
        set_template_value = ET.SubElement(response_processing, "setTemplateValue",{"identifier": identifier})
        custom_operator = ET.SubElement(set_template_value, "customOperator", {"definition":"MAXIMA", "value":maxima_code})
        for variable in variables:
            ET.SubElement(custom_operator, "variable", {"identifier":variable})

    def template_processing_after(self, response_processing, variant_assignment):
        if isinstance(variant_assignment, VariableDependentAssignment):
            self.set_template_value(response_processing, "RESPONSE_TO_STRING", 'charlist("$(1)")', ["RESPONSE"])
            set_correct_response = ET.SubElement(response_processing, "setCorrectResponse", {"identifier":"RESPONSE"})
            ET.SubElement(set_correct_response, "variable", {"identifier":"IS_INTEGER"})
            for variable in variant_assignment.list_variables:
                maxima_code = variable.maxima_code_id()
                self.set_template_value(response_processing, variable.id, maxima_code, ["RESPONSE_TO_STRING"])
            for variable in variant_assignment.list_variables:
                for v in variable.variables:
                    maxima_code = variable.maxima_code_variable(v)
                    self.set_template_value(response_processing, v, maxima_code, [variable.id])

            variables = [v.id for v in variant_assignment.list_variables]
            maxima_code = variant_assignment.maxima_code_variants()
            self.set_template_value(response_processing, "Variante", maxima_code, variables)

        elif isinstance(variant_assignment, StudentIdToVariantAssignment):
            set_correct_response = ET.SubElement(response_processing, "setCorrectResponse", {"identifier": "RESPONSE"})
            ET.SubElement(set_correct_response, "variable", {"identifier": "IS_INTEGER"})
            maxima_code = variant_assignment.maxima_code_variants()
            self.set_template_value(response_processing, "Variante", maxima_code, ["RESPONSE"])
            
        elif isinstance(variant_assignment, ManualAssignment):
            response_condition = ET.SubElement(response_processing, "responseCondition")
            response_if = ET.SubElement(response_condition, "responseIf")
            and_tag = ET.SubElement(response_if, "and")
            gte = ET.SubElement(and_tag, "gte")
            ET.SubElement(gte, "variable", {"identifier": "RESPONSE"})
            ET.SubElement(gte, "baseValue", {"baseType": "float"}).text = "1"
            lte = ET.SubElement(and_tag, "lte")
            ET.SubElement(lte, "variable", {"identifier": "RESPONSE"})
            ET.SubElement(lte, "baseValue", {"baseType": "float"}).text = str(variant_assignment.get_count_variants())
            self.set_template_value(response_if, "Variante", "$(1)", ["RESPONSE"])

    def response_processing(self, responses, feedback, variant_assignment):

        equal_attribs = {}
        if isinstance(variant_assignment, VariableDependentAssignment) or isinstance(variant_assignment, StudentIdToVariantAssignment):
            equal_attribs = {"toleranceMode":"absolute", "tolerance":"10000 99999", "includeLowerBound":"true", "includeUpperBound":"true"}
        elif isinstance(variant_assignment, ManualAssignment):
            upper_bound = str(variant_assignment.get_count_variants())
            equal_attribs = {"toleranceMode": "absolute", "tolerance": "1 "+upper_bound, "includeLowerBound": "true", "includeUpperBound": "true"}
        response_processing = ET.SubElement(self.root, "responseProcessing")
        for response in responses:
            response_processing_response(response_processing, response.id, equal_attribs)

        set_outcome_value = ET.SubElement(response_processing, "setOutcomeValue", {"identifier":"SCORE"})
        sum = ET.SubElement(set_outcome_value, "sum")
        for response in responses:
            ET.SubElement(sum, "variable", {"identifier":"SCORE_"+response.id})

        self.template_processing_after(response_processing, variant_assignment)

        if isinstance(variant_assignment, ManualAssignment):
            response_condition = ET.SubElement(response_processing, "responseCondition", {"class": "ONYX_SET_SCORE"})
            response_if = ET.SubElement(response_condition, "responseIf")
            or_tag = ET.SubElement(response_if, "or")
            lt = ET.SubElement(or_tag, "lt")
            ET.SubElement(lt, "variable", {"identifier": "RESPONSE"})
            ET.SubElement(lt, "baseValue", {"baseType": "float"}).text = "1"
            gt = ET.SubElement(or_tag, "gt")
            ET.SubElement(gt, "variable", {"identifier": "RESPONSE"})
            ET.SubElement(gt, "baseValue", {"baseType": "float"}).text = str(variant_assignment.get_count_variants())
            set_outcome_if = ET.SubElement(response_if, "setOutcomeValue", {"identifier": "SCORE", "class": "ONYX_SET_SCORE"})
            ET.SubElement(set_outcome_if, "baseValue", {"baseType": "float"}).text = "0"

            response_else = ET.SubElement(response_condition, "responseElse")
            set_outcome_else = ET.SubElement(response_else, "setOutcomeValue", {"identifier": "SCORE", "class": "ONYX_SET_SCORE"})
            base_else = ET.SubElement(set_outcome_else, "baseValue", {"baseType": "float"})
            base_else.text = "1"

        if isinstance(variant_assignment, VariableDependentAssignment) or isinstance(variant_assignment, StudentIdToVariantAssignment):
            response_condition = ET.SubElement(response_processing, "responseCondition", {"class": "ONYX_SET_SCORE"})
            response_if = ET.SubElement(response_condition, "responseIf")
            is_null = ET.SubElement(response_if, "isNull")
            ET.SubElement(is_null, "variable", {"identifier": "Matr_Nr_automatisch"})
            set_outcome_if = ET.SubElement(response_if, "setOutcomeValue", {"identifier": "SCORE", "class": "ONYX_SET_SCORE"})
            base_if = ET.SubElement(set_outcome_if, "baseValue", {"baseType": "float"})
            base_if.text = "1"
            response_elseif = ET.SubElement(response_condition, "responseElseIf")
            and_tag = ET.SubElement(response_elseif, "and")
            not_tag = ET.SubElement(and_tag, "not")
            is_null2 = ET.SubElement(not_tag, "isNull")
            ET.SubElement(is_null2, "variable", {"identifier": "Matr_Nr_automatisch"})
            match = ET.SubElement(and_tag, "match")
            ET.SubElement(match, "variable", {"identifier": "RESPONSE_TO_STRING_AUTOMATISCH"})
            ET.SubElement(match, "variable", {"identifier": "RESPONSE_TO_STRING"})
            set_outcome_elseif = ET.SubElement(response_elseif, "setOutcomeValue", {"identifier": "SCORE", "class": "ONYX_SET_SCORE"})
            base_elseif = ET.SubElement(set_outcome_elseif, "baseValue", {"baseType": "float"})
            base_elseif.text = "1"
            response_else = ET.SubElement(response_condition, "responseElse")
            set_outcome_else = ET.SubElement(response_else, "setOutcomeValue", {"identifier": "SCORE", "class": "ONYX_SET_SCORE"})
            base_else = ET.SubElement(set_outcome_else, "baseValue", {"baseType": "float"})
            base_else.text = "0"

        response_condition = ET.SubElement(response_processing, "responseCondition", {"class": "ONYX_SET_SCORE"})
        response_if = ET.SubElement(response_condition, "responseIf")
        equal = ET.SubElement(response_if, "equal", {"toleranceMode": "exact"})
        ET.SubElement(equal, "variable", {"identifier": "SCORE"})
        base_val = ET.SubElement(equal, "baseValue", {"baseType": "float"})
        base_val.text = "1"
        set_outcome_if = ET.SubElement(response_if, "setOutcomeValue", {"identifier": "SCORE_RESPONSE", "class": "ONYX_SET_SCORE"})
        base_val_if = ET.SubElement(set_outcome_if, "baseValue", {"baseType": "float"})
        base_val_if.text = "1"
        response_else = ET.SubElement(response_condition, "responseElse")
        set_outcome_else = ET.SubElement(response_else, "setOutcomeValue", {"identifier": "SCORE_RESPONSE", "class": "ONYX_SET_SCORE"})
        base_val_else = ET.SubElement(set_outcome_else, "baseValue", {"baseType": "float"})
        base_val_else.text = "0"

        response_processing_score_bounds(response_processing)
        response_processing_feedback(response_processing, feedback, None, 1)
