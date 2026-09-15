from dash import Output, Input, State, callback, html, dcc
from dash.exceptions import PreventUpdate

from backend.TestStructure import TestStructure
from backend.stores import TestStore
from frontend.components.teststructure.layout import (
    control_bar,
    get_stack_content,
    variants,
    load_images,
    testconfig
)


@callback(
    Output(
        "container_sidebar",
        "children",
        allow_duplicate=True
    ),

    Output(
        "div_edit_test",
        "style",
        allow_duplicate=True
    ),

    Output(
        "div_load_test",
        "style",
        allow_duplicate=True
    ),

    Input(
        "b_edit_test",
        "n_clicks"
    ),

    State(
        "store_teststructure",
        "data"
    ),

    prevent_initial_call=True
)
def edit_test(n_clicks, data):
    teststructure_obj = TestStructure.from_dict(
        data or {}
    )

    sidebar_children = html.Div(
        children=[
            html.Div(
                children=[
                    control_bar,
                    get_stack_content(
                        teststructure_obj.list,
                        teststructure_obj.get_object
                    )
                ],
                style={
                    "overflowY": "auto",
                    "flex": "1"
                }
            ),

            variants,
            load_images,
            testconfig
        ],
        style={
            "position": "fixed",
            "top": "50px",
            "left": "0",
            "width": "250px",
            "backgroundColor": "#f0f0f0",
            "zIndex": 1000,
            "height": "calc(100vh - 60px)",
            "display": "flex",
            "flexDirection": "column",
            "boxShadow": (
                "0 2px 4px rgba(0, 0, 0, 0.3)"
            )
        }
    )

    return (
        sidebar_children,
        {"display": "block"},
        {"display": "none"}
    )


@callback(
    Output(
        "div_load_test",
        "children",
        allow_duplicate=True
    ),

    Output(
        "div_load_test",
        "style",
        allow_duplicate=True
    ),

    Output(
        "div_edit_test",
        "style",
        allow_duplicate=True
    ),

    Input(
        "b_div_load_test",
        "n_clicks"
    ),

    prevent_initial_call=True
)
def div_load_test(n_clicks):
    if not n_clicks:
        raise PreventUpdate

    div_load = html.Div(
        children=[
            dcc.Input(
                id="path_load_test",
                type="text",
                placeholder="Pfad zum Test",
                style={
                    "width": "500px"
                }
            ),

            html.Button(
                "Test laden",
                id="b_load_test",
                n_clicks=0,
                style={
                    "marginLeft": "20px"
                }
            )
        ],
        style={
            "padding": "10px"
        }
    )

    return (
        div_load,
        {"display": "block"},
        {"display": "none"}
    )


@callback(
    Output(
        "store_teststructure",
        "data",
        allow_duplicate=True
    ),

    Output(
        "store_item_body",
        "data",
        allow_duplicate=True
    ),

    Output(
        "store_images",
        "data",
        allow_duplicate=True
    ),

    Output(
        "store_responses",
        "data",
        allow_duplicate=True
    ),

    Output(
        "store_tables",
        "data",
        allow_duplicate=True
    ),

    Output(
        "store_feedback",
        "data",
        allow_duplicate=True
    ),

    Output(
        "store_selections",
        "data",
        allow_duplicate=True
    ),

    Output(
        "store_matchings",
        "data",
        allow_duplicate=True
    ),

    Output(
        "store_graphical_assignment",
        "data",
        allow_duplicate=True
    ),

    Output(
        "store_configurations",
        "data",
        allow_duplicate=True
    ),

    Output(
        "store_variants",
        "data",
        allow_duplicate=True
    ),

    Input(
        "b_load_test",
        "n_clicks"
    ),

    State(
        "path_load_test",
        "value"
    ),

    prevent_initial_call=True
)
def load_test(n_clicks, path_file):
    if not n_clicks:
        raise PreventUpdate

    test_store = TestStore.load_test(
        path_file
    )

    return (
        test_store.test_structure.to_dict(),
        test_store.store_item_body.items,
        test_store.store_images.to_dict(),
        test_store.store_responses.to_dict(),
        test_store.store_tables.to_dict(),
        test_store.store_feedback.to_dict(),
        test_store.store_selections.to_dict(),
        test_store.store_matchings.to_dict(),
        test_store.store_graphical_assignment.to_dict(),
        test_store.store_configurations.to_dict(),
        test_store.store_variants.to_dict()
    )


@callback(
    Input("b_export_test", "n_clicks"),
    State("store_teststructure", "data"),
    State("store_item_body", "data"),
    State("store_images", "data"),
    State("store_responses", "data"),
    State("store_tables", "data"),
    State("store_selections", "data"),
    State("store_matchings", "data"),
    State("store_graphical_assignment", "data"),
    State("store_feedback", "data"),
    State("store_configurations", "data"),
    State("store_variants", "data"),

    prevent_initial_call=True)
def test_erstellen(n_clicks, store_test_structure, store_item_body, store_images, store_responses, store_tables, store_selections, store_matchings, store_graphical_assignment, store_feedback, store_configurations, store_variants):
    if not n_clicks:
        raise PreventUpdate

    data = {
        "test_structure": (
            store_test_structure
        ),
        "store_item_body": (
            store_item_body
        ),
        "store_images": (
            store_images
        ),
        "store_responses": (
            store_responses
        ),
        "store_tables": (
            store_tables
        ),
        "store_selections": (
            store_selections
        ),
        "store_matchings": (
            store_matchings
        ),
        "store_graphical_assignment": (
            store_graphical_assignment
        ),
        "store_feedback": (
            store_feedback
        ),
        "store_configurations": (
            store_configurations
        ),
        "store_variants": (
            store_variants
        )
    }

    test_store = TestStore.from_dict(
        data
    )

    test_store.create_test(
        store_configurations["path_export"]
    )