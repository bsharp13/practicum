
# Import libraries
import dash 
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import datetime
import pickle

from dash.dependencies import Input, Output
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.externals import joblib

# Read in data
schedule = pd.read_csv('sample_schedule.csv')

# Read in model object
with open('Schedule_gb00.pkl', 'rb') as file:  
    model = pickle.load(file)

# Make predictions
pred_data = schedule[[
	'DaysBetween', 'PreviousMiss', 'Gender', 'Age', 'Hipertension', 'Diabetes',
	'Alcoholism', 'Handcap', 'SMS_received', 'Scholarship'
]]
probs = model.predict_proba(pred_data)
probs = pd.Series(i[1] for i in probs)

schedule['Prob'] = probs

# Define label
schedule['Label'] = round(schedule['Prob'] * 100, 2).map(str) + '%'

# Define styles
dash_style = {
	'margin-left': 50,
	'margin-top': 50
}

h1_style = {
	'font-family': 'Helvetica',
	'font-weight': 'lighter',
	'font-size': '48pt',
}

h2_style = {
	'font-family': 'Helvetica',
	'font-weight': 'lighter',
	'font-size': '24pt'	
}

h3_style = {
	'font-family': 'Helvetica',
	'font-weight': 'lighter',
	'font-size': '12pt'
}



app = dash.Dash()

app.layout = html.Div(
	html.Div([
		html.H1("Today's Schedule", style = h1_style),

		html.Div(
			dcc.Graph(
				id = 'calendar',
				figure = {
					'data': [
						go.Scatter(
							x = schedule['X'],
							y = schedule['AppointmentTime'],
							mode = 'markers+text',
							marker = {
								'symbol': 'square',
								'size': 56,
								'color': schedule['Prob'],
								'colorscale': 'YlGnBu',
								'cauto': False,
								'cmin': 0,
								'cmax': 1,
								'colorbar': {
									'title': 'Probability of No Show',
									'len': 0.8,
									'tickformat': ".0%"
								}
							},
							text = schedule['Label'],
							textposition = 'middle center',
							textfont = {
								'color': '#FFFFFF'
							}
						)
					],
					'layout': go.Layout(
						xaxis = {
							'title': '', 
							'showgrid': False,
							'zeroline': False,
							'showline': False,
							'showticklabels': False
						},
						yaxis = {
							'title': '', 
							'showgrid': False,
							'zeroline': False,
							'showline': False,
							'autorange': 'reversed',
							'nticks': 16
						},
						hovermode = 'closest',
						height = 800,
						width = 400
					)
				}
			)
		),
	]),
	style = dash_style
)

if __name__ == '__main__':
	app.run_server(debug = True)
