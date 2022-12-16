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
    external_stylesheets=[dbc.themes.JOURNAL],
    name='Tech Layoffs 2020-2022'
    )

app.title = 'Tech Layoffs 2020-2022'

df = pd.read_csv(r'layoffs_1.csv')
df['date']= pd.to_datetime(df['date'])
df['bulan']= df['date'].dt.to_period('M')
df['bulan']= df['bulan'].dt.to_timestamp()
df['status'] = ['Publicly traded' if x =='IPO' else 'Privately owned' for x in df['stage']]
most_updated_date = df['date'].max()

options_dropdown = df['country'].unique().tolist()
options_dropdown.sort()
options_dropdown.insert(0, 'All country')

## Navigation bar
navbar = dbc.NavbarSimple(
    
    brand="Tech Layoffs Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)

## Card Content
total_companies = [
    dbc.CardHeader('Number of companies'),
    dbc.CardBody([
        html.H5(id='total_companies')
    ]),
]

total_laid_off = [
    dbc.CardHeader('Number of people laid off'),
    dbc.CardBody([
        html.H5(id='total_laid_off')
    ]),
]

data_terbaru = [
    dbc.CardHeader('Data updated as of'),
    dbc.CardBody([
        html.H5(f"{most_updated_date.strftime('%A')}, {most_updated_date.strftime('%d')} {most_updated_date.strftime('%b')} {most_updated_date.strftime('%Y')}")
    ])
]


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
                [   dbc.CardHeader(html.H5('Select country')),
                    dcc.Dropdown(
                            id='pick_country',
                            options=options_dropdown,
                            value='All country'),
                    html.Br(),
                    dbc.Card(total_companies, color='white'),
                    html.Br(),
                    dbc.Card(total_laid_off, color='white'),
                    html.Br(),
                    dbc.Card(data_terbaru, color='white'),
                ],
                width=2),

            ### Column 2
            dbc.Col([
                html.H3('Trends'),
                dcc.Graph(id='area_plot'),
            ], width=5),
            
            dbc.Col([
                html.H3('Correlation'),
                dcc.Graph(id='scatter_plot')],
            width=5),

            ]
        ),

        html.Hr(),

        ## Row 2
        dbc.Row(
            [
            ### Column 1
            dbc.Col([
                html.H3('Rankings'),
                dbc.Tabs([
                    #TAB 1 : Ranking by industry
                    dbc.Tab(
                        dcc.Graph(
                            id='bar_industry'
                        ),  
                        label='By Industry'),

                    #TAB 2: Ranking by company
                    dbc.Tab(
                        dcc.Graph(
                            id='bar_company',
                        ), 
                        label='By Company'),

                    #TAB 3: Ranking by City
                    dbc.Tab(
                        dcc.Graph(
                            id='bar_city',
                        ), 
                        label='By City'),
                ]),
            ], width=6),

            ### Column 2
            dbc.Col([
                html.H3('Proportion'),
                dcc.Graph(
                    id='pie_plot',
                ),
            ],
                
                width=6),
            
            ]
        )
    ], style={
        'paddingLeft':'30px',
        'paddingRight':'30px'
    }), 

])
# Callback update company

@app.callback(
    Output(component_id='total_companies', component_property='children'),
    Input(component_id='pick_country', component_property='value')
)

def update_company(country):

    if  country=='All country':

        default = df['company'].nunique()

        return default

    else:

        x = df[df['country']==country]['company'].nunique()

        return x

#Callback update total laid off

@app.callback(
    Output(component_id='total_laid_off', component_property='children'),
    Input(component_id='pick_country', component_property='value')
)

def update_number_laid_off(country):

    if  country=='All country':
        
        default = df['total_laid_off'].sum()

        return default
    else:

        x = df[df['country']==country]['total_laid_off'].sum()

        return x

@app.callback(
    Output(component_id='area_plot', component_property='figure'),
    Input(component_id='pick_country', component_property='value')
)

def update_area_plot(country):

    if country== 'All country':
        group = pd.pivot_table(df, index='bulan', values='total_laid_off', aggfunc='sum').reset_index()

        area_plot = px.area(group, 
                x='bulan', 
                y='total_laid_off', 
                labels= {'bulan': 'Month', 'total_laid_off':'Number of people laid off'},
            template= 'ggplot2',
            title='Number of people laid off, by months')

        area_plot.update_traces(hovertemplate='<b>%{y}</b> employees were laid off in <b>%{x}</b>')

        return area_plot
    
    else:
        group = pd.pivot_table(df[df['country']==country], index='bulan', values='total_laid_off', aggfunc='sum').reset_index()

        area_plot = px.area(group, 
                x='bulan', 
                y='total_laid_off', 
                labels= {'bulan': 'Month', 'total_laid_off':'Number of people laid off'},
            template= 'ggplot2',
            title=f'Number of people laid off, by months in {country}')

        area_plot.update_traces(hovertemplate='<b>%{y}</b> employees were laid off in <b>%{x}</b>')

        return area_plot


# Callback Pie plot

@app.callback(
    Output(component_id='pie_plot', component_property='figure'),
    Input(component_id='pick_country', component_property='value')

)
def update_pie(country):
    if country == 'All country':
        
        status = pd.pivot_table(df, 
                                    index='status', 
                                    values='total_laid_off', 
                                    aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index()

        percentage = round(100*(status.iloc[0][1]/(status['total_laid_off'].sum())), 1)

        pie_plot = px.pie(status.sort_values('total_laid_off', ascending=True), 
                    values='total_laid_off', 
                    names='status',
                    title=f"{percentage}% layoffs came from {str(status['status'].head(1)[0])} companies",
                    template='ggplot2')

        pie_plot.update_traces(hovertemplate='<b>%{value}</b> employees have been laid off from <b>%{label}</b> companies',
                textinfo='label+percent')

        return pie_plot

    else:
        status = pd.pivot_table(df[df['country']==country], 
                                    index='status', 
                                    values='total_laid_off', 
                                    aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index()

        percentage = round(100*(status.iloc[0][1]/(status['total_laid_off'].sum())), 1)

        pie_plot = px.pie(status.sort_values('total_laid_off', ascending=True), 
                    values='total_laid_off', 
                    names='status',
                    title=f"In {country}, {percentage}% layoffs came from {str(status['status'].head(1)[0])} companies",
                    template='ggplot2')

        pie_plot.update_traces(hovertemplate='<b>%{value}</b> employees have been laid off from <b>%{label}</b> companies',
                textinfo='label+percent')

        return pie_plot  

# Callback Scatter

@app.callback(
    Output(component_id='scatter_plot', component_property='figure'),
    Input(component_id='pick_country', component_property='value')

)

def update_scatter(country):
    
    if country == 'All country':

        sketer = px.scatter(df[(df['total_laid_off'] != 0) & (df['funds_raised'] != 0)], 'funds_raised', 'total_laid_off',
          template='ggplot2', log_x=True, hover_data=['company'], custom_data=['company'],
          title = 'correlation between log(funds raised) and number of people laid off',
          labels= {'funds_raised': 'Log(funds raised)', 'total_laid_off':'Number of people laid off'})
        
        sketer.update_traces(hovertemplate='%{customdata[0]} have raised <b>%{x}</b> million USD and have laid off <b>%{y}</b> employees')

        return sketer

    else:

        sketer = px.scatter(df[df['country']==country][(df['total_laid_off'] != 0) & (df['funds_raised'] != 0)], 'funds_raised', 'total_laid_off',
          template='ggplot2', log_x=True, hover_data=['company'], custom_data=['company'],
          title = 'correlation between log(funds raised) and number of people laid off',
          labels= {'funds_raised': 'Log(funds raised)', 'total_laid_off':'Number of people laid off'})
        
        sketer.update_traces(hovertemplate='%{customdata[0]} have raised <b>%{x}</b> million USD and have laid off <b>%{y}</b> employees')

        return sketer


@app.callback(
    Output(component_id='bar_industry', component_property='figure'),
    Input(component_id='pick_country', component_property='value')
)

def update_industry(country):
    if country == 'All country':

        industry = pd.pivot_table(df, 
                            index='industry', 
                            values='total_laid_off', 
                            aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index().head(10)

        bar_1 = px.bar(industry.sort_values('total_laid_off', ascending=True), 
            x='total_laid_off', 
            y='industry',
            title=f'Top {len(industry)} industries with most layoffs',
            template='ggplot2',
            labels= {'industry': 'Industry', 'total_laid_off':'Number of people laid off'})
        
        bar_1.update_traces(hovertemplate='<b>%{y}</b> industry has laid off <b>%{x}</b> employees')

        return bar_1

    else:

        industry = pd.pivot_table(df[df['country']==country], 
                            index='industry', 
                            values='total_laid_off', 
                            aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index().head(10)

        bar_1 = px.bar(industry.sort_values('total_laid_off', ascending=True), 
            x='total_laid_off', 
            y='industry',
            title=f'Top {len(industry)} industries with most layoffs in {country}',
            template='ggplot2',
            labels= {'industry': 'Industry', 'total_laid_off':'Number of people laid off'})

        bar_1.update_traces(hovertemplate='<b>%{y}</b> industry has laid off <b>%{x}</b> employees')

        return bar_1


@app.callback(
    Output(component_id='bar_company', component_property='figure'),
    Input(component_id='pick_country', component_property='value')
)

def update_company(country):
    if country == 'All country':

        company = pd.pivot_table(df, 
                            index='company', 
                            values='total_laid_off', 
                            aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index().head(10)

        bar_2 = px.bar(company.sort_values('total_laid_off', ascending=True), 
            x='total_laid_off', 
            y='company',
            title=f'Top {len(company)} companies with most layoffs',
            template='ggplot2',
            labels= {'company': 'Company', 'total_laid_off':'Number of people laid off'})
        
        bar_2.update_traces(hovertemplate='<b>%{y}</b>  has laid off <b>%{x}</b> employees')

        return bar_2

    else:

        company = pd.pivot_table(df[df['country']==country], 
                            index='company', 
                            values='total_laid_off', 
                            aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index().head(10)

        bar_2 = px.bar(company.sort_values('total_laid_off', ascending=True), 
            x='total_laid_off', 
            y='company',
            title=f'Top {len(company)} companies with most layoffs in {country}',
            template='ggplot2',
            labels= {'company': 'Company', 'total_laid_off':'Number of people laid off'})
        
        bar_2.update_traces(hovertemplate='<b>%{y}</b> has laid off <b>%{x}</b> employees')

        return bar_2


@app.callback(
    Output(component_id='bar_city', component_property='figure'),
    Input(component_id='pick_country', component_property='value')
)

def update_city(country):
    if country == 'All country':

        lokasi = pd.pivot_table(df, 
                            index='location', 
                            values='total_laid_off', 
                            aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index().head(10)

        bar_3 = px.bar(lokasi.sort_values('total_laid_off', ascending=True), 
            x='total_laid_off', 
            y='location',
            title=f'Top {len(lokasi)} cities with most layoffs',
            template='ggplot2',
            labels= {'location': 'City', 'total_laid_off':'Number of people laid off'})

        bar_3.update_traces(hovertemplate=' <b>%{x}</b> employees working in <b>%{y}</b> were laid off')
        
        return bar_3

    else:

        lokasi = pd.pivot_table(df[df['country']==country], 
                            index='location', 
                            values='total_laid_off', 
                            aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index().head(10)

        bar_3 = px.bar(lokasi.sort_values('total_laid_off', ascending=True), 
            x='total_laid_off', 
            y='location',
            title=f'Top {len(lokasi)} cities with most layoffs',
            template='ggplot2',
            labels= {'location': 'City', 'total_laid_off':'Number of people laid off'})

        bar_3.update_traces(hovertemplate=' <b>%{x}</b> employees working in <b>%{y}</b> were laid off')
        
        return bar_3


# 3. Start the Dash server
if __name__ == "__main__":
    app.run_server()