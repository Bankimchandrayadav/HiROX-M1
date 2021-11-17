#%%[markdown]
## About 
# This code is for converting daily netcdf files to mean monthly during the bkgn's period i.e. 2000-2009




# %% [markdown]
## Libs and vars
from tqdm.notebook import tqdm as td 
import xarray as xr, shutil, os, time, numpy as np, matplotlib.pyplot as plt, glob, rioxarray as rx
from xarray.backends import rasterio_
from xarray.backends.rasterio_ import open_rasterio 
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']  
def fresh(where):  
    if os.path.exists(where):
        shutil.rmtree(where)
        os.mkdir(where)
    else:
        os.mkdir(where)
start = time.time()




# %% [markdown]
## Read file 
ds = xr.open_dataset("../../3_RSData/1_Rasters/GeneratedRasters/02_DailyNetcdf/04_2000_2009_GPM/SingleFile/prcp_2000_2009.nc")




# %% [markdown]
## Get mean monthly 
# [1] resample to daily scale 
ds = ds.resample(time='MS').sum()  # firstly set to monthly scale 
ds = ds.groupby('time.month').mean()  # then monthly mean




# %% [markdown]
## Save to netcdf 
outDir = "../../3_RSData/1_Rasters/GeneratedRasters/03_MeanMonthly/40_2000_2009_GPM/01_Netcdf/"
fresh(outDir)
for i in td(range(len(ds.month)), desc='Saving to netcdf'):
    outName = outDir + "{}_{}.nc".format(str(i+1).zfill(2), months[i])
    ds.isel(month=i).to_netcdf(outName)




# %% [markdown]
# # Convert the files to tiff
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/GeneratedRasters/03_MeanMonthly/40_2000_2009_GPM/01_Netcdf/*.nc"))
outDir = "../../3_RSData/1_Rasters/GeneratedRasters/03_MeanMonthly/40_2000_2009_GPM/02_Tiff/"
fresh(outDir)

for i in td(range(len(rasters))):
    fileName = rasters[i].split('/')[-1].split('.')[0] + ".tif"
    outName = outDir + fileName

    # 2 convert to tiff
    ds = rx.open_rasterio(rasters[i])
    ds = ds.squeeze()  # dims with size zero or one removed (here time)
    ds = ds.rio.write_crs("epsg:4326")  # crs set 
    ds['prcp_renoj'].rio.to_raster(outName) # saved as tif




# %%
