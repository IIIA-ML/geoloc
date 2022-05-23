import os
import re
import json
import pandas as pd
import numpy as np
import requests
import itertools
import math
from tqdm import tqdm
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape, Point

df_districts = gpd.read_file('districtes.geojson')
df_barris = gpd.read_file('../gran-barri.geojson')
df = pd.read_csv('flickr_data.csv')

df['district'] = ""
df['neighborhood'] = ""

with tqdm(total=df.shape[0]) as pbar: 
    for index, row in df.iterrows():
        lat = row.lat
        long = row.long
        point = Point(long, lat)

        for district in range(0,len(df_districts)):
            polygon = shape(df_districts['geometry'][district])
            if polygon.contains(point):
                df.loc[index, 'district'] = df_districts['NOM'][district]

        for neighborhood in range(0,len(df_barris)):
            polygon = shape(df_barris['geometry'][neighborhood])
            if polygon.contains(point):
                df.loc[index, 'neighborhood'] = df_barris['NOM'][neighborhood]
        pbar.update(1)
        
df = df.drop(['Unnamed: 0', 'tag'], axis=1).reset_index().drop('index', axis=1)
df = df[df['district']!=""]
df = df[df['neighborhood']!=""]
df = df.drop_duplicates(subset=['url']).reset_index().drop('index', axis=1)
df.to_csv('data/bcn/flickr.csv', index=False)
print('Csv correctly generated.')

n_images = df['district'].value_counts().rename_axis('NOM').reset_index(name='counts')

df_districts = df_districts.merge(n_images, on='NOM', how='left')
df_districts['counts'] = df_districts['counts'].fillna(0)
df_districts.plot(column='counts', legend=True, figsize=(15,8))
plt.ylabel('Latitude')
plt.xlabel('Longitude')
plt.savefig('img/districts_dist.png')


df_districts['geometry'].plot()
plt.ylabel('Latitude')
plt.xlabel('Longitude')
plt.scatter(df['long'], df['lat'], alpha=0.5, s=2, c='red')
plt.savefig('img/districts_scatter_hd.png')

# download images
with tqdm(total=df.shape[0]) as pbar: 
    for index, row in df.iterrows():

        if not os.path.exists(f'flickr/train/{row.district}'):
            os.makedirs(f'flickr/train/{row.district}')
        if not os.path.exists(f'flickr/val/{row.district}'):
            os.makedirs(f'flickr/val/{row.district}')

        path, dirs, files = next(os.walk(f'flickr/train/{row.district}'))
        file_count = len(files)

        if (file_count < (0.9 * len(df[df['district'] == row.district]))):
            path = 'flickr/train'
        else:
            path = 'flickr/val'
            
        try:
            urllib.request.urlretrieve(row.url, f'{path}/{row.district}/{index}.jpeg')
            image = Image.open(f'{path}/{row.district}/{index}.jpeg') 
            image = image.resize((256, 256), Image.ANTIALIAS)
            image.save(f'{path}/{row.district}/{index}.jpeg')
        except:
            print("Image not available.")
        pbar.update(1)

print('Download finished!')