from traffic import download
from extract import extractTraffic
import os
import pandas as pd
import numpy as np
import glob
import sys
from multiprocessing import Pool
from functools import partial

def downloadExtractTrafficData(column, output_dir):
    lat = column['latitude']
    long = column['longitude']
    out = os.path.join(output_dir,f'img{lat}_{long}')
    download(lat, long, 20, out)
    data = extractTraffic(out)
    data['latitude'] = lat
    data['longitude'] = long
    return data

def downloadTrafficData(column, output_dir):
    lat = column['latitude']
    long = column['longitude']
    out = os.path.join(output_dir,f'img{lat}_{long}')
    download(lat, long, 19, out)
    return out

def extractTrafficData(imgs_dir):
    imgs_dir = imgs_dir['dir']
    imgs = imgs_dir.split('img')[-1]
    imgs = imgs.split('/')[0]
    lat, long = imgs.split("_")
    data = extractTraffic(imgs_dir)
    data['latitude'] = float(lat)
    data['longitude'] = float(long)
    return data

def downloadTrafficApply(func, output, data):
    return data.apply(func, axis=1, args=(output,))
def extractTrafficApply(func, data):
    return data.apply(func, axis=1, result_type="expand")

def parallelDownloadTraffic(data, output, processes=4):
    chunk_len = len(data)//processes
    chunks = 0
    if chunk_len > 0:
        chunks = (len(data) // chunk_len) -1
    data_chunk = []
    for i in range(chunks):
        data_chunk.append(data.iloc[chunk_len*i:chunk_len*(i+1)])
    data_chunk.append(data.iloc[chunk_len*chunks:len(data)])
    with Pool(processes) as pool:
        function = partial(downloadTrafficApply, downloadTrafficData, output)
        data = pd.concat(pool.map(function, data_chunk))
    data = data.apply((lambda col: glob.glob(f"{col}/*-*.png")))
    data = data.explode()
    return pd.DataFrame({'dir':data})

def parallelExtractTraffic(data, processes=None):
    if processes is None:
        processes = len(os.sched_getaffinity(0))
    chunk_len = len(data)//processes
    chunks = 0
    if chunk_len > 0:
        chunks = (len(data) // chunk_len) -1
    data_chunk = []
    for i in range(chunks):
        data_chunk.append(data.iloc[chunk_len*i:chunk_len*(i+1)])
    data_chunk.append(data.iloc[chunk_len*chunks:len(data)])
    with Pool(processes) as pool:
        function = partial(extractTrafficApply, extractTrafficData)
        data = pd.concat(pool.map(function, data_chunk))
    return data

def getTraffic(files, output):
    data = []
    for file in files:
        data.append(pd.read_csv(file))
    data = pd.concat(data)
    data = data.drop_duplicates(subset=["latitude", "longitude"])
    previous_out = None
    if os.path.exists(output):
        previous_out = pd.DataFrame({'dir':glob.glob(output+"/**/*-*-*.png", recursive=True)})
    traffic_out = parallelDownloadTraffic(data, output)
    if not previous_out is None:
        traffic_out = pd.concat([traffic_out, previous_out])
        traffic_out = traffic_out.drop_duplicates(subset=["dir"])
    traffic = parallelExtractTraffic(traffic_out)
    traffic = traffic.explode(['avg','max','day','hour'], ignore_index=True)
    return traffic

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"python {sys.argv[0]} [input csvs] [output_dir]")
    else:
        files = glob.glob(f'{sys.argv[1]}/*')
        if not os.path.exists(sys.argv[2]):
            os.mkdir(sys.argv[2])
        getTraffic(files, sys.argv[2]).to_csv(os.path.join(sys.argv[2], "traffic.csv"))
