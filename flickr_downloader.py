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
    # download images into flickr directory
    with tqdm(total=df.shape[0]) as pbar: 
        for index, row in df.iterrows():

            if not os.path.exists(f'flickr/train/{row.district}'):
                os.makedirs(f'flickr/train/{row.district}')
            if not os.path.exists(f'flickr/val/{row.district}'):
                os.makedirs(f'flickr/val/{row.district}')

            path, dirs, files = next(os.walk(f'flickr/train/{row.district}'))
            file_count = len(files)

            # split into 90% training 10% validation
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
    
    
if __name__ == '__main__':
    main()