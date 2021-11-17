# %% [markdown]
# # About 
# This code does the following:
# > 1. converts daily netcdf gpm files to tiff 
# 2. resamples, reprojects and clips the tiff files to study area's extent




# %% [markdown]
# # Libs 
from tqdm.notebook import tqdm as td 
import glob, os, rioxarray, numpy as np, time, datetime, xarray as xr, matplotlib.pyplot as plt, rasterio as rio, gdal  
start = time.time()



# %% [markdown]
# # Read files to be converted to tiff
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/1_GPM/daily/*.nc4"))
outDir = "../../3_RSData/1_Rasters/1_GPM/daily_to_tiff/"



# %% [markdown]
# # Convert the files to tiff
for i in td(range(len(rasters))):

    y = rasters[i].split('RG.')[-1].split('-')[0][:4]  # 1 set name of the outfile
    m = rasters[i].split('RG.')[-1].split('-')[0][4:6]
    d = rasters[i].split('RG.')[-1].split('-')[0][6:]
    outName = outDir + "{}_{}_{}.tif".format(y,m,d)

    ds = xr.open_dataset(rasters[i])  # 2 convert to tiff
    ds = ds.squeeze()  # dims with size zero or one removed (here time)
    ds = ds.drop_vars(['precipitationCal_cnt', 'precipitationCal_cnt_cond', 'HQprecipitation','HQprecipitation_cnt','randomError','randomError_cnt','HQprecipitation_cnt_cond','time_bnds'])  # other variables removed
    ds = ds.rio.write_crs("epsg:4326")  # crs set 
    ds = ds.transpose('lat','lon')  # order of dims changes as per rioxarray
    ds['precipitationCal'].rio.to_raster(outName) # saved as tif



# %% [markdown]
## Read the files to be warped 
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/1_GPM/daily_to_tiff/*.tif"))
outDir = "../../3_RSData/1_Rasters/1_GPM/daily_to_tiff_rsmpld/"




# %% [markdown]
# # Reproject, resample and clip
for i in td(range(len(rasters)), desc='Warping'):
    outName = outDir + rasters[i].split('/')[-1]
    gdal.Warp(
        destNameOrDestDS=outName,
        srcDSOrSrcDSTab=rasters[i],
        dstSRS="epsg:32644",  # reprojection
        xRes = 5000,  # resampling
        yRes=5000,
        outputBounds = [159236.23230056558, 3170068.6251568096, 509236.2323005656, 3500068.6251568096]  # clipping
    )




# %%
print('Time elapsed: {} mins '.format((np.round(time.time() - start)/60),2))



