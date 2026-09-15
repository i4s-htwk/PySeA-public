import os
from pathlib import Path

from dash import ALL, Input, Output, State, callback, ctx, dcc, html
from dash.exceptions import PreventUpdate

from backend.stores import StoreMatchings
from backend.stores.StoreGraphicalAssignment import StoreGraphicalAssignments


MATCHING_TYPE = "matching"
GRAPHICAL_TYPE = "graphical_assignment"


def get_images(store_images):
    if not store_images:
        return []
    return store_images.get("images", [])


def find_image(images, value):
    if value is None:
        return None

    value = str(value).strip()
    if not value:
        return None

    return next(
        (
            image
            for image in images
            if image.get("id") == value
            or image.get("href") == value
            or os.path.basename(str(image.get("href", ""))) == os.path.basename(value)
        ),
        None
    )


def image_value_to_path(images, value):
    """Löst eine Bild-ID oder einen Dateinamen in einen lokalen Asset-Pfad auf."""
    image = find_image(images, value)
    if image is None:
        return value

    return str(Path("assets") / image["href"])


def path_to_image_value(images, path):
    """Zeigt für gespeicherte Pfade möglichst wieder die Bild-ID an."""
    if not path:
        return ""

    image = find_image(images, path)
    if image is not None:
        return image["id"]

    file_name = os.path.basename(path)
    image = find_image(images, file_name)
    return image["id"] if image is not None else path


def image_preview(images, value, width="180px"):
    image = find_image(images, value)

    if image is None:
        return html.Div(
            "-",
            style={
                "marginLeft": "20px",
                "minWidth": width
            }
        )

    return html.Img(
        src=f"/assets/{image['href']}",
        style={
            "maxWidth": width,
            "maxHeight": "130px",
            "marginLeft": "20px",
            "objectFit": "contain"
        }
    )


def image_input_row(label, input_id, value, images, placeholder="Bild-ID, z. B. BILD_1"):
    return html.Div(
        [
            html.Div(label, style={"width": "170px"}),
            dcc.Input(
                id=input_id,
                type="text",
                value=value or "",
                placeholder=placeholder,
                debounce=True,
                style={"width": "300px"}
            ),
            image_preview(images, value)
        ],
        style={
            "display": "flex",
            "alignItems": "center",
            "marginBottom": "12px"
        }
    )


def get_assignment_type(current_obj, matchings, graphical_assignments):
    if graphical_assignments.get_item(current_obj) is not None:
        return GRAPHICAL_TYPE
    if matchings.get_matching(current_obj) is not None:
        return MATCHING_TYPE
    return None


def build_matching_layout(current_obj, matchings, images):
    matching = matchings.get_matching(current_obj)

    if matching is None:
        pairs = [("", "")]
    else:
        source_by_id = {
            choice.id: choice.text
            for choice in matching.source_choices
        }
        target_by_id = {
            choice.id: choice.text
            for choice in matching.target_choices
        }
        pairs = [
            (
                source_by_id.get(pair.source_id, ""),
                target_by_id.get(pair.target_id, "")
            )
            for pair in matching.correct_pairs
        ]
        if not pairs:
            pairs = [("", "")]

    return html.Div(
        [
            html.Div(
                "Gib Text oder die ID eines Bildes ein. Wird eine Bild-ID erkannt, "
                "erscheint rechts daneben eine Vorschau.",
                style={"marginBottom": "18px", "color": "#555"}
            ),
            html.Div(
                [
                    html.Div("Linkes Element", style={"width": "300px", "marginLeft": "10px"}),
                    html.Div("Rechtes Element", style={"width": "300px", "marginLeft": "30px"})
                ],
                style={"display": "flex", "marginBottom": "8px", "fontWeight": "bold"}
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.Input(
                                        id={"type": "i_matching_source", "index": index},
                                        type="text",
                                        value=source,
                                        placeholder="Text oder Bild-ID",
                                        debounce=True,
                                        style={"width": "300px"}
                                    ),
                                    image_preview(images, source, width="120px")
                                ],
                                style={"display": "flex", "alignItems": "center"}
                            ),
                            html.Div(
                                [
                                    dcc.Input(
                                        id={"type": "i_matching_target", "index": index},
                                        type="text",
                                        value=target,
                                        placeholder="Text oder Bild-ID",
                                        debounce=True,
                                        style={"width": "300px"}
                                    ),
                                    image_preview(images, target, width="120px")
                                ],
                                style={"display": "flex", "alignItems": "center", "marginLeft": "30px"}
                            )
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "marginBottom": "12px"
                        }
                    )
                    for index, (source, target) in enumerate(pairs)
                ]
            ),
            html.Button(
                "Neues Zuordnungspaar",
                id="b_new_matching_pair",
                n_clicks=0,
                style={"marginLeft": "10px", "marginTop": "5px"}
            ),
            dcc.Input(id="i_graphical_original", style={"display": "none"}),
            dcc.Input(id="i_graphical_mask", style={"display": "none"}),
            dcc.Input(id="i_graphical_correct", style={"display": "none"}),
            html.Button(id="b_new_graphical_wrong", style={"display": "none"})
        ]
    )


def build_graphical_layout(
    current_obj,
    graphical_assignments,
    images,
    wrong_count=None
):
    assignment = graphical_assignments.get_item(current_obj)

    original = path_to_image_value(images, assignment.original_image_path) if assignment else ""
    mask = path_to_image_value(images, assignment.mask_image_path) if assignment else ""
    correct = path_to_image_value(images, assignment.correct_image_path) if assignment else ""
    wrong = (
        [path_to_image_value(images, path) for path in assignment.wrong_image_paths]
        if assignment else [""]
    )
    if not wrong:
        wrong = [""]

    if wrong_count is None:
        wrong_count = len(wrong)

    wrong_count = max(1, wrong_count)

    while len(wrong) < wrong_count:
        wrong.append("")

    return html.Div(
        [
            html.Div(
                "Alle Bilder müssen bereits über den Bilderordner geladen worden sein und "
                "dieselbe Größe besitzen. Gib jeweils die Bild-ID an.",
                style={"marginBottom": "18px", "color": "#555"}
            ),
            image_input_row(
                "Originalbild:",
                "i_graphical_original",
                original,
                images
            ),
            image_input_row(
                "Maskenbild:",
                "i_graphical_mask",
                mask,
                images
            ),
            image_input_row(
                "Bild mit richtigen Inhalten:",
                "i_graphical_correct",
                correct,
                images
            ),
            html.Div(
                [
                    image_input_row(
                        "Falschbilder:" if index == 0 else "",
                        {"type": "i_graphical_wrong", "index": index},
                        value,
                        images
                    )
                    for index, value in enumerate(wrong)
                ]
            ),
            html.Button(
                "Weiteres Falschbild",
                id="b_new_graphical_wrong",
                n_clicks=0,
                style={"marginLeft": "170px", "marginTop": "5px"}
            ),
            html.Button(id="b_new_matching_pair", style={"display": "none"})
        ]
    )


def build_assignment_layout(
    current_obj,
    store_matchings,
    store_graphical_assignment,
    store_images,
    selected_type=None,
    wrong_count=None
):
    matchings = StoreMatchings.from_dict(store_matchings or {})
    graphical_assignments = StoreGraphicalAssignments.from_dict(
        store_graphical_assignment or {}
    )
    images = get_images(store_images)

    stored_type = get_assignment_type(
        current_obj,
        matchings,
        graphical_assignments
    )
    assignment_type = selected_type or stored_type

    if wrong_count is None:
        assignment = graphical_assignments.get_item(current_obj)
        wrong_count = max(
            1,
            len(assignment.wrong_image_paths)
            if assignment is not None
            else 1
        )

    # Eingabefelder werden nur angezeigt, wenn für den ausgewählten Typ
    # bereits eine Zuordnung angelegt wurde. Die reine Auswahl im Dropdown
    # zeigt daher zunächst nur den Hinzufügen-Button.
    if assignment_type == MATCHING_TYPE and stored_type == MATCHING_TYPE:
        content = build_matching_layout(current_obj, matchings, images)
    elif (
        assignment_type == GRAPHICAL_TYPE
        and stored_type == GRAPHICAL_TYPE
    ):
        content = build_graphical_layout(
            current_obj,
            graphical_assignments,
            images,
            wrong_count=wrong_count
        )
    else:
        content = html.Div([
            html.Button(id="b_new_matching_pair", style={"display": "none"}),
            dcc.Input(id="i_graphical_original", style={"display": "none"}),
            dcc.Input(id="i_graphical_mask", style={"display": "none"}),
            dcc.Input(id="i_graphical_correct", style={"display": "none"}),
            html.Button(id="b_new_graphical_wrong", style={"display": "none"})
        ])

    return html.Div(
        [
            html.Div(
                [
                    dcc.Dropdown(
                        id="dd_graphical_assignment_type",
                        options=[
                            {
                                "label": "Einfache Zuordnung (Matching)",
                                "value": MATCHING_TYPE
                            },
                            {
                                "label": "Grafische Zuordnung mit Bildausschnitten",
                                "value": GRAPHICAL_TYPE
                            }
                        ],
                        value=assignment_type,
                        placeholder="Zuordnungsart auswählen",
                        clearable=False,
                        style={"width": "330px"}
                    ),
                    html.Button(
                        "Zuordnung hinzufügen",
                        id="b_add_graphical_assignment",
                        n_clicks=0,
                        style={"width": "220px", "marginLeft": "10px"}
                    ),
                    html.Button(
                        "x",
                        id="b_delete_graphical_assignment",
                        n_clicks=0,
                        style={"marginLeft": "15px"}
                    )
                ],
                style={"display": "flex", "alignItems": "center", "marginBottom": "25px"}
            ),
            dcc.Store(
                id="graphical_wrong_count",
                data=(
                    wrong_count
                    if wrong_count is not None
                    else 1
                )
            ),
            content
        ],
        style={"marginLeft": "280px", "marginTop": "80px"}
    )


@callback(
    Output("div_graphical_assignment", "children"),
    Output("view_edit_item", "data", allow_duplicate=True),

    Input("b_graphical_assignment", "n_clicks"),

    State("store_matchings", "data"),
    State("store_graphical_assignment", "data"),
    State("store_images", "data"),
    State("store_current_obj", "data"),
    prevent_initial_call=True
)
def render_graphical_assignment(
    n_clicks,
    store_matchings,
    store_graphical_assignment,
    store_images,
    current_obj
):
    if not (ctx.triggered_id and n_clicks):
        raise PreventUpdate

    return (
        build_assignment_layout(
            current_obj,
            store_matchings,
            store_graphical_assignment,
            store_images
        ),
        "graphical_assignment"
    )


@callback(
    Output("store_matchings", "data", allow_duplicate=True),
    Output("store_graphical_assignment", "data", allow_duplicate=True),
    Output("div_graphical_assignment", "children", allow_duplicate=True),

    Input("dd_graphical_assignment_type", "value"),
    Input("b_add_graphical_assignment", "n_clicks"),
    Input("b_delete_graphical_assignment", "n_clicks"),
    Input("b_new_matching_pair", "n_clicks"),
    Input({"type": "i_matching_source", "index": ALL}, "value"),
    Input({"type": "i_matching_target", "index": ALL}, "value"),
    Input("i_graphical_original", "value"),
    Input("i_graphical_mask", "value"),
    Input("i_graphical_correct", "value"),
    Input({"type": "i_graphical_wrong", "index": ALL}, "value"),
    Input("b_new_graphical_wrong", "n_clicks"),

    State("store_matchings", "data"),
    State("store_graphical_assignment", "data"),
    State("store_images", "data"),
    State("store_current_obj", "data"),
    State("graphical_wrong_count", "data"),
    prevent_initial_call=True
)
def save_graphical_assignment(
    selected_type,
    add_clicks,
    delete_clicks,
    new_pair_clicks,
    source_values,
    target_values,
    original_value,
    mask_value,
    correct_value,
    wrong_values,
    new_wrong_clicks,
    store_matchings,
    store_graphical_assignment,
    store_images,
    current_obj,
    wrong_count
):
    if not ctx.triggered_id:
        raise PreventUpdate

    matchings = StoreMatchings.from_dict(store_matchings or {})
    graphical_assignments = StoreGraphicalAssignments.from_dict(
        store_graphical_assignment or {}
    )
    images = get_images(store_images)
    triggered_id = ctx.triggered_id

    if triggered_id == "b_delete_graphical_assignment" and delete_clicks:
        matchings.items.pop(current_obj, None)
        graphical_assignments.items.pop(current_obj, None)
        selected_type = None

    elif triggered_id == "b_add_graphical_assignment" and add_clicks:
        if selected_type == MATCHING_TYPE:
            graphical_assignments.items.pop(current_obj, None)
            if matchings.get_matching(current_obj) is None:
                matchings.add_item(current_obj)

        elif selected_type == GRAPHICAL_TYPE:
            matchings.items.pop(current_obj, None)
            if graphical_assignments.get_item(current_obj) is None:
                graphical_assignments.add_item(
                    current_obj,
                    original_image_path=image_value_to_path(images, original_value),
                    mask_image_path=image_value_to_path(images, mask_value),
                    correct_image_path=image_value_to_path(images, correct_value),
                    wrong_image_paths=[
                        image_value_to_path(images, value)
                        for value in (wrong_values or [])
                        if value
                    ]
                )

    elif triggered_id == "dd_graphical_assignment_type":
        # Der Typ wird zunächst nur in der Oberfläche gewechselt. Erst der
        # Button "Zuordnung hinzufügen" ersetzt eine vorhandene Zuordnung.
        pass

    elif selected_type == MATCHING_TYPE:
        matching = matchings.get_matching(current_obj)
        if matching is None:
            matching = matchings.add_item(current_obj)

        if triggered_id == "b_new_matching_pair" and new_pair_clicks:
            source_values = list(source_values or []) + [""]
            target_values = list(target_values or []) + [""]

        matching.source_choices.clear()
        matching.target_choices.clear()
        matching.correct_pairs.clear()

        for source, target in zip(source_values or [], target_values or []):
            matching.add_pair(source or "", target or "")

        matchings.update_item(current_obj, matching)

    elif selected_type == GRAPHICAL_TYPE:
        assignment = graphical_assignments.get_item(current_obj)

        if triggered_id == "b_new_graphical_wrong" and new_wrong_clicks:
            wrong_count = max(1, wrong_count or 1) + 1

        if assignment is None:
            assignment = graphical_assignments.add_item(
                current_obj,
                original_image_path=image_value_to_path(images, original_value),
                mask_image_path=image_value_to_path(images, mask_value),
                correct_image_path=image_value_to_path(images, correct_value)
            )

        assignment.original_image_path = image_value_to_path(images, original_value)
        assignment.mask_image_path = image_value_to_path(images, mask_value)
        assignment.correct_image_path = image_value_to_path(images, correct_value)
        assignment.wrong_image_paths = [
            image_value_to_path(images, value)
            for value in (wrong_values or [])
            if value
        ]
        graphical_assignments.update_item(current_obj, assignment)

    layout = build_assignment_layout(
        current_obj,
        matchings.to_dict(),
        graphical_assignments.to_dict(),
        store_images,
        selected_type=selected_type,
        wrong_count=wrong_count
    )

    return matchings.to_dict(), graphical_assignments.to_dict(), layout
