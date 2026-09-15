from types import SimpleNamespace

import pytest
from dash import dcc

import frontend.components.teststructure.variants as module

from .conftest import find_by_id, find_by_type


def test_assignment_options_cover_three_modes():
    assert {o["value"] for o in module.ASSIGNMENT_OPTIONS} == {
        "variable_dependent_assignment", "manual_assignment", "student_id_to_variant_assignment"
    }


def test_get_assignment_value_unknown_returns_none():
    assert module.get_assignment_value(None) is None


def test_get_triggered_value_without_trigger_returns_none(monkeypatch):
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered=[]))
    assert module.get_triggered_value() is None


def test_get_triggered_value_returns_first_value(monkeypatch):
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered=[{"value": 7}]))
    assert module.get_triggered_value() == 7


def test_render_conditions_empty_contains_add_button():
    layout = module.render_conditions([], "VARIABLE_1", 0)
    assert find_by_id(layout, {"type": "b_new_condition", "index": 0})


def test_render_conditions_populates_bounds_and_values():
    condition = SimpleNamespace(lower_bound=1, upper_bound=9, values={"A": 3})
    layout = module.render_conditions([condition], "VARIABLE_1", 0)
    assert find_by_id(layout, {"type": "i_condition_lower_bound", "variable": 0, "index": 0})[0].value == 1
    assert find_by_id(layout, {"type": "i_condition_upper_bound", "variable": 0, "index": 0})[0].value == 9
    assert find_by_id(layout, {"type": "i_condition_value", "variable": 0, "index": 0, "key": "A"})[0].value == 3


def test_render_variables_empty_contains_new_variable_button():
    assert find_by_id(module.render_variables([]), "b_new_variable")


def test_render_variables_creates_name_inputs():
    variable = SimpleNamespace(id="VARIABLE_1", value_response=0, variables=["x", "y"], list_conditions=[])
    layout = module.render_variables([variable])
    names = [c for c in find_by_type(layout, dcc.Input) if isinstance(c.id, dict) and c.id.get("type") == "i_variable_name"]
    assert [c.value for c in names] == ["x", "y"]


def test_render_manual_uses_variant_count():
    assignment = SimpleNamespace(get_count_variants=lambda: 4)
    assert find_by_id(module.render_manual(assignment), "i_count_variants")[0].value == 4


def test_render_feedback_defaults_to_empty_strings():
    layout = module.render_feedback({})
    assert find_by_id(layout, "i_feedback_correct_variants")[0].value == ""
    assert find_by_id(layout, "i_feedback_incorrect_variants")[0].value == ""
