from types import SimpleNamespace

from dash import dcc

import frontend.components.edit.general as module

from .conftest import find_by_id, find_by_type


def test_render_point_distribution_contains_task_points():
    layout = module.render_point_distribution({"task": 5, "gap": 2})
    assert find_by_id(layout, "i_points_task")[0].value == 5


def test_render_point_distribution_contains_gap_points():
    layout = module.render_point_distribution({"task": 5, "gap": 2})
    assert find_by_id(layout, "i_points_per_gap_tasks")[0].value == 2


def test_render_variant_dependent_images_empty_has_no_inputs():
    layout = module.render_variant_dependent_images([])
    assert find_by_type(layout, dcc.Input) == []


def test_render_variant_dependent_images_creates_inputs():
    image = SimpleNamespace(
        id="V_BILD_1",
        images={
            "entry_1": {
                "image_id": "BILD_1",
                "lower": 1,
                "upper": 3,
            }
        },
    )
    layout = module.render_variant_dependent_images([image])
    image_id = {"type": "vdi_image_id", "vdi": 0, "image": "entry_1"}
    assert find_by_id(layout, image_id)[0].value == "BILD_1"


def test_render_variant_dependent_tables_empty_has_no_inputs():
    layout = module.render_variant_dependent_tables([])
    assert find_by_type(layout, dcc.Input) == []


def test_render_variant_dependent_content_contains_type_dropdown():
    current = SimpleNamespace(
        variant_dependent_images=[],
        variant_dependent_tables=[],
    )
    layout = module.render_variant_dependent_content(current)
    dropdown = find_by_id(layout, "dd_variant_dependent_content_type")[0]
    assert dropdown.options == ["Bild", "Tabelle"]


def test_render_variant_dependent_table_creates_inputs():
    table = SimpleNamespace(
        id="V_TABLE_1",
        tables={
            "entry_1": {
                "table_id": "TABLE_1",
                "lower": 2,
                "upper": 4,
            }
        },
    )
    layout = module.render_variant_dependent_tables([table])
    table_id = {"type": "vdt_table_id", "vdt": 0, "table": "entry_1"}
    assert find_by_id(layout, table_id)[0].value == "TABLE_1"
