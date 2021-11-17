# %% [markdown]
# ## About 
# This code was converts the BKGN netcdf files to tiff format 



# %% [markdown]
# # Libs 
from tqdm.notebook import tqdm as td 
import glob, os, rioxarray, numpy as np, time 
start = time.time()



# %% [markdown]
# # Read files and set vars
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/2_BKGN/01_netcdf/renamed/*.nc"))  
outDir = "../../3_RSData/1_Rasters/2_BKGN/02_tiff/"
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']



# %% [markdown]
# # Convert the files to tiff
for i in td(range(0, len(rasters)), desc='Converting to tiff'):
    outName = outDir + "{}_{}.tif".format(str(i+1).zfill(2), months[i])  # outfile name
    ds = rioxarray.open_rasterio(rasters[i])
    ds = ds.rio.write_crs("epsg:4326")  # crs set 
    ds.rio.to_raster(outName) # saved as tif    



# %%
print('Time elapsed: {} secs'.format(np.round(time.time()-start, 2)))


