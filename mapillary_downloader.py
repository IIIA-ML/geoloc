import os
from pathlib import Path
import geopandas as gpd
import wget
from mapillary_crawler import crawl_multipolygon
import time
import pandas as pd
import urllib
import urllib.request
from PIL import Image
from tqdm import tqdm

if not os.path.exists("data/bcn/spatial/terme-municipal.geojson"):
    site_url = 'https://raw.githubusercontent.com/martgnz/bcn-geodata/master/terme-municipal/terme-municipal.geojson'
    file_name = wget.download(site_url)

df_places = gpd.read_file('data/bcn/spatial/terme-municipal.geojson')

bcn_mp = df_places["geometry"].values[0]
bp = Path("bcn")
ACC_TOK = os.environ.get("MAPILLARY_ACC_TOK")


df = pd.DataFrame(columns=['id', 'url', 'lat', 'long', 'district'])
df.to_csv('data/bcn/mapillary.csv')

start = time.perf_counter()
crawl_multipolygon(bp, bcn_mp[0], ACC_TOK, df, force_new_ids=True)
finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2)} seconds')

df = pd.read_csv('data/bcn/mapillary.csv')
df = df.drop('Unnamed: 0', axis=1)
df.to_csv('data/bcn/mapillary.csv')
print('Csv correctly generated.')

# download images
with tqdm(total=df.shape[0]) as pbar: 
    for index, row in df.iterrows():

        if not os.path.exists(f'mapillary/train/{row.district}'):
            os.makedirs(f'mapillary/train/{row.district}')
        if not os.path.exists(f'mapillary/val/{row.district}'):
            os.makedirs(f'mapillary/val/{row.district}')

        path, dirs, files = next(os.walk(f'mapillary/train/{row.district}'))
        file_count = len(files)

        if (file_count < (0.9 * len(df[df['district'] == row.district]))):
            path = 'mapillary/train'
        else:
            path = 'mapillary/val'
            
        try:
            urllib.request.urlretrieve(row.url, f'{path}/{row.district}/{index}.jpeg')
            image = Image.open(f'{path}/{row.district}/{index}.jpeg') 
            image = image.resize((256, 256), Image.ANTIALIAS)
            image.save(f'{path}/{row.district}/{index}.jpeg')
        except:
            print("Image not available.")
        pbar.update(1)
        
print('Download finished!')