#%% [markdown]
## About
# This code does the following:
# > 1. prepares daily BKGN maps on the basis of daily and monthly GLDAS data 




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
# [1] daily GLADS data 
rasGLDASDaily = sorted(glob.glob("../../3_RSData/1_Rasters/12_GLDAS/02_TiffResampled/*.tif"))

# [2] mean monthly BKGN data 
rasBKGN = sorted(glob.glob("../../3_RSData/1_Rasters/2_BKGN/04_refined/*.tif"))
dfBKGN = {} 
for i in range(len(rasBKGN)):
    dfBKGN[i+1] = rio.open(rasBKGN[i]).read(1)




# %% [markdown]
## Prepare dict to store outMaps  
dfOut = {}
for i in range(len(rasGLDASDaily)):
    dfOut[i] = np.zeros((66,70))




# %% [markdown]
## Make daily BKGN maps
for i in td(range(len(rasGLDASDaily)), desc='Generating'):
    # [1] find year and month of the daily GLADS file 
    year = rasGLDASDaily[i].split('/')[-1].split('.')[0].split('_')[0]
    month = rasGLDASDaily[i].split('/')[-1].split('.')[0].split('_')[1]

    # [2] read the daily GLADS file & convert from kg/m^2/s to mm/day
    dsGLDASDaily = rio.open(rasGLDASDaily[i]).read(1)*86400  

    # [3] read the corresponding monthly GLADS file & convert from kg/m^2/s to mm/day
    dsGLDASMonthly = xr.open_dataset("../../3_RSData/1_Rasters/12_GLDAS/04_NCToMonthly/{}-{}-01.nc".format(year, month)).GLDAS.values[0]*86400  

    # [4] read the corresponding months' bkgn file 
    dsBKGN = dfBKGN[int(month)]

    # [5] generate daily bkgn file 
    dfOut[i] = (dsGLDASDaily/dsGLDASMonthly) * dsBKGN




# %% [markdown]
## Save the daily BKGN maps 
# [1] set ref ras and outDir 
referenceRas = gdal.Open(rasGLDASDaily[0])
outDir = "../../3_RSData/1_Rasters/2_BKGN/06_DailyBasedOnGLDAS/"
fresh(outDir)

# [2] create new tiff files 
for i in td(range(len(dfOut)), desc='Saving'):
    outName = outDir + rasGLDASDaily[i].split('/')[-1]  # outfile name set
    outMap = gdal.GetDriverByName('GTiff').Create(outName, xsize=referenceRas.RasterXSize, ysize=referenceRas.RasterYSize, bands=1, eType=gdal.GDT_Float32)  # geotiff created
    outMap.SetGeoTransform(referenceRas.GetGeoTransform()) # geotransform set
    outMap.SetProjection(referenceRas.GetProjection())  # projection set 
    outMap.GetRasterBand(1).WriteArray(dfOut[i])  # data in file set 
    outMap=None  # geotiff closed 
print('Time elapsed', np.round((time.time()-start)/60,2), 'mins')




# %%
