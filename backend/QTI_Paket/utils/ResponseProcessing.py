import xml.etree.ElementTree as ET

from backend.utils import Response, ExcelResponse


def response_processing_response(response_processing_tag, response_id, equal_attribs):
    response_condition = ET.SubElement(response_processing_tag, "responseCondition")
    response_if = ET.SubElement(response_condition, "responseIf")
    equal = ET.SubElement(response_if, "equal", equal_attribs)
    ET.SubElement(equal, "variable", {"identifier": response_id})
    ET.SubElement(equal, "correct", {"identifier": response_id})
    set_outcome_value = ET.SubElement(response_if, "setOutcomeValue", {"identifier": "SCORE_" + response_id})
    ET.SubElement(set_outcome_value, "variable", {"identifier": "MAXSCORE_" + response_id})

def response_processing_score_bounds(response_processing_tag):
    response_condition = ET.SubElement(response_processing_tag, "responseCondition")
    response_if = ET.SubElement(response_condition, "responseIf")
    lt = ET.SubElement(response_if, "lt")
    ET.SubElement(lt, "variable", {"identifier": "SCORE"})
    ET.SubElement(lt, "variable", {"identifier": "MINSCORE"})
    set_outcome = ET.SubElement(response_if, "setOutcomeValue", {"identifier": "SCORE"})
    ET.SubElement(set_outcome, "variable", {"identifier": "MINSCORE"})

    response_condition = ET.SubElement(response_processing_tag, "responseCondition")
    response_if = ET.SubElement(response_condition, "responseIf")
    gt = ET.SubElement(response_if, "gt")
    ET.SubElement(gt, "variable", {"identifier": "SCORE"})
    ET.SubElement(gt, "variable", {"identifier": "MAXSCORE"})
    set_outcome = ET.SubElement(response_if, "setOutcomeValue", {"identifier": "SCORE"})
    ET.SubElement(set_outcome, "variable", {"identifier": "MAXSCORE"})

def response_processing_feedback(response_processing_tag, feedback, point_deduction=None, max_score= 0):
    response_condition = ET.SubElement(response_processing_tag, "responseCondition")
    response_if = ET.SubElement(response_condition, "responseIf")
    lt = ET.SubElement(response_if, "lt")
    ET.SubElement(lt, "variable", {"identifier": "SCORE"})
    ET.SubElement(lt, "variable", {"identifier": "MAXSCORE"})
    set_outcome_if = ET.SubElement(response_if, "setOutcomeValue", {"identifier": "FEEDBACKBASIC"})
    ET.SubElement(set_outcome_if, "baseValue", {"baseType": "identifier"}).text = "incorrect"

    response_else = ET.SubElement(response_condition, "responseElse")
    set_outcome_else = ET.SubElement(response_else, "setOutcomeValue", {"identifier": "FEEDBACKBASIC"})
    ET.SubElement(set_outcome_else, "baseValue", {"baseType": "identifier"}).text = "correct"
    if feedback:
        # FEEDBACK correct
        feedback_tag(response_processing_tag, feedback["feedback_correct"], point_deduction=point_deduction, max_score=max_score)

        # FEEDBACK incorrect
        for i, fb in enumerate(feedback["feedback_incorrect"], start=0):
            feedback_tag(response_processing_tag, fb, point_deduction=point_deduction,i=i, max_score=max_score)

def feedback_tag(response_processing_tag, feedback, point_deduction=None, i=None, max_score=None):
    if point_deduction and point_deduction.is_used:
        variable, value, op_incorrect, op_correct = ("mindestpunktzahl", "0", "equal", "gt")
    else:
        variable, value, op_incorrect, op_correct = ("SCORE", str(max_score), "lt", "equal")

    response_condition = ET.SubElement(response_processing_tag, "responseCondition")
    response_if = ET.SubElement(response_condition, "responseIf")
    and_tag = ET.SubElement(response_if, "and")
    if feedback.type == "incorrect":
        lower_bound = None
        if not feedback.condition:
            lower_bound = str(i)
        elif isinstance(feedback.condition, int):
            lower_bound = str(feedback.condition -1)
        elif isinstance(feedback.condition, list):
            lower_bound = str(feedback.condition[0] -1)

        if lower_bound:
            gte = ET.SubElement(and_tag, "gte")
            ET.SubElement(gte, "variable", {"identifier": "numAttempts"})
            ET.SubElement(gte, "baseValue", {"baseType": "integer"}).text = lower_bound

            if isinstance(feedback.condition, list):
                lte = ET.SubElement(and_tag, "lte")
                ET.SubElement(lte, "variable", {"identifier": "numAttempts"})
                ET.SubElement(lte, "baseValue", {"baseType": "integer"}).text = str(feedback.condition[1] -1)

        elif isinstance(feedback.condition, Response) or isinstance(feedback.condition, ExcelResponse):
            equal = ET.SubElement(and_tag, "equal", {"toleranceMode":"exact"})
            ET.SubElement(equal, "variable", {"identifier": "SCORE_"+feedback.condition.id})
            ET.SubElement(equal, "baseValue", {"baseType": "float"}).text = "0"

        tag = ET.SubElement(and_tag, op_incorrect)
        ET.SubElement(tag, "variable", {"identifier": variable})
        ET.SubElement(tag, "baseValue", {"baseType": "float"}).text = value
        if op_incorrect == "equal":
            tag.set("toleranceMode", "exact")

    else:
        tag = ET.SubElement(and_tag, op_correct)
        ET.SubElement(tag, "variable", {"identifier": variable})
        ET.SubElement(tag, "baseValue", {"baseType": "float"}).text = value
        if op_correct == "equal":
            tag.set("toleranceMode", "exact")

    set_outcome = ET.SubElement(response_if, "setOutcomeValue", {"identifier": "FEEDBACKMODAL"})
    multiple = ET.SubElement(set_outcome, "multiple")
    ET.SubElement(multiple, "variable", {"identifier": "FEEDBACKMODAL"})
    ET.SubElement(multiple, "baseValue", {"baseType": "identifier"}).text = feedback.id
