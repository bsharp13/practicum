
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

# Read in date data
dates = pd.read_csv('Dates.csv')
dates.loc[:, 'Date'] = pd.to_datetime(dates.loc[:, 'Date']).dt.date
day_array = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

# Input option lists
months = dates['MonthName'].unique()
patients = ['New Patient', 'Returning Patient']
genders = ['M', 'F']

# Filter to current month
display = dates[dates['Month'] == datetime.datetime.today().month]
display_label = datetime.datetime.today().strftime('%B')

# Define styles
dash_style = {
	'margin-left': 50,
	'margin-top': 50
}

input_style = {
	'width': '20%',
	'height': '10px',
	'display': 'table-cell',
	'padding-left': 5,
	'padding-right': 5,
	'verticalAlign': 'middle',
	'font-family': 'Helvetica',
	'font-weight': 'lighter',
	'font-size': '12pt'
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

# Read in model object
with open('Calendar_gb00.pkl', 'rb') as file:  
    model = pickle.load(file)

app = dash.Dash()

app.layout = html.Div(
	html.Div([
		html.H1('Appointment Scheduler', style = h1_style),
		html.H2('General Information', style = h2_style),

		html.Div([
			html.Div([
				html.H3('Month', style =  h3_style),
				dcc.Dropdown(
					id = 'month',
					value = 'June',
					options = [{'label': i, 'value': i} for i in months]
				),
			],
			style = input_style),
		
			html.Div([
				html.H3('Gender', style = h3_style),
				dcc.Dropdown(
					id = 'gender',
					value = 'M',
					options = [{'label': i, 'value': i} for i in genders]
				),
			],
			style = input_style),

			html.Div([
				html.H3('Age', style = h3_style),
				dcc.Input(
					id = 'age',
					value = 25,
					type = 'number'
				),
			],
			style = input_style),

		],
		style = {
			'width': '50%',
			'display': 'table'
		}),

		html.Div(
			id = 'output-month'
		),
	]),
	style = dash_style
)

@app.callback(
	Output(component_id = 'output-month', component_property = 'children'),
	[
		Input(component_id = 'month', component_property = 'value'),
		Input(component_id = 'gender', component_property = 'value'),
		Input(component_id = 'age', component_property = 'value'),

	]
)
def update_cal(input_month, input_gender, input_age):

	# Filter dates data to show selected month
	display = dates[dates['MonthName'] == input_month]
	display = display.reset_index()
	display = display.drop('index', axis = 1)

	# FIXME:: Run predictions on display data
	display.loc[:,'DaysBetween'] = display['Date'] - datetime.date.today()
	display.loc[:,'DaysBetween'] = display['DaysBetween'].dt.days

	if input_gender == 'M':
		display.loc[:, 'Gender'] = 1
	else:
		display.loc[:, 'Gender'] = 0

	display.loc[:, 'Age'] = input_age

	pred_data = display.drop(
		[
	    	'MonthName', 'Month', 'Year', 'Day', 'Date', 'Weekday', 'DayOfWeek', 
	    	'DayLabel', 'WeekOfMonth',
		],
		axis = 1
	)


	probs = model.predict_proba(pred_data)
	probs = pd.Series([i[1] for i in probs])

	display['Prob'] = probs
	display['ProbLabel'] = round(display['Prob'] * 100, 2).map(str) + '%'
	display['Label'] = display['Day'].map(str) + ': ' + display['ProbLabel']

	# Define calendar ratio
	cal_width = 1200
	weeks = display['WeekOfMonth'].unique().size

	return dcc.Graph(
		id = 'calendar',
		figure = {
			'data': [
				go.Scatter(
					x = display['DayLabel'],
					y = 7 - display['WeekOfMonth'],
					mode = 'markers+text',
					marker = {
						'symbol': 'square',
						'size': 114,
						'color': display['Prob'],
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
					text = display['Label'],
					textposition = 'middle center',
					textfont = {
						'color': '#FFFFFF'
					}
				)
			],
			'layout': go.Layout(
				xaxis = {
					'title': '', 
					'side': 'top',
					'categoryarray': day_array,
					'showgrid': False,
					'zeroline': False,
					'showline': False,
				},
				yaxis = {
					'title': '', 
					'showgrid': False,
					'zeroline': False,
					'showline': False,
					'showticklabels': False
				},
				hovermode = 'closest',
				height = 182.5 * weeks,
				width = cal_width
			)
		}
	)


if __name__ == '__main__':
	app.run_server(debug = True)
