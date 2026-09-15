from dash import html

from frontend.components.teststructure import div_edit_test

button_style = {"backgroundColor": "#f0f0f0", "border": "1px solid #ccc", "borderRadius": "6px", "cursor": "pointer", "transition": "background-color 0.2s ease",}

b_new_test = html.Button("Test bearbeiten", id="b_edit_test", style=button_style)
b_load_test = html.Button("Test laden", id="b_div_load_test", style=button_style)
b_export_test = html.Button("Exportieren", id="b_export_test", style=button_style)

menubar = html.Div(children=[html.Div([
                html.Div([b_new_test, b_load_test], style={"display": "flex", "gap": "0.5rem"}),
                html.Div(b_export_test, style={"marginLeft": "auto"})], style={"display": "flex", "width": "100%"})],
    style={"position": "sticky", "top": 0, "zIndex": 999, "backgroundColor": "#ffffff", "padding": "10px", "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)"})

container_menu = html.Div(id="test_panel_container", children=[div_edit_test, html.Div(id="div_load_test")])