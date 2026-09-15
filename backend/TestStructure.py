from backend import Section, Task

class TestStructure:
    def __init__(self):
        self.list = []

        self.images_used = []
        self.path_images = ""

    def append_section(self, section):
        self.list.append(section)

    def add_section(self, title=None):
        new_id = "section" + str(len(self.list) + 1)
        if not title: title = "Sektion " + str(len(self.list) + 1)
        section = Section(title, len(self.list) + 1, new_id)
        self.append_section(section)
        return section

    def delete_section(self, section):
        id_map = {}

        index = 0
        for i, section_obj in enumerate(self.list):
            if section_obj.id == section.id:
                for task in section_obj.list_tasks: id_map[task.id] = None
                self.list.pop(i)
                index = i
                id_map[section_obj.id] = None

        for i in range(index, len(self.list)):
            old_id = self.list[i].id
            self.list[i].section_nr -= 1
            new_id = old_id[:-1] + str(int(old_id[-1]) - 1)
            self.list[i].id = new_id
            id_map[old_id] = new_id

            for task in self.list[i].list_tasks:
                old_task_id = task.id
                task.section_nr -= 1
                prelast = int(old_task_id[-2]) - 1
                new_task_id = old_task_id[:-2] + str(prelast) + old_task_id[-1]
                task.id = new_task_id
                id_map[old_task_id] = new_task_id
        return id_map

    def add_variants(self, variants):
        task = Task(variants.title, 0, 0, variants.task_id)
        section = Section("Variantenzuweisung", 0, variants.section_id)
        section.list_tasks.append(task)
        self.list.insert(0, section)

    def get_object(self, current_obj):
        for s in self.list:
            if s.id == current_obj:
                return s
            for t in s.list_tasks:
                if t.id == current_obj:
                    return t
        return None

    def get_insert_position(self, obj_id):
        for i, section in enumerate(self.list):
            if section.id == obj_id:
                return i
            if "task" in obj_id:
                for j, task in enumerate(section.list_tasks):
                    if task.id == obj_id:
                        return i, j
        return None

    def to_dict(self):
        return {
            "list": [section.to_dict() for section in self.list],
        }

    @staticmethod
    def from_dict(data):
        ts = TestStructure()
        for section_data in data.get("list", []):
            ts.append_section(Section.from_dict(section_data) )
        return ts