# %% [markdown]
# # About
#  1. This notebook adds time coordinate to every TRMM file
#  2. The files were then saved with the added coordinates



# %% [markdown]
# # Libraries
from tqdm.notebook import tqdm as td
import os, shutil, xarray as xr, numpy as np, datetime, shutil, time, glob
start = time.time()



# %% [markdown]
# # Read the files into a list
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/5_TRMM/*.nc4"))



# %% [markdown]
# # Add time coordinate to each TRMM file
for i in td(range(len(rasters)), desc='Added time dimension'):
    ds = xr.open_dataset(rasters[i])
    year = rasters[i].split('/')[-1][5:9]  # year extracted
    yearInt = int(year)
    month = rasters[i].split('/')[-1][9:11]  # month extracted
    monthInt = int(month)
    day = rasters[i].split('/')[-1][11:13]  # day extracted
    dayInt = int(day)
    ds.coords['time'] = [datetime.datetime(yearInt, monthInt, dayInt)]  # time coords setup
    ds.to_netcdf(r"../../3_RSData/1_Rasters/5_TRMM/with_time_dim/{}_{}_{}.nc".format(year, month.zfill(2), day.zfill(2)))



# %%
print("Time elapsed: {} secs".format(np.round(time.time()-start)))


