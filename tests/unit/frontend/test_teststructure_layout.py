from types import SimpleNamespace

import pytest

from frontend.components.teststructure.layout import (
    container_sidebar,
    get_stack_content,
    layout_manager as structure_layout_manager,
)

from .conftest import find_by_id, ids


def make_structure():
    task1 = SimpleNamespace(id="TASK_1", title="Aufgabe 1")
    task2 = SimpleNamespace(id="TASK_2", title="Aufgabe 2")
    section = SimpleNamespace(id="SECTION_1", title="Sektion 1", list_tasks=[task1, task2])
    return [section]


def test_stack_contains_section_and_tasks():
    layout = get_stack_content(make_structure(), None)
    assert "div_teststructure" in ids(layout)
    assert find_by_id(layout, {"type": "b-sektion-bearbeiten", "index": "SECTION_1"})
    assert find_by_id(layout, {"type": "b-aufgabe-bearbeiten", "index": "TASK_1"})


def test_stack_marks_current_section_bold():
    button = find_by_id(get_stack_content(make_structure(), "SECTION_1"), {"type": "b-sektion-bearbeiten", "index": "SECTION_1"})[0]
    assert button.style["fontWeight"] == "bold"


def test_stack_marks_current_task_bold():
    button = find_by_id(get_stack_content(make_structure(), "TASK_2"), {"type": "b-aufgabe-bearbeiten", "index": "TASK_2"})[0]
    assert button.style["fontWeight"] == "bold"


def test_sidebar_contains_hidden_control_buttons():
    assert set(ids(container_sidebar)) >= {"loeschen", "neue-aufgabe", "neue-sektion", "configuration", "load_images", "b_variants"}


@pytest.mark.parametrize(("state", "index"), [("config", 0), ("edit_item", 1), ("images", 2), ("variants", 3)])
def test_structure_layout_manager(state, index):
    styles = structure_layout_manager(state)
    assert styles[index] == {"display": "block"}
    assert all(s == {"display": "none"} for i, s in enumerate(styles) if i != index)
