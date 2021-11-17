#%%[markdown]
## About 
# This code does the following:
# > 1. converts daily netcdf GLDAS data to tiff format 
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
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/12_GLDAS/*.nc4"))
dateEnd = '20000531'  # subset data fill 2000 May 31
for i in range(len(rasters)):  # find the index of 2000 May 31 
    if dateEnd in rasters[i]:
        print(rasters[i], 'at index', i)  # index of 2000 May 31 found 
rasters = rasters[:10379]  # subset done




# %% [markdown]
## Convert to tiff 
outDir = "../../3_RSData/1_Rasters/12_GLDAS/01_NCToTiff/"
fresh(outDir)

# [1] prepare outFile name
for i in td(range(len(rasters)), desc='Converting to tiff'):
    date = rasters[i].split('.')[5][1:]  # date of file extracted
    outName = outDir + "{}_{}_{}.tif".format(date[:4], date[4:6], date[6:]) #outFile name set 

    # [2] convert nc file to tiff
    # [2.1] read file, choose dataarray and set crs 
    ds=xr.open_dataset(rasters[i])
    da = ds.Rainf_f_tavg
    da = da.rio.write_crs("epsg:4326")  # crs set 

    # [2.2] convert to tiff
    da.rio.to_raster(outName)
    ds = None  # close files




# %% [markdown]
## Reproject, resample and clip 
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/12_GLDAS/01_NCToTiff/*.tif"))
outDir = "../../3_RSData/1_Rasters/12_GLDAS/02_TiffResampled/"
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
