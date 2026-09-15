from dash import Output, Input, State, callback, html, dcc, ALL, ctx
from dash.exceptions import PreventUpdate

from backend.stores import StoreVariants
from backend.utils.Variants.ManualAssignment import ManualAssignment
from backend.utils.Variants.StudentIdToVariantAssignment import (
    StudentIdToVariantAssignment,
)
from backend.utils.Variants.VariableDependentAssignment.VariableDependentAssignment import (
    VariableDependentAssignment,
)


ASSIGNMENT_OPTIONS = [
    {
        "label": "Matrikelnummer + Variablen",
        "value": "variable_dependent_assignment",
    },
    {
        "label": "Manuell",
        "value": "manual_assignment",
    },
    {
        "label": "Automatisch über Matrikelnummer",
        "value": "student_id_to_variant_assignment",
    },
]


def get_assignment_value(assignment):
    """Liefert den Dropdown-Wert für die aktuelle Vergabeart."""

    if isinstance(assignment, VariableDependentAssignment):
        return "variable_dependent_assignment"

    if isinstance(assignment, ManualAssignment):
        return "manual_assignment"

    if isinstance(assignment, StudentIdToVariantAssignment):
        return "student_id_to_variant_assignment"

    return None


def get_triggered_value():
    """Liefert den Wert der Komponente, die den Callback ausgelöst hat."""

    if not ctx.triggered:
        return None

    triggered_entry = ctx.triggered[0]

    if not isinstance(triggered_entry, dict):
        return None

    return triggered_entry.get("value")


def update_assignment_variants(assignment):
    """Aktualisiert die Varianten, sofern die Vergabeart dies unterstützt."""

    if isinstance(assignment, VariableDependentAssignment):
        assignment.update_variants()


def render_conditions(list_conditions, variable_id, variable_index):
    condition_divs = []

    for condition_index, condition in enumerate(list_conditions):
        value_inputs = []

        for key, value in sorted(condition.values.items()):
            value_inputs.append(
                html.Div(
                    [
                        html.Span(
                            f"{key}: ",
                            style={"marginRight": "5px"},
                        ),
                        dcc.Input(
                            id={
                                "type": "i_condition_value",
                                "variable": variable_index,
                                "index": condition_index,
                                "key": key,
                            },
                            value=value,
                            type="number",
                            style={
                                "width": "100px",
                                "marginRight": "5px",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "marginBottom": "5px",
                    },
                )
            )

        condition_divs.append(
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Input(
                                id={
                                    "type": "i_condition_lower_bound",
                                    "variable": variable_index,
                                    "index": condition_index,
                                },
                                value=condition.lower_bound,
                                type="number",
                                style={"width": "70px"},
                            ),
                            html.Span(
                                f" ≤ {variable_id} ≤ ",
                                style={"margin": "0 5px"},
                            ),
                            dcc.Input(
                                id={
                                    "type": "i_condition_upper_bound",
                                    "variable": variable_index,
                                    "index": condition_index,
                                },
                                value=condition.upper_bound,
                                type="number",
                                style={"width": "70px"},
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                        },
                    ),
                    html.Div(
                        value_inputs,
                        style={"marginLeft": "50px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "flex-start",
                    "marginBottom": "10px",
                },
            )
        )

    condition_divs.append(
        html.Button(
            "Neue Bedingung",
            id={
                "type": "b_new_condition",
                "index": variable_index,
            },
            style={
                "width": "250px",
                "padding": "0",
            },
        )
    )

    return html.Div(
        condition_divs,
        style={"marginLeft": "100px"},
    )


def render_variables(list_variables):
    variable_divs = []

    for variable_index, variable in enumerate(list_variables):
        variable_name_inputs = []

        for name_index, name in enumerate(variable.variables):
            variable_name_inputs.append(
                dcc.Input(
                    id={
                        "type": "i_variable_name",
                        "index": variable_index,
                        "name_index": name_index,
                    },
                    value=name,
                    type="text",
                    style={
                        "width": "190px",
                        "marginTop": "10px",
                    },
                )
            )

        variable_divs.append(
            html.Div(
                [
                    html.Button(
                        "×",
                        id={
                            "type": "b_delete_variable",
                            "index": variable_index,
                        },
                        title="Variable löschen",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        f"{variable.id} = {{RESPONSE}}["
                                    ),
                                    dcc.Input(
                                        id={
                                            "type": "i_variable_value_response",
                                            "index": variable_index,
                                        },
                                        value=variable.value_response,
                                        type="number",
                                        min=0,
                                        step=1,
                                        style={"width": "60px"},
                                    ),
                                    html.Span("]"),
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                },
                            ),
                            html.Div(
                                variable_name_inputs,
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                },
                            ),
                            html.Button(
                                "Neue Wertzuweisung",
                                id={
                                    "type": "b_new_dependent_variable",
                                    "index": variable_index,
                                },
                                style={
                                    "width": "250px",
                                    "padding": "0",
                                    "marginTop": "10px",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                        },
                    ),
                    render_conditions(
                        variable.list_conditions or [],
                        variable.id,
                        variable_index,
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "flex-start",
                    "marginBottom": "25px",
                },
            )
        )

    variable_divs.append(
        html.Button(
            "Neue Variable",
            id="b_new_variable",
            style={
                "width": "250px",
                "padding": "0",
            },
        )
    )

    return html.Div(
        variable_divs,
        style={
            "border": "0.5px solid black",
            "padding": "20px",
            "width": "100%",
        },
    )


def render_manual(assignment):
    count_variants_input = dcc.Input(
        id="i_count_variants",
        value=assignment.get_count_variants(),
        type="number",
        min=1,
        step=1,
    )

    return html.Div(
        count_variants_input,
        style={
            "border": "0.5px solid black",
            "padding": "20px",
            "width": "100%",
        },
    )


def render_variants_div(variants):
    variants_div = []

    for variant_index, combination in enumerate(
        variants.assignment.list_variants
    ):
        condition_elements = []

        for condition in combination:
            for key, value in sorted(condition.values.items()):
                condition_elements.append(
                    html.Div(
                        f"{key} = {value}",
                        style={"marginRight": "10px"},
                    )
                )

        variants_div.append(
            html.Div(
                [
                    html.Div(
                        f"Variante_{variant_index + 1}",
                        style={
                            "marginRight": "80px",
                            "minWidth": "100px",
                        },
                    ),
                    html.Div(
                        condition_elements,
                        style={
                            "display": "flex",
                            "gap": "10px",
                            "flexWrap": "wrap",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "marginBottom": "15px",
                },
            )
        )

    return html.Div(
        variants_div,
        style={
            "border": "0.5px solid black",
            "padding": "20px",
            "width": "100%",
        },
    )


def render_feedback(feedback):
    feedback = feedback or {}

    feedback_correct = feedback.get("feedback_correct")
    feedback_incorrect = feedback.get("feedback_incorrect")

    correct_value = (
        feedback_correct.value
        if feedback_correct is not None
        else ""
    )

    incorrect_value = (
        feedback_incorrect.value
        if feedback_incorrect is not None
        else ""
    )

    return html.Div(
        [
            html.Div(
                [
                    html.H4(
                        "Feedback korrekt",
                        style={
                            "marginTop": "0",
                            "minWidth": "180px",
                        },
                    ),
                    dcc.Textarea(
                        id="i_feedback_correct_variants",
                        value=correct_value,
                        style={
                            "width": "100%",
                            "height": 100,
                            "resize": "vertical",
                            "fontSize": 16,
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "marginBottom": "20px",
                },
            ),
            html.Div(
                [
                    html.H4(
                        "Feedback falsch",
                        style={
                            "marginTop": "0",
                            "minWidth": "180px",
                        },
                    ),
                    dcc.Textarea(
                        id="i_feedback_incorrect_variants",
                        value=incorrect_value,
                        style={
                            "width": "100%",
                            "height": 100,
                            "resize": "vertical",
                            "fontSize": 16,
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "row",
                },
            ),
        ],
        style={
            "border": "0.5px solid black",
            "padding": "20px",
            "width": "100%",
        },
    )


@callback(
    Output("div_variants", "children"),
    Output("view_edit", "data"),
    Input("b_variants", "n_clicks"),
    State("store_variants", "data"),
    prevent_initial_call=True,
)
def edit_variants(n_clicks, store_variants):
    if not n_clicks:
        raise PreventUpdate

    variants = StoreVariants.from_dict(store_variants or {})

    assignment_value = get_assignment_value(variants.assignment)

    assignment_dropdown = dcc.Dropdown(
        id="dd_assignment",
        options=ASSIGNMENT_OPTIONS,
        value=assignment_value,
        placeholder="Vergabeart auswählen",
        clearable=False,
        style={"width": "280px"},
    )

    use_variants_checkbox = dcc.Checklist(
        id="cb_use_variants",
        options=[
            {
                "label": "Variantenabhängigen Test erstellen",
                "value": "use",
            }
        ],
        value=["use"] if variants.use_variants else [],
    )

    header = html.Div(
        [
            html.Div(
                [
                    html.H4(
                        "Art der Variantenvergabe:",
                        style={"paddingRight": "20px"},
                    ),
                    assignment_dropdown,
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "marginTop": "20px",
                },
            ),
            use_variants_checkbox,
        ]
    )

    if not variants.use_variants:
        return (
            html.Div(
                [
                    header,

                    # Platzhalter für Callback-Komponenten
                    dcc.Input(
                        id="i_variants_title",
                        style={"display": "none"},
                    ),
                    dcc.Textarea(
                        id="i_variants_text",
                        style={"display": "none"},
                    ),
                    html.Button(
                        id="b_new_variable",
                        style={"display": "none"},
                    ),
                    dcc.Textarea(
                        id="i_feedback_incorrect_variants",
                        style={"display": "none"},
                    ),
                    dcc.Textarea(
                        id="i_feedback_correct_variants",
                        style={"display": "none"},
                    ),
                    dcc.Input(
                        id="i_count_variants",
                        style={"display": "none"},
                    ),
                ],
                style={
                    "marginLeft": "260px",
                    "paddingLeft": "20px",
                },
            ),
            "variants",
        )

    assignment_content = html.Div()
    hidden_elements = []

    if isinstance(
        variants.assignment,
        VariableDependentAssignment,
    ):
        assignment_content = html.Div(
            [
                html.Div(
                    [
                        html.H4(
                            "Variablen",
                            style={
                                "marginTop": 0,
                                "marginRight": "35px",
                            },
                        ),
                        render_variables(
                            variants.assignment.list_variables or []
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "flex-start",
                        "marginBottom": "20px",
                    },
                ),
                html.Div(
                    [
                        html.H4(
                            "Varianten",
                            style={
                                "marginTop": 0,
                                "marginRight": "35px",
                            },
                        ),
                        render_variants_div(variants),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "flex-start",
                        "marginBottom": "20px",
                    },
                ),
            ]
        )

        hidden_elements.append(
            dcc.Input(
                id="i_count_variants",
                style={"display": "none"},
            )
        )

    elif isinstance(
        variants.assignment,
        (ManualAssignment, StudentIdToVariantAssignment),
    ):
        assignment_content = html.Div(
            [
                html.H4(
                    "Anzahl Varianten",
                    style={
                        "marginTop": 0,
                        "marginRight": "15px",
                    },
                ),
                render_manual(variants.assignment),
            ],
            style={
                "display": "flex",
                "alignItems": "flex-start",
                "marginBottom": "20px",
            },
        )

        # Nur diese Komponente fehlt bei manueller Vergabe.
        hidden_elements.append(
            html.Button(
                id="b_new_variable",
                style={"display": "none"},
            )
        )

    return (
        html.Div(
            [
                header,
                html.Div(
                    [
                        html.H3(
                            "Titel der Variantenaufgabe",
                            style={
                                "marginRight": "10px",
                                "minWidth": "180px",
                            },
                        ),
                        dcc.Input(
                            id="i_variants_title",
                            type="text",
                            placeholder="Titel",
                            value=variants.title or "",
                            style={"width": "300px"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "marginBottom": "20px",
                    },
                ),
                html.Div(
                    [
                        html.H4(
                            "Fragenkörper",
                            style={
                                "marginTop": 0,
                                "marginRight": "10px",
                                "minWidth": "180px",
                            },
                        ),
                        dcc.Textarea(
                            id="i_variants_text",
                            value=variants.item_body or "",
                            style={
                                "width": "100%",
                                "height": 300,
                                "resize": "vertical",
                                "fontSize": 16,
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "flex-start",
                        "marginBottom": "20px",
                    },
                ),
                assignment_content,
                html.Div(
                    [
                        html.H4(
                            "Feedback",
                            style={
                                "marginTop": 0,
                                "marginRight": "35px",
                            },
                        ),
                        render_feedback(variants.feedback),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "flex-start",
                        "marginBottom": "20px",
                    },
                ),
                *hidden_elements,
            ],
            style={
                "marginLeft": "260px",
                "paddingLeft": "20px",
            },
        ),
        "variants",
    )


@callback(
    Output(
        "variants_is_saved",
        "data",
        allow_duplicate=True,
    ),
    Output(
        "div_variants",
        "children",
        allow_duplicate=True,
    ),
    Input("variants_is_saved", "data"),
    State("store_variants", "data"),
    prevent_initial_call=True,
)
def rerender_variants(is_saved, store_variants):
    if not ctx.triggered_id or not is_saved:
        raise PreventUpdate

    layout, _ = edit_variants(1, store_variants)

    return False, layout


@callback(
    Output(
        "store_variants",
        "data",
        allow_duplicate=True,
    ),
    Output(
        "variants_is_saved",
        "data",
        allow_duplicate=True,
    ),

    Input("cb_use_variants", "value"),
    Input("dd_assignment", "value"),

    Input("i_variants_title", "value"),
    Input("i_variants_text", "value"),

    Input("b_new_variable", "n_clicks"),
    Input(
        {
            "type": "b_delete_variable",
            "index": ALL,
        },
        "n_clicks",
    ),

    Input("i_count_variants", "value"),

    Input(
        {
            "type": "i_variable_value_response",
            "index": ALL,
        },
        "value",
    ),
    Input(
        {
            "type": "b_new_condition",
            "index": ALL,
        },
        "n_clicks",
    ),
    Input(
        {
            "type": "b_new_dependent_variable",
            "index": ALL,
        },
        "n_clicks",
    ),
    Input(
        {
            "type": "i_variable_name",
            "index": ALL,
            "name_index": ALL,
        },
        "value",
    ),
    Input(
        {
            "type": "i_condition_value",
            "variable": ALL,
            "index": ALL,
            "key": ALL,
        },
        "value",
    ),
    Input(
        {
            "type": "i_condition_lower_bound",
            "variable": ALL,
            "index": ALL,
        },
        "value",
    ),
    Input(
        {
            "type": "i_condition_upper_bound",
            "variable": ALL,
            "index": ALL,
        },
        "value",
    ),

    Input("i_feedback_correct_variants", "value"),
    Input("i_feedback_incorrect_variants", "value"),

    State("store_variants", "data"),
    prevent_initial_call=True,
)
def save_variants(
    use_variants,
    assignment_type,
    title,
    item_body,
    new_variable,
    delete_variable,
    count_variants,
    variable_value_response,
    new_condition,
    new_dependent_variable,
    variable_names,
    condition_values,
    condition_lower_bounds,
    condition_upper_bounds,
    feedback_correct,
    feedback_incorrect,
    store_variants,
):
    if not ctx.triggered_id:
        raise PreventUpdate

    variants = StoreVariants.from_dict(store_variants or {})
    triggered_id = ctx.triggered_id
    triggered_value = get_triggered_value()

    if triggered_id == "cb_use_variants":
        should_use_variants = bool(
            use_variants
            and "use" in use_variants
            and assignment_type
        )

        if should_use_variants:
            current_assignment_type = get_assignment_value(
                variants.assignment
            )

            if current_assignment_type != assignment_type:
                variants.set_assignment(assignment_type)

        variants.use_variants = should_use_variants

    elif triggered_id == "dd_assignment":
        if assignment_type:
            current_assignment_type = get_assignment_value(
                variants.assignment
            )

            if current_assignment_type != assignment_type:
                variants.set_assignment(assignment_type)

            variants.use_variants = bool(
                use_variants and "use" in use_variants
            )

    elif triggered_id == "i_variants_title":
        variants.title = title or ""

    elif triggered_id == "i_variants_text":
        variants.item_body = item_body or ""

    elif triggered_id == "b_new_variable":
        if isinstance(
            variants.assignment,
            VariableDependentAssignment,
        ):
            variants.assignment.add_variable()
            update_assignment_variants(variants.assignment)

    elif triggered_id == "i_count_variants":
        if isinstance(
            variants.assignment,
            (ManualAssignment, StudentIdToVariantAssignment),
        ):
            if count_variants is not None:
                variants.assignment.count_variants = int(
                    count_variants
                )

    elif (
        isinstance(triggered_id, dict)
        and triggered_id.get("type") == "b_delete_variable"
    ):
        if isinstance(
            variants.assignment,
            VariableDependentAssignment,
        ):
            variable_index = int(triggered_id["index"])

            if (
                0
                <= variable_index
                < len(variants.assignment.list_variables)
            ):
                variants.assignment.list_variables.pop(
                    variable_index
                )

                for index, variable in enumerate(
                    variants.assignment.list_variables
                ):
                    variable.id = f"VARIABLE_{index + 1}"

                update_assignment_variants(
                    variants.assignment
                )

    elif isinstance(triggered_id, dict):
        component_type = triggered_id.get("type")
        index = int(triggered_id.get("index", 0))

        if not isinstance(
            variants.assignment,
            VariableDependentAssignment,
        ):
            return variants.to_dict(), True

        if component_type == "i_variable_value_response":
            if index < len(
                variants.assignment.list_variables
            ):
                variants.assignment.list_variables[
                    index
                ].value_response = triggered_value

                update_assignment_variants(
                    variants.assignment
                )

        elif component_type == "b_new_condition":
            if index < len(
                variants.assignment.list_variables
            ):
                variants.assignment.list_variables[
                    index
                ].add_condition()

                update_assignment_variants(
                    variants.assignment
                )

        elif component_type == "b_new_dependent_variable":
            if index < len(
                variants.assignment.list_variables
            ):
                variants.assignment.list_variables[
                    index
                ].add_variable()

                update_assignment_variants(
                    variants.assignment
                )

        elif component_type == "i_variable_name":
            name_index = int(
                triggered_id.get("name_index", 0)
            )

            if index < len(
                variants.assignment.list_variables
            ):
                variants.assignment.list_variables[
                    index
                ].set_variable_name(
                    name_index,
                    triggered_value,
                )

                update_assignment_variants(
                    variants.assignment
                )

        elif component_type in {
            "i_condition_value",
            "i_condition_lower_bound",
            "i_condition_upper_bound",
        }:
            variable_index = int(
                triggered_id.get("variable", 0)
            )
            condition_index = index

            if variable_index >= len(
                variants.assignment.list_variables
            ):
                return variants.to_dict(), True

            variable = variants.assignment.list_variables[
                variable_index
            ]

            if condition_index >= len(
                variable.list_conditions
            ):
                return variants.to_dict(), True

            condition = variable.list_conditions[
                condition_index
            ]

            if component_type == "i_condition_value":
                key = triggered_id.get("key")
                condition.values[key] = triggered_value

            elif component_type == "i_condition_lower_bound":
                condition.lower_bound = triggered_value

            elif component_type == "i_condition_upper_bound":
                condition.upper_bound = triggered_value

            update_assignment_variants(
                variants.assignment
            )

    elif triggered_id == "i_feedback_correct_variants":
        variants.set_feedback(
            feedback_correct or "",
            "feedback_correct",
        )

    elif triggered_id == "i_feedback_incorrect_variants":
        variants.set_feedback(
            feedback_incorrect or "",
            "feedback_incorrect",
        )

    return variants.to_dict(), True