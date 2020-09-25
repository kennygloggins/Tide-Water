import pandas as pd
from pymongo import MongoClient
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from config import mongo

labels = {
    "water_level": ["height", "Feet"],
    "water_temperature": ["temp", "Temperature(degrees F)"],
    "wind": ["Speed", "Gust", "Direction"],
}

app = dash.Dash(__name__)

server = MongoClient(mongo)
db = server["Ocean_City_Inlet"]

# pd.set_option("display.max_columns", 10)
# pd.set_option("display.max_rows", 85)

# df.head()
# df.info()
# print(df[["time", "water_level data"]])

app.layout = html.Div(
    [
        html.H1("Kayak?", style={"text-align": "center"}),
        dcc.Dropdown(
            id="slct_cat",
            options=[
                {"label": "Water Level", "value": "water_level"},
                {"label": "Water Temp", "value": "water_temperature"},
                {"label": "Wind", "value": "wind"},
            ],
            multi=False,
            value="water_level",
            style={"width": "40%"},
        ),
        html.Div(id="output_container", children=[]),
        html.Br(),
        dcc.Graph(id="tide_op", figure={}),
    ]
)


@app.callback(
    [
        Output(component_id="output_container", component_property="children"),
        Output(component_id="tide_op", component_property="figure"),
    ],
    [Input(component_id="slct_cat", component_property="value")],
)
def update_graph(option_slctd):
    df = pd.DataFrame(list(db[option_slctd].find()))
    print(option_slctd)

    container = "The category chosen by user was: {}".format(option_slctd)

    fig = go.Figure()

    if option_slctd == "wind":
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df[f"{labels[option_slctd][0]}"],
                name=f"{labels[option_slctd][0]}",
                line=dict(color="firebrick", width=4),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df[f"{labels[option_slctd][1]}"],
                name=f"{labels[option_slctd][1]}",
                line=dict(color="blue", width=4),
            )
        )
        fig.update_layout(xaxis_title="Time", yaxis_title="MPH")
    else:
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df[f"{labels[option_slctd][0]}"],
                name=f"{option_slctd} data",
                line=dict(color="blue", width=4),
            )
        )
        fig.update_layout(xaxis_title="Time", yaxis_title=labels[option_slctd][1])

    return container, fig


if __name__ == "__main__":
    app.run_server(debug=True)
