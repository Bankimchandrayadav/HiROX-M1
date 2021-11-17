# %% [markdown]
# # About
# This code prepares the modelled *daily precipitation* dataset for the duration 2000-2018
### Method
# 1. Here, ML is applied and learning is done over GPM data, BKGN data and STN data




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
## Station Key  
# [1] read station shape file 
stnKey = gpd.read_file("../../3_RSData/2_Vectors/1_Stations/01_stations_UTM44N1.shp")
stnKey.sort_values('Sno', inplace=True)  # sort all cols according to 'Sno'
stnKey.reset_index(drop=True, inplace=True)  # reset index 

# [2] read dem, slope and aspect files
ds = rio.open("../../3_RSData/1_Rasters/DEM/02_srtm_epsg_32644.tif")  # dem 
dsAspect = rio.open("../../3_RSData/1_Rasters/DEM/03_srtm_epsg_32644_aspect.tif")  # aspect 
dsSlope  = rio.open("../../3_RSData/1_Rasters/DEM/04_srtm_epsg_32644_slope.tif")  # slope 

# [3] add info from above files in columns
stnKey["row"], stnKey["col"] = rio.transform.rowcol(ds.transform, stnKey.geometry.x, stnKey.geometry.y)  # row,col cols added
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
## Read and subset station data
# [1] read station data 
dfStn = pd.read_csv("../../2_ExcelFiles/01_StationData/04_daily.csv")  

# [2] subset station data to bkgn's duration 
# [2.1] change the datatype of dates
for i in range(len(dfStn)):  
    dateString = (dfStn.Date[i]).split('/')  # date read as string
    dfStn.Date[i] = datetime(year=int(dateString[2]), month=int(dateString[1]), day=int(dateString[0]))  # dtype converted 

# [2.2] set the start and end dates 
dateBegin = datetime(year=2000, month=6, day=1)  
# dateEnd = datetime(year=2009, month=12, day=31)  # subset till 2009-12-31
dateEnd = datetime(year=2018, month=5, day=31)  # subset till 2018-05-31

# [2.3] subset to bkgn's duration
dfStn = dfStn[(dfStn.Date>=dateBegin) & (dfStn.Date<=dateEnd)]
dfStn.set_index('Date', inplace=True)  # dates set as index 
dfStn.index.names=[None] # extra rows in col heads removed
dfStn = dfStn[stnKey.Station]  # set according to station key
dfStn = dfStn.astype('float32')




# %% [markdown]
# # Read and subset GPM data
rasGPM = sorted(glob.glob("../../3_RSData/1_Rasters/1_GPM/daily_to_tiff_rsmpld/*.tif")) 
# dateEnd = '2009_12_31'  # subset data fill 2009 Dec 31
dateEnd = '2018_05_31'  # subset data till 2018 May 31
for i in range(len(rasGPM)):  # find the index of 20180531 file 
    if dateEnd in rasGPM[i]:
        print(rasGPM[i], 'at index', i)  # index of 20180531 file found 
rasGPM = rasGPM[:6574]  # subset done




# %% [markdown]
## Remove old files 
outDir = "../../3_RSData/1_Rasters/GeneratedRasters/01_Daily/01_2000_2018_GPM/"
fresh(outDir)




# %% [markdown]
## Make maps - Decision Tree regressor 
# [1] prepare 'X' for GPM data
XGPM = pd.DataFrame()
elev = rio.open("../../3_RSData/1_Rasters/DEM/02_srtm_epsg_32644.tif").read(1)
aspect = rio.open("../../3_RSData/1_Rasters/DEM/03_srtm_epsg_32644_aspect.tif").read(1)
slope = rio.open("../../3_RSData/1_Rasters/DEM/04_srtm_epsg_32644_slope.tif").read(1)
XGPM['elev'] = elev.flatten()  # add info from above files to XGPM
XGPM['aspect'] = aspect.flatten()
XGPM['slope'] = slope.flatten()
row, col = np.zeros((66,70)), np.zeros((66,70))  # add (row, col) to XGPM
for a in range(66):
    for b in range(70):
        row[a,b], col[a,b] = a,b
XGPM['row'] = row.flatten()
XGPM['col'] = col.flatten()  # XGPM prepared 

# [2] prepare 'X' for station data 
XSTN = stnKey.iloc[:,6:]
XSTN.rename(columns={'srtm':'elev'}, inplace=True)
XSTN = XSTN[XGPM.columns]

# [3] prepare 'X' for BKGN data  
XBKGN = XGPM.copy()

# [4] append them  
X = pd.concat([XGPM, XSTN, XBKGN])
X.reset_index(drop=True, inplace=True)




#%% [markdown]
## Make maps [contd.]
# [2] prepare 'y'
# [2.1] prepare 'y' from GPM data 
for i in td(range(len(rasGPM)), desc='Making maps'):
    yGPM = rio.open(rasGPM[i]).read(1).flatten()
    fileName = rasGPM[i].split('/')[-1]  # filename extracted from path
    date = fileName.split('.')[0].replace('_','-')  # date extracted from filename

    # [2.2] prepare 'y' from station data 
    ySTN = dfStn.loc["{}".format(date)].values   

    # [2.3] prepare 'y' from bkgn daily data
    yBKGN = rio.open("../../3_RSData/1_Rasters/2_BKGN/05_DailyBasedOnGPM/{}".format(fileName)).read(1).flatten()

    # [2.4] append them  
    y = pd.DataFrame(np.concatenate([yGPM, ySTN, yBKGN]))
    y.interpolate(method='linear', inplace=True)  # NaNs filled

    # [3] train 'X' with 'y'
    regressor = DecisionTreeRegressor(random_state=0)
    regressor.fit(X, y)

    # [4] predict results 
    yPred = regressor.predict(XGPM).reshape(66,70)

    # [5] save the output to tiff files
    referenceRas = gdal.Open(rasGPM[0])
    date = rasGPM[i].split('/')[-1].split('.')[0]  # date of file extracted
    outMap = gdal.GetDriverByName('GTiff').Create(outDir + "{}.tif".format(date), xsize=referenceRas.RasterXSize, ysize=referenceRas.RasterYSize, bands=1, eType=gdal.GDT_Float32)  # geotiff created
    outMap.SetGeoTransform(referenceRas.GetGeoTransform())  # geotransform set
    outMap.SetProjection(referenceRas.GetProjection())  # projection set (UTM44N)
    outMap.GetRasterBand(1).WriteArray(yPred)  # data in file set 
    outMap=None  # geotiff closed 




# %% [markdown]
## Get values at station points from modelled outputs
# [1] prepare the dataframe and outfiles list
dfOut = pd.DataFrame(columns=dfStn.columns, index=dfStn.index)
rasOut = sorted(glob.glob("../../3_RSData/1_Rasters/GeneratedRasters/01_Daily/01_2000_2018_GPM/*.tif"))  # outfiles list 

# [2] get the values at station points into the dataframe
for i in td(range(len(rasOut)), desc='Getting values'):

    # [2.1] read the tiff file and get its date
    dsOut = rio.open(rasOut[i]).read(1)  # file read
    date = rasOut[i].split('/')[-1].split('.')[0].replace('_','-')  # date extracted

    # [2.2] get the values at station point from the tiff file 
    dfOut.loc["{}".format(date)] = dsOut[stnKey.row, stnKey.col]

# [2.3] change the datatype
dfOut = dfOut.astype('float32')  




# %% [markdown]
## Get mean monthly data for the bkgn period 
# [1] subset data till bkgn duration 
dateEnd = datetime(year=2009, month=12, day=31)
dfOut2 = dfOut[(dfOut.index<=dateEnd)]

# [2] Resample the data to monthy scale
dfOut2 = dfOut2.resample('M').sum()  # .mean() also gives same results

# [3] Get monthly mean 
dfOut2 = dfOut2.groupby(dfOut2.index.month).mean()  

# [4] save it to a csv file 
outFileName = "../../2_ExcelFiles/02_SatDataAtSations/14_modelled.csv"
dfOut2.to_csv(outFileName)
print('File saved as .csv')




# %%
