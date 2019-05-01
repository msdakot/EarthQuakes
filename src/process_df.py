import numpy as np 
import requests
import pandas as pd
import io
from shapely.geometry import Point
import geopandas as gpd

def datfram():

    headers = {
        'Pragma': 'no-cache',
        'Origin': 'http://ncedc.org',
        'Accept-Encoding': 'gzip, deflate',
    }

    data = {
      'format': 'nccsv',
      'mintime': '1967/01/01,00:00:00',
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

    df.head()

    df['date'] = pd.to_datetime(df['DateTime'],unit='ns')
    df['year']= df['date'].dt.year
    df['month']= df['date'].dt.month
    return df



