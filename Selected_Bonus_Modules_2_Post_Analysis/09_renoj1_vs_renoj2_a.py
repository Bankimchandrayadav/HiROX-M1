# %% [markdown] 
## This code compares RENOJ-1 and RENOJ-2 datasets on annual basis



# %% [markdown]
## Libs 
import xarray as xr, matplotlib.pyplot as plt, pandas as pd, geopandas as gpd, rasterio as rio, warnings, numpy as np
warnings.filterwarnings("ignore")  # for supressing warnings
from datetime import datetime
from tqdm.notebook import tqdm as td



# %% [markdown]
## Station Key 
def stationKey(): 
    # [1] read station shape file 
    stnKey = gpd.read_file(r"../../3_RSData/2_Vectors/1_Stations/01_stations_UTM44N1.shp") 
    stnKey.sort_values('Sno', inplace=True)  # sort all cols according to 'Sno'
    stnKey.reset_index(drop=True, inplace=True)  # reset index 

    # [2] read dem, slope and aspect files
    ds = rio.open("../../3_RSData/1_Rasters/DEM/02_srtm_epsg_32644.tif")  # dem 
    dsAspect = rio.open("../../3_RSData/1_Rasters/DEM/03_srtm_epsg_32644_aspect.tif")  # aspect 
    dsSlope  = rio.open("../../3_RSData/1_Rasters/DEM/04_srtm_epsg_32644_slope.tif")  # slope 

    # [3] add info from above files in columns
    stnKey["row"], stnKey["col"] = rio.transform.rowcol(ds.transform, stnKey.geometry.x, stnKey.geometry.y)  # 3 add more cols to stnkey - row,col cols added
    coords = [(x,y) for x, y in zip(stnKey.geometry.x, stnKey.geometry.y)]  # x,y zippped
    stnKey["srtm"]  = [x[0] for x in ds.sample(coords)]  # elevation info  added
    stnKey["aspect"]  = [x[0] for x in dsAspect.sample(coords)]  # aspect info added
    stnKey["slope"]  = [x[0] for x in dsSlope.sample(coords)]  # slope info added

    # [4] remove duplicates from stnKey
    # [4.1] get the row, cols in a list 
    rowcols = [(x,y) for x, y in zip(stnKey.row, stnKey.col)]

    # [4.2] get the ids of duplicates (taken from: https://stackoverflow.com/a/23645631)
    result=[idx for idx, item in enumerate(rowcols) if item in rowcols[:idx]]
    stnKey.drop(index=result, inplace=True)  # duplicates removed 
    stnKey.reset_index(drop=True, inplace=True)  # index reset [now 26 stations in total]
    
    # [5] sort according to elevation 
    # https://www.geeksforgeeks.org/how-to-move-a-column-to-first-position-in-pandas-dataframe/
    stnKey.drop(columns=['Sno'], inplace=True)  # SNo removed
    stnKey.insert(0,'srtm', stnKey.pop('srtm'))  # srtm brought to first position 
    stnKey.sort_values('srtm', inplace=True)  # sort acc. to elevation
    stnKey.reset_index(drop=True, inplace=True)  # reset index 

    return stnKey
stnKey = stationKey()



# %% [markdown]
## Annual station data
def readStnData():
    # [1] read 
    dfStn = pd.read_csv("../../2_ExcelFiles/01_StationData/04_daily.csv")

    # [2] change datatype of date
    for i in range(len(dfStn)):  
        dateString = (dfStn.Date[i]).split('/')  # date read as string
        dfStn.Date[i] = datetime(year=int(dateString[2]), month=int(dateString[1]), day=int(dateString[0]))  # dtype converted 

    # [3] set date as index and subset to RENOJ1/2's duration
    dfStn.set_index('Date', inplace=True)  # dates set as index 
    dfStn.index.names=[None] # extra rows in col heads removed
    dfStn = dfStn.loc['2000-06-01':'2018-05-31']  # subset to common duration 


    # [4] change datatype to 'float32'
    dfStn = dfStn.astype('float32')

    # [5] resample to annual scales and sort them acc. to stnKey
    dfStnAnn = dfStn.resample('AS').sum()  # annual

    # [6] sort them all according to stnKey 
    dfStn = dfStn[stnKey.Station]
    dfStnAnn = dfStnAnn[stnKey.Station]

    return dfStnAnn
dfStnAnn = readStnData()



# %% [markdown]
## Annual RENOJ1 and RENOJ2 data
def readModData():
    # [1] read
    ds1 = xr.open_dataset("../../3_RSData/1_Rasters/GeneratedRasters/02_DailyNetcdf/03_Complete_GPM_APHRO/SingleFile/prcp_1972_2018.nc")
    ds2 = xr.open_dataset("../../3_RSData/1_Rasters/GeneratedRasters/02_DailyNetcdf/05_RENOJ2/SingleFile/prod2.nc")

    # [2] clip to common duration 
    ds1 = ds1.sel(time=slice('2000-06-01','2018-05-31'))
    ds2 = ds2.sel(time=slice('2000-06-01','2018-05-31'))

    # [3] remove extra dims 
    ds1 = ds1.squeeze()
    ds2 = ds2.squeeze()

    # [4] resample to annual scale 
    ds1Ann = ds1.resample(time='AS').sum()
    ds2Ann = ds2.resample(time='AS').sum()


    return ds1Ann, ds2Ann
ds1Ann, ds2Ann = readModData()



# %% [markdown]
## Get RENOJ1/2 values in 'dfStnAnn' dataframe format 
def fetchModData():
    # [1] prepare dataframe template 
    df1Ann = pd.DataFrame(columns=dfStnAnn.columns, index=dfStnAnn.index)
    df2Ann = pd.DataFrame(columns=dfStnAnn.columns, index=dfStnAnn.index)

    # [2] get the row,cols of all stations together
    rowCols = [[x,y] for x, y in zip(stnKey.row, stnKey.col)]  # row and cols zipped

    # [3] get the values in RENOJ1/2 dataframes for every station (26) and every year (19)
    # [3.1] filling the RENOJ1 dataframe (column wise)
    for i in td(range(26), desc='Fetching values'):
        for j in range(19):
            df1Ann.iloc[j,i] = ds1Ann.prcp_renoj.isel(time=j).values[rowCols[i][0], rowCols[i][1]]

    # [3.2] filling the RENOJ2 dataframe (column wise)
    for i in td(range(26), desc='Fetching values'):
        for j in range(19):
            df2Ann.iloc[j,i] = ds2Ann.prcp_renoj.isel(time=j).values[rowCols[i][0], rowCols[i][1]]

    return df1Ann, df2Ann 
df1Ann, df2Ann = fetchModData()



# %% [markdown]
## Plots for annual comparison
def plots1():
    for i in td(range(26), desc='Annual plots'):
        plt.figure(dpi=300)
        plt.scatter(x=dfStnAnn.index, y=dfStnAnn.iloc[:,i], color='k', marker='x', label='Station')
        plt.plot(df1Ann.iloc[:,i], label='RENOJ-1', color='blue')
        plt.plot(df2Ann.iloc[:,i], label='RENOJ-2', color='green')
        plt.ylim([0,3500])
        # if i == 0:
        plt.legend(prop={'size': 8}, loc=1, ncol=1)
        plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
        plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
        plt.tight_layout()
        plt.title("Annual precipitation") 
        plt.xlabel("Years")  
        plt.ylabel("Annual precipitation (mm/year)")
        plt.savefig("../../5_Images/08_Validation/02_RENOJ1vs2/{}_{}.png".format(str(i+1).zfill(2), dfStnAnn.columns[i]), bbox_inches='tight', facecolor='w')
        plt.close()
plots1()



# %% [markdown]
## Correlation b.w RENOJ-1/2 and station values
def correlation():
    # [1] firstly change dtype from 'object' to 'float' or it will raise error 
    dfStnAnn = dfStnAnn.astype('float32')
    df1Ann = df1Ann.astype('float32')
    df2Ann = df2Ann.astype('float32')

    # [2] find correlation
    # [2.1] template dataframe
    dfcorr = pd.DataFrame(columns=['RENOJ2vsSTN', 'RENOJ1vsSTN'], index=df1Ann.columns) 

    # [2.2] find correlation
    for i in td(range(26), desc='Finding correlation'):
        dfcorr.iloc[i,0] = df2Ann.iloc[:,i].corr(dfStnAnn.iloc[:,i])
        dfcorr.iloc[i,1] = df1Ann.iloc[:,i].corr(dfStnAnn.iloc[:,i])

    # [2.3] round off and sort accoring to difference
    dfcorr = (dfcorr.astype(float)*100).round(2)
    dfcorr['Diff'] = (dfcorr['RENOJ2vsSTN'] - dfcorr['RENOJ1vsSTN']).abs()
    dfcorr.sort_values(by='Diff', inplace=True)

    return dfcorr
dfcorr = correlation()



# %%
