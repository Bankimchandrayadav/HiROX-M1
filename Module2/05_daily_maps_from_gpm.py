#%% [markdown]
## About
# This code prepares daily BKGN maps on the basis of daily and monthly GPM data 




# %% [markdown]
## Libs 
from tqdm.notebook import tqdm as td 
import glob, rasterio as rio, xarray as xr, gdal, numpy as np, shutil, os, time, matplotlib.pyplot as plt
def fresh(where):
    if os.path.exists(where):
        shutil.rmtree(where)
        os.mkdir(where)
    else:
        os.mkdir(where)  
start = time.time()




# %% [markdown]
## Read GPM and BKGN data
# [1] daily gpm data 
rasGPMDaily = sorted(glob.glob("../../3_RSData/1_Rasters/1_GPM/daily_to_tiff_rsmpld/*.tif"))

# [2] mean monthly BKGN data 
rasBKGN = sorted(glob.glob("../../3_RSData/1_Rasters/2_BKGN/04_refined/*.tif"))
dfBKGN = {} 
for i in range(len(rasBKGN)):
    dfBKGN[i+1] = rio.open(rasBKGN[i]).read(1)




# %% [markdown]
## Prepare dict to store outMaps  
dfOut = {}
for i in range(len(rasGPMDaily)):
    dfOut[i] = np.zeros((66,70))




# %% [markdown]
## Make daily BKGN maps
for i in td(range(len(rasGPMDaily)), desc='Generating'):
    # [1] find year and month of the daily gpm file 
    year = rasGPMDaily[i].split('/')[-1].split('.')[0].split('_')[0]
    month = rasGPMDaily[i].split('/')[-1].split('.')[0].split('_')[1]

    # [2] read the daily GPM file 
    dsGPMDaily = rio.open(rasGPMDaily[i]).read(1)

    # [3] read the corresponding monthly GPM file
    dsGPMMonthly = xr.open_dataset("../../3_RSData/1_Rasters/1_GPM/daily_to_tiff_rsmpld/02_NetcdfToMonthly/{}-{}-01.nc".format(year, month)).GPM.values[0]

    # [4] read the corresponding months' bkgn file 
    dsBKGN = dfBKGN[int(month)]

    # [5] generate daily bkgn file 
    dfOut[i] = (dsGPMDaily/dsGPMMonthly) * dsBKGN




# %% [markdown]
## Save the daily BKGN maps 
# [1] set ref ras and outDir 
referenceRas = gdal.Open(rasGPMDaily[0])
outDir = "../../3_RSData/1_Rasters/2_BKGN/05_DailyBKGNMaps/"
fresh(outDir)

# [2] create new tiff files 
for i in td(range(len(dfOut)), desc='Saving'):
    outName = outDir + rasGPMDaily[i].split('/')[-1]  # outfile name set
    outMap = gdal.GetDriverByName('GTiff').Create(outName, xsize=referenceRas.RasterXSize, ysize=referenceRas.RasterYSize, bands=1, eType=gdal.GDT_Float32)  # geotiff created
    outMap.SetGeoTransform(referenceRas.GetGeoTransform()) # geotransform set
    outMap.SetProjection(referenceRas.GetProjection())  # projection set 
    outMap.GetRasterBand(1).WriteArray(dfOut[i])  # data in file set 
    outMap=None  # geotiff closed 
print('Time elapsed', np.round((time.time()-start)/60,2), 'mins')




# %%
