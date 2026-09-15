import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
from unittest.mock import patch

import backend.QTI_Paket.utils.ItemBody as item_body_module
from backend.utils import Response, ExcelResponse


def make_item(
    item_id="task11",
    section_nr=1,
    excel_variables=None,
    variant_dependent_images=None,
    variant_dependent_tables=None,
):
    return SimpleNamespace(
        id=item_id,
        section_nr=section_nr,
        excel_variables=excel_variables,
        variant_dependent_images=variant_dependent_images or [],
        variant_dependent_tables=variant_dependent_tables or [],
        local_variables_used=[],
        global_variables_used=[],
        images_used=[],
    )


def make_image(
    image_id="BILD_1",
    href="bild.png",
    width="100",
    height="80",
):
    return SimpleNamespace(
        id=image_id,
        href=href,
        width=width,
        height=height,
    )


def make_cell(value, rowspan=1, colspan=1):
    return SimpleNamespace(
        value=value,
        rowspan=rowspan,
        colspan=colspan,
    )


class TestIsExcelVariableIdentifier(unittest.TestCase):

    def test_returns_false_without_excel_variables(self):
        item = make_item(
            item_id="section1",
            excel_variables=None,
        )

        result = item_body_module.is_excel_variable_identifier(
            item,
            "EXCEL_VARIABLE_1",
        )

        self.assertFalse(result)

    def test_returns_false_for_empty_variable_list(self):
        item = make_item(
            item_id="section1",
            excel_variables=SimpleNamespace(
                variables=[]
            ),
        )

        result = item_body_module.is_excel_variable_identifier(
            item,
            "EXCEL_VARIABLE_1",
        )

        self.assertFalse(result)

    def test_recognizes_excel_variable_object(self):
        item = make_item(
            item_id="section1",
            excel_variables=SimpleNamespace(
                variables=[
                    SimpleNamespace(
                        variable_id="EXCEL_VARIABLE_1"
                    )
                ]
            ),
        )

        result = item_body_module.is_excel_variable_identifier(
            item,
            "EXCEL_VARIABLE_1",
        )

        self.assertTrue(result)

    def test_recognizes_legacy_tuple_excel_variable(self):
        item = make_item(
            item_id="section1",
            excel_variables=SimpleNamespace(
                variables=[
                    ("EXCEL_VARIABLE_1", "C3")
                ]
            ),
        )

        result = item_body_module.is_excel_variable_identifier(
            item,
            "EXCEL_VARIABLE_1",
        )

        self.assertTrue(result)

    def test_returns_false_for_unknown_identifier(self):
        item = make_item(
            item_id="section1",
            excel_variables=SimpleNamespace(
                variables=[
                    SimpleNamespace(
                        variable_id="EXCEL_VARIABLE_1"
                    )
                ]
            ),
        )

        result = item_body_module.is_excel_variable_identifier(
            item,
            "UNKNOWN",
        )

        self.assertFalse(result)


class TestCreateItemBody(unittest.TestCase):

    def setUp(self):
        self.root = ET.Element("itemBody")
        self.item = make_item()

    def test_creates_one_paragraph_per_line(self):
        with (
            patch.object(item_body_module, "append_text"),
            patch.object(
                item_body_module,
                "include_image_templates",
            ),
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="Erste Zeile\nZweite Zeile\n",
                images=[],
                tables=[],
                selection=None,
                matching=None,
                variant_assignment=None,
            )

        paragraphs = self.root.findall("p")

        self.assertEqual(len(paragraphs), 2)

    def test_empty_trailing_line_does_not_create_paragraph(self):
        with (
            patch.object(item_body_module, "append_text"),
            patch.object(
                item_body_module,
                "include_image_templates",
            ),
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="Text\n",
                images=[],
                tables=[],
                selection=None,
                matching=None,
                variant_assignment=None,
            )

        paragraphs = self.root.findall("p")

        self.assertEqual(len(paragraphs), 1)

    def test_response_placeholder_creates_text_entry_interaction(self):
        with patch.object(
            item_body_module,
            "include_image_templates",
        ):
            used_content = item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="Antwort: {RESPONSE_1}",
                images=[],
                tables=[],
                selection=None,
                matching=None,
                variant_assignment=None,
            )

        interaction = self.root.find(
            ".//textEntryInteraction"
            "[@responseIdentifier='RESPONSE_1']"
        )

        self.assertIsNotNone(interaction)
        self.assertIn("RESPONSE_1", used_content)

    def test_table_placeholder_calls_insert_table(self):
        tables = [SimpleNamespace(id="TABELLE_1")]

        with (
            patch.object(
                item_body_module,
                "insert_table",
            ) as insert_table_mock,
            patch.object(
                item_body_module,
                "include_image_templates",
            ),
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="{TABELLE_1}",
                images=[],
                tables=tables,
                selection=None,
                matching=None,
                variant_assignment=None,
            )

        insert_table_mock.assert_called_once()

        arguments = insert_table_mock.call_args.args

        self.assertEqual(arguments[0], "TABELLE_1")
        self.assertIs(arguments[2], self.item)
        self.assertIs(arguments[3], tables)

    def test_image_placeholder_calls_insert_image(self):
        images = [
            make_image(
                image_id="BILD_1",
                href="bild.png",
            )
        ]

        with (
            patch.object(
                item_body_module,
                "insert_image",
            ) as insert_image_mock,
            patch.object(
                item_body_module,
                "include_image_templates",
            ),
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="{BILD_1}",
                images=images,
                tables=[],
                selection=None,
                matching=None,
                variant_assignment=None,
            )

        insert_image_mock.assert_called_once()

        arguments = insert_image_mock.call_args.args

        self.assertEqual(arguments[0], "BILD_1")
        self.assertIs(arguments[2], self.item)
        self.assertIs(arguments[3], images)

    def test_variant_image_placeholder_calls_insert_v_image(self):
        with (
            patch.object(
                item_body_module,
                "insert_v_image",
            ) as insert_v_image_mock,
            patch.object(
                item_body_module,
                "include_image_templates",
            ),
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="{V_BILD_1}",
                images=[],
                tables=[],
                selection=None,
                matching=None,
                variant_assignment=None,
            )

        insert_v_image_mock.assert_called_once()

        arguments = insert_v_image_mock.call_args.args

        self.assertEqual(arguments[0], "V_BILD_1")
        self.assertIs(arguments[2], self.root)
        self.assertIs(arguments[3], self.item)

    def test_selection_placeholder_calls_insert_selection(self):
        selection = SimpleNamespace()

        with (
            patch.object(
                item_body_module,
                "insert_selection",
            ) as insert_selection_mock,
            patch.object(
                item_body_module,
                "include_image_templates",
            ),
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="{SELECTION}",
                images=[],
                tables=[],
                selection=selection,
                matching=None,
                variant_assignment=None,
            )

        insert_selection_mock.assert_called_once()

        arguments = insert_selection_mock.call_args.args

        self.assertIs(arguments[1], self.item)
        self.assertIs(arguments[3], selection)

    def test_matching_placeholder_calls_insert_matching(self):
        matching = SimpleNamespace()

        with (
            patch.object(
                item_body_module,
                "insert_matching",
            ) as insert_matching_mock,
            patch.object(
                item_body_module,
                "include_image_templates",
            ),
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="{MATCHING}",
                images=[],
                tables=[],
                selection=None,
                matching=matching,
                variant_assignment=None,
            )

        insert_matching_mock.assert_called_once()

        arguments = insert_matching_mock.call_args.args

        self.assertIs(arguments[1], self.item)
        self.assertIs(arguments[3], matching)

    def test_graphical_assignment_placeholder_calls_insert_function(self):
        graphical_assignment = SimpleNamespace()

        with (
            patch.object(
                item_body_module,
                "insert_graphical_assignment",
            ) as insert_graphical_assignment_mock,
            patch.object(
                item_body_module,
                "include_image_templates",
            ),
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="{GRAPHICAL_ASSIGNMENT}",
                images=[],
                tables=[],
                selection=None,
                matching=None,
                variant_assignment=None,
                graphical_assignment=graphical_assignment,
            )

        insert_graphical_assignment_mock.assert_called_once()

        arguments = insert_graphical_assignment_mock.call_args.args

        self.assertIs(arguments[1], self.item)
        self.assertIs(arguments[3], graphical_assignment)

    def test_excel_variable_creates_printed_variable(self):
        item = make_item(
            item_id="section1",
            excel_variables=SimpleNamespace(
                variables=[
                    SimpleNamespace(
                        variable_id="EXCEL_VARIABLE_1"
                    )
                ]
            ),
        )

        with patch.object(
            item_body_module,
            "include_image_templates",
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=item,
                item_body="Wert: {EXCEL_VARIABLE_1}",
                images=[],
                tables=[],
                selection=None,
                matching=None,
                variant_assignment=None,
            )

        printed_variable = self.root.find(
            ".//printedVariable"
            "[@identifier='EXCEL_VARIABLE_1']"
        )

        self.assertIsNotNone(printed_variable)

    def test_unknown_placeholder_is_kept_as_text(self):
        with (
            patch.object(
                item_body_module,
                "append_text",
            ) as append_text_mock,
            patch.object(
                item_body_module,
                "include_image_templates",
            ),
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="{UNKNOWN}",
                images=[],
                tables=[],
                selection=None,
                matching=None,
                variant_assignment=None,
            )

        passed_texts = [
            call.args[1]
            for call in append_text_mock.call_args_list
        ]

        self.assertIn("{UNKNOWN}", passed_texts)

    def test_rest_after_placeholder_is_appended(self):
        with (
            patch.object(
                item_body_module,
                "append_text",
            ) as append_text_mock,
            patch.object(
                item_body_module,
                "include_image_templates",
            ),
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="{RESPONSE_1} kN",
                images=[],
                tables=[],
                selection=None,
                matching=None,
                variant_assignment=None,
            )

        passed_texts = [
            call.args[1]
            for call in append_text_mock.call_args_list
        ]

        self.assertIn(" kN", passed_texts)

    def test_latex_block_is_passed_to_append_text(self):
        with (
            patch.object(
                item_body_module,
                "append_text",
            ) as append_text_mock,
            patch.object(
                item_body_module,
                "include_image_templates",
            ),
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="Formel: $$a+b$$ Ende",
                images=[],
                tables=[],
                selection=None,
                matching=None,
                variant_assignment=None,
            )

        passed_texts = [
            call.args[1]
            for call in append_text_mock.call_args_list
        ]

        self.assertIn("$$a+b$$", passed_texts)

    def test_include_image_templates_is_called_after_body_creation(self):
        selection = SimpleNamespace()

        with (
            patch.object(item_body_module, "append_text"),
            patch.object(
                item_body_module,
                "include_image_templates",
            ) as include_templates_mock,
        ):
            item_body_module.create_item_body(
                item_body_tag=self.root,
                item=self.item,
                item_body="Text",
                images=[],
                tables=[],
                selection=selection,
                matching=None,
                variant_assignment=None,
            )

        include_templates_mock.assert_called_once_with(
            self.root,
            self.item,
            [],
            selection,
        )


class TestInsertResponse(unittest.TestCase):

    def test_insert_response_creates_text_entry_interaction(self):
        parent = ET.Element("p")
        used_content = []

        item_body_module.insert_response(
            placeholder="RESPONSE_1",
            p=parent,
            used_content=used_content,
        )

        interaction = parent.find("textEntryInteraction")

        self.assertIsNotNone(interaction)
        self.assertEqual(
            interaction.attrib["responseIdentifier"],
            "RESPONSE_1",
        )

    def test_insert_response_adds_identifier_to_used_content(self):
        parent = ET.Element("p")
        used_content = []

        item_body_module.insert_response(
            placeholder="RESPONSE_1",
            p=parent,
            used_content=used_content,
        )

        self.assertEqual(
            used_content,
            ["RESPONSE_1"],
        )


class TestInsertTable(unittest.TestCase):

    def test_insert_table_creates_table_body_rows_and_cells(self):
        parent = ET.Element("p")
        used_content = []

        table = SimpleNamespace(
            id="TABELLE_1",
            cells=[
                [
                    make_cell("Stab"),
                    make_cell("Länge"),
                ],
                [
                    make_cell("Stab 1"),
                    make_cell("12"),
                ],
            ],
        )

        item_body_module.insert_table(
            placeholder="TABELLE_1",
            p=parent,
            item=make_item(),
            tables=[table],
            used_content=used_content,
        )

        table_tag = parent.find("table")
        self.assertIsNotNone(table_tag)
        self.assertEqual(table_tag.attrib["id"], "TABELLE_1")

        tbody = table_tag.find("tbody")
        self.assertIsNotNone(tbody)

        rows = tbody.findall("tr")

        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows[0].findall("td")), 2)
        self.assertEqual(len(rows[1].findall("td")), 2)

    def test_insert_table_adds_table_to_used_content(self):
        parent = ET.Element("p")
        used_content = []

        table = SimpleNamespace(
            id="TABELLE_1",
            cells=[],
        )

        item_body_module.insert_table(
            placeholder="TABELLE_1",
            p=parent,
            item=make_item(),
            tables=[table],
            used_content=used_content,
        )

        self.assertEqual(
            used_content,
            ["TABELLE_1"],
        )

    def test_insert_table_copies_rowspan_and_colspan(self):
        parent = ET.Element("p")
        used_content = []

        table = SimpleNamespace(
            id="TABELLE_1",
            cells=[
                [
                    make_cell(
                        value="Überschrift",
                        rowspan=2,
                        colspan=3,
                    )
                ]
            ],
        )

        item_body_module.insert_table(
            placeholder="TABELLE_1",
            p=parent,
            item=make_item(),
            tables=[table],
            used_content=used_content,
        )

        cell = parent.find(".//td")

        self.assertEqual(cell.attrib["rowspan"], "2")
        self.assertEqual(cell.attrib["colspan"], "3")

    def test_insert_table_creates_response_interaction_for_response_cell(self):
        parent = ET.Element("p")
        used_content = []

        response = Response(
            id="RESPONSE_1",
            value="12",
        )

        table = SimpleNamespace(
            id="TABELLE_1",
            cells=[
                [
                    make_cell(response)
                ]
            ],
        )

        item_body_module.insert_table(
            placeholder="TABELLE_1",
            p=parent,
            item=make_item(),
            tables=[table],
            used_content=used_content,
        )

        interaction = parent.find(
            ".//textEntryInteraction"
            "[@responseIdentifier='RESPONSE_1']"
        )

        self.assertIsNotNone(interaction)
        self.assertIn("RESPONSE_1", used_content)

    def test_insert_table_creates_response_interaction_for_excel_response_cell(self):
        parent = ET.Element("p")
        used_content = []

        response = ExcelResponse(
            id="EXCEL_RESPONSE_1",
            cell="C3",
        )

        table = SimpleNamespace(
            id="TABELLE_1",
            cells=[
                [
                    make_cell(response)
                ]
            ],
        )

        item_body_module.insert_table(
            placeholder="TABELLE_1",
            p=parent,
            item=make_item(),
            tables=[table],
            used_content=used_content,
        )

        interaction = parent.find(
            ".//textEntryInteraction"
            "[@responseIdentifier='EXCEL_RESPONSE_1']"
        )

        self.assertIsNotNone(interaction)
        self.assertIn("EXCEL_RESPONSE_1", used_content)

    def test_insert_table_writes_normal_value_as_text(self):
        parent = ET.Element("p")
        used_content = []

        table = SimpleNamespace(
            id="TABELLE_1",
            cells=[
                [
                    make_cell(12)
                ]
            ],
        )

        item_body_module.insert_table(
            placeholder="TABELLE_1",
            p=parent,
            item=make_item(),
            tables=[table],
            used_content=used_content,
        )

        cell = parent.find(".//td")

        self.assertEqual(cell.text, "12")


class TestSelectionUsesTextSlots(unittest.TestCase):

    def test_returns_false_without_selection(self):
        result = item_body_module.selection_uses_text_slots(
            item=make_item(),
            images=[],
            selection=None,
        )

        self.assertFalse(result)

    def test_returns_false_when_visibility_is_not_adjusted(self):
        selection = SimpleNamespace(
            adjust_visibility=False,
            incorrect=["Antwort"],
        )

        result = item_body_module.selection_uses_text_slots(
            item=make_item(),
            images=[],
            selection=selection,
        )

        self.assertFalse(result)

    def test_returns_true_when_all_incorrect_answers_are_text(self):
        selection = SimpleNamespace(
            adjust_visibility=True,
            incorrect=["Antwort A", "Antwort B"],
        )

        result = item_body_module.selection_uses_text_slots(
            item=make_item(),
            images=[],
            selection=selection,
        )

        self.assertTrue(result)

    def test_returns_false_when_incorrect_answer_is_image(self):
        selection = SimpleNamespace(
            adjust_visibility=True,
            incorrect=["BILD_1", "Antwort B"],
        )

        images = [
            make_image(
                image_id="BILD_1",
            )
        ]

        result = item_body_module.selection_uses_text_slots(
            item=make_item(),
            images=images,
            selection=selection,
        )

        self.assertFalse(result)

    def test_returns_false_when_incorrect_answer_is_variant_image(self):
        selection = SimpleNamespace(
            adjust_visibility=True,
            incorrect=["V_BILD_1"],
        )

        item = make_item(
            variant_dependent_images=[
                SimpleNamespace(id="V_BILD_1")
            ],
        )

        result = item_body_module.selection_uses_text_slots(
            item=item,
            images=[],
            selection=selection,
        )

        self.assertFalse(result)


class TestInsertSelection(unittest.TestCase):

    def test_single_choice_creates_max_choices_one(self):
        parent = ET.Element("p")

        selection = SimpleNamespace(
            correct=["Richtig"],
            incorrect=["Falsch"],
            type="singleChoice",
            adjust_visibility=False,
        )

        item_body_module.insert_selection(
            p=parent,
            item=make_item(),
            images=[],
            selection=selection,
        )

        interaction = parent.find("choiceInteraction")

        self.assertIsNotNone(interaction)
        self.assertEqual(
            interaction.attrib["responseIdentifier"],
            "SELECTION",
        )
        self.assertEqual(interaction.attrib["shuffle"], "true")
        self.assertEqual(interaction.attrib["maxChoices"], "1")

    def test_multiple_choice_creates_max_choices_zero(self):
        parent = ET.Element("p")

        selection = SimpleNamespace(
            correct=["Richtig 1", "Richtig 2"],
            incorrect=["Falsch"],
            type="multipleChoice",
            adjust_visibility=False,
        )

        item_body_module.insert_selection(
            p=parent,
            item=make_item(),
            images=[],
            selection=selection,
        )

        interaction = parent.find("choiceInteraction")

        self.assertEqual(interaction.attrib["maxChoices"], "0")

    def test_unknown_selection_type_defaults_to_single_choice(self):
        parent = ET.Element("p")

        selection = SimpleNamespace(
            correct=["Richtig"],
            incorrect=["Falsch"],
            type="unknown",
            adjust_visibility=False,
        )

        item_body_module.insert_selection(
            p=parent,
            item=make_item(),
            images=[],
            selection=selection,
        )

        interaction = parent.find("choiceInteraction")

        self.assertEqual(interaction.attrib["maxChoices"], "1")

    def test_creates_choices_for_correct_and_incorrect_answers(self):
        parent = ET.Element("p")

        selection = SimpleNamespace(
            correct=["Richtig"],
            incorrect=["Falsch 1", "Falsch 2"],
            type="singleChoice",
            adjust_visibility=False,
        )

        item_body_module.insert_selection(
            p=parent,
            item=make_item(),
            images=[],
            selection=selection,
        )

        choices = parent.findall(
            "./choiceInteraction/simpleChoice"
        )

        self.assertEqual(len(choices), 3)

        identifiers = [
            choice.attrib["identifier"]
            for choice in choices
        ]

        self.assertEqual(
            identifiers,
            ["Richtig", "Falsch 1", "Falsch 2"],
        )

    def test_text_answers_are_written_into_paragraph(self):
        parent = ET.Element("p")

        selection = SimpleNamespace(
            correct=["Richtig"],
            incorrect=["Falsch"],
            type="singleChoice",
            adjust_visibility=False,
        )

        item_body_module.insert_selection(
            p=parent,
            item=make_item(),
            images=[],
            selection=selection,
        )

        paragraph_texts = [
            paragraph.text
            for paragraph in parent.findall(
                "./choiceInteraction/simpleChoice/p"
            )
        ]

        self.assertEqual(
            paragraph_texts,
            ["Richtig", "Falsch"],
        )

    def test_image_answer_calls_insert_image(self):
        parent = ET.Element("p")
        images = [
            make_image(
                image_id="BILD_1",
            )
        ]

        selection = SimpleNamespace(
            correct=["BILD_1"],
            incorrect=["Falsch"],
            type="singleChoice",
            adjust_visibility=False,
        )

        with patch.object(
            item_body_module,
            "insert_image",
        ) as insert_image_mock:
            item_body_module.insert_selection(
                p=parent,
                item=make_item(),
                images=images,
                selection=selection,
            )

        insert_image_mock.assert_called_once()

        arguments = insert_image_mock.call_args.args

        self.assertEqual(arguments[0], "BILD_1")

    def test_variant_image_answer_creates_include(self):
        parent = ET.Element("p")

        selection = SimpleNamespace(
            correct=["{V_BILD_1}"],
            incorrect=["Falsch"],
            type="singleChoice",
            adjust_visibility=False,
        )

        item_body_module.insert_selection(
            p=parent,
            item=make_item(),
            images=[],
            selection=selection,
        )

        include = parent.find(
            ".//include"
            "[@href='templates/task11/V_BILD_1.xml']"
        )

        self.assertIsNotNone(include)
        self.assertEqual(include.attrib["type"], "text/xml")

    def test_adjust_visibility_replaces_incorrect_answers_with_slots(self):
        parent = ET.Element("p")

        selection = SimpleNamespace(
            correct=["Richtig"],
            incorrect=["Falsch 1", "Falsch 2"],
            type="singleChoice",
            adjust_visibility=True,
            get_slot_ids=lambda: [
                "SELECTION_SLOT_1",
                "SELECTION_SLOT_2",
            ],
        )

        item_body_module.insert_selection(
            p=parent,
            item=make_item(),
            images=[],
            selection=selection,
        )

        choices = parent.findall(
            "./choiceInteraction/simpleChoice"
        )

        identifiers = [
            choice.attrib["identifier"]
            for choice in choices
        ]

        self.assertEqual(
            identifiers,
            [
                "Richtig",
                "SELECTION_SLOT_1",
                "SELECTION_SLOT_2",
            ],
        )

    def test_text_slots_create_printed_variables(self):
        parent = ET.Element("p")

        selection = SimpleNamespace(
            correct=["Richtig"],
            incorrect=["Falsch 1", "Falsch 2"],
            type="singleChoice",
            adjust_visibility=True,
            get_slot_ids=lambda: [
                "SELECTION_SLOT_1",
                "SELECTION_SLOT_2",
            ],
        )

        item_body_module.insert_selection(
            p=parent,
            item=make_item(),
            images=[],
            selection=selection,
        )

        variables = parent.findall(".//printedVariable")

        identifiers = [
            variable.attrib["identifier"]
            for variable in variables
        ]

        self.assertEqual(
            identifiers,
            [
                "SELECTION_SLOT_1",
                "SELECTION_SLOT_2",
            ],
        )

    def test_image_slots_create_template_includes(self):
        parent = ET.Element("p")

        images = [
            make_image(
                image_id="BILD_1",
            )
        ]

        selection = SimpleNamespace(
            correct=["Richtig"],
            incorrect=["BILD_1"],
            type="singleChoice",
            adjust_visibility=True,
            get_slot_ids=lambda: [
                "SELECTION_SLOT_1"
            ],
        )

        item_body_module.insert_selection(
            p=parent,
            item=make_item(),
            images=images,
            selection=selection,
        )

        include = parent.find(
            ".//include"
            "[@href='templates/task11/SELECTION_SLOT_1.xml']"
        )

        self.assertIsNotNone(include)


class TestInsertMatching(unittest.TestCase):

    def test_creates_match_interaction_with_attributes(self):
        parent = ET.Element("p")

        matching = SimpleNamespace(
            id="MATCHING_1",
            shuffle=True,
            max_associations=2,
            source_choices=[],
            target_choices=[],
        )

        interaction = item_body_module.insert_matching(
            p=parent,
            item=make_item(),
            images=[],
            matching=matching,
        )

        self.assertEqual(
            interaction.tag,
            "matchInteraction",
        )
        self.assertEqual(
            interaction.attrib["responseIdentifier"],
            "MATCHING_1",
        )
        self.assertEqual(
            interaction.attrib["shuffle"],
            "true",
        )
        self.assertEqual(
            interaction.attrib["maxAssociations"],
            "2",
        )

    def test_creates_two_simple_match_sets(self):
        parent = ET.Element("p")

        matching = SimpleNamespace(
            id="MATCHING_1",
            shuffle=False,
            max_associations=2,
            source_choices=[],
            target_choices=[],
        )

        interaction = item_body_module.insert_matching(
            p=parent,
            item=make_item(),
            images=[],
            matching=matching,
        )

        match_sets = interaction.findall("simpleMatchSet")

        self.assertEqual(len(match_sets), 2)

    def test_inserts_source_and_target_choices(self):
        parent = ET.Element("p")

        matching = SimpleNamespace(
            id="MATCHING_1",
            shuffle=True,
            max_associations=2,
            source_choices=[
                SimpleNamespace(
                    id="ID_1",
                    text="Quelle 1",
                    fixed=False,
                    match_max=1,
                ),
                SimpleNamespace(
                    id="ID_2",
                    text="Quelle 2",
                    fixed=True,
                    match_max=1,
                ),
            ],
            target_choices=[
                SimpleNamespace(
                    id="IDT_1",
                    text="Ziel 1",
                    fixed=False,
                    match_max=1,
                )
            ],
        )

        interaction = item_body_module.insert_matching(
            p=parent,
            item=make_item(),
            images=[],
            matching=matching,
        )

        match_sets = interaction.findall("simpleMatchSet")

        source_choices = match_sets[0].findall(
            "simpleAssociableChoice"
        )
        target_choices = match_sets[1].findall(
            "simpleAssociableChoice"
        )

        self.assertEqual(len(source_choices), 2)
        self.assertEqual(len(target_choices), 1)

        self.assertEqual(
            source_choices[0].attrib["identifier"],
            "ID_1",
        )
        self.assertEqual(
            source_choices[1].attrib["fixed"],
            "true",
        )
        self.assertEqual(
            target_choices[0].attrib["identifier"],
            "IDT_1",
        )


class TestInsertMatchChoice(unittest.TestCase):

    def test_text_choice_creates_paragraph(self):
        parent = ET.Element("simpleMatchSet")

        choice = SimpleNamespace(
            id="ID_1",
            text="Quelle",
            fixed=False,
            match_max=1,
        )

        result = item_body_module.insert_match_choice(
            parent=parent,
            choice=choice,
            item=make_item(),
            images=[],
        )

        self.assertEqual(
            result.attrib["identifier"],
            "ID_1",
        )
        self.assertEqual(
            result.attrib["fixed"],
            "false",
        )
        self.assertEqual(
            result.attrib["matchMax"],
            "1",
        )

        paragraph = result.find("p")

        self.assertIsNotNone(paragraph)
        self.assertEqual(paragraph.text, "Quelle")

    def test_image_choice_calls_insert_image(self):
        parent = ET.Element("simpleMatchSet")

        image = make_image(
            image_id="BILD_1",
        )

        choice = SimpleNamespace(
            id="ID_1",
            text="BILD_1",
            fixed=False,
            match_max=1,
        )

        with patch.object(
            item_body_module,
            "insert_image",
        ) as insert_image_mock:
            item_body_module.insert_match_choice(
                parent=parent,
                choice=choice,
                item=make_item(),
                images=[image],
            )

        insert_image_mock.assert_called_once()

        arguments = insert_image_mock.call_args.args

        self.assertEqual(arguments[0], "BILD_1")


class TestInsertGraphicalAssignment(unittest.TestCase):

    def test_creates_graphic_gap_match_interaction(self):
        parent = ET.Element("p")
        item = make_item()
        images = []

        background = make_image(
            image_id="BACKGROUND",
            href="background.png",
            width="320",
            height="200",
        )

        assignment = SimpleNamespace(
            correct_snippets=[],
            wrong_snippets=[],
            cut_areas=[],
            get_background_image=lambda: background,
        )

        interaction = item_body_module.insert_graphical_assignment(
            p=parent,
            item=item,
            images=images,
            graphical_assignment=assignment,
        )

        self.assertEqual(
            interaction.tag,
            "graphicGapMatchInteraction",
        )
        self.assertEqual(
            interaction.attrib["responseIdentifier"],
            "RESPONSE_1",
        )
        self.assertEqual(
            interaction.attrib["maxAssociations"],
            "0",
        )
        self.assertEqual(
            interaction.attrib["data-shuffle"],
            "true",
        )
        self.assertEqual(
            interaction.attrib["data-show-labels"],
            "false",
        )

    def test_inserts_background_image(self):
        parent = ET.Element("p")
        item = make_item()
        images = []

        background = make_image(
            image_id="BACKGROUND",
            href="background.png",
            width="320",
            height="200",
        )

        assignment = SimpleNamespace(
            correct_snippets=[],
            wrong_snippets=[],
            cut_areas=[],
            get_background_image=lambda: background,
        )

        interaction = item_body_module.insert_graphical_assignment(
            p=parent,
            item=item,
            images=images,
            graphical_assignment=assignment,
        )

        object_tag = interaction.find("object")

        self.assertIsNotNone(object_tag)
        self.assertEqual(
            object_tag.attrib["data"],
            "media/background.png",
        )
        self.assertEqual(
            object_tag.attrib["type"],
            "image/png",
        )
        self.assertEqual(
            object_tag.attrib["width"],
            "320",
        )

    def test_inserts_correct_and_wrong_gap_images(self):
        parent = ET.Element("p")
        item = make_item()
        images = []

        background = make_image(
            image_id="BACKGROUND",
            href="background.png",
            width="320",
            height="200",
        )

        correct_image = make_image(
            image_id="CORRECT_1",
            href="correct.png",
            width="64",
            height="64",
        )

        wrong_image = make_image(
            image_id="WRONG_1",
            href="wrong.png",
            width="64",
            height="64",
        )

        assignment = SimpleNamespace(
            correct_snippets=[
                SimpleNamespace(
                    output_path="correct_path"
                )
            ],
            wrong_snippets=[
                SimpleNamespace(
                    output_path="wrong_path"
                )
            ],
            cut_areas=[],
            get_background_image=lambda: background,
            get_image_by_path=lambda path: {
                "correct_path": correct_image,
                "wrong_path": wrong_image,
            }.get(path),
        )

        interaction = item_body_module.insert_graphical_assignment(
            p=parent,
            item=item,
            images=images,
            graphical_assignment=assignment,
        )

        gap_images = interaction.findall("gapImg")

        self.assertEqual(len(gap_images), 2)
        self.assertEqual(
            gap_images[0].attrib["identifier"],
            "ID_1",
        )
        self.assertEqual(
            gap_images[1].attrib["identifier"],
            "ID_2",
        )

        first_object = gap_images[0].find("object")
        second_object = gap_images[1].find("object")

        self.assertEqual(
            first_object.attrib["data"],
            "media/correct.png",
        )
        self.assertEqual(
            second_object.attrib["data"],
            "media/wrong.png",
        )

    def test_inserts_hotspots_with_reduced_coordinates(self):
        parent = ET.Element("p")
        item = make_item()

        background = make_image(
            image_id="BACKGROUND",
            href="background.png",
            width="320",
            height="200",
        )

        assignment = SimpleNamespace(
            correct_snippets=[],
            wrong_snippets=[],
            cut_areas=[
                (10, 20, 60, 70),
                (100, 110, 50, 40),
            ],
            get_background_image=lambda: background,
        )

        interaction = item_body_module.insert_graphical_assignment(
            p=parent,
            item=item,
            images=[],
            graphical_assignment=assignment,
        )

        hotspots = interaction.findall("associableHotspot")

        self.assertEqual(len(hotspots), 2)

        self.assertEqual(
            hotspots[0].attrib["identifier"],
            "IDT_1",
        )
        self.assertEqual(
            hotspots[0].attrib["coords"],
            "10,20,58,78",
        )

        self.assertEqual(
            hotspots[1].attrib["identifier"],
            "IDT_2",
        )
        self.assertEqual(
            hotspots[1].attrib["coords"],
            "100,110,138,138",
        )

    def test_raises_error_if_hotspot_becomes_too_small(self):
        parent = ET.Element("p")
        item = make_item()

        background = make_image(
            image_id="BACKGROUND",
            href="background.png",
            width="320",
            height="200",
        )

        assignment = SimpleNamespace(
            correct_snippets=[],
            wrong_snippets=[],
            cut_areas=[
                (10, 20, 12, 12)
            ],
            get_background_image=lambda: background,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Hotspot 1",
        ):
            item_body_module.insert_graphical_assignment(
                p=parent,
                item=item,
                images=[],
                graphical_assignment=assignment,
            )


class TestInsertGapImage(unittest.TestCase):

    def test_raises_error_when_local_image_does_not_exist(self):
        interaction = ET.Element(
            "graphicGapMatchInteraction"
        )

        assignment = SimpleNamespace(
            get_image_by_path=lambda path: None
        )

        with self.assertRaisesRegex(
            ValueError,
            "kein lokales Image-Objekt",
        ):
            item_body_module.insert_gap_image(
                interaction=interaction,
                identifier="ID_1",
                image_path="unknown.png",
                item=make_item(),
                images=[],
                graphical_assignment=assignment,
            )

    def test_adds_image_to_global_images_and_item_images(self):
        interaction = ET.Element(
            "graphicGapMatchInteraction"
        )

        image = make_image(
            image_id="IMAGE_1",
            href="snippet.png",
            width="64",
            height="32",
        )

        item = make_item()
        images = []

        assignment = SimpleNamespace(
            get_image_by_path=lambda path: image
        )

        item_body_module.insert_gap_image(
            interaction=interaction,
            identifier="ID_1",
            image_path="snippet.png",
            item=item,
            images=images,
            graphical_assignment=assignment,
        )

        self.assertEqual(images, [image])
        self.assertEqual(item.images_used, [image])

    def test_does_not_duplicate_existing_global_image(self):
        interaction = ET.Element(
            "graphicGapMatchInteraction"
        )

        image = make_image(
            image_id="IMAGE_1",
            href="snippet.png",
            width="64",
            height="32",
        )

        item = make_item()
        images = [image]

        assignment = SimpleNamespace(
            get_image_by_path=lambda path: image
        )

        item_body_module.insert_gap_image(
            interaction=interaction,
            identifier="ID_1",
            image_path="snippet.png",
            item=item,
            images=images,
            graphical_assignment=assignment,
        )

        self.assertEqual(len(images), 1)
        self.assertEqual(len(item.images_used), 1)

    def test_creates_gap_image_with_scaled_dimensions(self):
        interaction = ET.Element(
            "graphicGapMatchInteraction"
        )

        image = make_image(
            image_id="IMAGE_1",
            href="snippet.png",
            width="100",
            height="50",
        )

        assignment = SimpleNamespace(
            get_image_by_path=lambda path: image
        )

        item_body_module.insert_gap_image(
            interaction=interaction,
            identifier="ID_1",
            image_path="snippet.png",
            item=make_item(),
            images=[],
            graphical_assignment=assignment,
            display_scale=0.5,
        )

        gap_image = interaction.find("gapImg")
        object_tag = gap_image.find("object")

        self.assertEqual(
            gap_image.attrib["identifier"],
            "ID_1",
        )
        self.assertEqual(
            gap_image.attrib["matchMax"],
            "1",
        )
        self.assertEqual(
            object_tag.attrib["width"],
            "50",
        )
        self.assertEqual(
            object_tag.attrib["height"],
            "25",
        )

    def test_uses_correct_mime_type(self):
        interaction = ET.Element(
            "graphicGapMatchInteraction"
        )

        image = make_image(
            image_id="IMAGE_1",
            href="snippet.jpg",
            width="100",
            height="50",
        )

        assignment = SimpleNamespace(
            get_image_by_path=lambda path: image
        )

        item_body_module.insert_gap_image(
            interaction=interaction,
            identifier="ID_1",
            image_path="snippet.jpg",
            item=make_item(),
            images=[],
            graphical_assignment=assignment,
        )

        object_tag = interaction.find("./gapImg/object")

        self.assertEqual(
            object_tag.attrib["type"],
            "image/jpeg",
        )


class TestInsertGraphicalBackground(unittest.TestCase):

    def test_adds_background_to_global_and_used_images(self):
        interaction = ET.Element(
            "graphicGapMatchInteraction"
        )

        background = make_image(
            image_id="BACKGROUND",
            href="background.png",
            width="320",
            height="200",
        )

        item = make_item()
        images = []

        assignment = SimpleNamespace(
            get_background_image=lambda: background
        )

        item_body_module.insert_graphical_background(
            interaction=interaction,
            item=item,
            images=images,
            graphical_assignment=assignment,
        )

        self.assertEqual(images, [background])
        self.assertEqual(item.images_used, [background])

    def test_does_not_duplicate_existing_background(self):
        interaction = ET.Element(
            "graphicGapMatchInteraction"
        )

        background = make_image(
            image_id="BACKGROUND",
            href="background.png",
            width="320",
            height="200",
        )

        item = make_item()
        images = [background]

        assignment = SimpleNamespace(
            get_background_image=lambda: background
        )

        item_body_module.insert_graphical_background(
            interaction=interaction,
            item=item,
            images=images,
            graphical_assignment=assignment,
        )

        self.assertEqual(len(images), 1)
        self.assertEqual(len(item.images_used), 1)


class TestImageHelpers(unittest.TestCase):

    def test_get_image_mime_type_for_png(self):
        result = item_body_module.get_image_mime_type(
            "bild.png"
        )

        self.assertEqual(result, "image/png")

    def test_get_image_mime_type_for_jpeg(self):
        result = item_body_module.get_image_mime_type(
            "bild.jpg"
        )

        self.assertEqual(result, "image/jpeg")

    def test_get_image_mime_type_for_svg(self):
        result = item_body_module.get_image_mime_type(
            "bild.svg"
        )

        self.assertEqual(result, "image/svg+xml")

    def test_get_image_mime_type_uses_png_fallback(self):
        result = item_body_module.get_image_mime_type(
            "bild.unbekannt"
        )

        self.assertEqual(result, "image/png")

    def test_is_valid_image_identifier_returns_true(self):
        images = [
            make_image("BILD_1"),
            make_image("BILD_2"),
        ]

        result = item_body_module.is_valid_image_identifier(
            "BILD_1",
            images,
        )

        self.assertTrue(result)

    def test_is_valid_image_identifier_returns_false_for_unknown_id(self):
        images = [
            make_image("BILD_1")
        ]

        result = item_body_module.is_valid_image_identifier(
            "BILD_2",
            images,
        )

        self.assertFalse(result)

    def test_is_valid_image_identifier_returns_false_for_none_text(self):
        result = item_body_module.is_valid_image_identifier(
            None,
            [],
        )

        self.assertFalse(result)

    def test_is_valid_image_identifier_returns_false_for_none_images(self):
        result = item_body_module.is_valid_image_identifier(
            "BILD_1",
            None,
        )

        self.assertFalse(result)

    def test_get_image_href_accepts_string(self):
        result = item_body_module.get_image_href(
            "bild.png"
        )

        self.assertEqual(result, "bild.png")

    def test_get_image_href_uses_href(self):
        image = SimpleNamespace(
            href="bild.png"
        )

        result = item_body_module.get_image_href(image)

        self.assertEqual(result, "bild.png")

    def test_get_image_href_uses_file_name(self):
        image = SimpleNamespace(
            file_name="bild.png"
        )

        result = item_body_module.get_image_href(image)

        self.assertEqual(result, "bild.png")

    def test_get_image_href_uses_path(self):
        image = SimpleNamespace(
            path="files/bild.png"
        )

        result = item_body_module.get_image_href(image)

        self.assertEqual(result, "files/bild.png")

    def test_get_image_href_rejects_invalid_object(self):
        with self.assertRaisesRegex(
            ValueError,
            "keinen gültigen Pfad",
        ):
            item_body_module.get_image_href(
                SimpleNamespace()
            )


class TestImageTemplates(unittest.TestCase):

    def test_image_template_creates_hidden_div_and_include(self):
        root = ET.Element("itemBody")

        item_body_module.image_template(
            item_body_tag=root,
            path_part="task11/V_BILD_1",
        )

        div = root.find("div")

        self.assertIsNotNone(div)
        self.assertEqual(
            div.attrib["style"],
            "display:none;",
        )
        self.assertEqual(
            div.attrib["data-onyx-editor"],
            "template-nonref",
        )

        include = div.find("include")

        self.assertIsNotNone(include)
        self.assertEqual(
            include.attrib["href"],
            "templates/task11/V_BILD_1.xml",
        )
        self.assertEqual(
            include.attrib["type"],
            "text/xml",
        )

    def test_include_image_templates_adds_all_variant_images_without_selection(self):
        root = ET.Element("itemBody")

        item = make_item(
            variant_dependent_images=[
                SimpleNamespace(id="V_BILD_1"),
                SimpleNamespace(id="V_BILD_2"),
            ]
        )

        item_body_module.include_image_templates(
            item_body_tag=root,
            item=item,
            images=[],
            selection=None,
        )

        hrefs = [
            include.attrib["href"]
            for include in root.findall("./div/include")
        ]

        self.assertEqual(
            hrefs,
            [
                "templates/task11/V_BILD_1.xml",
                "templates/task11/V_BILD_2.xml",
            ],
        )

    def test_adjusted_text_selection_does_not_add_slot_templates(self):
        root = ET.Element("itemBody")

        selection = SimpleNamespace(
            adjust_visibility=True,
            incorrect=["Falsch 1", "Falsch 2"],
            get_slot_ids=lambda: [
                "SELECTION_SLOT_1",
                "SELECTION_SLOT_2",
            ],
        )

        item_body_module.include_image_templates(
            item_body_tag=root,
            item=make_item(),
            images=[],
            selection=selection,
        )

        includes = root.findall("./div/include")

        self.assertEqual(includes, [])

    def test_adjusted_image_selection_adds_slot_templates(self):
        root = ET.Element("itemBody")

        images = [
            make_image(
                image_id="BILD_1"
            )
        ]

        selection = SimpleNamespace(
            adjust_visibility=True,
            incorrect=["BILD_1"],
            get_slot_ids=lambda: [
                "SELECTION_SLOT_1"
            ],
        )

        item_body_module.include_image_templates(
            item_body_tag=root,
            item=make_item(),
            images=images,
            selection=selection,
        )

        include = root.find(
            "./div/include"
            "[@href='templates/task11/SELECTION_SLOT_1.xml']"
        )

        self.assertIsNotNone(include)

    def test_variant_image_used_as_incorrect_answer_is_not_added_twice(self):
        root = ET.Element("itemBody")

        item = make_item(
            variant_dependent_images=[
                SimpleNamespace(id="V_BILD_1"),
                SimpleNamespace(id="V_BILD_2"),
            ]
        )

        selection = SimpleNamespace(
            adjust_visibility=True,
            incorrect=["V_BILD_1"],
            get_slot_ids=lambda: [
                "SELECTION_SLOT_1"
            ],
        )

        item_body_module.include_image_templates(
            item_body_tag=root,
            item=item,
            images=[],
            selection=selection,
        )

        hrefs = [
            include.attrib["href"]
            for include in root.findall("./div/include")
        ]

        self.assertIn(
            "templates/task11/SELECTION_SLOT_1.xml",
            hrefs,
        )
        self.assertIn(
            "templates/task11/V_BILD_2.xml",
            hrefs,
        )
        self.assertNotIn(
            "templates/task11/V_BILD_1.xml",
            hrefs,
        )


if __name__ == "__main__":
    unittest.main()