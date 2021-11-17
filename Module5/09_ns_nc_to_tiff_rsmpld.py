#%%[markdown]
## About 
# This code does the following:
# > 1. resamples hourly netcdf NearSurface files to daily scale
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
## [1] Convert hourly netcdf files to daily scale
# [1] read the files
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/13_NearSurface/01_Original/*.nc"))
outDir = "../../3_RSData/1_Rasters/13_NearSurface/02_DailyNC/"
fresh(outDir)

# [2] subset to study area, and convert the files 
for i in td(range(len(rasters)), desc='To daily'):
    ds = xr.open_dataset(rasters[i])
    ds = ds.sel(lat=slice(25,35), lon=slice(75,85)) # lat,lon susbet
    ds = ds.resample(time='1D').sum()  # resampled to daily scale
    for j in range(len(ds.time)):
        date = str(ds.time[j].values).split('T')[0]  # date extracted
        outName = outDir + "{}.nc".format(date) # outFile name set 
        ds.isel(time=j).to_netcdf(outName)




# %% [markdown]
## [2] Convert to tiff 
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/13_NearSurface/02_DailyNC/*.nc"))
outDir = "../../3_RSData/1_Rasters/13_NearSurface/03_NCToTiff/"
fresh(outDir)

# [1] prepare outFile name
for i in td(range(len(rasters)), desc='To tiff'):
    date = rasters[i].split('/')[-1].split('.')[0]  # date extracted
    outName = outDir + "{}.tif".format(date) #outFile name set 

    # [2] convert nc file to tiff
    ds = rx.open_rasterio(rasters[i])
    ds = ds.rio.write_crs("epsg:4326")  # crs set
    ds.Rainf.rio.to_raster(outName)




# %% [markdown]
## [3] Reproject, resample and clip 
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/13_NearSurface/03_NCToTiff/*.tif"))
outDir = "../../3_RSData/1_Rasters/13_NearSurface/04_TiffResampled/"
fresh(outDir)

for i in td(range(len(rasters)), desc='Warping'):
    date = rasters[i].split('/')[-1]  # date of file extracted
    outName = outDir + date 
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
