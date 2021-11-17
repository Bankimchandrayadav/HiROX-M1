#%%[markdown]
## About 
# This code does the following:
# > 1. converts daily netcdf APHROV1101 data to tiff format 
# 2. resamples, reprojects and clips the tiff files to study area's extent




# %% [markdown]
## Libs 
from tqdm.notebook import tqdm as td 
import glob, xarray as xr, shutil, os, rioxarray, gdal, time, numpy as np
def fresh(where):
    if os.path.exists(where):
        shutil.rmtree(where)
        os.mkdir(where)
    else:
        os.mkdir(where)
start = time.time()




# %% [markdown]
## Read and subset files 
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/6_APHRODITE/V1101/*.nc"))
ds = xr.open_mfdataset(rasters)  
ds = ds.sel(time=slice("1972-01-01", "2000-05-31"), latitude=slice(25,35), longitude=slice(75,85))  # subset till the req duration 




# %% [markdown]
## Convert to tiff 
outDir = "../../3_RSData/1_Rasters/6_APHRODITE/V1101/daily/01_NCToTiff/"
fresh(outDir)

# [1] prepare outFile name
for i in td(range(len(ds.time)), desc='Converting to tiff'):
    date = str(ds.time[i].values).split('T')[0]  # date extracted
    outName = outDir + "{}.tif".format(date) #outFile name set 

    # [2] convert nc file to tiff
    # [2.1] read file, choose dataarray and set crs 
    da = ds.isel(time=i).precip
    da = da.rio.write_crs("epsg:4326")  # crs set 

    # [2.2] convert to tiff
    da.rio.to_raster(outName)




# %% [markdown]
## Reproject, resample and clip 
rasters = sorted(glob.glob(outDir + "*.tif"))
outDir1 = "../../3_RSData/1_Rasters/6_APHRODITE/V1101/daily/02_TiffResampled/"
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
