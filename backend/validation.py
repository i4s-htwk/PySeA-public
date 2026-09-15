import numbers
import os

class PySeAError(Exception):
    pass

class PySeATypeError(PySeAError, TypeError):
    pass

class PySeAValueError(PySeAError, ValueError):
    pass

class PySeAConsistencyError(PySeAError):
    pass

class TestValidator:
    def __init__(self, test_store):
        self.test_store = test_store
        self.test_structure = test_store.test_structure
        self.configurations = test_store.store_configurations
        self.tables = test_store.store_tables
        self.images = test_store.store_images
        self.item_body = test_store.store_item_body
        self.responses = test_store.store_responses
        self.selections = test_store.store_selections
        self.matchings = test_store.store_matchings
        self.graphical_assignments = test_store.store_graphical_assignment
        self.variants = test_store.store_variants
        self.feedback = test_store.store_feedback

    def validate_before_export(self):
        self.validate_test_has_sections()
        self.validate_sections_have_tasks()
        self.validate_unique_ids()
        self.validate_variant_assignment()
        self.validate_variant_dependent_tables_require_test_path_control()
        self.validate_variant_dependent_tables()
        self.validate_variant_dependent_images()
        self.validate_item_bodies()
        self.validate_tasks_have_answer_interaction()
        self.validate_response_values_are_numeric()
        self.validate_selections()
        self.validate_tables()
        self.validate_images_exist()

    def validate_test_has_sections(self):
        if not self.test_structure.list:
            raise PySeAConsistencyError("Der Test enthält keine Sections. Füge zuerst mindestens eine Section hinzu.")

    def validate_sections_have_tasks(self):
        for section in self.test_structure.list:
            if not section.list_tasks:
                raise PySeAConsistencyError(f"Section {section.id!r} enthält keine Aufgaben.")

    def validate_unique_ids(self):
        seen = set()
        for section in self.test_structure.list:
            self._check_unique_id(section.id, seen, "Section")

            for task in section.list_tasks:
                self._check_unique_id(task.id, seen, "Task")

    def _check_unique_id(self, object_id, seen, object_type):
        if not isinstance(object_id, str):
            raise PySeATypeError(f"{object_type}-ID muss ein String sein, bekommen: {type(object_id).__name__}.")

        if not object_id.strip():
            raise PySeAValueError(f"{object_type}-ID darf nicht leer sein.")

        if object_id in seen:
            raise PySeAConsistencyError(f"Doppelte ID gefunden: {object_id!r}")
        seen.add(object_id)

    def uses_variant_dependent_tables(self):
        return any(
            task.variant_dependent_tables
            for section in self.test_structure.list
            for task in section.list_tasks)

    def uses_variant_dependent_images(self):
        return any(
            task.variant_dependent_images
            for section in self.test_structure.list
            for task in section.list_tasks)

    def validate_variant_assignment(self):
        uses_variant_content = (
            self.uses_variant_dependent_tables()
            or self.uses_variant_dependent_images()
        )

        if uses_variant_content and not self.variants.use_variants:
            raise PySeAConsistencyError(
                "Es werden variantenabhängige Inhalte verwendet, aber Varianten sind nicht aktiviert. "
                "Rufe test.variants(...) auf.")

        if self.variants.use_variants and self.variants.assignment is None:
            raise PySeAConsistencyError(
                "Varianten sind aktiviert, aber es wurde keine Varianten-Zuweisung gesetzt.")

        if self.variants.use_variants:
            count = self.variants.assignment.get_count_variants()
            if not isinstance(count, int):
                raise PySeATypeError("Die Anzahl der Varianten muss ein Integer sein.")

            if count <= 0:
                raise PySeAConsistencyError("Die Anzahl der Varianten muss größer als 0 sein.")

    def validate_variant_dependent_tables_require_test_path_control(self):
        if not self.uses_variant_dependent_tables():
            return

        navigation_mode = self.configurations.advanced_settings.navigation_mode

        if navigation_mode != "test_path_control":
            raise PySeAConsistencyError("Variantenabhängige Tabellen benötigen navigation_mode='test_path_control'. " f"Aktuell gesetzt: {navigation_mode!r}.")

    def validate_variant_dependent_tables(self):
        available_table_references_by_task = {}

        for item_id, entry in self.tables.items.items():
            references = set()

            for table in entry.get("tables", []):
                if table is None:
                    continue
                references.add(table.id)
                if hasattr(table, "list_areas"):
                    for area in table.list_areas:
                        references.add(area.id)

            available_table_references_by_task[item_id] = references

        for section in self.test_structure.list:
            for task in section.list_tasks:
                identifier = task.parent_id or task.id

                for vdt in task.variant_dependent_tables:
                    if not vdt.tables:
                        raise PySeAConsistencyError(
                            f"Variantenabhängige Tabelle {vdt.id!r} in Task {task.id!r} "
                            "enthält keine Tabellenzuweisungen.")

                    for key, entry in vdt.tables.items():
                        self._validate_variant_bounds(
                            entry.get("lower"),
                            entry.get("upper"),
                            f"{task.id}.{vdt.id}.{key}")

                        table_id = entry.get("table_id")
                        available = available_table_references_by_task.get(identifier, set())

                        if table_id not in available:
                            raise PySeAConsistencyError(
                                f"Task {task.id!r} verwendet in {vdt.id!r} die Tabelle/Area "
                                f"{table_id!r}, aber diese ID existiert nicht im StoreTables-Eintrag ")

    def validate_variant_dependent_images(self):
        available_image_ids = {image.id for image in self.images.images}

        for section in self.test_structure.list:
            for task in section.list_tasks:
                for vdi in task.variant_dependent_images:
                    if not vdi.images:
                        raise PySeAConsistencyError(
                            f"Variantenabhängiges Bild {vdi.id!r} in Task {task.id!r} "
                            "enthält keine Bildzuweisungen.")

                    for key, entry in vdi.images.items():
                        self._validate_variant_bounds(
                            entry.get("lower"),
                            entry.get("upper"),
                            f"{task.id}.{vdi.id}.{key}")

                        image_id = entry.get("image_id")
                        if image_id not in available_image_ids:
                            raise PySeAConsistencyError(
                                f"Task {task.id!r} verwendet in {vdi.id!r} das Bild {image_id!r}, "
                                "aber dieses Bild wurde nicht geladen.")

    def _validate_variant_bounds(self, lower, upper, context):
        if float(lower) > float(upper):
            raise PySeAValueError(
                f"Ungültige Varianten-Grenzen in {context}: lower={lower}, upper={upper}.")

    def validate_item_bodies(self):
        for section in self.test_structure.list:

            for task in section.list_tasks:
                if task.id not in self.item_body.items:
                    raise PySeAConsistencyError(
                        f"Für Task {task.id!r} fehlt ein item_body-Eintrag.")

    def _is_automatic_excel_table_or_area(self, task_id, referenced_id):
        tables_entry = self.tables.items.get(task_id)
        if tables_entry is None:
            return False
        for table in tables_entry.get("tables", []):
            if table is None:
                continue
            if table.__class__.__name__ != "ExcelTable":
                continue
            if not table.automatic_responses:
                continue

            if referenced_id == table.id:
                return True

            for area in table.list_areas:
                if referenced_id == area.id:
                    return True
        return False

    def _task_uses_automatic_excel_table_area(self, task_id):
        item_body = self.item_body.get_item(task_id)
        if not item_body:
            return False
        tables_entry = self.tables.items.get(task_id)
        if tables_entry is None:
            return False

        for table in tables_entry.get("tables", []):
            if table is None:
                continue
            if table.__class__.__name__ != "ExcelTable":
                continue
            if not table.automatic_responses:
                continue
            for area in table.list_areas:
                area_placeholder = "{" + area.id + "}"
                if area_placeholder in item_body:
                    return True

        task = self.test_structure.get_object(task_id)
        if task is None:
            return False
        for vdt in task.variant_dependent_tables:
            vdt_placeholder = "{" + vdt.id + "}"
            if vdt_placeholder not in item_body:
                continue
            for entry in vdt.tables.values():
                referenced_id = entry.get("table_id")
                if self._is_automatic_excel_table_or_area(task_id, referenced_id):
                    return True
        return False

    def validate_tasks_have_answer_interaction(self):
        for section in self.test_structure.list:
            for task in section.list_tasks:
                identifier = task.parent_id or task.id

                response_item = self.responses.get_item(identifier)
                selection = self.selections.get_selection(identifier)
                matching = self.matchings.get_matching(identifier)
                graphical_assignment = self.graphical_assignments.get_item(identifier)

                has_response = (
                        response_item is not None
                        and len(response_item.responses) > 0)

                has_excel_response = (
                        response_item is not None
                        and response_item.excel_responses is not None
                        and len(response_item.excel_responses.responses) > 0)

                has_selection = selection is not None
                has_matching = matching is not None
                has_graphical_assignment = graphical_assignment is not None
                has_automatic_excel_table_response = (self._task_uses_automatic_excel_table_area(identifier))

                if (not has_response and not has_excel_response and not has_selection and not has_matching and not has_graphical_assignment  and not has_automatic_excel_table_response):
                    raise PySeAConsistencyError(
                        f"Aufgabe {task.id!r} hat keine Antwort-Interaktion. "
                        "Jede Aufgabe braucht mindestens eine response, excel_response oder selection ")

    def validate_selections(self):
        for task_id, selection in self.selections.items.items():
            if selection.type not in ["singleChoice", "multipleChoice"]:
                raise PySeAValueError(f"Selection in Task {task_id!r} hat ungültigen Typ {selection.type!r}.")

            if not selection.correct:
                raise PySeAConsistencyError(f"Selection in Task {task_id!r} hat keine korrekte Antwort.")

            if selection.type == "singleChoice" and len(selection.correct) != 1:
                raise PySeAConsistencyError(f"SingleChoice in Task {task_id!r} muss genau eine korrekte Antwort haben.")

            all_answers = selection.correct + selection.incorrect

            if len(all_answers) != len(set(all_answers)):
                raise PySeAConsistencyError(f"Selection in Task {task_id!r} enthält doppelte Antwortoptionen.")

            if selection.adjust_visibility:
                if not isinstance(selection.visible_wrong_count, int):
                    raise PySeATypeError(f"visible_wrong_count in Task {task_id!r} muss ein Integer sein.")

                if selection.visible_wrong_count < 0:
                    raise PySeAValueError(f"visible_wrong_count in Task {task_id!r} darf nicht negativ sein.")

                if selection.visible_wrong_count > len(selection.incorrect):
                    raise PySeAConsistencyError(f"visible_wrong_count in Task {task_id!r} ist größer als die Anzahl falscher Antworten.")
                self.validate_selection_adjust_visibility_answer_types(task_id, selection)

    def validate_selection_adjust_visibility_answer_types(self, task_id, selection):
        if not selection.adjust_visibility:
            return

        if not selection.incorrect:
            raise PySeAConsistencyError(
                f"Selection in Task {task_id!r} verwendet adjust_visibility, "
                "hat aber keine falschen Antworten.")

        answer_types = set()
        for answer in selection.incorrect:
            answer_type = self._classify_selection_answer(answer)
            answer_types.add(answer_type)

        if len(answer_types) > 1:
            raise PySeAConsistencyError(
                f"Selection in Task {task_id!r} verwendet adjust_visibility, "
                "aber die falschen Antworten sind gemischt. "
                f"Gefunden: {sorted(answer_types)}. "
                "Erlaubt ist nur eine Art gleichzeitig: nur Text, nur Bild oder nur VDI.")

    def _classify_selection_answer(self, answer):
        value = str(answer).strip()
        if value.startswith("{") and value.endswith("}"):
            value = value[1:-1]
        if value.startswith("V_BILD_"):
            return "vdi"
        if value.startswith("BILD_"):
            return "image"
        return "text"

    def validate_response_values_are_numeric(self):
        for task_id, response_item in self.responses.items.items():
            if response_item is None:
                continue

            for index, response in enumerate(response_item.responses):
                self._validate_numeric_response(
                    response=response,
                    task_id=task_id,
                    response_type="Response",
                    index=index)

    def _validate_numeric_response(self, response, task_id, response_type, index):
        value = response.value
        if isinstance(value, bool):
            raise PySeATypeError(
                f"{response_type} {index} in Task {task_id!r} muss einen "
                f"numerischen Antwortwert enthalten. "
                f"Bekommen: {value!r} vom Typ bool.")

        if isinstance(value, str) and not value.strip():
            raise PySeATypeError(
                f"{response_type} {index} in Task {task_id!r} muss einen "
                "numerischen Antwortwert enthalten. Bekommen wurde ein leerer String.")

        try:
            float(value)
        except (TypeError, ValueError):
            raise PySeATypeError(
                f"{response_type} {index} in Task {task_id!r} muss einen "
                f"numerischen Antwortwert enthalten. "
                f"Bekommen: {value!r} vom Typ {type(value).__name__}.")

    def validate_tables(self):
        for item_id, entry in self.tables.items.items():
            for table in entry.get("tables", []):
                if table is None:
                    raise PySeAConsistencyError(
                        f"Tabellenliste von {item_id!r} enthält None. "
                        "Wahrscheinlich wurde ein ungültiger table_type übergeben."
                    )

                if table.__class__.__name__ == "CustomTable":
                    self._validate_custom_table(item_id, table)

                if table.__class__.__name__ == "ExcelTable":
                    self._validate_excel_table(item_id, table)

    def _validate_custom_table(self, item_id, table):
        if not table.cells:
            raise PySeAConsistencyError(f"CustomTable {table.id!r} in {item_id!r} hat keine Zellen.")
        width = len(table.cells[0])

        if width == 0:
            raise PySeAConsistencyError(f"CustomTable {table.id!r} in {item_id!r} hat 0 Spalten.")

        for row_index, row in enumerate(table.cells):
            if len(row) != width:
                raise PySeAConsistencyError(
                    f"CustomTable {table.id!r} in {item_id!r} hat ungleich lange Zeilen. "
                    f"Zeile {row_index} hat {len(row)} Spalten, erwartet {width}.")

    def _validate_excel_table(self, item_id, table):
        if not table.excel_file:
            raise PySeAConsistencyError(
                f"ExcelTable {table.id!r} in {item_id!r} hat keine Excel-Datei.")

        if not os.path.isfile(table.excel_file):
            raise PySeAConsistencyError(
                f"Excel-Datei für ExcelTable {table.id!r} existiert nicht: {table.excel_file!r}")

        if not table.page:
            raise PySeAConsistencyError(
                f"ExcelTable {table.id!r} in {item_id!r} hat kein Arbeitsblatt/page gesetzt.")

        if not table.list_areas:
            raise PySeAConsistencyError(
                f"ExcelTable {table.id!r} in {item_id!r} enthält keine Bereiche.")

    def validate_images_exist(self):
        if not self.images.images:
            return

        if not self.images.path_images:
            raise PySeAConsistencyError(
                "Es wurden Bilder geladen, aber path_images ist leer.")

        if not os.path.isdir(self.images.path_images):
            raise PySeAConsistencyError(
                f"Bildordner existiert nicht: {self.images.path_images!r}")

        for image in self.images.images:
            image_path = os.path.join(self.images.path_images, image.href)
            if not os.path.isfile(image_path):
                raise PySeAConsistencyError(f"Bild {image.id!r} verweist auf fehlende Datei: {image_path!r}")