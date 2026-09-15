from __future__ import annotations

import os
from pathlib import Path

import pytest
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.integration.frontend.helpers import (
    click,
    click_and_wait_for_pattern,
    click_pattern,
    initialize_feedback_if_needed,
    load_images,
    open_task,
    pattern_count,
    select_dcc_option,
    set_checkbox,
    set_debounced_pattern_value,
    set_pattern_value,
    set_value,
    toggle_checkbox,
    wait_element,
)


TIMEOUT = 10


def wait_pattern(pysea, minimum=1, **expected):
    WebDriverWait(
        pysea.driver,
        TIMEOUT,
        poll_frequency=0.05,
        ignored_exceptions=(StaleElementReferenceException,),
    ).until(
        lambda _: pattern_count(pysea, **expected) >= minimum
    )


@pytest.mark.frontend_integration
def test_frontend_all_controls(pysea):
    project_root = Path(__file__).resolve().parents[3]

    media_dir = Path(
        os.environ.get(
            "PYSEA_MEDIA_SCRIPT2",
            project_root
            / "tests"
            / "integration_test_data"
            / "input_dir"
            / "media_script2",
        )
    )

    excel_file = Path(
        os.environ.get(
            "PYSEA_TEST_EXCEL",
            project_root
            / "tests"
            / "integration_test_data"
            / "input_dir"
            / "Beispiel.xlsx",
        )
    )

    assert media_dir.is_dir()

    # ================================================================
    # 1. TESTEDITOR
    # ================================================================

    click(pysea, "#b_edit_test")
    wait_element(pysea, "#neue-sektion")

    # ================================================================
    # 2. SEKTION + AUFGABEN
    # ================================================================

    click(pysea, "#neue-sektion")
    wait_element(pysea, "#neue-aufgabe")

    # Sechs Aufgaben:
    # 0 normale Antwort / Feedback
    # 1 Excelantwort
    # 2 Single Choice
    # 3 Multiple Choice
    # 4 Zuordnungen
    # 5 Tabellen + variantenabhängiger Inhalt
    for _ in range(6):
        old_count = pattern_count(
            pysea,
            type="b-aufgabe-bearbeiten",
        )

        click(pysea, "#neue-aufgabe")

        WebDriverWait(
            pysea.driver,
            TIMEOUT,
            poll_frequency=0.05,
            ignored_exceptions=(StaleElementReferenceException,),
        ).until(
            lambda _: pattern_count(
                pysea,
                type="b-aufgabe-bearbeiten",
            ) > old_count
        )

    assert pattern_count(
        pysea,
        type="b-aufgabe-bearbeiten",
    ) == 6

    # ================================================================
    # 3. BILDER LADEN
    # ================================================================

    load_images(pysea, media_dir)

    assert pysea.driver.find_elements(By.CSS_SELECTOR, "img")

    if pattern_count(pysea, type="breite"):
        set_pattern_value(
            pysea,
            "300",
            commit=False,
            element_index=0,
            type="breite",
        )

    if pattern_count(pysea, type="hoehe"):
        set_pattern_value(
            pysea,
            "200",
            commit=False,
            element_index=0,
            type="hoehe",
        )

    # ================================================================
    # 4. SEKTION BEARBEITEN
    # ================================================================

    assert pattern_count(pysea, type="b-sektion-bearbeiten") > 0
    click_pattern(
        pysea,
        element_index=0,
        type="b-sektion-bearbeiten",
    )

    click(pysea, "#b_general")
    wait_element(pysea, "#i_title")

    set_value(pysea, "#i_title", "Frontend Smoke Test Sektion")
    set_value(pysea, "#i_text", "Text der Testsektion.")

    # ================================================================
    # 5. EXCELVARIABLEN DER SEKTION
    # ================================================================

    click(pysea, "#b_excel_variables")
    wait_element(pysea, "#b_initialize_excel_variables")

    initialize_buttons = pysea.driver.find_elements(
        By.CSS_SELECTOR,
        "#b_initialize_excel_variables",
    )

    if any(_is_displayed(button) for button in initialize_buttons):
        click(pysea, "#b_initialize_excel_variables")
        wait_element(pysea, "#b_new_excel_variable")

    # Das Dropdown kann erst sinnvoll befüllt werden, wenn in der
    # Testkonfiguration Exceldateien hinterlegt wurden. Der eigentliche
    # Excelpfad wird weiter unten getestet.
    if excel_file.is_file():
        pysea.driver.find_elements(By.CSS_SELECTOR, "#excel_variable_doc")

    click(pysea, "#b_new_excel_variable")
    wait_pattern(pysea, type="i_excel_variable_cell")
    set_pattern_value(
        pysea,
        "C10",
        commit=False,
        element_index=0,
        type="i_excel_variable_cell",
    )

    click(pysea, "#b_new_excel_variable")
    wait_pattern(pysea, minimum=2, type="i_excel_variable_cell")
    set_pattern_value(
        pysea,
        "C11",
        commit=False,
        element_index=1,
        type="i_excel_variable_cell",
    )

    # ================================================================
    # 6. AUFGABE 1 – ALLGEMEIN
    # ================================================================

    open_task(pysea, 0)
    click(pysea, "#b_general")
    wait_element(pysea, "#i_title")

    set_value(pysea, "#i_title", "Normale Antwort")
    set_value(pysea, "#i_text", "Wie lautet die Antwort? {RESPONSE_1}")
    set_value(pysea, "#i_points_task", "5")
    set_value(pysea, "#i_points_per_gap_tasks", "2")

    # ================================================================
    # 7. NORMALE ANTWORTEN
    # ================================================================

    click(pysea, "#b_answers")

    click_and_wait_for_pattern(
        pysea,
        "#b_new_response",
        type="answer",
    )

    set_pattern_value(
        pysea,
        42,
        commit=True,
        element_index=0,
        type="answer",
    )

    click_and_wait_for_pattern(
        pysea,
        "#b_new_response",
        type="answer",
    )

    set_pattern_value(
        pysea,
        84,
        commit=True,
        element_index=1,
        type="answer",
    )

    assert pattern_count(pysea, type="answer") == 2

    if pattern_count(pysea, type="b_remove_answer"):
        click_pattern(
            pysea,
            element_index=-1,
            type="b_remove_answer",
        )

        WebDriverWait(
            pysea.driver,
            TIMEOUT,
            poll_frequency=0.05,
            ignored_exceptions=(StaleElementReferenceException,),
        ).until(
            lambda _: pattern_count(pysea, type="answer") == 1
        )

    # ================================================================
    # 8. FEEDBACK
    # ================================================================

    click(pysea, "#b_feedback")

    incorrect = initialize_feedback_if_needed(pysea)
    assert incorrect

    set_pattern_value(
        pysea,
        "Falsche Antwort",
        commit=False,
        element_index=0,
        type="feedback_incorrect",
    )

    if pysea.driver.find_elements(By.CSS_SELECTOR, "#feedback_correct"):
        set_value(pysea, "#feedback_correct", "Richtige Antwort")

    click(pysea, "#add_incorrect_feedback")
    wait_pattern(pysea, minimum=2, type="feedback_incorrect")

    set_pattern_value(
        pysea,
        "Noch einmal versuchen",
        commit=False,
        element_index=1,
        type="feedback_incorrect",
    )

    # ================================================================
    # 9. AUFGABE 2 – EXCELANTWORTEN
    # ================================================================

    open_task(pysea, 1)
    click(pysea, "#b_answers")

    click(pysea, "#b_initialize_excel_responses")
    wait_element(pysea, "#b_new_excel_response", enabled=True)
    click(pysea, "#b_new_excel_response")

    wait_pattern(pysea, type="excel_answer")
    assert pattern_count(pysea, type="excel_answer") == 1

    set_pattern_value(
        pysea,
        "C3",
        commit=False,
        element_index=0,
        type="excel_answer",
    )

    assert pattern_count(pysea, type="excel_answer_points") > 0
    set_pattern_value(
        pysea,
        "2",
        commit=False,
        element_index=0,
        type="excel_answer_points",
    )

    set_checkbox(
        pysea,
        "#cb_acc_from_excel input",
        True,
    )

    # ================================================================
    # 10. AUFGABE 3 – SINGLE CHOICE
    # ================================================================

    open_task(pysea, 2)
    click(pysea, "#b_selections")
    wait_element(pysea, "#dd_selection_type")

    select_dcc_option(
        pysea,
        "#dd_selection_type",
        "single Choice",
    )

    click(pysea, "#b_add_selection")
    wait_pattern(pysea, type="i_selection_correct")

    set_pattern_value(
        pysea,
        "Richtig",
        commit=False,
        element_index=0,
        type="i_selection_correct",
    )

    if pattern_count(pysea, type="i_selection_wrong"):
        set_pattern_value(
            pysea,
            "Falsch",
            commit=False,
            element_index=0,
            type="i_selection_wrong",
        )

    click_pattern(
        pysea,
        id="b_new_selection",
        type="incorrect",
    )

    wait_pattern(pysea, minimum=2, type="i_selection_wrong")

    set_pattern_value(
        pysea,
        "Auch falsch",
        commit=False,
        element_index=1,
        type="i_selection_wrong",
    )

    if pysea.driver.find_elements(By.CSS_SELECTOR, "#cb_adjust_visibility input"):
        set_checkbox(
            pysea,
            "#cb_adjust_visibility input",
            True,
        )

        wait_element(pysea, "#dd_visible_wrong_count")
        select_dcc_option(
            pysea,
            "#dd_visible_wrong_count",
            "1 anzeigen",
        )

    # ================================================================
    # 11. AUFGABE 4 – MULTIPLE CHOICE
    # ================================================================

    open_task(pysea, 3)
    click(pysea, "#b_selections")

    select_dcc_option(
        pysea,
        "#dd_selection_type",
        "multiple Choice",
    )

    click(pysea, "#b_add_selection")
    wait_pattern(pysea, type="i_selection_correct")

    click_pattern(
        pysea,
        id="b_new_selection",
        type="correct",
    )

    wait_pattern(pysea, minimum=2, type="i_selection_correct")

    set_pattern_value(
        pysea,
        "Antwort A",
        commit=False,
        element_index=0,
        type="i_selection_correct",
    )
    set_pattern_value(
        pysea,
        "Antwort B",
        commit=False,
        element_index=1,
        type="i_selection_correct",
    )

    click(pysea, "#b_delete_selection")

    # ================================================================
    # 12. AUFGABE 5 – MATCHING
    # ================================================================

    open_task(pysea, 4)
    click(pysea, "#b_graphical_assignment")

    select_dcc_option(
        pysea,
        "#dd_graphical_assignment_type",
        "Einfache Zuordnung (Matching)",
    )

    click_and_wait_for_pattern(
        pysea,
        "#b_add_graphical_assignment",
        type="i_matching_source",
    )

    set_debounced_pattern_value(
        pysea,
        "Begriff A",
        element_index=0,
        type="i_matching_source",
        index=0,
    )
    set_debounced_pattern_value(
        pysea,
        "BILD_1",
        element_index=0,
        type="i_matching_target",
        index=0,
    )

    click_and_wait_for_pattern(
        pysea,
        "#b_new_matching_pair",
        type="i_matching_source",
    )

    set_debounced_pattern_value(
        pysea,
        "Begriff B",
        element_index=0,
        type="i_matching_source",
        index=1,
    )
    set_debounced_pattern_value(
        pysea,
        "BILD_2",
        element_index=0,
        type="i_matching_target",
        index=1,
    )

    assert pattern_count(pysea, type="i_matching_source") == 2
    assert pattern_count(pysea, type="i_matching_target") == 2

    # ================================================================
    # 13. GRAFISCHE ZUORDNUNG
    # ================================================================

    click(pysea, "#b_delete_graphical_assignment")

    select_dcc_option(
        pysea,
        "#dd_graphical_assignment_type",
        "Grafische Zuordnung mit Bildausschnitten",
    )

    click(pysea, "#b_add_graphical_assignment")
    wait_element(pysea, "#i_graphical_original", enabled=True)

    set_value(pysea, "#i_graphical_original", "BILD_1")
    set_value(pysea, "#i_graphical_mask", "BILD_2")
    set_value(pysea, "#i_graphical_correct", "BILD_3")

    click(pysea, "#b_new_graphical_wrong")
    wait_pattern(pysea, minimum=2, type="i_graphical_wrong")

    set_pattern_value(
        pysea,
        "BILD_4",
        commit=False,
        element_index=0,
        type="i_graphical_wrong",
    )
    set_pattern_value(
        pysea,
        "BILD_5",
        commit=False,
        element_index=1,
        type="i_graphical_wrong",
    )

    # ================================================================
    # 14. AUFGABE 6 – CUSTOM TABLE
    # ================================================================

    open_task(pysea, 5)
    click(pysea, "#b_tables")
    wait_element(pysea, "#dd_table_type")

    select_dcc_option(
        pysea,
        "#dd_table_type",
        "Benuterdefinierte Tabelle",
    )

    click(pysea, "#b_new_table")
    wait_pattern(pysea, type="i_row_count_custom_table")

    set_pattern_value(
        pysea,
        "3",
        commit=False,
        element_index=0,
        type="i_row_count_custom_table",
    )
    set_pattern_value(
        pysea,
        "2",
        commit=False,
        element_index=0,
        type="i_col_count_custom_table",
    )

    wait_pattern(pysea, type="i_cell_custom_table")

    if pattern_count(pysea, type="i_cell_custom_table"):
        set_pattern_value(
            pysea,
            "Zelle A",
            commit=False,
            element_index=0,
            type="i_cell_custom_table",
        )

    # ================================================================
    # 15. EXCELTABLE
    # ================================================================

    select_dcc_option(
        pysea,
        "#dd_table_type",
        "Exceltabelle",
    )

    click(pysea, "#b_new_table")
    wait_pattern(pysea, type="neuer_bereich")

    assert pattern_count(pysea, type="excel") > 0

    if pattern_count(pysea, type="b_automatic_responses"):
        click_pattern(
            pysea,
            element_index=-1,
            type="b_automatic_responses",
        )

    click_pattern(
        pysea,
        element_index=-1,
        type="neuer_bereich",
    )

    wait_pattern(pysea, type="von_zelle")

    set_pattern_value(
        pysea,
        "C4",
        commit=False,
        element_index=-1,
        type="von_zelle",
    )
    set_pattern_value(
        pysea,
        "H8",
        commit=False,
        element_index=-1,
        type="bis_zelle",
    )

    if pattern_count(pysea, type="b_delete_area"):
        click_pattern(
            pysea,
            element_index=-1,
            type="b_delete_area",
        )

    if pysea.driver.find_elements(By.CSS_SELECTOR, "#b_show_tables input"):
        toggle_checkbox(pysea, "#b_show_tables input")

    # ================================================================
    # 16. VARIANTENABHÄNGIGES BILD
    # ================================================================

    click(pysea, "#b_general")
    wait_element(pysea, "#dd_variant_dependent_content_type")

    select_dcc_option(
        pysea,
        "#dd_variant_dependent_content_type",
        "Bild",
    )

    click(pysea, "#b_new_variant_dependent_content")
    wait_pattern(pysea, type="b_new_image_vdi")

    click_pattern(pysea, type="b_new_image_vdi")
    wait_pattern(pysea, type="vdi_image_id")

    set_pattern_value(
        pysea,
        "BILD_1",
        commit=False,
        element_index=0,
        type="vdi_image_id",
    )
    set_pattern_value(
        pysea,
        "1",
        commit=False,
        element_index=0,
        type="vdi_image_lb",
    )
    set_pattern_value(
        pysea,
        "3",
        commit=False,
        element_index=0,
        type="vdi_image_ub",
    )

    click_pattern(pysea, type="b_new_image_vdi")
    wait_pattern(pysea, minimum=2, type="vdi_image_id")

    set_pattern_value(
        pysea,
        "BILD_2",
        commit=False,
        element_index=1,
        type="vdi_image_id",
    )
    set_pattern_value(
        pysea,
        "4",
        commit=False,
        element_index=1,
        type="vdi_image_lb",
    )
    set_pattern_value(
        pysea,
        "6",
        commit=False,
        element_index=1,
        type="vdi_image_ub",
    )

    # ================================================================
    # 17. VARIANTENABHÄNGIGE TABELLE
    # ================================================================

    select_dcc_option(
        pysea,
        "#dd_variant_dependent_content_type",
        "Tabelle",
    )

    click(pysea, "#b_new_variant_dependent_content")
    wait_pattern(pysea, type="b_new_table_vdt")

    click_pattern(pysea, type="b_new_table_vdt")
    wait_pattern(pysea, type="vdt_table_id")

    set_pattern_value(
        pysea,
        "TABLE_1",
        commit=False,
        element_index=0,
        type="vdt_table_id",
    )
    set_pattern_value(
        pysea,
        "1",
        commit=False,
        element_index=0,
        type="vdt_table_lb",
    )
    set_pattern_value(
        pysea,
        "3",
        commit=False,
        element_index=0,
        type="vdt_table_ub",
    )

    click_pattern(pysea, type="b_new_table_vdt")
    wait_pattern(pysea, minimum=2, type="vdt_table_id")

    set_pattern_value(
        pysea,
        "TABLE_2",
        commit=False,
        element_index=1,
        type="vdt_table_id",
    )
    set_pattern_value(
        pysea,
        "4",
        commit=False,
        element_index=1,
        type="vdt_table_lb",
    )
    set_pattern_value(
        pysea,
        "6",
        commit=False,
        element_index=1,
        type="vdt_table_ub",
    )

    # ================================================================
    # 18. VARIANTENSYSTEM
    # ================================================================

    click(pysea, "#b_variants")
    wait_element(pysea, "#dd_assignment")

    select_dcc_option(
        pysea,
        "#dd_assignment",
        "Matrikelnummer + Variablen",
    )

    wait_element(pysea, "#cb_use_variants")
    set_checkbox(pysea, "#cb_use_variants input", True)
    wait_element(pysea, "#i_variants_title")

    set_value(pysea, "#i_variants_title", "Variantentest")
    set_value(pysea, "#i_variants_text", "Matrikelnummer: {RESPONSE}")

    wait_element(pysea, "#b_new_variable")
    click(pysea, "#b_new_variable")
    wait_pattern(pysea, type="i_variable_value_response")

    set_pattern_value(
        pysea,
        "1",
        commit=False,
        element_index=0,
        type="i_variable_value_response",
    )

    click_pattern(
        pysea,
        type="b_new_dependent_variable",
        index=0,
    )

    wait_pattern(pysea, type="i_variable_name")
    set_pattern_value(
        pysea,
        "a",
        commit=False,
        element_index=0,
        type="i_variable_name",
    )

    click_pattern(
        pysea,
        type="b_new_condition",
        index=0,
    )

    wait_pattern(pysea, type="i_condition_lower_bound")

    set_pattern_value(
        pysea,
        "0",
        commit=False,
        element_index=0,
        type="i_condition_lower_bound",
    )
    set_pattern_value(
        pysea,
        "3",
        commit=False,
        element_index=0,
        type="i_condition_upper_bound",
    )

    if pattern_count(pysea, type="i_condition_value"):
        set_pattern_value(
            pysea,
            "1",
            commit=False,
            element_index=0,
            type="i_condition_value",
        )

    select_dcc_option(
        pysea,
        "#dd_assignment",
        "Manuell",
    )
    wait_element(pysea, "#i_count_variants")
    set_value(pysea, "#i_count_variants", "3")

    select_dcc_option(
        pysea,
        "#dd_assignment",
        "Automatisch über Matrikelnummer",
    )
    wait_element(pysea, "#i_count_variants")
    set_value(pysea, "#i_count_variants", "9")

    # ================================================================
    # 19. TESTKONFIGURATION
    # ================================================================

    click(pysea, "#configuration")
    wait_element(pysea, "#i_test_title")

    set_value(pysea, "#i_test_title", "Frontend Smoke Test")

    click(pysea, "#b_new_excel_file")
    wait_pattern(pysea, type="b_path_excel_file")

    if excel_file.is_file():
        set_pattern_value(
            pysea,
            str(excel_file.resolve()),
            commit=False,
            element_index=0,
            type="b_path_excel_file",
        )

    export_dir = project_root / "test_output"
    set_value(pysea, "#path_export", str(export_dir.resolve()))

    # ================================================================
    # 20. GENAUIGKEIT
    # ================================================================

    select_dcc_option(pysea, "#dropdown_acc_responses", "Relativ")
    set_value(pysea, "#i_acc_answers", "2")

    select_dcc_option(pysea, "#dropdown_acc_responses", "Absolut")
    set_value(pysea, "#i_acc_answers", "0.1")

    select_dcc_option(pysea, "#dropdown_acc_responses", "Exakt")

    # ================================================================
    # 21. PUNKTE
    # ================================================================

    set_value(pysea, "#i_points_per_gap", "1")
    set_value(pysea, "#i_points_per_selection", "2")

    # ================================================================
    # 22. NAVIGATION
    # ================================================================

    select_dcc_option(pysea, "#dd_navigation_mode", "Nicht linear")
    select_dcc_option(pysea, "#dd_navigation_mode", "Linear")
    select_dcc_option(
        pysea,
        "#dd_navigation_mode",
        "Linear mit Testwegsteuerung",
    )

    # ================================================================
    # 23. PUNKTABZUG
    # ================================================================

    set_checkbox(
        pysea,
        "#cb_use_point_deduction input",
        True,
    )

    wait_element(
        pysea,
        "#i_point_deduction_per_attempt",
        enabled=True,
    )

    set_value(pysea, "#i_point_deduction_per_attempt", "0.5")
    set_value(pysea, "#i_min_score_percentage", "40")

    # ================================================================
    # 24. ERWEITERTE EINSTELLUNGEN
    # ================================================================

    toggle_checkbox(pysea, "#cb_keep_responses input")

    set_value(pysea, "#i_pass_score_percentage", "40")
    set_value(pysea, "#i_feedback_correct_config", "Test bestanden")
    set_value(pysea, "#i_feedback_incorrect_config", "Test nicht bestanden")

    if pattern_count(pysea, type="b_remove_excel_file"):
        click_pattern(
            pysea,
            element_index=0,
            type="b_remove_excel_file",
        )

    # ================================================================
    # 25. TEST LADEN
    # ================================================================

    click(pysea, "#b_div_load_test")
    wait_element(pysea, "#path_load_test", enabled=True)

    test_json = os.environ.get("PYSEA_TEST_JSON")

    if test_json:
        test_json_path = Path(test_json)
        assert test_json_path.is_file()

        set_value(
            pysea,
            "#path_load_test",
            str(test_json_path.resolve()),
        )

        click(pysea, "#b_load_test")
        click(pysea, "#b_edit_test")

        WebDriverWait(
            pysea.driver,
            5,
            poll_frequency=0.05,
            ignored_exceptions=(StaleElementReferenceException,),
        ).until(
            lambda _: pattern_count(
                pysea,
                type="b-sektion-bearbeiten",
            ) > 0
        )
    else:
        # Ohne PYSEA_TEST_JSON ist der Laden-Button absichtlich nicht
        # nutzbar. Der Smoke-Test prüft hier nur, dass die Ansicht geöffnet
        # werden kann und kehrt anschließend zum Editor zurück.
        click(pysea, "#b_edit_test")

    # ================================================================
    # 26. AUFGABE LÖSCHEN
    # ================================================================

    wait_element(pysea, "#neue-sektion")

    task_count_before = pattern_count(
        pysea,
        type="b-aufgabe-bearbeiten",
    )

    if task_count_before > 1:
        click_pattern(
            pysea,
            element_index=-1,
            type="b-aufgabe-bearbeiten",
        )

        click(pysea, "#loeschen")

        WebDriverWait(
            pysea.driver,
            TIMEOUT,
            poll_frequency=0.05,
            ignored_exceptions=(StaleElementReferenceException,),
        ).until(
            lambda _: pattern_count(
                pysea,
                type="b-aufgabe-bearbeiten",
            ) == task_count_before - 1
        )

    # ================================================================
    # 27. EXPORT
    # ================================================================

    if os.environ.get("PYSEA_TEST_EXPORT") == "1":
        export_dir.mkdir(parents=True, exist_ok=True)

        click(pysea, "#configuration")
        set_value(pysea, "#path_export", str(export_dir.resolve()))
        click(pysea, "#b_export_test")


def _is_displayed(element) -> bool:
    try:
        return element.is_displayed()
    except StaleElementReferenceException:
        return False
