#%%[markdown]
## About 
# This code is for converting daily netcdf files to mean monthly during the bkgn's period 




# %% [markdown]
## Libs and vars
from datetime import date
from tqdm.notebook import tqdm as td
import xarray as xr, shutil, os, time, numpy as np, matplotlib.pyplot as plt, glob, rioxarray as rx, gdal
def fresh(where):  
    if os.path.exists(where):
        shutil.rmtree(where)
        os.mkdir(where)
    else:
        os.mkdir(where)
start = time.time()
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']  




# %% [markdown]
## Read file 
ds = xr.open_dataset("../../3_RSData/1_Rasters/GeneratedRasters/02_DailyNetcdf/03_Complete_GPM_APHRO/SingleFile/prcp_1972_2018.nc")




# %% [markdown]
## Get mean monthly 
# [1] resample to daily scale 
ds = ds.resample(time='MS').sum()  # firstly set to monthly scale 
ds = ds.groupby('time.month').mean()  # then monthly mean




# %% [markdown]
## Save to netcdf 
outDir = "../../3_RSData/1_Rasters/GeneratedRasters/03_MeanMonthly/03_Complete_GPM_APHRO/01_Netcdf/"
fresh(outDir)
for i in td(range(len(ds.month)), desc='Saving to netcdf'):
    outName = outDir + "{}_{}.nc".format(str(i+1).zfill(2), months[i])
    ds.isel(month=i).to_netcdf(outName)




# %% [markdown] 
## Save as images 
outDir = "../../5_Images/05_MeanMonthlyMaps/"
fresh(outDir)
for i in td(range(len(ds.month)), desc='Saving as images'):
    outName = outDir + "{}_{}.png".format(str(i+1).zfill(2), months[i])
    plt.figure(dpi=300)
    ds.isel(month=i).prcp_renoj.plot()
    plt.savefig(outName, facecolor='w')
    plt.close()




# %% [markdown]
## Save as tiff files 
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/GeneratedRasters/03_MeanMonthly/03_Complete_GPM_APHRO/01_Netcdf/*.nc"))
outDir = "../../3_RSData/1_Rasters/GeneratedRasters/03_MeanMonthly/03_Complete_GPM_APHRO/02_Tiff/"
fresh(outDir)
for i in td(range(len(rasters)), desc='Saving to tiff'):
    # [1] set name
    month = rasters[i].split('/')[-1].split('.')[0]
    outName = outDir + month + '.tif'

    # [2] convert
    ds = xr.open_dataset(rasters[i])
    ds = ds.rio.write_crs("epsg:32644")  # crs set 
    ds.prcp_renoj.rio.to_raster(outName)
print('Time elapsed: ', np.round(time.time()-start,2), 'secs')





# %%
