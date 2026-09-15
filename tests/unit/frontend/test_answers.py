from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from dash import dcc, html
from dash.exceptions import PreventUpdate

import frontend.components.edit.answers as module
from frontend.components.edit.answers import render_excel_responses, render_responses

from .conftest import find_by_id, find_by_type


def test_render_responses_empty_still_contains_add_button():
    layout = render_responses([])
    assert find_by_id(layout, "b_new_response")


def test_render_responses_creates_one_input_per_answer():
    responses = [SimpleNamespace(id="RESPONSE_1", value="4"), SimpleNamespace(id="RESPONSE_2", value="5")]
    layout = render_responses(responses)
    inputs = [c for c in find_by_type(layout, dcc.Input) if isinstance(c.id, dict) and c.id.get("type") == "answer"]
    assert [c.value for c in inputs] == ["4", "5"]


def test_render_responses_creates_remove_button_per_answer():
    layout = render_responses([SimpleNamespace(id="RESPONSE_1", value="4")])
    assert find_by_id(layout, {"type": "b_remove_answer", "index": 0})


def test_render_excel_responses_inactive_contains_initialization_button():
    layout = render_excel_responses(None, [])
    assert find_by_id(layout, "b_initialize_excel_responses")
    assert find_by_id(layout, "b_new_excel_response")[0].style["display"] == "none"


def test_render_excel_responses_builds_file_options_from_paths():
    excel = SimpleNamespace(responses=[], page=None, excel_file=None, answer_acc_from_excel=False)
    layout = render_excel_responses(excel, ["/tmp/a.xlsx", "/tmp/b.xlsx", ""])
    dropdown = find_by_id(layout, "excel")[0]
    assert dropdown.options == [
        {"label": "a.xlsx", "value": "/tmp/a.xlsx"},
        {"label": "b.xlsx", "value": "/tmp/b.xlsx"},
    ]


def test_render_excel_responses_uses_existing_page_as_option():
    excel = SimpleNamespace(responses=[], page="Tabelle1", excel_file="a.xlsx", answer_acc_from_excel=False)
    page = find_by_id(render_excel_responses(excel, ["a.xlsx"]), "page")[0]
    assert page.options == [{"label": "Tabelle1", "value": "Tabelle1"}]


def test_render_excel_responses_marks_accuracy_checkbox():
    excel = SimpleNamespace(responses=[], page=None, excel_file=None, answer_acc_from_excel=True)
    checkbox = find_by_id(render_excel_responses(excel, []), "cb_acc_from_excel")[0]
    assert checkbox.value == ["true"]


def test_load_pages_rejects_missing_path(tmp_path):
    with pytest.raises(PreventUpdate):
        module.lade_seitenoptionen(str(tmp_path / "missing.xlsx"), False)


def test_load_pages_reads_sheet_names(tmp_path):
    from openpyxl import Workbook
    path = tmp_path / "book.xlsx"
    wb = Workbook()
    wb.active.title = "A"
    wb.create_sheet("B")
    wb.save(path)
    assert module.lade_seitenoptionen(str(path), False) == [
        {"label": "A", "value": "A"}, {"label": "B", "value": "B"}
    ]


def test_render_answers_requires_trigger(monkeypatch):
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered_id=None))
    with pytest.raises(PreventUpdate):
        module.render_answers(1, {}, {}, "TASK_1")
