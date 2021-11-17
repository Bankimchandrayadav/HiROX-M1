#%%[markdown]
## About 
# This code does the following:
# >
##  Part A (getting annual modelled data within basin)
# > 1. Resample modelled data from daily to annual scale and save as tiff
# > 2. Clip the tiff files to rishikesh basin boundary  

## Part B (getting annual stn data within basin)
# > 3. Resample station data from daily to annual scale

## Part C (comparisons of modelled and stn data)
# > 4. Get the annual modelled and station values into a dataframe
# > 5. Plot the comparisons





# %% [markdown]
## Libs
from tqdm.notebook import tqdm as td 
from datetime import datetime
import gdal, rasterio as rio, matplotlib.pyplot as plt, numpy as np, geopandas as gpd, xarray as xr, rioxarray as rx, glob, os, time, pandas as pd
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




# %% [markdown]
## Part A
# ---
# %% [markdown]
## [1] Resample modelled data from daily to annual scale and save as tiff
# [1] Read and resample 
dsMod = xr.open_dataset("../../3_RSData/1_Rasters/GeneratedRasters/02_DailyNetcdf/03_Complete_GPM_APHRO/SingleFile/prcp_1972_2018.nc")  # data read
dsMod = dsMod.resample(time='AS').sum()  # resampled to yearly scale

# [2] Save annual maps to tiff 
for i in td(range(len(dsMod.time)), 'Saving annual tiff'):
    year = str(dsMod.time[i].values)[:10].replace('-','_')
    outName = "../../3_RSData/1_Rasters/GeneratedRasters/04_Annual_Rishikesh/01_Annual/{}.tif".format(year)
    da = dsMod.prcp_renoj.isel(time=i)
    da = da.rio.write_crs("epsg:32644")
    da.rio.to_raster(outName)




# %% [markdown]
## [2] Clip the tiff files to rishikesh basin boundary
# [1] Read the input files
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/GeneratedRasters/04_Annual_Rishikesh/01_Annual/*.tif"))
cutLine = "../../3_RSData/2_Vectors/5_Rishi-Basin/rishi_wshed_pro_merged.shp"

# [2] Clip to rsksh basin extent
# [2.1] set outDir
outDir = "../../3_RSData/1_Rasters/GeneratedRasters/04_Annual_Rishikesh/02_Clipped/"
for i in td(range(len(rasters)), desc='Clipping'):
    outName = outDir + rasters[i].split('/')[-1].split('.')[0] + "_RSKSH.tif"
    result = gdal.Warp(srcDSOrSrcDSTab=rasters[i], destNameOrDestDS=outName, cutlineDSName=cutLine, cropToCutline=True)
    result = None
print('Time elapsed: ', np.round(time.time()-start,2), 'secs')



# %% [markdown]
## Part B
# ---
# %% [markdown]
## [3] Resample station data from daily to annual scale
# [1] Read daily data 
dfStn = pd.read_csv("../../2_ExcelFiles/01_StationData/04_daily.csv")

# [2] Change the datatype of dates
for i in td(range(len(dfStn)), desc="Changing date's dtype"):  
    dateString = (dfStn.Date[i]).split('/')  # date read as string
    dfStn.Date[i] = datetime(year=int(dateString[2]), month=int(dateString[1]), day=int(dateString[0]))  # dtype converted 

# [3] Resample to annual scale
dfStn.set_index('Date', inplace=True)  # dates set as index 
dfStn.index.names=[None] # extra rows in col heads removed
dfStn = dfStn.resample('AS').sum()  # resampled to yearly scale

# [4] Remove the stations from dfStn lying outside the rishikesh basin 
dfStn = dfStn.drop(columns=['BHOGPUR', 'DHANOLTI','KEERTINAGAR'])




# %% [markdown]
## Part C
# ---
# %% [markdown]
## [4] Get the annual modelled and station values into a dataframe
# [1] Structure the dataframe to store values
df = pd.DataFrame(index=range(len(dfStn)))
df['ModMean'] = ""
df['StnMean'] = ""
df['ModSum'] = ""
df['StnSum'] = ""

# [2] Get the mean and sum of stn values into the dataframe
df['StnMean'] = dfStn.mean(axis=1).values
df['StnSum'] = dfStn.sum(axis=1).values

# [3] Read modelled annual raster files
rasters1 = sorted(glob.glob("../../3_RSData/1_Rasters/GeneratedRasters/04_Annual_Rishikesh/02_Clipped/*.tif"))
dc = {}
for i in range(len(rasters1)):
    dc[i] = rio.open(rasters1[i]).read(1)

# [3.1] Set the values outside basin to np.nan
for i in range(len(dc)):
    dc[i][dc[i]==0] = np.nan

# [3.2] Get the mean and sum of annual values into the dataframe
for i in range(len(df)):
    df['ModMean'][i] = np.nanmean(dc[i])
    df['ModSum'][i] = np.nansum(dc[i])

# [4] remove the last two rows
df.index = dfStn.index
df.drop(df.index[-2:], inplace=True)




# %% [markdown]
## [5] Plot the comparisons
plt.figure(dpi=300)
plt.plot(df.ModMean, label='Modelled')
plt.plot(df.StnMean, label='Station')
# plt.plot(df.ModSum, label='Modelled')
# plt.plot(df.StnSum, label='Station')
plt.legend(loc=2, prop={'size': 8})
plt.title("Station Mean vs. Modelled Mean over Risikesh basin") 
plt.xlabel("Years")  # title, labels and grid
plt.ylabel("Precipitation (mm)")
plt.minorticks_on()
plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
plt.tight_layout()
plt.savefig("../../5_Images/08_Validation/01_RisikeshBasin/image_01.png", facecolor='w', bbox_inches='tight')
plt.close()




# %%
