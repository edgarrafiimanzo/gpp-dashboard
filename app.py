import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from statistics import mode
import pandas as pd
import plotly.express as px

# 2. Create a Dash app instance
app = dash.Dash(
    external_stylesheets=[dbc.themes.LUX],
    name='Global power plant'
    )

app.title = 'World power plant dashboard'

## Navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="NavbarSimple",
    brand_href="#",
    color="primary",
    dark=True,
)

#Import data untuk dashboard
gpp = pd.read_csv('power_plant.csv')

## Card Content
total_country = [
    dbc.CardHeader('Number of Country'),
    dbc.CardBody([
        html.H1(gpp['country_long'].nunique())
    ]),
]

total_pp = [
    dbc.CardHeader('Number of Power plants'),
    dbc.CardBody([
        html.H1(gpp['name of powerplant'].nunique())
    ]),
]

total_fuel = [
    dbc.CardHeader('Most Used Fuel', style={"color":"black"}),
    dbc.CardBody([
        html.H1(f"{mode(gpp['primary_fuel'])} = {len(gpp[gpp['primary_fuel']==(gpp.describe(include='object')).loc['top','primary_fuel']])}")
    ])
]


####CHOROPLEY
# Data aggregation
agg1 = pd.crosstab(
    index=[gpp['country code'], gpp['start_year']],
    columns='No of Power Plant'
).reset_index()

# Visualization
plot_map = px.choropleth(agg1.sort_values(by="start_year"),
             locations='country code',
              color_continuous_scale='tealgrn',
             color='No of Power Plant',
             animation_frame='start_year',
             template='ggplot2')

### BARPLOT Ranking
# Data aggregation
gpp_indo = gpp[gpp['country_long'] == 'Indonesia']



#### BOXPLOT: DISTRIBUTION


### PIE Chart



#### Layout

app.layout = html.Div([
    navbar,

    html.Br(),

    # Component main page

    html.Div([ 
        ## Row 1  
        dbc.Row(
            [
            ### Column 1
            dbc.Col(
                [
                    dbc.Card(total_country, color='white'),
                    html.Br(),
                    dbc.Card(total_pp, color='blue'),
                    html.Br(),
                    dbc.Card(total_fuel, color='turquoise'),
                ],
                width=3),

            ### Column 2
            dbc.Col([
                dcc.Graph(figure=plot_map),
            ], width=9),
            ]
        ),

        html.Hr(),

        ## Row 2
        dbc.Row(
            [
            ### Column 1
            dbc.Col([
                html.H1('Analysis by Country'),
                dbc.Tabs([
                    #TAB 1 : Ranking
                    dbc.Tab(
                        dcc.Graph(
                            id='plotranking'
                        ),  
                        label='Ranking'),

                    #TAB 2: distribution
                    dbc.Tab(
                        dcc.Graph(
                            id='plotdistribution',
                        ), 
                        label='Distribution'),
                ]),
            ], width=8),

            ### Column 2
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Select Country'),
                    dbc.CardBody(
                        dcc.Dropdown(
                            id='choose_country',
                            options=gpp['country_long'].unique(),
                            value='Indonesia'
                        ),
                    ),
                ]),
                dcc.Graph(
                    id='plotpie',
                ),
            ],
                
                width=4),
            
            ]
        )
    ], style={
        'paddingLeft':'30px',
        'paddingRight':'30px'
    }), 

])

### Callback plot ranking
@app.callback(
    Output(component_id='plotranking', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_plotrank(country_name):
    gpp_indo = gpp[gpp['country_long']== country_name]

    top_indo = gpp_indo.sort_values('capacity in MW').tail(10)

# Visualize
    plot_ranking = px.bar(
    top_indo,
    x = 'capacity in MW',
    y = 'name of powerplant',
    template = 'ggplot2',
    title = f'Ranking of Overall Power Plants in {str(country_name)}'
)
    return plot_ranking


### Callback plot distribution
@app.callback(
    Output(component_id='plotdistribution', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_plotdist(country_name):
    gpp_indo = gpp[gpp['country_long']== country_name]

    plot_distribution = px.box(
    gpp_indo,
    color='primary_fuel',
    y='capacity in MW',
    template='ggplot2',
    title='Distribution of capacity in MW in each fuel',
    labels={
        'primary_fuel': 'Type of Fuel'
    }
    ).update_xaxes(visible=False)
    return plot_distribution

### Callback pie chart
@app.callback(
    Output(component_id='plotpie', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_pie(country_name):
    gpp_indo = gpp[gpp['country_long']== country_name]

    # aggregation
    agg2=pd.crosstab(
    index=gpp_indo['primary_fuel'],
    columns='No of Power Plant'
    ).reset_index()

    # visualize
    plot_pie = px.pie(
    agg2,
    values='No of Power Plant',
    names='primary_fuel',
    color_discrete_sequence=['aquamarine', 'salmon', 'plum', 'grey', 'slateblue'],
    template='ggplot2',
    hole=0.4,
    title = f'Proportion of Overall Power Plants primary fuel in {str(country_name)}',
    labels={
        'primary_fuel': 'Type of Fuel'
    }
    )
    return plot_pie


# 3. Start the Dash server
if __name__ == "__main__":
    app.run_server()