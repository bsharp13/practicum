
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
#dates['Prob'] = np.random.uniform(0, 1, len(dates.index)) # pseudo model pred
day_array = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

# Input option lists
months = dates['MonthName'].unique()
patients = ['New Patient', 'Returning Patient']
genders = ['M', 'F']

display = dates[dates['Month'] == datetime.datetime.today().month]
display_label = datetime.datetime.today().strftime('%B')

# Define styles
dropdown_style = {'width': '25%', 'display': 'inline-block', 'padding': 10}

# Read in model object
with open('gb00.pkl', 'rb') as file:  
    model = pickle.load(file)

app = dash.Dash()

app.layout = html.Div(
	html.Div([
		html.H1('Appointment Scheduler'),
		html.H2('General Information'),

		html.Div([
			dcc.Dropdown(
				id = 'month',
				value = 'June',
				options = [{'label': i, 'value': i} for i in months]
			),
		],
		style = dropdown_style),
		
		html.Div([
			dcc.Dropdown(
				id = 'patient',
				value = 'New Patient',
				options = [{'label': i, 'value': i} for i in patients]
			),		
		],
		style = dropdown_style),

		html.Div([
			dcc.Dropdown(
				id = 'gender',
				value = 'M',
				options = [{'label': i, 'value': i} for i in genders]
			),
		],
		style = dropdown_style),


		dcc.Input(
			id = 'age',
			value = 25,
			type = 'number'
		),

		html.H2('Medical History'),
		dcc.Input(
			id = 'hipertension',
			value = 0,
			type = 'number'
		),
		dcc.Input(
			id = 'diabetes',
			value = 0,
			type = 'number'
		),
		dcc.Input(
			id = 'handcap',
			value = 0,
			type = 'number'
		),
		dcc.Input(
			id = 'sms',
			value = 0,
			type = 'number'
		),
		html.Div(
			id = 'output-month'
		),
	])
)

@app.callback(
	Output(component_id = 'output-month', component_property = 'children'),
	[Input(component_id = 'month', component_property = 'value')]
)
def update_cal(input_month):

	# Filter dates data to show selected month
	display = dates[dates['MonthName'] == input_month]
	display = display.reset_index()
	display = display.drop('index', axis = 1)

	# FIXME:: Run predictions on display data
	display.loc[:,'DaysBetween'] = display['Date'] - datetime.date.today()
	display.loc[:,'DaysBetween'] = display['DaysBetween'].dt.days

	display.loc[:, 'Gender'] = 1
	display.loc[:, 'Age'] = 24
	display.loc[:, 'Scholarship'] = 0
	display.loc[:, 'Hipertension'] = 0
	display.loc[:, 'Diabetes'] = 0
	display.loc[:, 'PreviousMiss'] = 0
	display.loc[:, 'Alcoholism'] = 0
	display.loc[:, 'Handcap'] = 0
	display.loc[:, 'SMS_received'] = 0

	pred_data = display.drop(
		[
	    	'MonthName', 'Month', 'Year', 'Day', 'Date', 'Weekday', 'DayOfWeek', 
	    	'DayLabel', 'WeekOfMonth',
		],
		axis = 1
	)


	probs = model.predict_proba(pred_data)
	probs = pd.Series([i[1] for i in probs])

	display['Prob'] = probs + np.random.uniform(-0.0001, 0.0001, len(display.index))

	# FIXME:: Dynamic ratio for graph based on number of weeks in month
	# Define calendar ratio
	cal_height = 1000


	cal_ratio = ((7 + 0.3) / 6)

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
					text = display['Prob'].round(5),
					textposition = 'middle center'
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
				height = cal_height,
				width = cal_height * cal_ratio
			)
		}
	)


if __name__ == '__main__':
	app.run_server(debug = True)








