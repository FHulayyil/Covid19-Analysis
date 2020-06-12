#Importing libraries
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
from datetime import datetime


# importing the dataset
covid_data = requests.get('https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/Coronavirus_2019_nCoV_Cases/FeatureServer/1/query?where=1%3D1&outFields=*&outSR=4326&f=json')
covid_json = covid_data.json()
df = pd.DataFrame(covid_json['features'])


# Transforming the data
covid_list = df['attributes'].tolist()
covid = pd.DataFrame(covid_list)
covid.set_index('OBJECTID')
covid = covid[["Country_Region", "Province_State", "Lat", "Long_", "Confirmed", "Deaths", "Recovered", "Last_Update"]]


# Deleting missing data
covid = covid.dropna(subset=["Last_Update"])
covid['Province_State'].fillna(value="", inplace=True)


# mS to yyyy-mm-dd-hh-mm-ss
def convert(x):
    x = int(x)
    return datetime.fromtimestamp(x)
covid['Last_Update'] = covid['Last_Update']/1000
covid['Last_Update'] = covid['Last_Update'].apply(convert)

# Aggregating by country
covid_total = covid.groupby('Country_Region', as_index=False).agg(
    {
        "Confirmed": "sum",
        "Deaths": "sum",
        "Recovered": "sum"
    }
)


# Calculating total deaths
total_confirmed = covid["Confirmed"].sum()
total_recovered = covid["Recovered"].sum()
total_deaths = covid["Deaths"].sum()

df_top10 = covid.nlargest(10, "Confirmed")
top10_countries_1 = df_top10["Country_Region"].tolist()
top10_confirmed = df_top10["Confirmed"].tolist()

df_top10 = covid.nlargest(10, "Recovered")
top10_countries_2 = df_top10["Country_Region"].tolist()
top10_recovered = df_top10["Recovered"].tolist()

df_top10 = covid.nlargest(10, "Deaths")
top10_countries_3 = df_top10["Country_Region"].tolist()
top10_deaths = df_top10["Deaths"].tolist()


# Visualising the data
fig = make_subplots(
    rows=4, cols=6,
    specs=[
            [{"type": "scattergeo", "rowspan": 4, "colspan": 3}, None, None, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [None, None, None,               {"type": "bar", "colspan":3}, None, None],
            [None, None, None,              {"type": "bar", "colspan":3}, None, None],
            [None, None, None,               {"type": "bar", "colspan":3}, None, None],
          ]
)

message = covid["Country_Region"] + " " + covid["Province_State"] + "<br>"
message += "Confirmed: " + covid["Confirmed"].astype(str) + "<br>"
message += "Deaths: " + covid["Deaths"].astype(str) + "<br>"
message += "Recovered: " + covid["Recovered"].astype(str) + "<br>"
message += "Last updated: " + covid["Last_Update"].astype(str)
covid["text"] = message

fig.add_trace(
    go.Scattergeo(
        locationmode="country names",
        lon=covid["Long_"],
        lat=covid["Lat"],
        hovertext=covid["text"],
        showlegend=False,
        marker=dict(
            size=10,
            opacity=0.8,
            reversescale=True,
            autocolorscale=True,
            symbol='square',
            line=dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            cmin=0,
            color=covid['Confirmed'],
            cmax=covid['Confirmed'].max(),
            colorbar_title="Confirmed Cases<br>Latest Update",
            colorbar_x=-0.05
        )

    ),

    row=1, col=1
)

fig.add_trace(
    go.Indicator(
        mode="number",
        value=total_confirmed,
        title="Confirmed Cases",
    ),
    row=1, col=4
)

fig.add_trace(
    go.Indicator(
        mode="number",
        value=total_recovered,
        title="Recovered Cases",
    ),
    row=1, col=5
)

fig.add_trace(
    go.Indicator(
        mode="number",
        value=total_deaths,
        title="Deaths Cases",
    ),
    row=1, col=6
)

fig.add_trace(
    go.Bar(
        x=top10_countries_1,
        y=top10_confirmed,
        name= "Confirmed Cases",
        marker=dict(color="Yellow"),
        showlegend=True,
    ),
    row=2, col=4
)

fig.add_trace(
    go.Bar(
        x=top10_countries_2,
        y=top10_recovered,
        name= "Recovered Cases",
        marker=dict(color="Green"),
        showlegend=True),
    row=3, col=4
)

fig.add_trace(
    go.Bar(
        x=top10_countries_3,
        y=top10_deaths,
        name= "Deaths Cases",
        marker=dict(color="crimson"),
        showlegend=True),
    row=4, col=4
)

fig.update_layout(
    template="plotly_dark",
    title = "Global COVID-19 Cases (Last Updated: " + str(covid["Last_Update"][0]) + ")",
    showlegend=True,
    legend_orientation="h",
    legend=dict(x=0.65, y=0.8),
    geo = dict(
            projection_type="orthographic",
            showcoastlines=True,
            landcolor="white",
            showland= True,
            showocean = True,
            lakecolor="LightBlue"
    ),

    annotations=[
        dict(
            text="Source: https://bit.ly/3aEzxjK",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.35,
            y=0)
    ]
)

fig.write_html('first_figure.html', auto_open=True)