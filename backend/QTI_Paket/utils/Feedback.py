import xml.etree.ElementTree as ET
from .helpers import append_text, insert_image, insert_v_image
from ...utils.Variants.VariableDependentAssignment.VariableDependentAssignment import VariableDependentAssignment


def create_feedback(root_tag, feedback, feedback_titles, images, item=None, variant_assignment=None):
    if feedback:
        for i, type in enumerate(["feedback_correct", "feedback_incorrect"]):
            fb_entrys = feedback[type]
            if not isinstance(fb_entrys, list):
                fb_entrys = [fb_entrys]

            for fb in fb_entrys:
                if item:   feedback_tag = ET.SubElement(root_tag, "modalFeedback", {"identifier": fb.id, "outcomeIdentifier": "FEEDBACKMODAL", "showHide": "show"})
                else:                   feedback_tag = ET.SubElement(root_tag, "testFeedback", {"identifier": fb.id, "outcomeIdentifier": "FEEDBACKMODAL", "showHide": "show", "access": "atEnd"})
                if feedback_titles[i]: feedback_tag.set("title", feedback_titles[i])

                lines = fb.value.split("\n")
                if lines and lines[-1].strip() == "":
                    lines.pop()

                for line in lines:
                    p = ET.SubElement(feedback_tag, "p")
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
                                if "V_BILD" in placeholder:
                                    insert_v_image(placeholder, p, p, item)
                                elif "BILD" in placeholder:
                                    insert_image(placeholder, p, item, images)
                                elif variant_assignment and isinstance(variant_assignment, VariableDependentAssignment) and variant_assignment.get_variable_name(placeholder) == placeholder:
                                    ET.SubElement(p, "printedVariable", {"identifier": placeholder})
                                elif placeholder in ["SCORE", "MAXSCORE"]:
                                    ET.SubElement(p, "printedVariable", {"identifier": placeholder})
                                else:
                                    append_text(p, "{" + placeholder + "}")

                                if rest:
                                    append_text(p, rest)
                            else:
                                append_text(p, part)