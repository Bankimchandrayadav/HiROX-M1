# %% [markdown]
# # About
# 1. This code prepares the modelled *mean monthly precipitation* dataset for the duration 2000-2009
# 2. The method used here will be updated as we find the best method of generating *daily precipitation maps* in the following codes



# %% [markdown]
# # Libs
from tqdm.notebook import tqdm as td 
import pandas as pd, glob, geopandas as gpd, rasterio as rio, numpy as np, richdem as rd, matplotlib.pyplot as plt, os, gdal, shutil
from sklearn.svm import SVR
# from sklearn.preprocessing import StandardScaler
def fresh(where):
    if os.path.exists(where):
        shutil.rmtree(where)
        os.mkdir(where)
    else:
        os.mkdir(where)  


# %% [markdown]
# # Remove old files
fresh(where="../../5_Images/05_MeanMonthlyMaps")



# %% [markdown]
# # Station Key
stnKey = gpd.read_file(r"../../3_RSData/2_Vectors/1_Stations/01_stations_UTM44N1.shp") 
stnKey.sort_values('Sno', inplace=True)  # sort all cols according to 'Sno'
stnKey.reset_index(drop=True, inplace=True)  # reset index 

ds = rio.open("../../3_RSData/1_Rasters/DEM/02_srtm_epsg_32644.tif")  # read dem 
dsAspect = rio.open("../../3_RSData/1_Rasters/DEM/03_srtm_epsg_32644_aspect.tif")  # aspect
dsSlope  = rio.open("../../3_RSData/1_Rasters/DEM/04_srtm_epsg_32644_slope.tif")  # slope 

stnKey["row"], stnKey["col"] = rio.transform.rowcol(ds.transform, stnKey.geometry.x, stnKey.geometry.y)  # add more cols to stnkey - row,col cols added
coords = [(x,y) for x, y in zip(stnKey.geometry.x, stnKey.geometry.y)]  # x,y coords zippped
stnKey["srtm"]  = [x[0] for x in ds.sample(coords)]  # elevation info  added
stnKey["aspect"]  = [x[0] for x in dsAspect.sample(coords)]  # aspect info added
stnKey["slope"]  = [x[0] for x in dsSlope.sample(coords)]  # slope info added
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']  



# %% [markdown]
# # Read files
rasters = glob.glob("../../3_RSData/1_Rasters/1_GPM/monthly_means/3_resampled/*.tif")  
dfStn = pd.read_csv("../../2_ExcelFiles/01_StationData/07_monthly_mean.csv").drop(columns=['Unnamed: 0'])  # mean monthly station data



# %% [markdown]
# # Prepare training data
df = {}
for i in td(range(0, len(rasters)), desc='Preparing training data'):
    df[i] = pd.DataFrame() # dataframe to store X and y 
    df[i]['y'] = rio.open(rasters[i]).read(1).flatten()  # y (or dependent variable)
    df[i]['elev'] = rio.open("../../3_RSData/1_Rasters/DEM/02_srtm_epsg_32644.tif").read(1).flatten()  # X parameters (elevation, aspect and slope)
    df[i]['aspect'] = rio.open("../../3_RSData/1_Rasters/DEM/03_srtm_epsg_32644_aspect.tif").read(1).flatten()
    df[i]['slope'] = rio.open("../../3_RSData/1_Rasters/DEM/04_srtm_epsg_32644_slope.tif").read(1).flatten()
    row, col = np.zeros((66,70)), np.zeros((66,70))  # X parameters (row, col)
    for a in range(66):
        for b in range(70):
            row[a,b], col[a,b] = a,b
    df[i]['row'] = row.flatten()
    df[i]['col'] = col.flatten()
    for j in range(0, len(stnKey)):  # X parameters (station data)
        df[i]['stn_{}'.format(j+1)] = dfStn[stnKey.Station[j]][i]



# %% [markdown]
# # Train 'X' with 'y'
dfReg = {}
for i in td(range(0, len(rasters))):
    dfReg[i] = SVR(kernel='rbf')
    dfReg[i].fit(df[i].iloc[:, 1:], df[i]['y'])



# %% [markdown]
# # Predict 'y'
dfOut = {}
for i in td(range(0, len(rasters))):
    dfOut[i] = dfReg[i].predict(df[i].iloc[:,1:]).reshape(66,70)



# %% [markdown]
# # Save 'y' (as images)
for i in td(range(0, len(rasters)), desc='Saving plots'):
    plt.figure(dpi=300)
    plt.imshow(dfOut[i].reshape(66,70))
    plt.colorbar(extend='both')
    plt.title('Month = {}'.format(months[i]))
    plt.savefig("../../5_Images/05_MeanMonthlyMaps/{}_{}.png".format(str(i+1).zfill(2), months[i]), bbox_inches='tight', facecolor='w')
    plt.close()



# %% [markdown]
# # Save 'y' (as tiff maps)
referenceRas = gdal.Open(rasters[0])
dsTiff = {}
for i in td(range(len(rasters)), desc='Saving'):
    dsTiff[i] = gdal.GetDriverByName('GTiff').Create("../../3_RSData/1_Rasters/GeneratedRasters/02_MeanMonthly/{}_{}.tif".format(str(i+1).zfill(2), months[i]), xsize=referenceRas.RasterXSize, ysize=referenceRas.RasterYSize, bands=1, eType=gdal.GDT_Float32) 
    dsTiff[i].SetGeoTransform(referenceRas.GetGeoTransform())  # geotransform set
    dsTiff[i].SetProjection(referenceRas.GetProjection())  # projection set (UTM44N)
    dsTiff[i].GetRasterBand(1).WriteArray(dfOut[i].reshape(66,70))  # data in file set 
    dsTiff[i]=None  # close dataset



# %% [markdown]
# 

