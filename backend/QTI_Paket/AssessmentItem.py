import xml.etree.ElementTree as ET
from itertools import combinations

from backend.utils import Response, ExcelResponse, Selection, VariantDependentImage, Matching, GraphicalAssignment
from .utils import *

class AssessmentItem:

    def __init__(self, task, images, answer_acc, item_body, merged_responses,excel_responses, merged_tables, feedback, selection, matching, graphical_assignment, variants, configuration, temp_dir):
        self.max_score = 0
        variant_assignment = variants.assignment if variants else None
        self.root = ET.Element("assessmentItem", attrib={
            "xmlns": "http://www.imsglobal.org/xsd/imsqti_v2p1",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1p1.xsd http://www.w3.org/1998/Math/MathML http://www.w3.org/Math/XMLSchema/mathml2/mathml2.xsd",
            "identifier": task.id,
            "title": task.title,
            "adaptive": "false",
            "timeDependent": "false"})

        item_body_tag = ET.SubElement(self.root, "itemBody")
        used_content = create_item_body(item_body_tag, task, item_body, images, merged_tables, selection, matching, variant_assignment, graphical_assignment)

        create_feedback(self.root, feedback,["Richtig!", "Falsch!"], images, item=task )
        self.clear_content(used_content, merged_responses, merged_tables)

        self.response_declaration(merged_responses)
        point_distribution_gap = self.outcome_declaration(task, merged_responses, used_content, configuration.point_distribution)
        self.template_declaration(excel_responses, used_content, configuration.point_deduction.is_used, variants, task, selection, images)
        if variants.use_variants or (selection and selection.adjust_visibility): self.template_processing(excel_responses, used_content, variant_assignment, task, images, selection)
        if selection: self.style_sheet(task)
        self.response_processing(answer_acc, merged_responses, excel_responses.answer_acc_from_excel if excel_responses else None , feedback, configuration, selection, matching, graphical_assignment, point_distribution_gap)

        self.file_path = write_xml_document(self.root, str(task.id) + ".xml", temp_dir)

    def response_declaration (self, responses):
        for response in responses:
            if isinstance(response, Response) or isinstance(response, ExcelResponse): basetype = "float"
            elif isinstance(response, Matching) or isinstance(response, GraphicalAssignment): basetype = "directedPair"
            else: basetype = "identifier"
            if (isinstance(response, Selection) and len(response.correct) >1) or isinstance(response, Matching) or isinstance(response, GraphicalAssignment): cardinality = "multiple"
            else: cardinality = "single"

            response_declaration = ET.SubElement(self.root, "responseDeclaration",{"identifier": response.id, "cardinality": cardinality, "baseType": basetype})
            if isinstance(response, Response):
                correct_response = ET.SubElement(response_declaration, "correctResponse")
                ET.SubElement(correct_response, "value").text = response.value
            elif isinstance(response, Selection):
                correct_response = ET.SubElement(response_declaration, "correctResponse")
                for c in response.correct:
                    ET.SubElement(correct_response, "value").text = c
            elif isinstance(response, Matching):
                correct_response = ET.SubElement(response_declaration, "correctResponse")
                for pair in response.correct_pairs:
                    ET.SubElement(correct_response, "value").text = f"{pair.source_id} {pair.target_id}"
            elif isinstance(response, GraphicalAssignment):
                correct_response = ET.SubElement(response_declaration, "correctResponse")
                for index, _ in enumerate(response.correct_snippets, start=1):
                    ET.SubElement(correct_response, "value").text = f"ID_{index} IDT_{index}"

    def get_outcome_data_response(self, id, max_score):
        outcome_data = [
                {"identifier": "SCORE_"+id, "default": "0"},
                {"identifier": "MINSCORE_"+id, "default": "0"},
                {"identifier": "MAXSCORE_"+id, "default": str(max_score)}]
        for outcome in outcome_data:
            outcome_declaration = ET.SubElement(self.root, "outcomeDeclaration", {"identifier": outcome["identifier"], "cardinality": "single", "baseType": "float"})
            default_value = ET.SubElement(outcome_declaration, "defaultValue")
            ET.SubElement(default_value, "value").text = outcome["default"]

    def get_point_distribution(self, answer, task, point_distribution, len_responses):
        if task.point_distribution["task"] is not None:
            point_distribution_gap = str(float(task.point_distribution["task"])/len_responses)
            return point_distribution_gap, task.point_distribution["task"], task.point_distribution["task"]
        if not isinstance(answer, Selection) and not isinstance(answer, Matching) and not isinstance(answer, GraphicalAssignment) and answer.points is not None:
            point_distribution_gap = answer.points
        elif task.point_distribution["gap"] is not None:
            point_distribution_gap = task.point_distribution["gap"]
        else:
            point_distribution_gap = point_distribution["gap"]
        return point_distribution_gap, point_distribution["selection"], point_distribution["matching"]

    def outcome_declaration(self, task, responses, used_content, point_distribution):
        used_responses = sum(1 for r in used_content if "RESPONSE" in r)
        sum_points=0
        point_distribution_gap = "0"
        for antwort in responses:
            point_distribution_gap, point_distribution_selection, point_distribution_matching = self.get_point_distribution(antwort, task, point_distribution, used_responses)
            max_score = 0
            if isinstance(antwort, Response) or isinstance(antwort, ExcelResponse):
                max_score = float(point_distribution_gap)
            elif isinstance(antwort, Selection):
                max_score = float(point_distribution_selection)
            elif isinstance(antwort, Matching) or isinstance(antwort, GraphicalAssignment):
                max_score = float(point_distribution_matching)
            sum_points += max_score
            self.get_outcome_data_response(antwort.id, max_score)
        self.max_score = sum_points
        outcome_data = [
            {"identifier": "SCORE", "cardinality":"single", "baseType": "float", "default": "0"},
            {"identifier": "MINSCORE","cardinality":"single", "baseType": "float", "default": "0", "view": "testConstructor"},
            {"identifier": "MAXSCORE", "cardinality":"single","baseType": "float", "default": str(sum_points)},
            {"identifier": "FEEDBACKBASIC","cardinality":"single", "baseType": "identifier", "default": "empty"},
            {"identifier": "FEEDBACKMODAL", "cardinality":"multiple","baseType": "identifier", "default": "empty", "view": "testConstructor"}]
        for outcome in outcome_data:
            outcome_declaration = ET.SubElement(self.root, "outcomeDeclaration",{"identifier": outcome["identifier"], "cardinality": outcome["cardinality"], "baseType": outcome["baseType"]})
            if "view" in outcome:
                outcome_declaration.set("view", outcome["view"])
            default_value = ET.SubElement(outcome_declaration, "defaultValue")
            ET.SubElement(default_value, "value").text = outcome["default"]
        return point_distribution_gap

    def template_declaration(self, excel_responses, used_content, point_deduction_is_used, variants, task,
                             selection, images):
        if variants.use_variants: ET.SubElement(self.root, "templateDeclaration",
                                           {"identifier": "Variante", "cardinality": "single", "baseType": "integer"})
        if excel_responses:
            for response in excel_responses.responses:
                if response.id not in used_content:
                    continue
                ET.SubElement(self.root, "templateDeclaration",
                              {"identifier": "VARIABLE_" + response.id, "cardinality": "single", "baseType": "float"})
                if excel_responses.answer_acc_from_excel:
                    ET.SubElement(self.root, "templateDeclaration",
                                  {"identifier": "VARIABLE_ACC_" + response.id, "cardinality": "single",
                                   "baseType": "float"})
        if task.excel_variables:
            for variable in task.excel_variables.variables:
                nks = task.excel_variables.get_nks(variants.assignment.get_count_variants(), variable.cell)
                ET.SubElement(self.root, "templateDeclaration",
                              {"identifier": variable.variable_id, "cardinality": "single", "baseType": "float",
                               "format": f"%.{nks}f"})

        if point_deduction_is_used:
            ET.SubElement(self.root, "templateDeclaration",
                          {"identifier": "mindestpunktzahl", "cardinality": "single", "baseType": "float"})
        for vdi in task.variant_dependent_images:
            if selection and selection.adjust_visibility and vdi.id in selection.incorrect:
                continue
            ET.SubElement(self.root, "templateDeclaration",
                          {"identifier": vdi.id, "cardinality": "single", "baseType": "identifier"})
        for v in task.local_variables_used:
            ET.SubElement(self.root, "templateDeclaration",
                          {"identifier": v[0], "cardinality": "single", "baseType": "float"})
            ET.SubElement(self.root, "templateDeclaration",
                          {"identifier": v[2], "cardinality": "single", "baseType": "float"})
        if selection and selection.adjust_visibility:
            ET.SubElement(self.root, "templateDeclaration",
                          {"identifier": "KOMBI", "cardinality": "single", "baseType": "integer"})
            image_ids = {image.id for image in images}
            vdi_ids = {vdi.id for vdi in task.variant_dependent_images}
            uses_text_slots = all(answer not in image_ids and answer not in vdi_ids for answer in selection.incorrect)
            slot_base_type = "string" if uses_text_slots else "identifier"
            for slot_id in selection.get_slot_ids():
                ET.SubElement(self.root, "templateDeclaration",
                              {"identifier": slot_id, "cardinality": "single", "baseType": slot_base_type})

    def set_template_value(self, template_processing, identifier, maxima_code, variables):
        set_template_value = ET.SubElement(template_processing, "setTemplateValue", {"identifier": identifier})
        custom_operator = ET.SubElement(set_template_value, "customOperator",
                                        {"definition": "MAXIMA", "value": maxima_code})
        for variable in variables:
            ET.SubElement(custom_operator, "variable", {"identifier": variable})

    def template_processing(self, excel_responses, used_content, variant_assignment, task, images, selection):
        count_variants = variant_assignment.get_count_variants() if variant_assignment else 1
        template_processing = ET.SubElement(self.root, "templateProcessing")

        def add_random_values(identifier, values, base_type="identifier"):
            values = sorted({v for v in values if v is not None})
            set_template_value = ET.SubElement(template_processing, "setTemplateValue", {"identifier": identifier})
            random = ET.SubElement(set_template_value, "random")
            multiple = ET.SubElement(random, "multiple")
            for value in values:
                ET.SubElement(multiple, "baseValue", {"baseType": base_type}).text = value

        def add_image_to_task(image_id):
            image = next((img for img in images if img.id == image_id), None)
            if image and image not in task.images_used:
                task.images_used.append(image)

        def add_kombi_condition(parent, kombi_index):
            equal_kombi = ET.SubElement(parent, "equal", {"toleranceMode": "exact"})
            ET.SubElement(equal_kombi, "variable", {"identifier": "KOMBI"})
            ET.SubElement(equal_kombi, "baseValue", {"baseType": "integer"}).text = str(kombi_index)

        def add_variant_condition(parent, value):
            lower = value.get("lower", "")
            upper = value.get("upper", "")
            if lower != "" and upper != "":
                gte = ET.SubElement(parent, "gte")
                ET.SubElement(gte, "variable", {"identifier": "Variante"})
                ET.SubElement(gte, "baseValue", {"baseType": "integer"}).text = str(lower)

                lte = ET.SubElement(parent, "lte")
                ET.SubElement(lte, "variable", {"identifier": "Variante"})
                ET.SubElement(lte, "baseValue", {"baseType": "integer"}).text = str(upper)
            else:
                equal_variante = ET.SubElement(parent, "equal", {"toleranceMode": "exact"})
                ET.SubElement(equal_variante, "variable", {"identifier": "Variante"})
                ET.SubElement(equal_variante, "baseValue", {"baseType": "integer"}).text = str(lower)

        def set_base_value(parent, identifier, value, base_type="identifier"):
            set_template_value = ET.SubElement(parent, "setTemplateValue", {"identifier": identifier})
            ET.SubElement(set_template_value, "baseValue", {"baseType": base_type}).text = value

        if excel_responses:
            for response in excel_responses.responses:
                if response.id not in used_content:
                    continue
                maxima_code = excel_responses.maxima_code(count_variants, response.cell)
                self.set_template_value(template_processing, "VARIABLE_" + response.id, maxima_code, ["Variante"])
                if excel_responses.answer_acc_from_excel:
                    maxima_code = excel_responses.maxima_code(count_variants, response.cell, 1)
                    self.set_template_value(template_processing, "VARIABLE_ACC_" + response.id, maxima_code,
                                            ["Variante"])
                set_correct_response = ET.SubElement(template_processing, "setCorrectResponse",
                                                     {"identifier": response.id})
                ET.SubElement(set_correct_response, "variable", {"identifier": "VARIABLE_" + response.id})

        if task.excel_variables:
            for v in task.excel_variables.variables:
                set_template_value = ET.SubElement(template_processing, "setTemplateValue",
                                                   {"identifier": v.variable_id})
                custom_operator = ET.SubElement(set_template_value, "customOperator", {"definition": "MAXIMA",
                                                                                       "value": task.excel_variables.maxima_code(
                                                                                           count_variants,
                                                                                           v.cell)})
                ET.SubElement(custom_operator, "variable", {"identifier": "Variante"})

        for vdi in list(task.variant_dependent_images):
            if selection and selection.adjust_visibility and vdi.id in selection.incorrect:
                continue

            add_random_values(vdi.id, [value["image_id"] for value in vdi.images.values()])
            template_condition = ET.SubElement(template_processing, "templateCondition")
            for i, value in enumerate(vdi.images.values()):
                template_if = ET.SubElement(template_condition, "templateIf" if i == 0 else "templateElseIf")
                and_tag = ET.SubElement(template_if, "and")
                add_variant_condition(and_tag, value)
                set_base_value(template_if, vdi.id, value["image_id"])
                add_image_to_task(value["image_id"])

        if selection and selection.adjust_visibility:
            kombis = selection.get_visible_wrong_combinations()
            slot_ids = selection.get_slot_ids()

            if not kombis:
                raise Exception("selection.visible_wrong_count must be smaller than or equal to the number of incorrect answers")

            set_kombi = ET.SubElement(template_processing, "setTemplateValue", {"identifier": "KOMBI"})
            ET.SubElement(set_kombi, "randomInteger", {"min": "1", "max": str(len(kombis))})

            image_ids = {image.id for image in images}
            vdi_by_id = {vdi.id: vdi for vdi in task.variant_dependent_images}
            wrong_uses_vdi = any(answer in vdi_by_id for answer in selection.incorrect)

            if wrong_uses_vdi:
                for slot_position, slot_id in enumerate(slot_ids):
                    possible_image_ids = []
                    slot_vdi = VariantDependentImage(slot_id)

                    for kombi_index, kombi in enumerate(kombis, start=1):
                        source_vdi = vdi_by_id[kombi[slot_position]]
                        for value in source_vdi.images.values():
                            possible_image_ids.append(value["image_id"])
                            slot_vdi.images[f"k{kombi_index}_{value['image_id']}"] = {
                                "image_id": value["image_id"],
                                "lower": value["lower"],
                                "upper": value["upper"],
                                "kombi": kombi_index}

                    add_random_values(slot_id, possible_image_ids)
                    task.variant_dependent_images.append(slot_vdi)

                    template_condition = ET.SubElement(template_processing, "templateCondition")
                    sorted_values = sorted(
                        slot_vdi.images.values(),
                        key=lambda value: (int(value.get("kombi", 0)), str(value.get("lower", "")),
                                           str(value.get("upper", "")), value.get("image_id", "")))

                    for i, value in enumerate(sorted_values):
                        template_if = ET.SubElement(template_condition, "templateIf" if i == 0 else "templateElseIf")
                        and_tag = ET.SubElement(template_if, "and")
                        add_kombi_condition(and_tag, value["kombi"])
                        add_variant_condition(and_tag, value)
                        set_base_value(template_if, slot_id, value["image_id"])
                        add_image_to_task(value["image_id"])

            else:
                uses_text_slots = all(answer not in image_ids for answer in selection.incorrect)
                slot_base_type = "string" if uses_text_slots else "identifier"
                slot_template_data = {slot_id: {} for slot_id in slot_ids}

                for slot_position, slot_id in enumerate(slot_ids):
                    possible_values = []
                    assignments = []

                    for kombi_index, kombi in enumerate(kombis, start=1):
                        answer = kombi[slot_position]
                        slot_value = answer
                        possible_values.append(slot_value)
                        assignments.append((kombi_index, slot_value))

                        if not uses_text_slots:
                            slot_template_data[slot_id][slot_value] = {"image_id": answer, "lower": "", "upper": ""}
                            add_image_to_task(answer)

                    add_random_values(slot_id, possible_values, slot_base_type)

                    template_condition = ET.SubElement(template_processing, "templateCondition")
                    for i, (kombi_index, slot_value) in enumerate(assignments):
                        template_if = ET.SubElement(template_condition, "templateIf" if i == 0 else "templateElseIf")
                        add_kombi_condition(template_if, kombi_index)
                        set_base_value(template_if, slot_id, slot_value, slot_base_type)

                if not uses_text_slots:
                    for slot_id in slot_ids:
                        slot_vdi = VariantDependentImage(slot_id)
                        slot_vdi.images.update(slot_template_data[slot_id])
                        task.variant_dependent_images.append(slot_vdi)

        for v in task.local_variables_used:
            self.set_template_value(template_processing, v[0], v[1], [v[2]])

    def style_sheet(self, task):
        style_sheet = ET.SubElement(self.root, "stylesheet", {"type":"text/css", "href":"files/"+task.id+"/redtick-display-none.css"})

    def clear_content(self, used_content, responses, tables):
        responses[:] = [
            r for r in responses
            if r.id in used_content or isinstance(r, Selection) or isinstance(r, Matching) or isinstance(r,GraphicalAssignment)]
        for i, t in enumerate(tables):
            if t.id not in used_content:
                del tables[i]

    def set_score_excel_response(self, parent, response_id):
        set_outcome_value = ET.SubElement(
            parent,
            "setOutcomeValue",
            {"identifier": f"SCORE_{response_id}", "class": "ONYX_SET_SCORE"}
        )
        custom_operator = ET.SubElement(set_outcome_value,
                "customOperator",
                {
                    "definition": "MAXIMA",
                    "value": "float(if (($(1) - $(2) >= -$(3)) and ($(1) - $(2) <= $(3))) then $(4) else $(5));"
                })
        ET.SubElement(custom_operator, "variable", {"identifier": response_id})
        ET.SubElement(custom_operator, "correct", {"identifier": response_id})
        ET.SubElement(custom_operator, "variable", {"identifier": f"VARIABLE_ACC_{response_id}"})
        ET.SubElement(custom_operator, "variable", {"identifier": f"MAXSCORE_{response_id}"})
        ET.SubElement(custom_operator, "variable", {"identifier": f"MINSCORE_{response_id}"})

    def response_processing(self, answer_acc, responses, answer_acc_from_excel, feedback, configuration, selection, matching, graphical_assignment, point_distribution_gap):

        point_deduction_is_used = configuration.point_deduction.is_used
        point_deduction_per_attempt = configuration.point_deduction.point_deduction_per_attempt
        min_score_percentage = configuration.point_deduction.min_score_percentage/100

        if answer_acc.selection == "relative":
            equal_attribs={"toleranceMode":"relative", "tolerance": str(answer_acc.relative) + " " + str(answer_acc.relative), "includeLowerBound": "true", "includeUpperBound": "true"}
        elif answer_acc.selection == "absolute":
            equal_attribs = {"toleranceMode": "absolute", "tolerance": str(answer_acc.absolute) + " " + str(answer_acc.absolute), "includeLowerBound": "true", "includeUpperBound": "true"}
        else: equal_attribs = {"toleranceMode":"exact"}
        response_processing = ET.SubElement(self.root, "responseProcessing")

        for response in responses:
            if isinstance(response, ExcelResponse):
                set_correct_response = ET.SubElement(response_processing, "setCorrectResponse", {"identifier": response.id})
                ET.SubElement(set_correct_response, "variable", {"identifier": "VARIABLE_" + response.id})

        for response in responses:
            if isinstance(response, ExcelResponse) and answer_acc_from_excel:
                self.set_score_excel_response(response_processing, response.id)
            elif isinstance(response, Matching) or isinstance(response, GraphicalAssignment):
                continue
            else:
                response_processing_response(response_processing, response.id, equal_attribs)

        set_outcome_value = ET.SubElement(response_processing, "setOutcomeValue", {"identifier":"SCORE"})
        sum = ET.SubElement(set_outcome_value, "sum")
        for response in responses:
            ET.SubElement(sum, "variable", {"identifier":"SCORE_"+response.id})

        if matching or graphical_assignment:
            id = matching.id if matching else graphical_assignment.id
            response_condition = ET.SubElement(response_processing, "responseCondition")
            response_if = ET.SubElement(response_condition, "responseIf")
            is_null = ET.SubElement(response_if, "isNull")
            ET.SubElement(is_null, "variable", {"identifier": id})
            response_else_if = ET.SubElement(response_condition, "responseElseIf")
            match = ET.SubElement(response_else_if, "match")
            ET.SubElement(match, "variable", {"identifier": id})
            ET.SubElement(match, "correct", {"identifier": id})
            set_outcome_value = ET.SubElement(
                response_else_if,
                "setOutcomeValue",
                {"identifier": "SCORE"})
            sum_element = ET.SubElement(set_outcome_value, "sum")
            ET.SubElement(sum_element, "variable", {"identifier": "SCORE"})
            ET.SubElement(sum_element, "variable", {"identifier": "MAXSCORE"})
        if not selection and not matching and not graphical_assignment:
            set_outcome_value = ET.SubElement(response_processing, "setOutcomeValue", {"identifier": "SCORE", "class": "ONYX_SET_SCORE"})
            if "." in point_distribution_gap and len(point_distribution_gap.split(".")[1]) > 3:
                value_expr = "float(round((" + "+".join([f"$({i})" for i in range(1, len(responses) + 1)]) + ")*100)/100);"
            else:
                value_expr = "float(" + "+".join([f"$({i})" for i in range(1, len(responses) + 1)]) + ");"
            custom_operator = ET.SubElement(set_outcome_value, "customOperator", {"definition": "MAXIMA", "value": value_expr})
            for response in responses:
                ET.SubElement(custom_operator, "variable", {"identifier": "SCORE_" + response.id})

        if point_deduction_is_used:

            response_condition_1 = ET.SubElement(response_processing,"responseCondition")
            response_if = ET.SubElement(response_condition_1, "responseIf")
            equal = ET.SubElement(response_if, "equal", {"toleranceMode": "exact"})
            ET.SubElement(equal, "variable", {"identifier": "SCORE"})
            ET.SubElement(equal, "variable", {"identifier": "MAXSCORE"})

            set_template_value_if = ET.SubElement(response_if, "setTemplateValue", {"identifier": "mindestpunktzahl"})
            custom_operator_if = ET.SubElement(set_template_value_if, "customOperator", {"definition": "MAXIMA", "value": "float("+str(min_score_percentage)+"*$(1));"})
            ET.SubElement(custom_operator_if, "variable", {"identifier": "MAXSCORE"})

            response_else = ET.SubElement(response_condition_1, "responseElse")
            set_template_value_else = ET.SubElement(response_else, "setTemplateValue", {"identifier": "mindestpunktzahl"})
            ET.SubElement(set_template_value_else, "baseValue", {"baseType": "float"}).text = "0"

            response_condition_2 = ET.SubElement(response_processing, "responseCondition", {"class": "ONYX_SET_SCORE"})
            response_if_2 = ET.SubElement(response_condition_2, "responseIf")
            gt = ET.SubElement(response_if_2, "gt")
            ET.SubElement(gt, "variable", {"identifier": "SCORE"})
            ET.SubElement(gt, "baseValue", {"baseType": "float"}).text = "0"

            set_outcome_value_2 = ET.SubElement(response_if_2, "setOutcomeValue", {"identifier": "SCORE", "class": "ONYX_SET_SCORE"})
            custom_operator_2 = ET.SubElement(set_outcome_value_2, "customOperator", {"definition": "MAXIMA", "value": "float(max($(2)-($(3)*"+str(point_deduction_per_attempt)+"),$(1)));"})
            ET.SubElement(custom_operator_2, "variable", {"identifier": "mindestpunktzahl"})
            ET.SubElement(custom_operator_2, "variable", {"identifier": "SCORE"})
            ET.SubElement(custom_operator_2, "variable", {"identifier": "numAttempts"})

        response_processing_score_bounds(response_processing)
        response_processing_feedback(response_processing, feedback, configuration.point_deduction, self.max_score)