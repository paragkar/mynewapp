'''
 # @ Create Time: 2023-03-04 12:20:51.084705
'''

from datetime import date
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import init_notebook_mode, iplot
import dash_bootstrap_components as dbc 
import os

os.chdir("/Users/pkar/Documents/Documents - Parag’s MacBook Pro/parag_qc_files/2022/2022_11_26_New_Data_Processing/Currency_Rates") #working dir
print(os.getcwd())

#incoporate data in the app

df = pd.read_csv("currencyratesimf.csv")
df = df.iloc[:,1:]
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index("Date")

#procesing dataframe

def processed_data(date_value):
    closest_date_index = df.index.get_loc(date_value, method="nearest")
    ref_values = df.iloc[closest_date_index]
    df1 = df/ref_values
    df1 = df.div(ref_values)*100-100
    df1 = df1.iloc[closest_date_index:,:]
    df1 = df1.reset_index()
    df1 = pd.melt(df1, id_vars="Date")
    df1.columns = ["Date", "Country", "%Change"]
    for i, country in enumerate(df1["Country"]):
        country = country.split()
        country = " ".join(country)
        df1.loc[i,"Country"] = country
    return df1

#main application

app = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])
server = app.server 
datepicker = html.Div(dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=date(2000,1, 1),
        max_date_allowed=date(2023,3, 31),
        initial_visible_month=date(2022,1,31),
        date=date(2022, 1, 31)
    ))
mygraph = dcc.Graph(figure={})

mytext = dcc.Markdown(children='')

app.layout = dbc.Container([datepicker, mygraph, mytext])

@app.callback(
    Output(mygraph, component_property='figure'),
    Output(mytext, component_property='children'),
    Input("my-date-picker-single", 'date'))

def update_output(date_value):
    
    df1 = processed_data(date_value)
        
    fig = px.line(df1, x="Date", y="%Change", color="Country", 
                  title='% Change in the value of currencies with reference to a selected reference date [+(dep),-(app)]',
                  height = 600)

    string_prefix = 'You have selected: '
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
        date_string = date_object.strftime('%B %d, %Y')
        date_string = "Selected Reference Date is -> "+date_string
    return fig, date_string


# Run app
if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=False)