#%% [markdown]
## About
# This code does the following:
# > 1. prepares daily BKGN maps on the basis of daily and monthly ERA5 data 




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
## Read daily GLADS data and mm BKGN data
# [1] daily ERA5 data 
rasERA5Daily = sorted(glob.glob("../../3_RSData/1_Rasters/4_ERA5/daily/03_TiffResampled/*.tif"))

# [2] mean monthly BKGN data 
rasBKGN = sorted(glob.glob("../../3_RSData/1_Rasters/2_BKGN/04_refined/*.tif"))
dfBKGN = {} 
for i in range(len(rasBKGN)):
    dfBKGN[i+1] = rio.open(rasBKGN[i]).read(1)




# %% [markdown]
## Prepare dict to store outMaps  
dfOut = {}
for i in range(len(rasERA5Daily)):
    dfOut[i] = np.zeros((66,70)) 




# %% [markdown]
## Make daily BKGN maps
for i in td(range(len(rasERA5Daily)), desc='Generating'):
    # [1] find year and month of the daily ERA5 file 
    year = rasERA5Daily[i].split('/')[-1].split('.')[0].split('-')[0]
    month = rasERA5Daily[i].split('/')[-1].split('.')[0].split('-')[1] 

    # [2] read the daily ERA5 file
    dsERA5Daily = rio.open(rasERA5Daily[i]).read(1) 

    # [3] read the corresponding monthly ERA5 file
    dsERA5Monthly = xr.open_dataset("../../3_RSData/1_Rasters/4_ERA5/daily/05_NCToNCMonthly/{}-{}-01.nc".format(year, month)).ERA5.values[0]

    # [4] read the corresponding months' bkgn file 
    dsBKGN = dfBKGN[int(month)]

    # [5] generate daily bkgn file 
    dfOut[i] = (dsERA5Daily/dsERA5Monthly) * dsBKGN




# %% [markdown]
## Save the daily BKGN maps 
# [1] set ref ras and outDir 
referenceRas = gdal.Open(rasERA5Daily[0])
outDir = "../../3_RSData/1_Rasters/2_BKGN/08_DailyBasedOnERA5/"
fresh(outDir)

# [2] create new tiff files 
for i in td(range(len(dfOut)), desc='Saving'):
    outName = outDir + rasERA5Daily[i].split('/')[-1]  # outfile name set
    outMap = gdal.GetDriverByName('GTiff').Create(outName, xsize=referenceRas.RasterXSize, ysize=referenceRas.RasterYSize, bands=1, eType=gdal.GDT_Float32)  # geotiff created
    outMap.SetGeoTransform(referenceRas.GetGeoTransform()) # geotransform set
    outMap.SetProjection(referenceRas.GetProjection())  # projection set 
    outMap.GetRasterBand(1).WriteArray(dfOut[i])  # data in file set 
    outMap=None  # geotiff closed 
print('Time elapsed', np.round(time.time()-start,2), 'secs')




# %%
