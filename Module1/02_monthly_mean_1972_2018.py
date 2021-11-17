# %% [markdown]
# # About
# > This code generates the mean monthly data for entire duration i.e. 1972-2018, from the daily data



# %% [markdown]
# # Libraries
from datetime import datetime
import pandas as pd, numpy as np, time, rasterio as rio, geopandas as gpd
start = time.time()




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




# %% [markdown]
## Read and subset station data
# [1] read station data 
dfStn = pd.read_csv("../../2_ExcelFiles/01_StationData/04_daily.csv")  

# [2] subset station data to bkgn's duration 
# [2.1] change the datatype of dates
for i in range(len(dfStn)):  
    dateString = (dfStn.Date[i]).split('/')  # date read as string
    dfStn.Date[i] = datetime(year=int(dateString[2]), month=int(dateString[1]), day=int(dateString[0]))  # dtype converted 

# [2.2] set index and cols a/c to stationKey
dfStn.set_index('Date', inplace=True)  # dates set as index 
dfStn.index.names=[None] # extra rows in col heads removed
dfStn = dfStn[stnKey.Station]  # set according to station key
dfStn = dfStn.astype('float32')



# %% [markdown]
## Get monthly mean
# [1] resample to monthly duration 
dfStn = dfStn.resample('MS').sum()

# [2] get monthly mean 
dfStn = dfStn.groupby(dfStn.index.month).mean() 



# %% [markdown]
# # Save to csv
dfStn.to_csv("../../2_ExcelFiles/01_StationData/06_monthly_mean_1972_2018.csv") 
print('Time elapsed: ', np.round(time.time()-start,2), 'secs')




# %%


