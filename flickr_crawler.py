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
                'eixampla',
                'sants',
                'montjuic',
                'les corts',
                'sarria',
                'sant gervasi',
                'gracia',
                'horta',
                'guinardo',
                'nou barris',
                'sant andreu',
                'sant marti']
MAX_COUNT = 10000

def main():       
    data_crawler = _data_crawler
    elems = []
    dictionary = PyDictionary()
    synonym_list = []
    save_counter = 0
    for elem in data_crawler:
        get_urls(elem, elem, MAX_COUNT, elems)
        
    save_csv(elems)
    
    df_districts = gpd.read_file('bcn/districtes.geojson')
    df_barris = gpd.read_file('bcn/gran-barri.geojson')
    df = pd.read_csv('bcn/flickr_raw.csv')
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
    #save_csv(elems)


def put_images(FILE_NAME):
    urls = []
    with open(FILE_NAME, newline="") as csvfile:
        doc = csv.reader(csvfile, delimiter=",")
        for row in doc:
            if row[1].startswith("https"):
                urls.append(row[1])
    """if not os.path.isdir(os.path.join(os.getcwd(), FILE_NAME.split("_")[0])):
        os.mkdir(FILE_NAME.split("_")[0])"""
    t0 = time.time()
    dup_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for url in enumerate(urls):
            if os.path.exists(os.path.join("E:", "dataset", "train", url[1].split("/")[-1])) or \
                    os.path.exists(os.path.join("E:", "dataset", "train_1", url[1].split("/")[-1]) or os.path.exists(os.path.join("E:", "dataset", "train_2", url[1].split("/")[-1]))):
                dup_count += 1
                print("already downloaded: {}".format(dup_count))
                continue
            executor.submit(download_from_url, url)
    t1 = time.time()
    print("Done with download, job took {} seconds".format(t1 - t0))


def download_from_url(url):
    try:
        resp = requests.get(url[1], stream=True)
        c = 0
        """
        while resp.status_code != 200 and c < 10:
            print("Failed to download")
            time.sleep(3)
            resp = requests.get(url[1], stream=True)
            c += 1
        """
        path_to_write = os.path.join("E:", "dataset", "train_3", url[1].split("/")[-1])
        outfile = open(path_to_write, 'wb')
        outfile.write(resp.content)
        outfile.close()
        print("Done downloading {} ".format(url[0] + 1))
    except Exception as e:
        print("Failed to download url number {} because {}".format(url[0], e))

def save_csv(elems):
    pdElems = pd.DataFrame(elems)
    pdElems = pdElems.drop_duplicates()
    print("Writing out the urls in the current directory")
    pdElems.to_csv('bcn/flickr_raw.csv', index=False)


def merge_csvs(main_path, diff_path):
    main = pd.read_csv(main_path, index_col=False)
    diff = pd.read_csv(diff_path, index_col=False)
    main.append(diff, ignore_index=True)
    main.to_csv(main_path)
    
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
