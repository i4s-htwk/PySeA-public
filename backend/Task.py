from backend.QTI_Paket import AssessmentItem, AssessmentItemVariantAssignment
from backend.utils import VariantDependentImage, VariantDependentTable, ExcelVariables


class Task:
    def __init__(self, title, task_nr, section_nr, id):
        self.title = title
        self.task_nr = task_nr
        self.section_nr = section_nr
        self.id = id
        self.parent_id = None

        self.images_used = []
        self.global_variables_used = []
        self.local_variables_used = []
        self.excel_variables = None
        self.variant_dependent_images = []
        self.variant_dependent_tables = []
        self.point_distribution = {"task": None, "gap": None}

    def add_variant_dependent_image(self):
        vdi = VariantDependentImage("V_BILD_" + str(len(self.variant_dependent_images) + 1))
        self.variant_dependent_images.append(vdi)
        return vdi

    def add_variant_dependent_table(self):
        vdt = VariantDependentTable("V_TABELLE_" + str(len(self.variant_dependent_tables) + 1))
        self.variant_dependent_tables.append(vdt)
        return vdt

    def add_excel_variables(self):
        ev = ExcelVariables(self.section_nr)
        self.excel_variables = ev
        return ev

    def create_assessmentitem(self, images, answer_acc, store_item_body, store_responses, store_tables, store_feedbacks, store_selections, store_matchings, store_graphical_assignment, variants, configuration, temp_dir):
        identifier = self.parent_id or self.id
        item_body = store_item_body.get_item(identifier)
        selections = store_selections.get_selection(identifier)
        matching = store_matchings.get_matching(identifier)
        graphical_assignment = store_graphical_assignment.get_item(identifier)
        responses = store_responses.get_item(identifier)
        merged_responses = responses.get_merged_responses(selections, matching, graphical_assignment)
        merged_tables = store_tables.create_tables(self, merged_responses)
        feedbacks = store_feedbacks.get_item(identifier)

        item = AssessmentItem(self, images, answer_acc, item_body,merged_responses, responses.excel_responses, merged_tables, feedbacks, selections, matching, graphical_assignment, variants, configuration, temp_dir)
        return item.max_score

    def create_assessmentitem_variant_assignment(self, images, store_item_body, store_responses, store_feedbacks, variants, temp_dir):
        identifier = self.parent_id or self.id
        item_body = store_item_body.get_item(identifier)
        responses = store_responses.get_responses(identifier)
        feedbacks = store_feedbacks.get_item(identifier)

        AssessmentItemVariantAssignment(self, images, item_body, responses, feedbacks, variants, temp_dir)

    def to_dict(self):
        return {
            "title": self.title,
            "task_nr": self.task_nr,
            "section_nr": self.section_nr,
            "id": self.id,
            "point_distribution": self.point_distribution,
            "variant_dependent_images": [vdi.to_dict() for vdi in self.variant_dependent_images],
            "variant_dependent_tables": [vdt.to_dict() for vdt in self.variant_dependent_tables],
            "excel_variables": self.excel_variables.to_dict() if self.excel_variables else None
        }

    @staticmethod
    def from_dict(data):
        item = Task(data["title"], data["task_nr"], data["section_nr"], data["id"])
        item.point_distribution = data["point_distribution"]
        for vdi_data in data.get("variant_dependent_images", []):
            vdi = VariantDependentImage.from_dict(vdi_data)
            item.variant_dependent_images.append(vdi)
        for vdt_data in data.get("variant_dependent_tables", []):
            vdt = VariantDependentTable.from_dict(vdt_data)
            item.variant_dependent_tables.append(vdt)
        ev_data = data.get("excel_variables")
        item.excel_variables = ExcelVariables.from_dict(ev_data) if ev_data else None
        return item