from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import json

df = pd.read_csv("./data/rent_inc.csv")
with open("./data/bezirke_95_geo.json", "r") as f:
    geojson = json.loads(f.read())

app = Dash(
    #external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
)

app.layout = html.Div(
    children=[
        # Header
        html.Div(
            id="header",
            children=[
                html.Div(
                    className="ag-theme-alpine-dark",
                    children=[html.H1(children = "Excercise 3 - InfoVis UE"),
                     html.H4(children="Paul Hoenes, Jonas Unruh")],
                    style = {
                        "textAlign":"center",
                        "padding": "10px 0px 0px 10px"
                    }
                ), 
            ]
        ),
        html.Div(
            className="row",
            children=[
                 # Plot Controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.Dropdown(df.columns, "Rent", id = "dropdown-selection")
                            ]
                        )
                    ]
                ),
                # Plots
                html.Div(
                    children=[
                        dcc.Graph(id="choropleth")
                    ]
                )
            ]
        )
       
    ]
)

@callback(
    Output("choropleth", "figure"),
    Input("dropdown-selection", "value")
)
def update_graph(test):
    fig = px.choropleth_mapbox(
        df, geojson=geojson, color="rent",
        locations="district", featureidkey="properties.iso",
        mapbox_style="carto-positron",
        color_continuous_scale = px.colors.sequential.Viridis_r,
        zoom = 9.5,
        animation_frame = "year",
        width = 750,
        height = 550,
        center = {"lat": 48.210033, "lon": 16.363449},
        opacity = 0.3)
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0})

    return fig

if __name__ == '__main__':
    app.run(debug=True)