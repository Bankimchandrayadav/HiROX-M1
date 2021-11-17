# %% [markdown]
# # About
# 1. This notebook extracts TRMM monthly mean data at station locations during BKGN data's duration (1998-2009)
# 2. The values are then written to an excel file for handy usage



# %% [markdown]
# # Libraries
from tqdm.notebook import tqdm as td
import os, matplotlib.pyplot as plt, numpy as np, xarray as xr, geopandas as gpd, pandas as pd, time, glob, rasterio as rio
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

coords = [(x,y) for x, y in zip(stnKey.geometry.x, stnKey.geometry.y)]  # x,y coords zippped



# %% [markdown]
# # Structure the dataframe
df = pd.read_csv(r"../../2_ExcelFiles/01_StationData/05_monthly_mean.csv")
df.rename(columns={'Unnamed: 0': 'MonthNo'}, inplace=True)  # removed extra cols 
df.set_index('MonthNo', inplace=True)  # month no. set as index
df.index.names = [None]
df = pd.DataFrame(columns=df.columns, index=df.index)  # removed all values



# %% [markdown]
# # Obtain data at point locations
# Sampling point values taken from: [here](https://gis.stackexchange.com/a/324830/173838)
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/5_TRMM/with_time_dim/monthly_means/03_resampled/*.tif"))
for i in td(range(0, len(rasters)), desc='Sampling point values'):
    ds = rio.open(rasters[i])
    df.iloc[i,:] = [x[0] for x in ds.sample(coords)]



# %% [markdown]
# # Save the dataframe to a csv
df1 = df.astype('float64')  # dtype changed
outFileName = "../../2_ExcelFiles/02_SatDataAtSations/04_trmm.csv"
df1.to_csv(outFileName)  # saved to excel file



# %%
print('Time elapsed: ', np.round(time.time()-start, 2), 'secs')


# %%



