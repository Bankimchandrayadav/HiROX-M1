#%% [markdown]
## About
# This code does the following:
# > 1. converts the daily resampled NearSurface data to netcdf   
# 2. converts the multiple netcdf files to a single netcdf   
# 3. converts the single netcdf to monthly scale netcdf files  




# %% [markdown]
## Libs 
from tqdm.notebook import tqdm as td 
from datetime import datetime
import glob, xarray as xr, gdal, shutil, os, rasterio as rio, matplotlib.pyplot as plt, rioxarray as rx  
def fresh(where):
    if os.path.exists(where):
        shutil.rmtree(where)
        os.mkdir(where)
    else:
        os.mkdir(where)  




# %% [markdown]
## Read files 
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/13_NearSurface/04_TiffResampled/*.tif"))




# %% [markdown]
## [1] Convert to netcdf 
outDir = "../../3_RSData/1_Rasters/13_NearSurface/05_TiffRsmpldToNC/"
fresh(outDir)

#[1] convert using rioxarray 
for i in td(range(len(rasters)), desc='Converting'):
    date = rasters[i].split('/')[-1].split('.')[0]  # date of file extracted
    outName = outDir + date + '.nc'  # outfile name set
    da = rx.open_rasterio(rasters[i])  # read as a dataarray
    da = da.rename('NS')  # variable given name 

    # [2] add time information to the file 
    # [2.1] set year, month and day variables
    year = int(date.split('-')[0])  
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])

    # [2.2] add time to coords and dimension
    da = da.assign_coords(time=datetime(year, month, day))  # time assigned
    da = da.expand_dims('time')  # time added to dim (was optional)
    da.to_netcdf(outName, engine='h5netcdf', invalid_netcdf=True)  # resaved




# %% [markdown]
## Convert multiple netcdf to a single netcdf 
rasMultiple = sorted(glob.glob(outDir+"*.nc"))
ds = xr.open_mfdataset(rasMultiple, concat_dim='time')
fresh(outDir + "SingleFile/")
ds.to_netcdf(outDir + "SingleFile/" + 'ns.nc')




# %% [markdown]
## Convert to monthly scale netcdf files
# [1] resample to monthly scale 
ds = xr.open_dataset("../../3_RSData/1_Rasters/13_NearSurface/05_TiffRsmpldToNC/SingleFile/ns.nc")
ds = ds.resample(time='MS').sum()  

# [2] save
outDir = "../../3_RSData/1_Rasters/13_NearSurface/06_NCToNCMonthly/"
fresh(outDir)
for i in td(range(len(ds.time)), desc='Saving'):
    date = str(ds.time[i].values).split('T')[0]  # date extracted
    outName = outDir + date + '.nc'
    ds.isel(time=i).to_netcdf(outName)




# %% [markdown]
