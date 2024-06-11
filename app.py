from dash import Dash, html, dcc, Output, Input
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json


app = Dash(
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)

mapbox_access_token = "pk.eyJ1Ijoiam9uYXN1bnJ1aCIsImEiOiJjbHhhajBxczYxdHZpMmtzYWt6OWp3NGtoIn0._QenClOEROqOMq2h-9kLog"

df = pd.read_csv("./assets/data/rent_inc.csv")
df["year"] = df["year"].astype(int)
with open("./assets/data/bezirke_95_geo.json", "r") as f:
    geojson = json.loads(f.read())


district_dict = {"1. District - Innere Stadt": 901, "2. District - Leopoldstadt": 902, "3. District - Landstraße": 903, "4. District - Wieden": 904, "5. District - Margareten": 905,
                 "6. District - Mariahilf": 906, "7. District - Neubau": 907, "8. District - Josefstadt": 908, "9. District - Alsergrund": 909, "10. District - Favoriten": 910,
                 "11. District - Simmering": 911, "12. District - Meidling": 912, "13. District - Hietzing": 913, "14. District - Penzing": 914, "15. District - Rudolfsheim-Fünfhaus": 915,
                 "16. District - Ottakring": 916, "17. District - Hernals": 917, "18. District - Währing": 918, "19. District - Döbling": 919, "20. District - Brigittenau": 920,
                 "21. District - Floridsdorf": 921, "22. District - Donaustadt": 922, "23. District - Liesing": 923}
indicator_dict = {"rent": "Rent", "INC_TOT_VALUE": "Total Income", "INC_MAL_VALUE": "Male Income", "INC_FEM_VALUE": "Female Income"}
years = df.year.unique()
selections = set()

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
                                dcc.Dropdown(
                                    id="year-dropdown",
                                    options=[
                                        {"label": str(year), "value": year}
                                        for year in years
                                    ],
                                    value=2023
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
                                        {"label": value, "value": key}
                                        for key, value in indicator_dict.items()
                                    ],
                                    value="rent"
                                )
                            ]
                        )
                    ]
                ),
                # Graphs
                html.Div(
                    className="eight columns div-for-charts bg-grey",
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
    Output("line-graph", "figure"),
    [
        Input("district-dropdown", "value"),
        Input("value-selector", "value")
    ]
)
def update_line(selected_districts, selected_indicator):
    data = df[df[selected_indicator].notnull()]

    if selected_districts:
        data = data[data['district'].isin(selected_districts)]
    else:
        data = data

    fig = px.line(
        data, 
        x='year', 
        y=selected_indicator, 
        color='district', 
        markers=True
    )

    fig.update_layout(
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        yaxis_title=indicator_dict[selected_indicator],
        xaxis_title="Year"
    )
    return fig


@app.callback(
    Output("map-graph", "figure"),
    [
        Input("district-dropdown", "value"),
        Input("year-dropdown", "value"),
        Input("value-selector", "value"),
        Input("map-graph", "clickData")
    ]
)
def update_map(selected_district, selected_year, selected_indicator, clicked_district):
    data = df[df[selected_indicator].notnull()]
    data = data[data["year"] == selected_year]

    if clicked_district:
        district = clicked_district["points"][0]["location"]
        
        if district not in selections:
            selections.add(district)
        else:
            selections.remove(district)
        
    '''fig = go.Figure(
        data=[
            go.Choroplethmapbox(
                geojson=geojson, 
                locations=df.district,
                marker=dict(
                    color=df["rent"][df["year"] == 2020]
                ),
                colorscale="Viridis"
            )
        ],
        layout=go.Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            mapbox=dict(
                center={"lat": 48.210033, "lon": 16.363449},
                style="carto-darkmatter",
                zoom = 9.5
            )
        )
    )'''

    fig = px.choropleth_mapbox(
        data,
        geojson=geojson,
        featureidkey="properties.iso",
        locations="district",
        color=selected_indicator,
        color_continuous_scale="Blues",
        opacity=0.3
    )

    if len(selections) > 0:
        color_list = ["white" if x in selections else "#444" for x in data["district"]]
        fig.update_traces(
            marker_line_color=color_list, 
            marker_line_width=3.0
        )

        '''fig.add_trace(
            px.choropleth_mapbox(
                data[data["district"].isin(selections)],
                geojson=geojson,
                featureidkey="properties.iso",
                locations="district",
                color=selected_indicator,
                opacity=1
            ).data[0]
        )'''

    fig.update_layout(
        margin={"r":35,"t":0,"l":0,"b":0},
        autosize=True,
        accesstoken=mapbox_access_token,
        mapbox_style="dark",
        mapbox_zoom=9.5,
        mapbox_center={"lat": 48.210033, "lon": 16.363449}
    )

    return fig


if __name__ == "__main__":
    app.run()