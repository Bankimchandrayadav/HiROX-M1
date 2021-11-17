#%%[markdown]
## About 
# This code does the following:
# > 1. resamples hourly netcdf ERA5 files to daily scale
# 2. converts daily netcdf files to tiff format 
# 3. resamples, reprojects and clips the tiff files to study area's extent




# %% [markdown]
## Libs 
from tqdm.notebook import tqdm as td 
import glob, xarray as xr, shutil, os, rioxarray as rx, gdal, time, numpy as np
def fresh(where):
    if os.path.exists(where):
        shutil.rmtree(where)
        os.mkdir(where)
    else:
        os.mkdir(where)
start = time.time() 




# %% [markdown] 
## Get daily netcdf files from hourly netcdf files 
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/4_ERA5/daily/*.nc"))

# [1] get daily netcdf from file 1/2 of rasters
ds1 = xr.open_dataset(rasters[0])
ds1 = ds1.resample(time='1D').sum()

# [2] save the daily netcdf files 
outDir = "../../3_RSData/1_Rasters/4_ERA5/daily/01_DailyNC/"
fresh(outDir)
for i in td(range(len(ds1.time)), desc='Saving daily files 1/2'):
    date = str(ds1.time[i].values).split('T')[0]  # date extracted
    outName = outDir + "{}.nc".format(date) # outFile name set 
    ds1.tp.isel(time=i).to_netcdf(outName)  # daily file saved

# [3] get daily netcdf from file 1/2 of rasters
ds2 = xr.open_dataset(rasters[1])
ds2 = ds2.resample(time='1D').sum()

# [4] save the daily netcdf files 
for i in td(range(len(ds2.time)), desc='Saving daily files 2/2'):
    date = str(ds2.time[i].values).split('T')[0]  # date extracted
    outName = outDir + "{}.nc".format(date) # outFile name set 
    ds2.tp.isel(time=i).to_netcdf(outName)  # daily file saved




# %% [markdown]
## Convert to tiff 
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/4_ERA5/daily/01_DailyNC/*.nc"))
outDir = "../../3_RSData/1_Rasters/4_ERA5/daily/02_NCToTiff/"
fresh(outDir)

# [1] prepare outFile name
for i in td(range(len(rasters)), desc='Converting to tiff'):
    date = rasters[i].split('/')[-1].split('.')[0]  # date extracted
    outName = outDir + "{}.tif".format(date) #outFile name set 

    # [2] convert nc file to tiff
    ds = rx.open_rasterio(rasters[i])
    ds = ds.rio.write_crs("epsg:4326")  # crs set
    ds.tp.rio.to_raster(outName)




# %% [markdown]
## Reproject, resample and clip 
rasters = sorted(glob.glob(outDir + "*.tif"))
outDir1 = "../../3_RSData/1_Rasters/4_ERA5/daily/03_TiffResampled/"
fresh(outDir1)

for i in td(range(len(rasters)), desc='Warping'):
    date = rasters[i].split('/')[-1]  # date of file extracted
    outName = outDir1 + date 
    gdal.Warp(
    destNameOrDestDS=outName,
    srcDSOrSrcDSTab=rasters[i],
    dstSRS="epsg:32644",  # reprojection
    xRes = 5000,  # resampling
    yRes=5000,
    outputBounds = [159236.23230056558, 3170068.6251568096, 509236.2323005656, 3500068.6251568096]  # clip
)
print('Time elapsed: ', np.round((time.time()-start)/60,2), 'mins') 




# %% [markdown]
