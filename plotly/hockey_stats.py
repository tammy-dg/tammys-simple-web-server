from dash import Dash, dcc, html, Input, Output
import plotly.express as px

import pandas as pd

app = Dash(__name__)

# clean the data
# source - https://www.rotowire.com/hockey/stats.php
df = pd.read_csv('nhl_stats.csv')
# # Filter to two teams 
# df = df[df['Team'].isin(['TOR', 'MTL'])]
# print(df)

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                options=sorted(x for x in df['Team'].unique()),
                # label='Team',
                id='team-select',
                value='TOR'
            ),
            dcc.Dropdown(
                id='stats',
                options=['Games', 'G', 'A', 'Pts', 'PIM', 'SOG', 'Hits'],
                value=['Pts'],
                multi=True),
            dcc.Dropdown(
                id='position',
                options=sorted(x for x in df['Pos'].unique()),
                value=df['Pos'].unique(),
                multi=True),
        ], style={'width': '50%'})
    ]),

    dcc.Graph(id='nhl-stats'),

    # dcc.Slider(
    #     df['Year'].min(),
    #     df['Year'].max(),
    #     step=None,
    #     id='year--slider',
    #     value=df['Year'].max(),
    #     marks={str(year): str(year) for year in df['Year'].unique()},

    # )
])

@app.callback(
    Output('nhl-stats', 'figure'),
    Input('team-select', 'value'),
    Input('stats', 'value'),
    Input('position', 'value'))
def update_graph(team_name, stats, position):
    # filters
    dff = df[df['Team'] == team_name]
    dff = dff[dff['Pos'].isin(position)]
    # convert df to long format to plot the stats desired as a grouped barplot
    columns = ['Player Name', 'Team'] + stats
    dff = dff[columns]
    dff_long = pd.melt(dff, id_vars=['Player Name', 'Team'], value_vars=stats)

    fig = px.bar(dff_long, y='Player Name', x='value', color='variable', barmode='group')

    # fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
    #                  y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
    #                  hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')


    return fig



if __name__ == '__main__':
    app.run_server(debug=True)
