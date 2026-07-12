#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
import more_itertools
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Load the data using pandas
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
#app.title = "Automobile Statistics Dashboard"

#---------------------------------------------------------------------------------
# Create the dropdown menu options
dropdown_options = [
    {'label': '...........', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': '.........'}
]
# List of years 
year_list = [i for i in range(1980, 2024, 1)]
#---------------------------------------------------------------------------------------
# Create the layout of the app
app.layout = html.Div([
    #TASK 2.1 Add title to the dashboard
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={'textAlign': 'center', 'color': '#503D36'}
    ),
    #TASK 2.2: Add two dropdown menus
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
        id='statistics-dropdown',
        options=[
                {'label': 'Yearly Automobile Sales Statistics', 'value': 'yearly'},
                {'label': 'Recession Period Statistics', 'value': 'recession'}
            ],
            value='yearly',
            placeholder='Select a report type'
        )
    ]),
    html.Div(
    dcc.Dropdown(
        id='select-year',
        options=[{'label': i, 'value': i} for i in year_list],
        value=1980
    )),html.Div([#TASK 2.3: Add a division for output display
    html.Div(id='output-container', className='chart-container', style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr'}),])
    
])
#TASK 2.4: Creating Callbacks
# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='statistics-dropdown',component_property='value'))

def update_input_container(selected_statistics):
    if selected_statistics =='yearly': 
        return False
    else: 
        return True

#Callback for plotting
# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id='output-container', component_property='children'),
        [
            Input(component_id='statistics-dropdown', component_property='value'),
            Input(component_id='select-year', component_property='value')
        ]
    )

def update_output_container(selected_statistics, selected_year):

    # ================= RECESSION REPORT =================
    if selected_statistics == 'recession':

        recession_data = data[data['Recession'] == 1]

        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(
                yearly_rec,
                x='Year',
                y='Automobile_Sales',
                title="Average Automobile Sales fluctuation over Recession Period"
            )
        )

        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(
                average_sales,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title="Average Number of Vehicles Sold by Vehicle Type"
            )
        )

        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(
                exp_rec,
                names='Vehicle_Type',
                values='Advertising_Expenditure',
                title="Total Expenditure Share by Vehicle Type during Recessions"
            )
        )

        unemp_data = recession_data.groupby(
            ['Vehicle_Type', 'unemployment_rate']
        )['Automobile_Sales'].mean().reset_index()

        R_chart4 = dcc.Graph(
            figure=px.bar(
                unemp_data,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title='Effect of Unemployment Rate on Vehicle Type and Sales'
            )
        )

        return [
            html.Div(
                children=[R_chart1, R_chart2],
                style={'display': 'flex'}
            ),
            html.Div(
                children=[R_chart3, R_chart4],
                style={'display': 'flex'}
            )
        ]

    # ================= YEARLY REPORT =================
    elif selected_statistics == 'yearly' and selected_year:

        yearly_data = data[data['Year'] == selected_year]

        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(
                yas,
                x='Year',
                y='Automobile_Sales',
                title='Yearly Automobile Sales Using Line Chart'
            )
        )

        mas = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(
                mas,
                x='Month',
                y='Automobile_Sales',
                title='Total Monthly Automobile Sales'
            )
        )

        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(
                avr_vdata,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title=f'Average Vehicles Sold by Vehicle Type in {selected_year}'
            )
        )

        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(
                exp_data,
                names='Vehicle_Type',
                values='Advertising_Expenditure',
                title='Total Advertisement Expenditure for each Vehicle'
            )
        )

        return [
            html.Div(
                children=[Y_chart1, Y_chart2],
                style={'display': 'flex'}
            ),
            html.Div(
                children=[Y_chart3, Y_chart4],
                style={'display': 'flex'}
            )
        ]

    else:
        return None
        
# Run the Dash app
if __name__ == '__main__':
    app.run(debug=True)

