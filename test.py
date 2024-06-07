from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import json

df = pd.read_csv("./data/rent_inc.csv")
with open("./data/BEZIRKSGRENZEOGD.json", "r") as f:
    geojson = json.loads(f.read())

app = Dash()

app.layout = [
    html.H1(children = "Test", style = {"textAlign":"center"}),
    dcc.Dropdown(df.district.unique(), "Canada", id = "dropdown-selection"),
    dcc.Graph(id="choropleth")
]

@callback(
    Output("choropleth", "figure"),
    Input("dropdown-selection", "value")
)
def update_graph(test):
    fig = px.choropleth_mapbox(
        df, geojson=geojson, color="rent",
        locations="district", featureidkey="properties.DISTRICT_CODE",
        mapbox_style="carto-positron")
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0})

    return fig

if __name__ == '__main__':
    app.run(debug=True)