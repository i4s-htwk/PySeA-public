from types import SimpleNamespace

import pytest
from dash import html
from dash.exceptions import PreventUpdate

import frontend.components.edit.tables as module

from .conftest import find_by_id


class CellRef:
    def __init__(self, value):
        self.value = value

    def is_excel_cell(self):
        return True


def make_excel_table():
    area = SimpleNamespace(
        id="AREA_1",
        cell_tl=CellRef("A1"),
        cell_br=CellRef("B2"),
        cells=[],
    )
    return SimpleNamespace(
        id="TABLE_1",
        excel_file="a.xlsx",
        page="Sheet1",
        automatic_responses=True,
        list_areas=[area],
        create_excel_table=lambda _area_id: None,
    )


def test_render_excel_table_contains_file_and_page_dropdowns():
    layout = module.render_excel_table([make_excel_table()], [], 0, 0, ["a.xlsx"], "task_1")
    assert find_by_id(layout, {"type": "excel", "table": 0, "count_excel": 0})
    assert find_by_id(layout, {"type": "seite", "table": 0, "count_excel": 0})


def test_render_excel_table_marks_automatic_responses():
    layout = module.render_excel_table([make_excel_table()], [], 0, 0, ["a.xlsx"], "task_1")
    component_id = {"type": "b_automatic_responses", "table": 0, "count_excel": 0}
    checkbox = find_by_id(layout, component_id)[0]
    assert checkbox.value == ["true"]


def test_show_excel_table_returns_empty_div_when_preview_disabled():
    result = module.show_excel_table(None, make_excel_table(), [])
    assert isinstance(result, html.Div)
    assert result.children is None


def test_page_loader_rejects_missing_path(tmp_path):
    with pytest.raises(PreventUpdate):
        module.lade_seitenoptionen(str(tmp_path / "missing.xlsx"), False)


def test_render_tables_requires_callback_trigger(monkeypatch):
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered_id=None))
    with pytest.raises(PreventUpdate):
        module.render_tables(1, {}, {}, "TASK_1")
