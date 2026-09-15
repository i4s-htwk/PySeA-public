import xml.etree.ElementTree as ET
import mimetypes

from backend.utils import Response, ExcelResponse
from .helpers import append_text, insert_image, insert_v_image
from ...utils.ExcelVariables import ExcelVariable
from ...utils.Variants.VariableDependentAssignment.VariableDependentAssignment import VariableDependentAssignment


def is_excel_variable_identifier(item, identifier):
    if not item.excel_variables or not item.excel_variables.variables:
        return False

    for variable in item.excel_variables.variables:
        if getattr(variable, "variable_id", None) == identifier:
            return True

        if isinstance(variable, (list, tuple)) and len(variable) > 0 and variable[0] == identifier:
            return True

    return False

def create_item_body(item_body_tag, item, item_body, images, tables, selection, matching, variant_assignment, graphical_assignment = None):
    used_content = []
    lines = item_body.split("\n")
    if lines and lines[-1].strip() == "":
        lines.pop()

    for line in lines:
        p = ET.SubElement(item_body_tag, "p")
        math_parts = line.split("$$")
        for idx, block in enumerate(math_parts):

            # Latex formulas
            if idx % 2 == 1:
                append_text(p, "$$" + block + "$$")
                continue

            # Normal text + keywords
            parts = block.split("{")
            for part in parts:
                if "}" in part:
                    placeholder, rest = part.split("}", 1)
                    if "TABELLE" in placeholder and tables:
                        insert_table(placeholder, p, item, tables, used_content)
                    elif "RESPONSE" in placeholder:
                        insert_response(placeholder, p, used_content)
                    elif "V_BILD" in placeholder:
                        insert_v_image(placeholder, p, item_body_tag, item)
                    elif "BILD" in placeholder:
                        insert_image(placeholder, p, item, images)
                    elif "SELECTION" in placeholder:
                        insert_selection(p, item, images, selection)
                    elif "MATCHING" in placeholder:
                        insert_matching(p, item, images, matching)
                    elif "GRAPHICAL_ASSIGNMENT" in placeholder:
                        insert_graphical_assignment(p, item, images, graphical_assignment)
                    elif is_excel_variable_identifier(item, placeholder):
                        ET.SubElement(p, "printedVariable", {"identifier": placeholder})
                    elif variant_assignment and isinstance(variant_assignment, VariableDependentAssignment) and any(
                            v in placeholder and any(op in placeholder for op in ("*", "/", "+", "-"))
                            for variable in variant_assignment.list_variables
                            for v in variable.variables):
                        matched_v = next(
                            v for variable in variant_assignment.list_variables for v in variable.variables
                            if v in placeholder)
                        maxima_code = placeholder.replace(matched_v, "$(1)")
                        identifier = "LOCAL_VARIABLE_" + str(item.section_nr) + "_" + str(len(item.local_variables_used))
                        item.local_variables_used.append((identifier, maxima_code, matched_v))
                        if "task" in item.id: item.global_variables_used.append(matched_v)
                        ET.SubElement(p, "printedVariable", {"identifier": identifier})
                    else:
                        append_text(p, "{" + placeholder + "}")

                    if rest:
                        append_text(p, rest)
                else:
                    append_text(p, part)
    include_image_templates(item_body_tag, item, images, selection)

    return used_content

def insert_table(placeholder, p, item, tables, used_content):
    if "V_TABELLE" in placeholder:
        vdt = next((t for t in item.variant_dependent_tables if t.id == placeholder), None)
        table = next((t for (key, t) in vdt.tables.items() if t["task_id"] == item.id), None)
        placeholder = table["table_id"]
    used_content.append(placeholder)
    table = None
    for t in tables:
        if t.id == placeholder:
            table = t
            break
    table_tag = ET.SubElement(p, "table", {"style": "border-collapse: collapse; min-width: 150px;", "border": "1", "id": placeholder})
    tbody = ET.SubElement(table_tag, "tbody")
    for i, row in enumerate(table.cells):
        tr = ET.SubElement(tbody, "tr")
        for j, cell in enumerate(row):
            if j > 0 or i == 0:
                td = ET.SubElement(tr, "td", {"rowspan": str(cell.rowspan), "colspan": str(cell.colspan),
                                              "style": "text-align: center; vertical-align: middle; min-width: 50px; padding:5px"})
            else:
                td = ET.SubElement(tr, "td", {"rowspan": str(cell.rowspan), "colspan": str(cell.colspan), "style":"min-width: 50px; padding:5px"})
            if isinstance(cell.value, Response) or isinstance(cell.value, ExcelResponse):
                insert_response(cell.value.id, td, used_content)
            elif isinstance(cell.value, ExcelVariable):
                ET.SubElement(td, "printedVariable", {"identifier": cell.value.variable_id})
            else:
                td.text = str(cell.value)

def insert_response(placeholder, p, used_content):
    used_content.append(placeholder)
    ET.SubElement(p, "textEntryInteraction", {"responseIdentifier": placeholder})

def selection_uses_text_slots(item, images, selection):
    if not selection or not selection.adjust_visibility:
        return False

    image_ids = {image.id for image in images}
    vdi_ids = {vdi.id for vdi in item.variant_dependent_images}

    return all(
        answer not in image_ids and answer not in vdi_ids
        for answer in selection.incorrect
    )


def insert_selection(p, item, images, selection):
    correct_answers = selection.correct
    incorrect_answers = selection.incorrect
    uses_text_slots = selection_uses_text_slots(item, images, selection)

    if selection.adjust_visibility:
        incorrect_answers = ["{" + slot_id + "}" for slot_id in selection.get_slot_ids()]

    if selection.type == "singleChoice":
        maxChoices = "1"
    elif selection.type == "multipleChoice":
        maxChoices = "0"
    else:
        maxChoices = "1"
    choiceInteraction = ET.SubElement(p,"choiceInteraction",{"responseIdentifier": "SELECTION", "shuffle": "true", "maxChoices": maxChoices})

    for answer in correct_answers + incorrect_answers:
        is_slot = answer.startswith("{SELECTION_SLOT_") and answer.endswith("}")
        choice_identifier = answer.strip("{}")

        simple_choice = ET.SubElement(choiceInteraction, "simpleChoice", {"identifier": choice_identifier})
        p_choice = ET.SubElement(simple_choice, "p")

        if is_slot and uses_text_slots:
            ET.SubElement(p_choice, "printedVariable", {"identifier": choice_identifier})
        elif is_slot:
            ET.SubElement(p_choice,"include",{"href": "templates/" + item.id + "/" + choice_identifier + ".xml", "type": "text/xml"})
        elif "V_BILD" in answer:
            image_id = answer.strip("{}")
            ET.SubElement(p_choice,"include",{"href": "templates/" + item.id + "/" + image_id + ".xml", "type": "text/xml"})
        elif any(i.id == answer for i in images):
            insert_image(answer, p_choice, item, images)
        else:
            p_choice.text = answer

def insert_matching(p, item, images, matching):
    match_interaction = ET.SubElement(
        p,
        "matchInteraction",
        {
            "responseIdentifier": matching.id,
            "shuffle": str(matching.shuffle).lower(),
            "maxAssociations": str(matching.max_associations)})

    source_match_set = ET.SubElement(match_interaction, "simpleMatchSet")
    for choice in matching.source_choices:
        insert_match_choice(source_match_set, choice, item, images)

    target_match_set = ET.SubElement(match_interaction, "simpleMatchSet")
    for choice in matching.target_choices:
        insert_match_choice(target_match_set, choice, item, images)

    return match_interaction

def insert_graphical_assignment(p, item, images, graphical_assignment):
    interaction = ET.SubElement(
        p,
        "graphicGapMatchInteraction",
        {
            "responseIdentifier": "RESPONSE_1",
            "maxAssociations": "0",
            "data-shuffle": "true",
            "data-show-labels":"false"})

    insert_graphical_background(interaction=interaction, item=item, images=images, graphical_assignment=graphical_assignment)
    gap_index = 1

    for snippet in graphical_assignment.correct_snippets:
        insert_gap_image(interaction=interaction, identifier=f"ID_{gap_index}", image_path=snippet.output_path, item=item, images=images, graphical_assignment=graphical_assignment)
        gap_index += 1

    for snippet in graphical_assignment.wrong_snippets:
        insert_gap_image(interaction=interaction, identifier=f"ID_{gap_index}", image_path=snippet.output_path, item=item, images=images, graphical_assignment=graphical_assignment)
        gap_index += 1

    hotspot_margin = 12
    for index, (x, y, width, height) in enumerate(graphical_assignment.cut_areas, start=1):
        x1 = x
        y1 = y
        x2 = x + width - hotspot_margin
        y2 = y + height - hotspot_margin

        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"Der Hotspot {index} ist durch hotspot_margin={hotspot_margin} zu klein geworden.")
        ET.SubElement(
            interaction,
            "associableHotspot",
            {
                "matchMax": "1",
                "identifier": f"IDT_{index}",
                "shape": "rect",
                "coords": f"{x1},{y1},{x2},{y2}"})
    return interaction

def get_image_mime_type(file_name: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_name)
    return mime_type or "image/png"

def insert_gap_image(interaction, identifier: str, image_path: str, item, images, graphical_assignment, display_scale: float = 1.0):
    image = graphical_assignment.get_image_by_path(image_path)
    if image is None:
        raise ValueError(f"Für '{image_path}' wurde kein lokales Image-Objekt gefunden.")
    global_image = next((stored_image for stored_image in images if stored_image.id == image.id or stored_image.href == image.href), None)

    if global_image is None:
        images.append(image)
        global_image = image

    if not any(used_image.id == global_image.id for used_image in item.images_used):
        item.images_used.append(global_image)
    gap_img = ET.SubElement(
        interaction,
        "gapImg",
        {
            "identifier": identifier,
            "matchMax": "1"})

    displayed_width = round(float(global_image.width) * display_scale)
    displayed_height = round(float(global_image.height) * display_scale)
    ET.SubElement(
        gap_img,
        "object",
        {
            "data": f"media/{global_image.href}",
            "type": get_image_mime_type(global_image.href),
            "width": str(displayed_width),
            "height": str(displayed_height)})

    return gap_img

def insert_graphical_background(interaction, item, images, graphical_assignment):
    image = graphical_assignment.get_background_image()
    global_image = next((stored_image for stored_image in images if stored_image.id == image.id or stored_image.href == image.href), None)

    if global_image is None:
        images.append(image)
        global_image = image

    if not any(used_image.id == global_image.id for used_image in item.images_used):
        item.images_used.append(global_image)
    ET.SubElement(
        interaction,
        "object",
        {
            "data": f"media/{global_image.href}",
            "type": get_image_mime_type(global_image.href),
            "width": global_image.width})

def insert_match_choice(parent, choice, item, images):
    simple_choice = ET.SubElement(
        parent,
        "simpleAssociableChoice",
        {
            "identifier": choice.id,
            "fixed": str(choice.fixed).lower(),
            "matchMax": str(choice.match_max)})

    if is_valid_image_identifier(choice.text, images):
        insert_image(choice.text, simple_choice, item, images)
    else:
        p_element = ET.SubElement(simple_choice, "p")
        p_element.text = choice.text

    return simple_choice


def is_valid_image_identifier(text: str, images) -> bool:
    if text is None:
        return False

    if images is None:
        return False
    for i in images:
        if text == i.id:
            return True
    return False


def get_image_href(image) -> str:
    if isinstance(image, str):
        return image

    if hasattr(image, "href"):
        return image.href

    if hasattr(image, "file_name"):
        return image.file_name

    if hasattr(image, "path"):
        return image.path

    raise ValueError(f"Bildobjekt hat keinen gültigen Pfad oder href: {image}")

def include_image_templates(item_body_tag, item, images, selection):
    if selection and selection.adjust_visibility:
        if not selection_uses_text_slots(item, images, selection):
            for slot_id in selection.get_slot_ids():
                image_template(item_body_tag, item.id + "/" + slot_id)

        for vdi in item.variant_dependent_images:
            if vdi.id not in selection.incorrect:
                image_template(item_body_tag, item.id + "/" + vdi.id)
    else:
        for vdi in item.variant_dependent_images:
            image_template(item_body_tag, item.id + "/" + vdi.id)

def image_template(item_body_tag, path_part):
    div = ET.SubElement(item_body_tag, "div", {"style": "display:none;", "data-onyx-editor": "template-nonref"})
    ET.SubElement(div, "include", {"href": "templates/" + path_part + ".xml", "type": "text/xml"})


