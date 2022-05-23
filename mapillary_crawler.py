from pathlib import Path
from filelock import FileLock
from shapely.geometry import box, Point, shape
import geopandas as gpd
import concurrent.futures
import requests
from tqdm import tqdm
import json
import pandas as pd

def crawl_box(bounds, token):
    coords = "{},{},{},{}".format(*bounds)
    # retrieve images in explicitated coordinates
    # url = "https://graph.mapillary.com/images?access_token="+token+"&fields=id&bbox="+coords+"&limit=20"  # limited to 20
    url = "https://graph.mapillary.com/images?access_token="+token+"&fields=id&bbox="+coords
    payload={}
    headers = {}
    try:
        response = requests.get(url, headers=headers, data=payload)

        #print(response.text[:10])  # to visualize which response produces a valid id list of retrieved images

        response = response.json()
    
        while ("error" in response):
            print("Error, retrying ", url)
            response = requests.get(url, headers=headers, data=payload)
            response = response.json()
    except Exception as exc:
        print('%s generated an exception: %s' % (url, exc))
        raise exc 
    return response
    
def crawl_box_rec(executor, lock, csv_file, token, mp, bbox):
    try:
        if not mp.intersects(bbox):
            print("Box is outside multipolygon, not crawling")
            return
        bounds = bbox.bounds
        response = crawl_box(bounds, token)
        images = response["data"]
        if len(images) == 2000:
            print("Splitting box ", bounds)
            # Too many images, split box into 4
            half_point_x = (bounds[0] + bounds[2]) / 2.
            half_point_y = (bounds[1] + bounds[3]) / 2.
            bboxes = [box(bounds[0], bounds[1], half_point_x, half_point_y),
                  box(half_point_x, bounds[1], bounds[2], half_point_y),
                  box(bounds[0], half_point_y, half_point_x, bounds[3]),
                  box(half_point_x, half_point_y, bounds[2], bounds[3])
                 ]
            futures = []
            for bb in bboxes:
                future = executor.submit(crawl_box_rec, executor, lock, csv_file, token, mp, bb)
                futures.append(future)
            concurrent.futures.wait(futures)
            #for future in futures:
            #    try:
            #        print(future)
            #        data = future.result()
            #        print(future, "done")
            #    except Exception as exc:
            #        print('%s generated an exception: %s' % (bb.bounds, exc))
            #    #else:
            #    #    print('%r page is %d bytes' % (url, len(data)))
        else:
            print("Finished box ", bounds, " with ", len(images), " image candidates")
            with lock:
                with open(csv_file, "a") as f:
                    f.writelines([image["id"]+"\n" for image in images])
    except Exception as exc:
        print("Exception:",exc)

def ids_filename(bp):
    csv_file = bp / "ids.csv"
    return csv_file

# Crawls ids and stores them in ids.csv file
def crawl_multipolygon_ids(basepath:Path, mp, token:str, df, force_new_ids=True):
    bbox = box(*mp.bounds)
    basepath.mkdir(exist_ok=True)
    lock_filename = basepath / "ids.csv.lock"
    #lock_filename.touch()
    lock = FileLock(lock_filename)
    
    csv_file = ids_filename(basepath)
    if force_new_ids:
        with open(csv_file,"w") as f:
            pass
    else:
        csv_file.touch()
    #with open(csv_file,"w") as f:
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
        #crawl_box_rec(executor, lock, csv_file, token, mp, bbox)
        future = executor.submit(crawl_box_rec, executor, lock, csv_file, token, mp, bbox)
        try:
            print("Finished all", future.result())
        except Exception as exc:
            print('%s generated an exception: %s' % (bbox.bounds, exc))
        #executor.shutdown(wait=True)
    
def get_info_from_id(index, token):
    url = "https://graph.mapillary.com/"+str(index)+"?access_token="+token+"&fields=id,computed_geometry,detections.value,captured_at,thumb_1024_url,height,width"
    payload={}
    headers = {}
    # retrieve data of a specific image from its ID
    response = requests.get(url, headers=headers, data=payload).json()
    return response

def make_file_name(basepath:Path, index, prefix=".png"):
    start = 0
    path = basepath
    for i in range(3):
        end = start + 2
        path = path / index[start:end]
        start = end
    path.mkdir(parents=True, exist_ok=True)
    outfile = path / (index + prefix)
    return outfile

def download_image(basepath:Path, d):
    index = d['id']
    url = d['thumb_1024_url']
    outfile = make_file_name(basepath, index)
    if not outfile.exists():
        img = requests.get(url)
        with open(outfile, "wb") as f:
            f.write(img.content)
            
def process_index(basepath:Path, mp, token, index, df):
    #print(index)
    outfile = make_file_name(basepath, index, prefix=".metadata")
    #print(outfile)
    if outfile.exists():
        with open(outfile,"r") as f:
            d = json.load(f)
    else:
        d = get_info_from_id(index, token)
        with open(outfile,"w") as f:
            json.dump(d,f)
    
    #print(d)
            
                
    df_places = gpd.read_file('districtes.geojson')
    #print(df_places)
    coord = d["computed_geometry"]["coordinates"]
    p = Point(coord[0],coord[1])
    if mp.contains(p):
        #print(p)
       
        for district in range(0,len(df_places)):
            #print(district)
            try:
                polygon = shape(df_places['geometry'][district])
            except:
                print("Error")
                continue
            if polygon.contains(p):
                #print(d['thumb_1024_url'])
                new_row = pd.DataFrame({'id': d['id'], 'url': d['thumb_1024_url'], 'lat': coord[0], 'long': coord[1],
                               'district': df_places['NOM'][district]}, index=[0])
                new_row.to_csv('mapillary.csv', index=True, header=False, mode='a')
                #print(new_row)
                #new_row = {'id':d['id'], 'url': d['thumb_1024_url'], 'lat': coord[0], 'long': coord[1],
                               #'district': df_places['NOM'][district]}
                #df = df.append(new_row, ignore_index = True)
                #df = pd.concat([df, new_row], ignore_index=True, axis=0)
                #print(df)
    #outfile = make_file_name(basepath, index, prefix=".isinside")
    #outfile.touch()
    ###print(outfile)
    #download_image(basepath, d)
        
def bunchify(l, size):
    n = len(l)
    start = 0
    while start <= n:
        end = min(start + size, n + 1)
        yield l[start:end]
        start = end

def process_id_bunch(bp, mp, token, id_bunch, df):
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(lambda index:process_index(bp, mp, token, index, df), id_bunch)

def process_all_ids(bp, mp, token, ids, df, bunch_size=2000):
    for id_bunch in tqdm(bunchify(ids, bunch_size)):
        #print(id_bunch)
        process_id_bunch(bp, mp, token, id_bunch, df)
        
def crawl_multipolygon(basepath:Path, mp, token:str, df, force_new_ids=False):
    csv_file = ids_filename(basepath)
    if not csv_file.exists() or force_new_ids:
        crawl_multipolygon_ids(basepath, mp, token, df, force_new_ids=True)
    with open(csv_file,"r") as f:
        ids = f.read().splitlines()
    print(len(ids))
    process_all_ids(basepath, mp, token, ids, df)