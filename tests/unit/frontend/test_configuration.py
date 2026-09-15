from types import SimpleNamespace

from frontend.components.teststructure.configuration import (
    render_advanced_settings,
    render_answers_acc,
    render_feedback,
    render_point_deduction,
    render_point_distribution,
)

from .conftest import find_by_id


def test_answer_accuracy_relative_uses_percent_unit():
    obj = SimpleNamespace(selection="relative", relative=10, absolute=2)
    layout = render_answers_acc(obj)
    assert find_by_id(layout, "dropdown_acc_responses")[0].value == "relative"
    assert find_by_id(layout, "i_acc_answers")[0].value == 10


def test_answer_accuracy_absolute_uses_absolute_value():
    obj = SimpleNamespace(selection="absolute", relative=10, absolute=2)
    assert find_by_id(render_answers_acc(obj), "i_acc_answers")[0].value == 2


def test_point_deduction_disabled_hides_inputs():
    obj = SimpleNamespace(is_used=False, point_deduction_per_attempt=1, min_score_percentage=50)
    layout = render_point_deduction(obj)
    assert find_by_id(layout, "i_point_deduction_per_attempt")[0].style["display"] == "none"


def test_point_deduction_enabled_populates_inputs():
    obj = SimpleNamespace(is_used=True, point_deduction_per_attempt=1, min_score_percentage=50)
    layout = render_point_deduction(obj)
    assert find_by_id(layout, "i_point_deduction_per_attempt")[0].value == 1
    assert find_by_id(layout, "i_min_score_percentage")[0].value == 50


def test_point_distribution_uses_values():
    layout = render_point_distribution({"gap": 2, "selection": 3})
    assert find_by_id(layout, "i_points_per_gap")[0].value == 2
    assert find_by_id(layout, "i_points_per_selection")[0].value == 3


def test_advanced_settings_uses_navigation_and_keep_responses():
    obj = SimpleNamespace(navigation_mode="linear", keep_responses=True)
    layout = render_advanced_settings(obj)
    assert find_by_id(layout, "dd_navigation_mode")[0].value == "linear"
    assert find_by_id(layout, "cb_keep_responses")[0].value == ["true"]


def test_configuration_feedback_populates_fields():
    feedback = {
        "feedback_correct": SimpleNamespace(value="bestanden"),
        "feedback_incorrect": SimpleNamespace(value="nicht bestanden"),
    }
    layout = render_feedback(feedback, 60)
    assert find_by_id(layout, "i_pass_score_percentage")[0].value == 60
    assert find_by_id(layout, "i_feedback_correct_config")[0].value == "bestanden"
