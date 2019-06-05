import dash 
import datetime
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

dates = pd.read_csv('Dates.csv')
display = dates[dates['Month'] == datetime.datetime.today().month]

app = dash.Dash()

app.layout = html.Div(
	children = [
		html.H1('Page Header'),
		dcc.Graph(
			id = 'calendar',
			figure = {
				'data': [
					go.Scatter(
						x = display['DayOfWeek'],
						y = 7 - display['WeekOfMonth'],
						mode = 'markers',
						marker = {
							'symbol': 'square'
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
						'showticklabels': False
                	},
                	margin = {'l': 40, 'b': 40, 't': 10, 'r': 10},
                	hovermode = 'closest'
				)
			}
		)
	]
)


if __name__ == '__main__':
	app.run_server(debug = True)