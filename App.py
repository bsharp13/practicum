
# Import libraries
import dash 
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import datetime

from dash.dependencies import Input, Output

# Read in date data
dates = pd.read_csv('Dates.csv')
dates['Prob'] = np.random.uniform(0, 1, len(dates.index)) # pseudo model pred
day_array = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

display = dates[dates['Month'] == datetime.datetime.today().month]
display_label = datetime.datetime.today().strftime('%B')

# Read in model object

app = dash.Dash()

app.layout = html.Div(
	children = [
		html.H1('Appointment Scheduler'),
		dcc.Input(
			id = 'month',
			value = display_label,
			type = 'text'
		),
		dcc.Input(
			id = 'patient',
			value = 'New Patient',
			type = 'text'
		),
		dcc.Input(
			id = 'gender',
			value = 'M',
			type = 'text'
		),
		dcc.Input(
			id = 'age',
			value = 25,
			type = 'number'
		),
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

	]
)

@app.callback(
	Output(component_id = 'output-month', component_property = 'children'),
	[Input(component_id = 'month', component_property = 'value')]
)
def update_cal(input_month):

	# Filter dates data to show selected month
	display = dates[dates['MonthName'] == input_month]

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
						'colorbar': {
							'title': 'Probability of No Show',
							'len': 0.8,
							'tickformat': ".0%"
						}
					},
					text = display['Day'],
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








