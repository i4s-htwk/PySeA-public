import xml.etree.ElementTree as ET

from .utils import write_xml_document, create_feedback, create_item_body


class AssessmentTest:

    def __init__(self, configurations, teststructure, images, item_body, variants, max_score, tables, temp_dir):

        self.root = ET.Element("assessmentTest", attrib={
            "xmlns": "http://www.imsglobal.org/xsd/imsqti_v2p1",  # Namespace hinzufügen
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1p1.xsd",
            "identifier": "assessmenttest",
            "title": configurations.title})
        self.test_part(configurations.advanced_settings, teststructure, images, item_body, variants, tables)
        self.outcome_declaration(configurations.pass_score_percentage, max_score, configurations.advanced_settings.navigation_mode)
        self.template_declaration(variants, teststructure)
        self.add_editordata()
        self.outcome_processing(variants, configurations.feedback, teststructure)
        create_feedback(self.root, configurations.feedback, ["Bestanden", "Nicht bestanden"], images)

        self.file_path = write_xml_document(self.root, "assessmenttest.xml", temp_dir)

    def outcome_declaration(self, pass_score_pertentage, max_score, navigation_mode):
        pass_score = float(max_score) * float(pass_score_pertentage)/100
        outcomes = [("SCORE", 0, "float", False), ("MINSCORE", 0, "float", None), ("PASS", "false", "boolean", None), ("PASS_SCORE", pass_score, "float", True)]
        if navigation_mode != "test_path_control": outcomes.append(("MAXSCORE", max_score, "float", None))
        for outcome_id, default_value, baseType, view in outcomes:
            outcome = ET.SubElement(self.root, "outcomeDeclaration",
                                    {"identifier": outcome_id, "cardinality": "single", "baseType": baseType})
            if view: outcome.attrib["view"]="testConstructor"
            default_value_elem = ET.SubElement(outcome, "defaultValue")
            ET.SubElement(default_value_elem, "value").text = str(default_value)
        ET.SubElement(self.root, "outcomeDeclaration",
                      {"identifier": "FEEDBACKMODAL", "cardinality": "multiple", "baseType": "identifier", "view":"testConstructor"})

    def template_declaration(self, variants, teststructure):
        if variants.use_variants:
            ET.SubElement(self.root, "templateDeclaration", {"identifier": "Variante", "cardinality": "single", "baseType": "integer"})
            ET.SubElement(self.root, "templateDeclaration", {"identifier": "Matr_Nr_automatisch", "cardinality": "single", "baseType": "string"})
            list_variables_used = []
            for section in teststructure:
                if section.excel_variables:
                    for variable in section.excel_variables.variables:
                        nks = section.excel_variables.get_nks(variants.assignment.get_count_variants(), variable.cell)
                        ET.SubElement(self.root, "templateDeclaration",
                                      {"identifier": variable.variable_id, "cardinality": "single", "baseType": "float", "format":f"%.{nks}f"})
                for v in section.local_variables_used:
                    ET.SubElement(self.root, "templateDeclaration",
                                  {"identifier": v[0], "cardinality": "single", "baseType": "float"})
                    ET.SubElement(self.root, "templateDeclaration",
                                  {"identifier": v[2], "cardinality": "single", "baseType": "float"})
                for task in section.list_tasks:
                    list_variables_used += task.global_variables_used
            for v in list_variables_used:
                ET.SubElement(self.root, "templateDeclaration", {"identifier": v, "cardinality": "single", "baseType": "float"})

    def add_editordata(self):
        ET.SubElement(self.root, "stylesheet", {
            "type": "application/json",
            "href": "files/assessmenttest/editordata.json"
        })

    def test_part(self, advanced_settings, test_struktur, bilder, item_body, variants, tables):
        if advanced_settings.navigation_mode == "test_path_control":
            navigation_mode = "linear"
            data_testcontrol = "true"
        else:
            navigation_mode = advanced_settings.navigation_mode
            data_testcontrol = "false"
        test_part = ET.SubElement(self.root, "testPart", {"identifier": "testpart", "navigationMode": navigation_mode, "data-testcontrol":data_testcontrol, "submissionMode": "individual"})
        attribs = {"allowComment": "false", "maxAttempts": "0"}
        if advanced_settings.keep_responses: attribs["data-features"]="keepResponses"
        ET.SubElement(test_part, "itemSessionControl", attribs)
        for sektion_obj in test_struktur:
                sektion_aktuell = ET.SubElement(test_part, "assessmentSection", {"identifier": sektion_obj.id, "fixed": "false", "title": sektion_obj.title, "visible": "true"})
                if advanced_settings.keep_responses: ET.SubElement(sektion_aktuell, "itemSessionControl", {"data-features":"keepResponses"})
                rubic_block = ET.SubElement(sektion_aktuell, "rubricBlock", {"view": "candidate"})
                current_item_body = item_body.get_item(sektion_obj.id)
                merged_tables = tables.create_tables(sektion_obj, None)

                variant_assignment = variants.assignment if variants else None
                create_item_body(rubic_block, sektion_obj, current_item_body, bilder, merged_tables, None, None, variant_assignment)

                for aufgabe_obj in sektion_obj.list_tasks:
                    assessment_item_ref = ET.SubElement(sektion_aktuell, "assessmentItemRef",{"identifier": aufgabe_obj.id,"href": str(aufgabe_obj.id)+".xml","fixed": "false"})
                    if advanced_settings.keep_responses: ET.SubElement(assessment_item_ref, "itemSessionControl", {"data-features": "keepResponses"})
                    if variants.use_variants and aufgabe_obj.id != variants.task_id:
                        template_default = ET.SubElement(assessment_item_ref, "templateDefault", {"templateIdentifier":"Variante"})
                        ET.SubElement(template_default, "variable", {"identifier":"Variante"})
                        for v in aufgabe_obj.global_variables_used:
                            template_default = ET.SubElement(assessment_item_ref, "templateDefault", {"templateIdentifier": v})
                            ET.SubElement(template_default, "variable", {"identifier": v})

                        pre_condition = ET.SubElement(assessment_item_ref, "preCondition", {"xmlns": "http://www.imsglobal.org/xsd/imsqti_v2p1"})
                        if len(aufgabe_obj.variant_dependent_tables) != 0:
                            table = None
                            for vdt in aufgabe_obj.variant_dependent_tables:
                                for key, t in vdt.tables.items():
                                    if t["task_id"] == aufgabe_obj.id:
                                        table = t
                            pre_condition = ET.SubElement(pre_condition, "and")
                            gte = ET.SubElement(pre_condition, "gte")
                            ET.SubElement(gte, "variable", {"identifier":"task_variant_assignment.Variante"})
                            ET.SubElement(gte, "baseValue", {"baseType":"float"}).text= str(table["lower"])
                            lte = ET.SubElement(pre_condition, "lte")
                            ET.SubElement(lte, "variable", {"identifier": "task_variant_assignment.Variante"})
                            ET.SubElement(lte, "baseValue", {"baseType": "float"}).text = str(table["upper"])
                        equal = ET.SubElement(pre_condition, "equal")
                        ET.SubElement(equal, "variable",{"identifier":"task_variant_assignment.SCORE"})
                        ET.SubElement(equal,"baseValue", {"baseType":"float"}).text = "1"
                    elif variants.use_variants and aufgabe_obj.id == variants.task_id:
                        template_default = ET.SubElement(assessment_item_ref, "templateDefault", {"templateIdentifier": "Matr_Nr_automatisch"})
                        ET.SubElement(template_default, "variable", {"identifier": "Matr_Nr_automatisch"})

    def outcome_processing (self, variants, feedback, test_structure):
        outcome_processing = ET.SubElement(self.root, "outcomeProcessing")
        set_outcomevalue = ET.SubElement(outcome_processing, "setOutcomeValue", {"identifier":"SCORE"})
        sum = ET.SubElement(set_outcomevalue, "sum")
        ET.SubElement(sum, "testVariables", {"variableIdentifier": "SCORE"})

        outcome_condition = ET.SubElement(outcome_processing, "outcomeCondition")
        outcome_if = ET.SubElement(outcome_condition, "outcomeIf")
        gte = ET.SubElement(outcome_if, "gte")
        ET.SubElement(gte, "variable", {"identifier":"SCORE"})
        ET.SubElement(gte, "variable", {"identifier": "PASS_SCORE"})
        set_outcome_value = ET.SubElement(outcome_if, "setOutcomeValue", {"identifier":"PASS"})
        ET.SubElement(set_outcome_value, "baseValue", {"baseType":"boolean"}).text = "true"
        outcome_else = ET.SubElement(outcome_condition, "outcomeElse")
        set_outcome_value = ET.SubElement(outcome_else, "setOutcomeValue", {"identifier": "PASS"})
        ET.SubElement(set_outcome_value, "baseValue", {"baseType": "boolean"}).text = "false"

        if variants.use_variants:
            set_template_value = ET.SubElement(outcome_processing, "setTemplateValue", {"identifier": "Variante"})
            ET.SubElement(set_template_value, "variable", {"identifier": variants.task_id+".Variante"})
            for section in test_structure:
                for task in section.list_tasks:
                    for v in task.global_variables_used:
                        set_template_value = ET.SubElement(outcome_processing, "setTemplateValue", {"identifier": v})
                        ET.SubElement(set_template_value, "variable", {"identifier": variants.task_id + "."+v})
            for section in test_structure:
                if section.excel_variables:
                    for v in section.excel_variables.variables:
                        set_template_value = ET.SubElement(outcome_processing, "setTemplateValue", {"identifier": v.variable_id})
                        custom_operator = ET.SubElement(set_template_value, "customOperator", {"definition": "MAXIMA", "value": section.excel_variables.maxima_code(variants.assignment.get_count_variants(), v.cell)})
                        ET.SubElement(custom_operator, "variable", {"identifier": "Variante"})
                for v in section.local_variables_used:
                    set_template_value = ET.SubElement(outcome_processing, "setTemplateValue", {"identifier": v[2]})
                    ET.SubElement(set_template_value, "variable", {"identifier": variants.task_id + "."+v[2]})

                    set_template_value = ET.SubElement(outcome_processing, "setTemplateValue", {"identifier": v[0]})
                    custom_operator = ET.SubElement(set_template_value, "customOperator", {"definition": "MAXIMA", "value": v[1]})
                    ET.SubElement(custom_operator, "variable", {"identifier": v[2]})

        feedback_dict = [("true", "feedback_correct"), ("false", "feedback_incorrect")]
        for bool, type in feedback_dict:
            outcome_condition = ET.SubElement(outcome_processing, "outcomeCondition")
            outcome_if = ET.SubElement(outcome_condition, "outcomeIf")
            and_tag = ET.SubElement(outcome_if, "and")
            match = ET.SubElement(and_tag, "match")
            ET.SubElement(match, "baseValue", {"baseType":"boolean"}).text = bool
            ET.SubElement(match, "variable", {"identifier":"PASS"})
            set_outcome_value = ET.SubElement(outcome_if, "setOutcomeValue", {"identifier":"FEEDBACKMODAL"})
            multiple = ET.SubElement(set_outcome_value, "multiple")
            ET.SubElement(multiple, "variable", {"identifier":"FEEDBACKMODAL"})
            ET.SubElement(multiple, "baseValue", {"baseType":"identifier"}).text = feedback[type].id
