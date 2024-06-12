from dash import Dash, html, dcc, Output, Input, State
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


district_dict = {
    901: "1. District - Innere Stadt", 902: "2. District - Leopoldstadt", 903: "3. District - Landstraße",
    904: "4. District - Wieden", 905: "5. District - Margareten", 906: "6. District - Mariahilf",
    907: "7. District - Neubau", 908: "8. District - Josefstadt", 909: "9. District - Alsergrund",
    910: "10. District - Favoriten", 911: "11. District - Simmering", 912: "12. District - Meidling",
    913: "13. District - Hietzing", 914: "14. District - Penzing", 915: "15. District - Rudolfsheim-Fünfhaus",
    916: "16. District - Ottakring", 917: "17. District - Hernals", 918: "18. District - Währing",
    919: "19. District - Döbling", 920: "20. District - Brigittenau", 921: "21. District - Floridsdorf",
    922: "22. District - Donaustadt", 923: "23. District - Liesing"
}
indicator_dict = {"fem_ratio": "Income to rent ratio female", "mal_ratio": "Income to rent ratio male", "tot_ratio": "Income to rent ratio", 
                  "mean_rent": "Rent per month", "rent": "Rent per sqm", "INC_TOT_VALUE": "Total Income", "INC_MAL_VALUE": "Male Income", "INC_FEM_VALUE": "Female Income"}
years = df.year.unique()

app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # User Controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.H2("Comparing Rent and Income in Vienna"),
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
                                    value=2020
                                )
                            ]
                        ),
                        html.Div(
                            className="div-dropdown",
                            children=[
                                dcc.Dropdown(
                                    id="district-dropdown",
                                    options=[
                                        {"label": value, "value": key}
                                        for key, value in district_dict.items()
                                    ],
                                    multi=True,
                                    placeholder="Select district",
                                    clearable=True
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
                                    value="tot_ratio"
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
                        html.Div(
                            className="text-padding",
                            children=[
                                
                            ]
                        ),
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
        data = data[data['district'] == 0]

    fig = px.line(
        data, 
        x='year', 
        y=selected_indicator, 
        color='district', 
        markers=True,
        title= indicator_dict[selected_indicator] + " over time in Vienna",
        custom_data=["district", "year", selected_indicator]
    )

    fig.update_layout(
        margin=go.layout.Margin(l=10, r=0, t=50, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        yaxis_title=indicator_dict[selected_indicator],
        xaxis_title="Year"
    )

    fig.update_traces(mode = "lines+markers",
                      hovertemplate = None)
    fig.update_traces(
        hovertemplate = "District: %{customdata[0]} <br>Year: %{customdata[1]}<br>" + indicator_dict[selected_indicator] + ": %{customdata[2]} </br><extra></extra>"
    )

    return fig


@app.callback(
    [
        Output("year-dropdown", "value"),
        Output("line-graph", "clickData")
    ],
    [
        Input("line-graph", "clickData"),
        Input("year-dropdown", "value")
    ]
)
def update_year_from_line_chart(clickData, value):
    if clickData:
        clicked_year = clickData["points"][0]["x"]

        return clicked_year, None
    
    return value, None


@app.callback(
        [
            Output("district-dropdown", "value"),
            Output("map-graph", "clickData")
        ],
        [
            Input("map-graph", "clickData"),
            Input("district-dropdown", "value")
        ]
)
def update_district_dropdown(clickData, selectedData):
    districts = selectedData if selectedData else []

    if clickData:
        clicked_district = clickData["points"][0]["location"]
        if clicked_district in districts:
            districts.remove(clicked_district)
        else:
            districts.append(clicked_district)

    return list(set(districts)), None


@app.callback(
    Output("map-graph", "figure"),
    [
        Input("district-dropdown", "value"),
        Input("year-dropdown", "value"),
        Input("value-selector", "value")
    ]
)
def update_map(selected_districts, selected_year, selected_indicator):
    data = df[df[selected_indicator].notnull()]
    data = data[data["year"] == selected_year]
    districts = []

    fig = px.choropleth_mapbox(
        data,
        geojson=geojson,
        featureidkey="properties.iso",
        locations="district",
        color=selected_indicator,
        color_continuous_scale="Viridis",
        opacity=0.3,
        custom_data=["district", selected_indicator]
    )

    if selected_districts:
        for x in selected_districts:
            districts.append(x)
        
        districts = set(districts)

        color_list = ["white" if x in list(districts) else "#444" for x in data["district"]]
        fig.update_traces(
            marker_line_color=color_list, 
            marker_line_width=3.0
        )

    fig.update_layout(
        coloraxis_colorbar=dict(title=indicator_dict[selected_indicator]),
        margin={"r":35,"t":0,"l":0,"b":0},
        autosize=True,
        mapbox_accesstoken=mapbox_access_token,
        mapbox_style="dark",
        mapbox_zoom=9.5,
        mapbox_center={"lat": 48.210033, "lon": 16.363449},
        font=dict(
            color="white"
        )         
    )

    fig.update_traces(
        hovertemplate = "District: %{customdata[0]} <br>" + indicator_dict[selected_indicator] + ": %{customdata[1]} </br>"
    )

    return fig


if __name__ == "__main__":
    app.run()