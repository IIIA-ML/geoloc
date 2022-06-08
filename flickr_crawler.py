import concurrent.futures
import csv
import os
import time
import geopandas as gpd
from shapely.geometry import shape, Point
import goslate
import requests
from PyDictionary import PyDictionary
from flickrapi import FlickrAPI
import pandas as pd
import sys

from tqdm import tqdm

key = os.environ.get("FLICKR_KEY")
secret = os.environ.get("FLICKR_SECRET")                      

_data_crawler = ['barcelona',
                'ciutat vella',
                'eixample',
                'sants montjuic',
                'les corts',
                'sarria sant gervasi',
                'gracia',
                'horta guinardo',
                'nou barris',
                'sant andreu',
                'sant marti']

_data_crawler_extended = ['barcelona',
                'ciutat vella',
                'eixample',
                'sants montjuic',
                'les corts',
                'sarria sant gervasi',
                'gracia',
                'horta guinardo',
                'nou barris',
                'sant andreu',
                'sant marti',
                'Sarrià, les Tres Torres i Vallvidrera',
                'Vallcarca, el Coll i la Salut',
                'la Vila de Gràcia',
                "el Camp d'en Grassot i Gràcia Nova",
                'el Guinardó',
                "el Carmel i Can Baró",
                "els Barris de la Vall d'Hebron",
                "Horta i la Font d'en Fargues",
                "Vilapicina, Porta, el Turó de la Peira i Can Peguera",
                "la Guineueta, Verdun i la Prosperitat",
                "Canyelles, les Roquetes i la Trinitat Nova",
                "Torre Baró, Ciutat Meridiana i Vallbona",
                "la Trinitat Vella, Baró de Viver i el Bon Pastor",
                "Sant Andreu",
                "la Sagrera, el Congrés i Navas",
                "el Clot i el Camp de l'Arpa",
                "el Parc, la Llacuna i la Vila Olímpica",
                "el Poblenou i Diagonal Mar",
                "el Besòs, el Maresme i Provençals",
                "Sant Martí, la Verneda i la Pau",
                "el Raval",
                "el Barri Gòtic",
                "la Barceloneta",
                "Sant Pere, Santa Caterina i la Ribera",
                "el Fort Pienc",
                "la Sagrada Família",
                "la Dreta de l'Eixample",
                "l'Antiga Esquerra de l'Eixample",
                "la Nova Esquerra de l'Eixample",
                "Sant Antoni",
                "el Poble Sec i Montjuïc",
                "la Marina i la Zona Franca - Port",
                "la Font de la Guatlla, Hostafrancs i la Bordeta",
                "Sants i Badal",
                "les Corts",
                "la Maternitat i Sant Ramon",
                "Pedralbes",
                "Vallvidrera, el Tibidabo i les Planes",
                "Sarrià i les Tres Torres",
                "Sant Gervasi - la Bonanova i el Putget"
                ]
MAX_COUNT = 1000000

def main():       
    data_crawler = _data_crawler
    elems = []
    dictionary = PyDictionary()
    synonym_list = []
    save_counter = 0
    for elem in data_crawler:
        get_urls(elem, elem, MAX_COUNT, elems)
    
    filename = 'bcn/flickr_raw.csv'
    save_csv(elems, filename)
    
    df_districts = gpd.read_file('bcn/districtes.geojson')
    df_barris = gpd.read_file('bcn/gran-barri.geojson')
    df = pd.read_csv(filename)
    label_imgs(df, df_districts, df_barris)


def get_urls(image_tag, term, MAX_COUNT, elems):
    print("Fetching urls for {}".format(term))
    flickr = FlickrAPI(key, secret)
    count = 0
    completed = False
    page = 1
    stop_counter = 0
    switch_date = 0
    end_date = 1590479033
    start_date = 1580114633
    DELTA_DATE = 10364400
    
    with tqdm(total=MAX_COUNT, position=0, leave=True) as pbar:
        while count < MAX_COUNT and completed is False and stop_counter < 3:
            try:

                photos = flickr.photos.search(text=term,
                                              tags=term,
                                              extras='url_sq, url_t, url_s, url_q, url_m, url_n, url_z, url_c, url_l, url_o, geo',
                                              sort='date-taken-asc',
                                              geo_context=2,
                                              has_geo=1,
                                              page=page,
                                              per_page=500
                                              # min_taken_date=start_date,
                                              # max_taken_date=end_date
                                              )

                photos = photos.find('photos')
                if page == photos.get('pages'):
                    completed = True
                page += 1
                
                urls = []
                photos = photos.findall('photo')
                c = 0
                
                for photo in photos:
                    pbar.update(1)
                    if count < MAX_COUNT:
                        count += 1
                        try:
                            url = photo.get('url_m')
                            lat = photo.get('latitude')
                            long = photo.get('longitude')
                            
                            if (url is not None):
                                try:
                                    elems.append({'url': url,
                                                  'lat': lat,
                                                  'long': long,
                                                  'tag': image_tag})
                                    c += 1
                                except Exception as e:
                                    print(e)
                                    count -= 1
                            else:
                                pbar.update(-1)
                                count -= 1
                        except Exception as e:
                            print("Url for image number {} could not be fetched because {}".format(count, e))
                    else:
                        print("Done fetching urls, fetched {} urls".format(len(elems)))
                        break
                if c == 0:
                    stop_counter += 1
                else:
                    stop_counter = 0

                if switch_date == 10:
                    switch_date = 0
                    stop_counter += 1
                    page = 300
                    end_date = start_date
                    start_date -= DELTA_DATE
            except:
                print('Server ERROR')
    print("Stop fetching urls for query {}".format(term))

    
def save_csv(elems, filename):
    pdElems = pd.DataFrame(elems)
    pdElems = pdElems.drop_duplicates()
    print("Writing out the urls in the current directory")
    pdElems.to_csv(filename, index=False)
    
    
def label_imgs(df, df_districts, df_barris):
    
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

    # df = df.drop(['Unnamed: 0', 'tag'], axis=1).reset_index().drop('index', axis=1)
    df = df[df['district']!=""]
    df = df[df['neighborhood']!=""]
    df = df.drop_duplicates(subset=['url']).reset_index().drop('index', axis=1)
    df.to_csv('bcn/flickr.csv', index=False)


if __name__ == '__main__':
    main()
