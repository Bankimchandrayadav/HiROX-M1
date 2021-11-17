# %% [markdown]
# # About
# This notebook renames the BKGN netcdf files in monthly order 



# %% [markdown]
# # Libs
from tqdm.notebook import tqdm as td 
import glob, numpy as np, shutil, time, os, subprocess
start = time.time()



# %% [markdown]
# # Read the files and set vars
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/2_BKGN/01_netcdf/*h.nc"))
outDir = "../../3_RSData/1_Rasters/2_BKGN/01_netcdf/renamed/"  
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']  



# %% [markdown]
# # Rename the files in monthly order
for i in td(range(0, len(rasters)), desc='Renaming'):
    fileMonth = rasters[i].split('/')[-1].split('_')[1].split('.')[0].upper()  # month found 
    idx = months.index(fileMonth)  # index of that month found in the list 'months'
    outName = outDir + "{}_{}.nc".format(str(idx+1).zfill(2), fileMonth)  # outfile name set
    shutil.copy(rasters[i], outName)  # file saved to outdir with new name



# %%
print('Time elapsed: {} mins'.format(np.round((time.time()-start)/60, 2)))



# %%



