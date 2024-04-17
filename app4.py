import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Sample data
data = pd.read_csv('historical_automobile_sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server
# Define the layout
app.layout = html.Div([
    html.H1('Automobile Sales Statistics Dashboard', style={'color':'#503D36', 'font-size':'24px'}),
    dcc.Dropdown(
    id='dropdown-statistics',
    options=[
        {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
        {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
    ],
    value='Yearly Statistics',
    clearable=False
    ),
    dcc.Dropdown(
        id='select-year',
        options=[{'label': str(year), 'value': year} for year in data['Year'].unique()],
        value=data['Year'].min(),
        clearable=False
    ),
    html.Div([
        html.Div(id='output-container', className='chart-grid', style={'display': 'flex'}),
    ]),

])

# Eingabecontainer basierend auf der ausgewählten Statistik aktivieren/deaktivieren
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False
    else:
        return True

# Ausgabecontainer basierend auf der Auswahl aktualisieren
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='select-year', component_property='value'), 
     Input(component_id='dropdown-statistics', component_property='value')]
)

def update_output_container(input_year, selected_statistics):
    data = pd.read_csv('historical_automobile_sales.csv')  # Daten laden
    if selected_statistics == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]  # Daten für Rezessionszeiträume filtern

        # Plot 1: Automobile sales fluctuate over Recession Period (year wise) using line chart
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(figure=px.line(yearly_rec, x='Year', y='Automobile_Sales', title="Automobile Sales Fluctuation Over Recession Period"))

        # Plot 2: Average number of vehicles sold by vehicle type represented as a bar chart
        avg_vehicle_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(figure=px.bar(avg_vehicle_sales, x='Vehicle_Type', y='Automobile_Sales', title="Average Vehicle Sales by Vehicle Type during Recession"))

        # Plot 3: Pie chart for total expenditure share by vehicle type during recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(figure=px.pie(exp_rec, values='Advertising_Expenditure', names='Vehicle_Type', title="Total Expenditure Share by Vehicle Type during Recession"))

        # Plot 4: Bar chart for the effect of unemployment rate on vehicle type and sales
        unemployment_effect = recession_data.groupby('Vehicle_Type')[['unemployment_rate', 'Automobile_Sales']].mean().reset_index()
        R_chart4 = dcc.Graph(figure=px.bar(unemployment_effect, x='Vehicle_Type', y='Automobile_Sales', color='unemployment_rate', title="Effect of Unemployment Rate on Vehicle Type and Sales during Recession"))

        return [
            html.Div(className='chart-item', children=[R_chart1, R_chart2]),
            html.Div(className='chart-item', children=[R_chart3, R_chart4])
        ]

    elif selected_statistics == 'Yearly Statistics' and input_year:
        yearly_data = data[data['Year'] == input_year]  # Daten für das ausgewählte Jahr filtern

        # Plot 1: Yearly Automobile sales using line chart for the whole period
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(figure=px.line(yas, x='Year', y='Automobile_Sales', title="Yearly Automobile Sales"))

        # Plot 2: Total Monthly Automobile sales using line chart
        total_monthly_sales = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(figure=px.line(total_monthly_sales, x='Month', y='Automobile_Sales', title="Total Monthly Automobile Sales"))

        # Plot 3: Bar chart for average number of vehicles sold during the given year
        avg_vehicle_data = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(figure=px.bar(avg_vehicle_data, x='Vehicle_Type', y='Automobile_Sales', title="Average Vehicles Sold by Vehicle Type in {}".format(input_year)))

        # Plot 4: Total Advertisement Expenditure for each vehicle using pie chart
        total_ad_exp = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(figure=px.pie(total_ad_exp, values='Advertising_Expenditure', names='Vehicle_Type', title="Total Advertisement Expenditure by Vehicle Type in {}".format(input_year)))

        return [
            html.Div(className='chart-item', children=[Y_chart1, Y_chart2]),
            html.Div(className='chart-item', children=[Y_chart3, Y_chart4])
        ]
    else:
        return "Bitte wählen Sie ein gültiges Jahr."

if __name__ == "__main__":
    app.run_server(debug=True)
