from itertools import product

from backend.utils import Feedback, VariableVariants
from backend.utils.Variants.ManualAssignment import ManualAssignment
from backend.utils.Variants.StudentIdToVariantAssignment import StudentIdToVariantAssignment
from backend.utils.Variants.VariableDependentAssignment.VariableDependentAssignment import VariableDependentAssignment

class StoreVariants:
    """Manages the variant assignment of a test.

    An instance of this class is returned by ``TestFacade.variants()``.
    Its ``assignment`` attribute holds one of ``ManualAssignment``,
    ``StudentIdToVariantAssignment`` or ``VariableDependentAssignment``,
    depending on the assignment type chosen when the variants were enabled.
    ``item_body`` defines the text of the variant-input task shown to the
    learner.
    """
    def __init__(self):
        self.use_variants = False
        self.title = "Variantenzuweisung"
        self.item_body = ""

        self.assignment = None
        self.feedback = {"feedback_correct":Feedback("FEEDBACK_CORRECT", "feddback_correct"), "feedback_incorrect":Feedback("FEEDBACK_INCORRECT", "feddback_incorrect")}
        self.task_id = "task_variant_assignment"
        self.section_id = "section_variant_assignment"

    def set_assignment(self, assignment_type):
        if assignment_type == "variable_dependent_assignment":
            self.assignment = VariableDependentAssignment()
        elif assignment_type == "manual_assignment":
            self.assignment = ManualAssignment()
        elif assignment_type == "student_id_to_variant_assignment":
            self.assignment = StudentIdToVariantAssignment()
        else:
            raise ValueError("assignment_type muss 'variable_dependent_assignment', 'manual_assignment' oder 'student_id_to_variant_assignment' sein.")

    def set_feedback(self, value, type):
        if type=="feedback_incorrect":
            self.feedback["feedback_incorrect"].value = value
        elif type=="feedback_correct":
            self.feedback["feedback_correct"].value = value

    def to_dict(self):
        assignment_key = None
        if isinstance(self.assignment, VariableDependentAssignment):
            assignment_key = "variable_dependent_assignment"
        elif isinstance(self.assignment, ManualAssignment):
            assignment_key = "manual_assignment"
        elif isinstance(self.assignment, StudentIdToVariantAssignment):
            assignment_key = "student_id_to_variant_assignment"

        data = {
            "use_variants" : self.use_variants,
            "test_title": self.title,
            "item_body": self.item_body,
            "feedback": {k: v.to_dict() for k, v in self.feedback.items()}
        }
        if assignment_key:
            data[assignment_key] = self.assignment.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        store = cls()

        if not data:
            return store

        store.use_variants = data.get("use_variants")
        store.title = data.get("test_title", "Variantenzuweisung")
        store.item_body = data.get("item_body")
        if data.get("variable_dependent_assignment"):
            store.assignment = VariableDependentAssignment.from_dict(data.get("variable_dependent_assignment"))
        elif data.get("manual_assignment"):
            store.assignment = ManualAssignment.from_dict(data.get("manual_assignment"))
        elif data.get("student_id_to_variant_assignment"):
            store.assignment = StudentIdToVariantAssignment.from_dict(data.get("student_id_to_variant_assignment"))
        elif data.get("use_variants") == True and data.get("list_variables"):
            store.assignment = VariableDependentAssignment.from_dict({"list_variables":data.get("list_variables")})
        feedback_data = data.get("feedback", {"feedback_correct":Feedback("FEEDBACK_CORRECT", "feddback_correct").to_dict(), "feedback_incorrect":Feedback("FEEDBACK_INCORRECT", "feddback_incorrect").to_dict()})
        store.feedback = {k: Feedback.from_dict(v) for k, v in feedback_data.items()}
        return store