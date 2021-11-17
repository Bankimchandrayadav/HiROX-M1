# %% [markdown]
# # About
# 1. This notebook prepares the modelled *daily precipitation* dataset (RENOJ-2) from the onset time of GPM data i.e. 2000 June 01




# %% [markdown]
# # Libs and functions
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
import subprocess




# %% [markdown]
# # Station Key
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




# %% [markdown]
# # Read modelled and GPM daily files 
# [1] read the files 
rasMod = sorted(glob.glob("../../3_RSData/1_Rasters/GeneratedRasters/01_Daily/06_1972_2018_GPM_APHRO/*.tif"))
rasGPM = sorted(glob.glob("../../3_RSData/1_Rasters/1_GPM/daily_to_tiff_rsmpld/*.tif"))

# [2] subset modelled data to 2010-2020
# [2.1] find the index of dates = 2000-06-01 in modelled data
dateSearch = '2000-06-01'
for i in range(len(rasMod)):  
    if dateSearch in rasMod[i]:
        print(rasMod[i], 'at index', i)  

# [2.2] subset the data
rasMod = rasMod[10379:]

# [3] subset GPM data to 2010-2020 
# [3.1] find the index of dates = 2010-01-01 in GPM data 
dateSearch1 = '2018_05_31'
for i in range(len(rasGPM)):  
    if dateSearch1 in rasGPM[i]:
        print(rasGPM[i], 'at index', i)  

# [3.2] subset the data
rasGPM = rasGPM[:6574]




# %% [markdown]
# # Prepare 'X'
# [1.1] prepare the constant part of 'X' for training
XConst = pd.DataFrame()
elev = rio.open("../../3_RSData/1_Rasters/DEM/02_srtm_epsg_32644.tif").read(1)
aspect = rio.open("../../3_RSData/1_Rasters/DEM/03_srtm_epsg_32644_aspect.tif").read(1)
slope = rio.open("../../3_RSData/1_Rasters/DEM/04_srtm_epsg_32644_slope.tif").read(1)
XConst['elev'] = elev.flatten()  # add info from above files to X
XConst['aspect'] = aspect.flatten()
XConst['slope'] = slope.flatten()
row, col = np.zeros((66,70)), np.zeros((66,70))  # add (row, col) to X
for a in range(66):
    for b in range(70):
        row[a,b], col[a,b] = a,b
XConst['row'] = row.flatten()
XConst['col'] = col.flatten()  

# [1.2] repeat the dataframe n times where n = no. of rasters 
XConstFull = pd.concat([XConst]*len(rasGPM), ignore_index=True)

# [1.3] prepare the variable part of 'X' 
XGPM = pd.DataFrame(columns=['gpm'])
for i in td(range(len(rasGPM)), desc="Preparing GPM part of 'X'"):
    tempdf = pd.DataFrame(columns=['gpm'], data=rio.open(rasGPM[i]).read(1).flatten())
    XGPM = pd.concat([XGPM,tempdf], ignore_index=True)

# [1.4] prepare complete 'X' 
X = pd.concat([XConstFull, XGPM], axis=1)

# [1.5] fill up nans
X.interpolate(method='linear', inplace=True)
X.fillna(method='bfill', inplace=True)  # in situations when the above filling fails




# %% [markdown]
# # Prepare 'y'
y = pd.DataFrame(columns=['mod'])
for i in td(range(len(rasMod)), desc="Preparing 'y'"):
    tempdf1 = pd.DataFrame(columns=['mod'], data=rio.open(rasMod[i]).read(1).flatten())
    y = pd.concat([y,tempdf1], ignore_index=True)




# %% [markdown]
# # Train 'X' with 'y'
start = time.time()
regressor = DecisionTreeRegressor(random_state=0)
regressor.fit(X, y)
print('Training time:', np.round((time.time()-start)/60,2), 'mins')




# %% [markdown]
# # Predict
# [1] read the daily GPM files 
rasGPMTest = sorted(glob.glob("../../3_RSData/1_Rasters/1_GPM/daily_to_tiff_rsmpld/*.tif"))

# [2] prepare variable part of XTest
for i in td(range(len(rasGPMTest)), desc='Making maps without stations'):
    XTestGPM = pd.DataFrame(columns=['gpm'], data=rio.open(rasGPMTest[i]).read(1).flatten())

    # [3] prepare complete XTest by appending variable and const parts
    XTest = pd.concat([XConst, XTestGPM], axis=1)

    # [4] predict 
    yPred = regressor.predict(XTest).reshape(66,70)

    # [5] save the output to tiff files
    # [5.1] get the filename, date, etc to save the file
    fileName = rasGPMTest[i].split('/')[-1]  # filename extracted from path
    date = fileName.split('.')[0].replace("_","-")  # date extracted from filename
    outDir = "../../3_RSData/1_Rasters/GeneratedRasters/01_Daily/07_Product2/"

    # [5.2] save the files as tiff 
    referenceRas = gdal.Open(rasGPM[0])
    outMap = gdal.GetDriverByName('GTiff').Create(
        outDir + "{}.tif".format(date), 
        xsize=referenceRas.RasterXSize, 
        ysize=referenceRas.RasterYSize, 
        bands=1, 
        eType=gdal.GDT_Float32)  # geotiff created
    outMap.SetGeoTransform(referenceRas.GetGeoTransform())  # geotransform
    outMap.SetProjection(referenceRas.GetProjection())  # projection set 
    outMap.GetRasterBand(1).WriteArray(yPred)  # data in file set 
    outMap=None  # geotiff closed 




# %% [markdown]
# # Open output folder
subprocess.Popen(["xdg-open", outDir])
print('Time elapsed: {} mins'.format(np.round((time.time()-start)/60, 2)))



# %%



