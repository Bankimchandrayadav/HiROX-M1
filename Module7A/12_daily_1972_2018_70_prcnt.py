# %% [markdown]
# # About
# > 1. This code prepares the modelled *daily precipitation* dataset for the duration 1972-2018  by usign only *70% of the stations*
# > 2. Here, ML is applied and learning is done over APHRODITE data, BKGN data and STN data




# %% [markdown]
# %% [markdown]
## Libs and functions
import pandas as pd, glob, geopandas as gpd, rasterio as rio, numpy as np, matplotlib.pyplot as plt, os, gdal, os, shutil, time 
from datetime import datetime
from tqdm.notebook import tqdm as td 
from sklearn.tree import DecisionTreeRegressor
start = time.time()
def fresh(where):  
    if os.path.exists(where):
        shutil.rmtree(where)
        os.mkdir(where)
    else:
        os.mkdir(where)




# %% [markdown]
# %% [markdown]
## Station Key  
# [1] read station shape file 
stnKey = gpd.read_file(r"../../3_RSData/2_Vectors/1_Stations/01_stations_UTM44N1.shp") 
stnKey.sort_values('Sno', inplace=True)  # sort all cols according to 'Sno'
stnKey.reset_index(drop=True, inplace=True)  # reset index 

# [2] read dem, slope and aspect files
ds = rio.open("../../3_RSData/1_Rasters/DEM/02_srtm_epsg_32644.tif")  # dem 
dsAspect = rio.open("../../3_RSData/1_Rasters/DEM/03_srtm_epsg_32644_aspect.tif")  # aspect 
dsSlope  = rio.open("../../3_RSData/1_Rasters/DEM/04_srtm_epsg_32644_slope.tif")  # slope 

# [3] add info from above files in columns
stnKey["row"], stnKey["col"] = rio.transform.rowcol(ds.transform, stnKey.geometry.x, stnKey.geometry.y)  # 3 add more cols to stnkey - row,col cols added
coords = [(x,y) for x, y in zip(stnKey.geometry.x, stnKey.geometry.y)]  # x,y coords zippped
stnKey["srtm"]  = [x[0] for x in ds.sample(coords)]  # elevation info  added
stnKey["aspect"]  = [x[0] for x in dsAspect.sample(coords)]  # aspect info added
stnKey["slope"]  = [x[0] for x in dsSlope.sample(coords)]  # slope info added

# [4] remove duplicates from stnKey
# [4.1] get the row, cols in a list 
rowcols = [(x,y) for x, y in zip(stnKey.row, stnKey.col)]

# [4.2] get the ids of duplicates (taken from: https://stackoverflow.com/a/23645631)
result=[idx for idx, item in enumerate(rowcols) if item in rowcols[:idx]]
stnKey.drop(index=result, inplace=True)  # duplicates removed 
stnKey.reset_index(drop=True, inplace=True)  # index reset [now 26 stations in total]



