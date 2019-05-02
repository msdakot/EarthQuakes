"""
This data visualization makes use of Earthquakes NCEDCAPI, describing
all quakes events in Northern California, registered by US goverment since 1988.

"""

import os
import io

import color_scale
import dash

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import requests
import geopandas as gpd
import datetime
from shapely.geometry import Point

import plotly.offline as py
import plotly.graph_objs as go


from dash.dependencies import Input, Output
# from process_df import process_df


mapbox_access_token = 'pk.eyJ1IjoiaXZhbm5pZXRvIiwiYSI6ImNqNTU0dHFrejBkZmoycW9hZTc5NW42OHEifQ._bi-c17fco0GQVetmZq0Hw'

app = dash.Dash(name=__name__)
app.config.supress_callback_exceptions = True
# server = app.server
# server.secret_key = os.environ.get("SECRET_KEY", "secret")

# Color scale for heatmap (green-to-red)
color_scale = color_scale.GREEN_RED

# Load styles
css_url = 'https://codepen.io/msdakot/pen/BEbawM.css'
css_bootstrap_url = 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/css/bootstrap.min.css'
app.css.append_css({
    "external_url": [css_bootstrap_url, css_url],
})

# calling the data 
# credits : https://curl.trillworks.com for converting the curl command to python request code

headers = {
    'Pragma': 'no-cache',
    'Origin': 'http://ncedc.org',
    'Accept-Encoding': 'gzip, deflate',
}

data = {
  'format': 'nccsv',
  'mintime': '1990/01/01,00:00:00',
  'maxtime': '',
  'minmag': '2.5',
  'maxmag': '',
  'mindepth': '',
  'maxdepth': '',
  'minlat': '',
  'maxlat': '',
  'minlon': '',
  'maxlon': '',
  'etype': 'E',
  'keywds': '',
  'outputloc': 'web',
  'searchlimit': '1000000'
}

response = requests.post('http://www.ncedc.org/cgi-bin/catalog-search2.pl', headers=headers, data=data)

d=response.text[290:-22]
df = pd.read_csv(io.StringIO(d))


geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]

df= gpd.GeoDataFrame(df,crs={'init' :'epsg:4326'}, geometry=geometry)

# data modifications 

df['date'] = pd.to_datetime(df['DateTime'],unit='ns')
df['year']= df['date'].dt.year
df['month']= df['date'].dt.month


# Get all valuable column headers
to_skip = ['Latitude',  'Longitude',  'year', 'date', 'DateTime','Source',"EventID","geometry",'month']
main_columns = [x for x in df.columns if x not in to_skip]


dfmax = df.groupby('year', as_index=False)[
    'Depth', 'Magnitude', 'Distance', 'Gap'].max()

dfmean = df.groupby('year', as_index=False)[
    'Depth', 'Magnitude', 'Distance', 'Gap'].mean()

dfmedian = df.groupby('year', as_index=False)[
    'Depth', 'Magnitude', 'Distance', 'Gap'].median()

dfmin = df.groupby('year', as_index=False)[
    'Depth', 'Magnitude', 'Distance', 'Gap'].min()


# Layout generation
app.layout = html.Div([
    # LANDING
    html.Div(
        className='section',
        children=[
            html.H1('Great EarthQuakes', className='landing-text')
        ]
    ),
    html.Div(
        className='content',
        children=[
            # SLIDER ROW
            html.Div(
                className='col',
                children=[
                  html.Div(
                      id='slider',
                      children=[
                          dcc.Slider(
                              id='date-slider',
                              min=min(df['year']),
                              max=max(df['year']),
                              marks={str(date): str(date)
                                     for date in df['year'].unique()},
                              value=2015,
                          ),
                      ], style={
                          'background': '#191a1a',
                          'margin-bottom': '50px'
                      }
                  )
                ], style={
                    'background': '#191a1a',
                }),
#             # GRAPHS ROW
            html.Div(
                id='graphs',
                className='row',
                children=[
                    html.Div(
                        className='col-4',
                        children=[
                          dcc.Graph(
                              id='freq-graph',
                          ),
                        ]),
                    html.Div(
                        className='col-4',
                        children=[
                            dcc.Graph(
                                id='another-graph',
                            ),
                        ]),
                    html.Div(
                        className='col-4',
                        children=[
                            dcc.Graph(
                                id='plot-graph',
                            ),
                        ])
                ], style={
                    'padding-bottom': 100
                }
            ),
#             # INFO ROW
            html.Div(
                id='group-x',
                className='row',
                children=[
                    html.Div(
                        className='col-6',
                        children=[
                          html.Div(
                              className='row',
                              children=[
                                  html.Div(
                                      className='col-3',
                                      children=[
                                          html.H1(
                                              id='this-year',
                                              style={
                                                  'fontSize': 60,
                                                  'color': '#FFF'
                                              }
                                          ),
                                      ]
                                  ),
                                  html.Div(
                                      className='col-3',
                                      children=[
                                          html.H3(
                                              'Total Number of Earthquakes',
                                              id='this-year-1st',
                                              style={
                                                  'fontSize': 12,
                                                  'color': '#FFF'
                                              }
                                          ),
                                          html.H1(
                                              id='tol-EQ',
                                              style={
                                                  'fontSize': 30,
                                                  'color': '#FFF'
                                              }
                                          )
                                      ]),
                                  html.Div(
                                      className='col-3',
                                      children=[
                                          html.H3(
                                              'Max Depth recorded',
                                              id='this-year-2nd',
                                              style={
                                                  'fontSize': 12,
                                                  'color': '#FFF'
                                              }
                                          ),
                                          html.H1(
                                              id='max-depth',
                                              style={
                                                  'fontSize': 30,
                                                  'color': '#FFF'
                                              }
                                          )
                                      ]),
                                  html.Div(
                                      className='col-3',
                                      children=[
                                          html.H3(
                                              'Max Magnitude',
                                              id='this-year-3rd',
                                              style={
                                                  'fontSize': 12,
                                                  'color': '#FFF'
                                              }
                                          ),
                                          html.H1(
                                              id='max-mag',
                                              style={
                                                  'fontSize': 30,
                                                  'color': '#FFF'
                                              }
                                          )
                                      ])
                              ]),

                        ]),
                    html.Div(
                        className='col-3',
                        children=[
                            dcc.Dropdown(
                                id='xaxis-dd',
                                className='col',
                                options=[{'label': i, 'value': i}
                                         for i in main_columns],
                                value='Depth',
                            ),
                            html.Div(
                                className='col radius-group',
                                children=[
                                    dcc.RadioItems(
                                        id='xaxis-type',
                                        options=[
                                          {'label': i, 'value': i} for i in ['Linear', 'Log']
                                        ],
                                        value='log',
                                        labelStyle={
                                            'color': '#FFF'
                                        }
                                    ),
                                ])
                        ]),
                    html.Div(
                        className='col-3',
                        children=[
                            dcc.Dropdown(
                                id='yaxis-dd',
                                className='col',
                                options=[{'label': i, 'value': i}
                                         for i in main_columns],
                                value='Magnitude',
                            ),
                            html.Div(
                                className='col radius-group',
                                children=[
                                    dcc.RadioItems(
                                        id='yaxis-type',
                                        options=[
                                          {'label': i, 'value': i} for i in ['Linear', 'Log']
                                        ],
                                        value='log',
                                        labelStyle={
                                            'color': '#FFF'
                                        }
                                    ),
                                ])
                        ]),
                ]
            ),
#             # MAP ROW
            html.Div(
                className='row',
                children=[
                    # Main graph holding the map
                    dcc.Graph(
                        id='map-graph',
                        animate=True,
                        style={
                          'width': '100%',
                          'height': 800
                        }
                    ),
                ]),
            # ABOUT ROW
            html.Div(
                className='row',
                children=[
                  html.Div(
                    className='col',
                    children=[
                      html.P(
                        'Data extracted from:',
                          style={
                                  'color': '#ebebeb'
                                }),
                      html.A(
                          'Earthquake API',
                          href='https://earthquake.usgs.gov/fdsnws/event/1/',
                          style={
                                  'color': '#fff'
                                }
                      )                    
                    ]
                  ),
                  html.Div(
                    className='col',
                    children=[
                      html.P(
                        'Code avaliable at:',
                          style={
                                  'color': '#ebebeb'
                                }
                      ),
                      html.A(
                          'Github',
                          href='https://github.com/msdakot/EarthQuakes',
                          style={
                                  'color': '#fff'
                                }
                      )                    
                    ]
                  ),
                  html.Div(
                    className='col',
                    children=[
                      html.P(
                        'Made with:',
                          style={
                                  'color': '#ebebeb'
                                }
                      ),
                      html.A(
                          'Dash / Plot.ly',
                          href='https://plot.ly/dash/',
                          style={
                                  'color': '#fff'
                                }
                      )                    
                    ]
                  ),
                  html.Div(
                    className='col',
                    children=[
                      html.P(
                        'Developer:',
                          style={
                                  'color': '#ebebeb'
                                }
                      ),
                      html.A(
                          'Dhruvi Kothari',
                          href='https://twitter.com/Dhruvs04',
                          style={
                                  'color': '#fff'
                                }
                      )                    
                    ]
                  )                                                          
                ]
            )
        ],
        style={
            'padding': 40
        }
    )
]
)


@app.callback(
    Output('this-year', 'children'),
    [Input('date-slider', 'value')]
)

def update_text(year_value):
    """
    Callbacks for year text col
    """
    return str(year_value)


@app.callback(
    Output('tol-EQ', 'children'),
    [Input('date-slider', 'value')]
)

def update_text(year_value):
    """
    Callback for Magnitude col
    """    # data from current selected year
    dff = df[df['year'] == year_value]
    return '{} quakes'.format(str(dff['year'].count()))



@app.callback(
    Output('max-depth', 'children'),
    [Input('date-slider', 'value')]
)
def update_text(year_value):
    """
    Callbacks for Depth col
    """
    # data from current selected year
    dff = df[df['year'] == year_value]
    if(np.isnan(dff['Depth'].max())):
        return 'N/A'
    return '{} below sea level'.format(round(dff['Depth'].max()))

                              
@app.callback(
    Output('max-mag', 'children'),
    [Input('date-slider', 'value')]
)

def update_text(year_value):
    """
    Callback for Magnitude col
    """    # data from current selected year
    dff = df[df['year'] == year_value]
    return '{} Ricter Scale'.format(str(dff['Magnitude'].max()))






@app.callback(
    Output('freq-graph', 'figure'),
    [Input('date-slider', 'value')]
)
def update_graph(year_value):
    """
    Top Left graph callback
    """

    data = go.Data([
        go.Scatter(
            name='Max magnitude',
            # events qty
            x=np.arange(1988, year_value),
            # year
            y=dfmax['Magnitude'],
            mode='lines',
            marker={
                'symbol': 'circle',
                'size': 5,
                'color': 'rgb(248, 177, 149)'
            },
            hoverlabel={
                'bgcolor': '#FFF',
            },
        ),
        go.Scatter(
            name='Mean magnitude',
            # events qty
            x=np.arange(1988, year_value + 1),
            # year
            y=dfmean['Magnitude'],
            mode='lines',
            marker={
                'symbol': 'circle',
                'size': 5,
                'color': 'rgb(145, 102, 129)'
            },
            hoverlabel={
                'bgcolor': '#FFF',
            },
        ),
        go.Scatter(
            name='Median magnitude',
            # events qty
            x=np.arange(1988, year_value + 1),
            # year
            y=dfmedian['Magnitude'],
            mode='lines',
            marker={
                'symbol': 'circle',
                'size': 5,
                'color': 'rgb(153, 190, 149)'
            },
            hoverlabel={
                'bgcolor': '#FFF',
            },
        ),
        go.Scatter(
            name='Min magnitude',
            # events qty
            x=np.arange(1988, year_value + 1),
            # year
            y=dfmin['Magnitude'],
            mode='lines',
            marker={
                'symbol': 'circle',
                'size': 5,
                'color': 'rgb(221, 178, 124)'
            },
            hoverlabel={
                'bgcolor': '#FFF',
            },
        )
    ])
    layout = go.Layout(
        xaxis={
            'autorange': True,
            'color': '#FFF',
            'title': 'year',
        },
        yaxis={
            'autorange': True,
            'color': '#FFF',
            'title': 'approx. recorded magnitude (ricter scale)',
        },
        margin={
            'l': 40,
            'b': 40,
            't': 10,
            'r': 0
        },
        hovermode='closest',
        paper_bgcolor='#191a1a',
        plot_bgcolor='#191a1a',
    )

    return go.Figure(
        data=data,  # 54b4e4
        layout=layout
    )


    

@app.callback(
    Output('another-graph', 'figure'),
    [Input('date-slider', 'value')]
)
def update_mid(year_value):
    """
    Top Mid graph callback
    """

    traces = []
    marker_color = ''

    for year in df['year'].unique():
        if year < 2003:
            continue
        dff = df[df['year'] == year]
        if(year == year_value):
            marker_color = '#C2FF0A'
        elif year_value >= 2003:
              marker_color = '#FF0A47'        
        trace = go.Box(
            y=round(dff['Depth'],2),
            name=str(year),
            boxpoints='all',
            jitter=0.5,
            whiskerwidth=0.2,
            fillcolor=marker_color,
            marker=dict(
                size=2,
            ),
            line=dict(color=marker_color, width=1),
        )
        traces.append(trace)
        
    data = go.Data(traces,
                   style={
                       'color': '#000'})

    layout = go.Layout(
#         title='xyc',
        yaxis=dict(
            autorange=True,
            showgrid=True,
            zeroline=True,
            dtick=5,
            gridcolor='rgb(255, 255, 255)',
            gridwidth=1,
            zerolinecolor='rgb(255, 255, 255)',
            zerolinewidth=2,
        ),
        hoverlabel={
            'bgcolor': '#FFF',
            'font': {
                'color': 'black'
            },
        },    
        margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
        hovermode='closest',
        paper_bgcolor='#191a1a',
        plot_bgcolor='#191a1a',
    )
    return go.Figure(
        data=data,
        layout=layout
    )



@app.callback(
    Output('plot-graph', 'figure'),
    [Input('date-slider', 'value'),
     Input('xaxis-dd', 'value'),
     Input('xaxis-type', 'value'),
     Input('yaxis-dd', 'value'),
     Input('yaxis-type', 'value')]
)
def update_plot(year_value, xaxis_value, xaxis_type, yaxis_value, yaxis_type):
    """
    Top Right graph callback
    """

    dff = df[df['year'] == year_value]
    data = [
        go.Scatter(
            x=dff[xaxis_value],
            y=dff[yaxis_value],
            mode='markers',
            marker={
                'symbol': 'circle',
                'size': dff['Magnitude']**2,
                'color': 'rgb(214, 222, 191)',
                'line': {'color': 'rgb(112, 158, 135)'}
            }
        )
    ]

    layout = go.Layout(
        autosize=True,
        xaxis={
            'color': '#FFF',
            'autorange': True,
            'title': xaxis_value,
            'type': 'Linear' if xaxis_type == 'Linear' else 'log',
            'showspikes': True
        },
        yaxis={
            'color': '#FFF',
            'autorange': True,
            'title': yaxis_value,
            'type': 'Linear' if yaxis_type == 'Linear' else 'log'
        },
        margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
        hovermode='closest',
        paper_bgcolor='#191a1a',
        plot_bgcolor='#191a1a',
    )

    return go.Figure(
        data=data,
        layout=layout
    )



@app.callback(
    Output('map-graph', 'figure'),
    [Input('date-slider', 'value')]
)


def update_map(year_value):
    """
    Map graph callback
    """

    # Update dataframe with the passed value
    dff = df[df['year'] == year_value]

    # Paint mapbox into the data
    data = [
        go.Scattermapbox(
            lat=dff['Latitude'],
            lon=dff['Longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=(dff['Magnitude']**2.5),
                colorscale=color_scale,
                cmin=dff['Magnitude'].min(),
                color=dff['Magnitude'],
                cmax=dff['Magnitude'].max(),
                colorbar=dict(
                    title='Magnitude'
                ),
                opacity=0.5
            )
        )
    ]

    # Layout and mapbox properties
    layout = go.Layout(
        autosize=True,
        hovermode='closest',
        showlegend=False,
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
            lat=37.437,
            lon=-119.451
        ),
            pitch=0,
            zoom=5,
            style='dark'
        ),
        paper_bgcolor='#191a1a',
        plot_bgcolor='#191a1a',
    )

    return go.Figure(
        data=data,
        layout=layout
    )


# Run dash server
if __name__ == '__main__':
#     app.run_server(debug=True)
   app.run_server(host="0.0.0.0", port=5000, debug=True)
    
