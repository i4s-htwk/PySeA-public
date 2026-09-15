from .Task import Task
from backend.utils import ExcelVariables, VariantDependentImage

class Section:
    def __init__(self, title, section_nr, id):
        self.title = title
        self.section_nr = section_nr
        self.id = id

        self.images_used = []
        self.list_tasks = []
        self.local_variables_used = []
        self.global_variables_used = []
        self.variant_dependent_images = []
        self.excel_variables = None

    def add_task(self, title = None):
        new_id = "task" + str(self.section_nr) + str(len(self.list_tasks) + 1)
        if not title: title = "Aufgabe" + str(len(self.list_tasks) + 1)
        task = Task(title, len(self.list_tasks) + 1, self.section_nr, new_id)
        self.list_tasks.append(task)
        return task


    def delete_task(self, task):
        id_map = {}

        index = 0
        for i, task_obj in enumerate(self.list_tasks):
            if task_obj.id == task.id:
                self.list_tasks.pop(i)
                index = i
                id_map[task_obj.id] = None  # Task gelöscht

        for i in range(index, len(self.list_tasks)):
            old_id = self.list_tasks[i].id
            self.list_tasks[i].task_nr -= 1
            new_id = old_id[:-1] + str(int(old_id[-1]) - 1)
            self.list_tasks[i].id = new_id
            id_map[old_id] = new_id

        return id_map

    def add_excel_variables(self):
        ev = ExcelVariables(self.section_nr)
        self.excel_variables = ev
        return ev

    def to_dict(self):
        return {
            "title": self.title,
            "section_nr": self.section_nr,
            "id": self.id,
            "list_tasks": [task.to_dict() for task in self.list_tasks],
            "variant_dependent_images": [vdi.to_dict() for vdi in self.variant_dependent_images],
            "excel_variables" : self.excel_variables.to_dict() if self.excel_variables else None
        }

    @staticmethod
    def from_dict(data):
        section = Section(data["title"], data["section_nr"], data["id"])
        for task_data in data.get("list_tasks", []):
            section.list_tasks.append(Task.from_dict(task_data))

        for vdi_data in data.get("variant_dependent_images", []):
            vdi = VariantDependentImage.from_dict(vdi_data)
            section.variant_dependent_images.append(vdi)
        ev_data = data.get("excel_variables")
        section.excel_variables = ExcelVariables.from_dict(ev_data) if ev_data else None
        return section