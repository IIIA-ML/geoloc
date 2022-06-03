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

def main():
    df = pd.read_csv('bcn/mapillary_raw.csv')
    df = df.drop_duplicates(subset=['url']).reset_index().drop('index', axis=1)
    df.to_csv('bcn/mapillary.csv', index=False)

    # download images into mapillary directory
    with tqdm(total=df.shape[0]) as pbar: 
        for index, row in df.iterrows():

            if not os.path.exists(f'mapillary/train/{row.district}'):
                os.makedirs(f'mapillary/train/{row.district}')
            if not os.path.exists(f'mapillary/val/{row.district}'):
                os.makedirs(f'mapillary/val/{row.district}')

            path, dirs, files = next(os.walk(f'mapillary/train/{row.district}'))
            file_count = len(files)

            # split into 90% training 10% validation
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
    
    
if __name__ == '__main__':
    main()