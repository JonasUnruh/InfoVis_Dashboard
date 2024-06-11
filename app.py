from dash import Dash, html, dcc, Output, Input
import plotly.graph_objects as go
import pandas as pd
import json


app = Dash(
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)

df = pd.read_csv("./assets/data/rent_inc.csv")
with open("./assets/data/bezirke_95_geo.json", "r") as f:
    geojson = json.loads(f.read())


district_dict = {"1. District - Innere Stadt": 901, "2. District - Leopoldstadt": 902, "3. District - Landstraße": 903, "4. District - Wieden": 904, "5. District - Margareten": 905,
                 "6. District - Mariahilf": 906, "7. District - Neubau": 907, "8. District - Josefstadt": 908, "9. District - Alsergrund": 909, "10. District - Favoriten": 910,
                 "11. District - Simmering": 911, "12. District - Meidling": 912, "13. District - Hietzing": 913, "14. District - Penzing": 914, "15. District - Rudolfsheim-Fünfhaus": 915,
                 "16. District - Ottakring": 916, "17. District - Hernals": 917, "18. District - Währing": 918, "19. District - Döbling": 919, "20. District - Brigittenau": 920,
                 "21. District - Floridsdorf": 921, "22. District - Donaustadt": 922, "23. District - Liesing": 923}


app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # User Controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.H2("Information Visualization"),
                        html.P("Paul Hoenes, Jonas Unruh"),
                        html.Div(
                            className="div-dropdown",
                            children=[
                                dcc.DatePickerSingle(

                                )
                            ]
                        ),
                        html.Div(
                            className="div-dropdown",
                            children=[
                                dcc.Dropdown(
                                    id="district-dropdown",
                                    options=[
                                        {"label": key, "value": value}
                                        for key, value in district_dict.items()
                                    ],
                                    multi=True,
                                    placeholder="Select district"
                                )
                            ]
                        ),
                        html.Div(
                            className="div-dropdown",
                            children=[
                                dcc.Dropdown(
                                    id="value-selector",
                                    options=[

                                    ],
                                    placeholder="Select value"
                                )
                            ]
                        )
                    ]
                ),
                # Graphs
                html.Div(
                    className="eight columns",
                    children=[
                        dcc.Graph(id="map-graph"),
                        dcc.Graph(id="line-graph")
                    ]
                )
            ]
        )
    ]
)


@app.callback(
    Output("map-graph", "figure"),
    Input("district-dropdown", "value")
)
def update_map(selected_district):
    fig = go.Figure(
        go.Choroplethmapbox(geojson=geojson, locations=df.district,
                            colorscale="Viridis")
    )

    fig.update_layout(mapbox_style = "carto-positron", 
                      mapbox_center = {"lat": 48.210033, "lon": 16.363449}, 
                      mapbox_zoom = 9.5)
    
    return fig


if __name__ == "__main__":
    app.run()