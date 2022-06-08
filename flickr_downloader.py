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


def main():    
    df = pd.read_csv('geoloc-data/bcn/flickr.csv')    
    # download images into flickr directory
    with tqdm(total=df.shape[0]) as pbar: 
        for index, row in df.iterrows():

            if not os.path.exists(f'flickr/train/{row.district}'):
                os.makedirs(f'flickr/train/{row.district}')
            if not os.path.exists(f'flickr/val/{row.district}'):
                os.makedirs(f'flickr/val/{row.district}')
            if not os.path.exists(f'flickr/test/{row.district}'):
                os.makedirs(f'flickr/test/{row.district}')

            path, dirs, files = next(os.walk(f'flickr/train/{row.district}'))
            path_val, dirs_val, files_val = next(os.walk(f'flickr/val/{row.district}'))
            file_count = len(files)
            file_count_val = len(files_val)

            # split into 80% training 10% validation 10% test
            if (file_count < (0.8 * len(df[df['district'] == row.district]))):
                path = 'flickr/train'
            elif (file_count_val < (0.1 * len(df[df['district'] == row.district]))):
                path = 'flickr/val'
            else:
                 path = 'flickr/test'   

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