# %% [markdown]
# # About 
# This notebook converts the tiff files of product 2 to netcdf form




# %% [markdown]
# # Libraries
from tqdm.notebook import tqdm as td 
from datetime import datetime
import glob, rioxarray as rx, shutil, xarray as xr, numpy as np, time, os, gdal
start = time.time()
def fresh(where):
    if os.path.exists(where):
        shutil.rmtree(where)
        os.mkdir(where)
    else:
        os.mkdir(where)  
import subprocess




# %% [markdown]
# # Convert the tiff files to netcdf
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/GeneratedRasters/01_Daily/07_Product2/*.tif"))  
outDir = "../../3_RSData/1_Rasters/GeneratedRasters/02_DailyNetcdf/05_RENOJ2/"  
fresh(outDir)  

for i in td(range(len(rasters)), desc='Converting'):                     
    date = rasters[i].split('/')[-1].split('.')[0].replace("_","-")  # date extracted
    year = int(date.split('-')[0])
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])  # year, month and day of the date extracted
    
    da = rx.open_rasterio(rasters[i])  # tiff file read as a dataarray
    da = da.rename('prcp_renoj')  # dataarray variable's name set

    da = da.assign_coords(time=datetime(year, month, day))  # time added as a coordinate
    da = da.expand_dims('time')  # time added as a dimension
    outName = outDir + date + '.nc'  # outfile name set
    da.to_netcdf(outName, engine="h5netcdf", invalid_netcdf=True)  # file saved as netcdf




# %% [markdown]
# # Convert all netcdf to a single netcdf
rasMultiple = sorted(glob.glob(outDir + "*.nc"))  # files read as a list
outDir1 = outDir + "SingleFile/"                            
fresh(outDir1)  

ds = xr.open_mfdataset(rasMultiple, concat_dim='time')  # files read as a single dataset file
outName = outDir1 + "prod2.nc"  # outfile name set 
ds.to_netcdf(outName)  # saved to the single netcdf
print('Files saved into a single netcdf')
print('Time elapsed: {} secs'.format(np.round((time.time()-start), 2)))




# %% [markdown]
# # Open output folder
subprocess.Popen(["xdg-open", outDir])




# %%



