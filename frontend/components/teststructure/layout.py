from frontend.components.edit import container_edit_item

from dash import html, callback, Output, Input

neue_aufgabe = html.Button("neue Aufgabe",  id="neue-aufgabe", style={"width": "115px", "marginLeft": "10px", "padding":"0","backgroundColor": "white", "border": "1px solid lightgray", "borderRadius": "7px"})
neue_sektion = html.Button("neue Sektion",  id="neue-sektion", style={"width": "115px", "padding":"0","backgroundColor": "white", "border": "1px solid lightgray", "borderRadius": "7px"})
loeschen = html.Button("Löschen",  id="loeschen", style={"width": "240px", "padding":"0", "backgroundColor": "white", "border": "1px solid lightgray", "borderRadius": "7px"})
control_bar = html.Div(id="control_bar", children=[
    html.Div(children=[neue_sektion, neue_aufgabe], style={"display": "flex", "marginBottom": "10px", "marginTop": "10px"}),
    html.Div(children=[loeschen], style={"display": "flex", "marginBottom": "10px"}),])

variants = html.Button("Varianten", id="b_variants", style={"width": "220px", "padding": "0", "borderRadius": "7px", "backgroundColor": "white", "border": "1px solid lightgray","marginLeft":"5px",  "marginBottom":"10px"})
load_images = html.Button("Bilder laden", id="load_images", style={"width": "220px", "padding": "0", "borderRadius": "7px", "backgroundColor": "white", "border": "1px solid lightgray","marginLeft":"5px",  "marginBottom":"10px"})
testconfig = html.Button("Test konfigurieren", id="configuration", style={"width": "220px", "padding": "0", "borderRadius": "7px", "backgroundColor": "white", "border": "1px solid lightgray","marginLeft":"5px", "marginBottom":"5px"})


def get_stack_content(teststruktur_liste, aktuelles_obj):
    stack = []
    for sektion in teststruktur_liste:
        if aktuelles_obj and sektion.id == aktuelles_obj: stack.append(html.Button(sektion.title, id={'type': 'b-sektion-bearbeiten', 'index': sektion.id}, style={"fontWeight": "bold", "width": "200px", "backgroundColor": "transparent", "height": "28px", "marginTop": "20px","paddingLeft": "10px", "textAlign":"left", "border": "none"}))
        else: stack.append(html.Button(sektion.title, id={'type': 'b-sektion-bearbeiten', 'index': sektion.id}, style={"width": "200px", "backgroundColor": "transparent", "height": "28px", "marginTop": "20px","paddingLeft": "10px", "textAlign":"left", "border": "none"}))
        for aufgabe in sektion.list_tasks:
            if aktuelles_obj and aufgabe.id == aktuelles_obj: stack.append(html.Button(aufgabe.title, id={'type': 'b-aufgabe-bearbeiten', 'index': aufgabe.id}, style={"fontWeight": "bold", "width": "200px", "backgroundColor": "transparent", "height": "28px", "paddingLeft": "40px", "textAlign":"left", "marginBottom": "5px", "border": "none"}))
            else: stack.append(html.Button(aufgabe.title, id={'type': 'b-aufgabe-bearbeiten', 'index': aufgabe.id}, style={"width": "200px", "backgroundColor": "transparent", "height": "28px", "marginBottom": "5px", "paddingLeft": "40px", "textAlign":"left",  "border": "none"}))
    return html.Div(id="div_teststructure", children=stack)

container_edit_test = html.Div(id="container_edit_test", children=[container_edit_item, html.Div(id="div_variants"), html.Div(id="div_images"), html.Div(id="div_config")])
container_sidebar = html.Div(id="container_sidebar", children=[html.Div(id="div_teststructure"), html.Button(id="loeschen", style={"display":"none"}), html.Button(id="neue-aufgabe", style={"display":"none"}), html.Button(id="neue-sektion", style={"display":"none"}), html.Button(id="configuration", style={"display":"none"}), html.Button(id="load_images", style={"display":"none"}), html.Button(id="b_variants", style={"display":"none"})])
div_edit_test = html.Div(id="div_edit_test", children=[container_sidebar, container_edit_test])

@callback(
    Output("div_config", "style"),
    Output("container_edit_item", "style"),
    Output("div_images", "style"),
    Output("div_variants", "style"),

    Input("view_edit", "data"),
    prevent_initial_call=True
)
def layout_manager(state):
    return (
        {"display": "block"} if state == "config" else {"display": "none"},
        {"display": "block"} if state == "edit_item" else {"display": "none"},
        {"display": "block"} if state == "images" else {"display": "none"},
        {"display": "block"} if state == "variants" else {"display": "none"}
    )


