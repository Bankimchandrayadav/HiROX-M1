# %% [markdown]
# # About 
# This code is for the conversion of 50 year modelled daily tiff files to netcdf format  




# %% [markdown]
## Libs and local vars
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




# %% [markdown]
## Convert tiff files to netcdf [1972-2018]
# [1] read files 
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/GeneratedRasters/01_Daily/06_1972_2018_GPM_APHRO/*.tif"))

# [2] set out directory
outDir = "../../3_RSData/1_Rasters/GeneratedRasters/02_DailyNetcdf/03_Complete_GPM_APHRO/"
fresh(outDir)  

#[2.1] convert using rioxarray 
for i in td(range(len(rasters)), desc='Converting'):  
    date = rasters[i].split('/')[-1].split('.')[0].replace("_","-")  # date extracted
    outName = outDir + date + '.nc'  # outfile name set
    da = rx.open_rasterio(rasters[i])  # read as a dataarray
    da = da.rename('prcp_renoj')  # variable given name 

    # [3] add time information to the file 
    # [3.1] set year, month and day variables
    year = int(date.split('-')[0])  
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])

    # [3.2] reopen the saved nc file and change some properties
    da = da.assign_coords(time=datetime(year, month, day))  # time assigned
    da = da.expand_dims('time')  # time added to dimesion (was optional)
    da.to_netcdf(outName, engine="h5netcdf", invalid_netcdf=True)  




# %% [markdown]
## Convert multiple netcdf to single netcdf 
# [1.1] set paths
rasMultiple = sorted(glob.glob(outDir + "*.nc"))
outDir1 = outDir + "SingleFile/"
fresh(outDir1)  

# [2] conversion
ds = xr.open_mfdataset(rasMultiple, concat_dim='time')
outName = outDir1 + "prcp_1972_2018.nc"  # outfile name set 
ds.to_netcdf(outName)  # saved to a single netcdf
print('Files saved into a single netcdf')
print('Time elapsed: {} secs'.format(np.round((time.time()-start), 2)))




# %% 



