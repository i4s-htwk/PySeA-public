import pytest

from frontend.components.edit.layout import (
    container_edit_item,
    container_task_editor,
    layout_manager as edit_layout_manager,
    render_edit_section,
    render_edit_task,
)

from .conftest import find_by_id, ids


def test_task_editor_contains_all_content_areas():
    assert set(ids(container_task_editor)) >= {
        "container_task_editor", "div_general", "div_answers", "div_tables",
        "div_selection", "div_feedback", "div_variables",
    }


def test_edit_item_contains_menu_and_editor():
    assert find_by_id(container_edit_item, "div_menu_edit_item")
    assert find_by_id(container_edit_item, "container_task_editor")


def test_task_menu_contains_expected_buttons():
    layout = render_edit_task()
    assert set(ids(layout)) >= {"b_general", "b_answers", "b_tables", "b_selections", "b_feedback"}


def test_section_menu_contains_expected_buttons():
    layout = render_edit_section()
    assert set(ids(layout)) >= {"b_general", "b_excel_variables", "b_tables"}


@pytest.mark.parametrize(
    ("state", "visible_index"),
    [
        ("answers", 0),
        ("feedback", 1),
        ("tables", 2),
        ("general", 3),
        ("selection", 4),
        ("graphical_assignment", 5),
        ("variables", 6),
    ],
)
def test_layout_manager_shows_only_selected_area(state, visible_index):
    styles = edit_layout_manager(state)

    assert styles[visible_index] == {"display": "block"}

    for index, style in enumerate(styles):
        if index != visible_index:
            assert style == {"display": "none"}

def test_layout_manager_hides_all_for_unknown_state():
    assert all(style == {"display": "none"} for style in edit_layout_manager("unknown"))
