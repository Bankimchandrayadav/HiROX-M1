# %% [markdown]
# # About
# 1. This notebook extracts modelled mean monthly data at station locations during BKGN data's duration (1998-2009) *[(obtained from mean monthly GPM data)]*
# 2. The values are then written to a csv file for handy usage



# %% [markdown]
# # Libraries
from tqdm.notebook import tqdm as td
import os, matplotlib.pyplot as plt, numpy as np, xarray as xr, geopandas as gpd, pandas as pd, time, glob, rasterio as rio, subprocess
start = time.time()



# %% [markdown]
# # Structure the dataframe
df = pd.read_csv(r"../../2_ExcelFiles/01_StationData/07_monthly_mean.csv")
df.rename(columns={'Unnamed: 0': 'MonthNo'}, inplace=True)  # removed extra cols 
df.set_index('MonthNo', inplace=True)  # month no. set as index
df.index.names = [None]
df = pd.DataFrame(columns=df.columns, index=df.index)  # removed all values



# %% [markdown]
# # Prepare station key
stnKey = gpd.read_file(r"../../3_RSData/2_Vectors/1_Stations/01_stations_UTM44N1.shp")
stnKey = stnKey.sort_values('Sno') 
stnKey.reset_index(drop=True, inplace=True)
stnKey['x'] = ""  # add col labels for adding x,y coordinates
stnKey['y'] = ""
for i in td(range(0, len(stnKey))):  # add values to x,y fields
    stnKey.x[i] = stnKey.geometry[i].x
    stnKey.y[i] = stnKey.geometry[i].y
coords = [(x,y) for x, y in zip(stnKey.x, stnKey.y)]  # extract out coordinates 



# %% [markdown]
# # Obtain data at point locations
# Sampling point values taken from: [here](https://gis.stackexchange.com/a/324830/173838)
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/GeneratedRasters/02_MeanMonthly/*.tif"))
for i in td(range(0, len(rasters)), desc='Sampling point values'):
    ds = rio.open(rasters[i])
    df.iloc[i,:] = [x[0] for x in ds.sample(coords)]



# %% [markdown]
# # Save the dataframe to a csv
df1 = df.astype('float64')  # dtype changed
outDir = "../../2_ExcelFiles/02_SatDataAtSations/"
outFileName = outDir + "14_modelled_mm.csv"
df1.to_csv(outFileName)  # saved to excel file



# %%
print('Time elapsed: ', np.round(time.time()-start, 2), 'secs')


