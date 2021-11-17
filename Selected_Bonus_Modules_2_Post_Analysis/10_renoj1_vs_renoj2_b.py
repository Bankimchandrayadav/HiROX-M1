# %% [markdown] 
## This code compares RENOJ-1 and RENOJ-2 datasets on monthly mean basis


# %% Libs 
import xarray as xr, matplotlib.pyplot as plt, pandas as pd, geopandas as gpd, rasterio as rio, warnings, numpy as np
warnings.filterwarnings("ignore")  # for supressing warnings
from datetime import datetime
from tqdm.notebook import tqdm as td
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']  


# %% Station Key 
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


# %% Get the monthly mean of station data
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

    # [5] get the monthly mean
    dfStn = dfStn.resample('MS').sum()  # resampled to monthly scale
    dfStnMM = dfStn.groupby(dfStn.index.month).mean() 

    # [6] sort according to stnKey 
    dfStnMM = dfStnMM[stnKey.Station]

    return dfStnMM
dfStnMM = readStnData()


# %% Get the monthly mean of RENOJ1 and RENOJ2
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

    # [4] get the monthly mean 
    ds1 = ds1.resample(time='MS').sum()
    ds1MM = ds1.groupby('time.month').mean()
    ds2 = ds2.resample(time='MS').sum()
    ds2MM = ds2.groupby('time.month').mean()


    return ds1MM, ds2MM
ds1MM, ds2MM = readModData()


# %% Get RENOJ1/2 values in 'dfStnMM' format 
def fetchModData():
    # [1] prepare dataframe template 
    df1MM = pd.DataFrame(columns=dfStnMM.columns, index=dfStnMM.index)
    df2MM = pd.DataFrame(columns=dfStnMM.columns, index=dfStnMM.index)

    # [2] get the row,cols of all stations together
    rowCols = [[x,y] for x, y in zip(stnKey.row, stnKey.col)]  # row and cols zipped

    # [3] get the values in RENOJ1/2 dataframes for every station (26) and every month (12)
    # [3.1] filling the RENOJ1 dataframe (column wise)
    for i in td(range(26), desc='Fetching RENOJ-1'):
        for j in range(12):
            df1MM.iloc[j,i] = ds1MM.prcp_renoj.isel(month=j).values[rowCols[i][0], rowCols[i][1]]

    # [3.2] filling the RENOJ2 dataframe (column wise)
    for i in td(range(26), desc='Fetching RENOJ-2'):
        for j in range(12):
            df2MM.iloc[j,i] = ds2MM.prcp_renoj.isel(month=j).values[rowCols[i][0], rowCols[i][1]]

    return df1MM, df2MM 
df1MM, df2MM = fetchModData()


# %% Plots for monthly mean comparison - station wise
def plots1():
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']  
    for i in td(range(26), desc='MM plots 1'):
        plt.figure(dpi=300)
        plt.scatter(x=dfStnMM.index, y=dfStnMM.iloc[:,i], color='k', marker='x', label='Station')
        plt.plot(df1MM.iloc[:,i], label='HiROX-1', color='blue')
        plt.plot(df2MM.iloc[:,i], label='HiROX-2', color='green')
        plt.ylim([0,600])
        plt.xticks(np.arange(1,13,1), labels=months)
        # if i == 0:
        plt.legend(prop={'size': 8}, loc=1, ncol=1)
        plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
        plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
        plt.tight_layout()
        plt.title("Monthly mean precipitation at stations") 
        plt.xlabel("Months")  
        plt.ylabel("Monthly mean precipitation (mm/month)")
        plt.savefig("../../5_Images/08_Validation/03_RENOJ1vs2_MM/{}_{}.png".format(str(i+1).zfill(2), dfStnMM.columns[i]), bbox_inches='tight', facecolor='w')
        plt.close()
    return months
months=plots1()


# %% Correlation for the above cell
def corr1():
    # [1] firstly change dtype from 'object' to 'float' or it will raise error 
    dfSTN = dfStnMM.astype('float32')
    df1 = df1MM.astype('float32')
    df2 = df2MM.astype('float32')

    # [2] find correlation
    # [2.1] template dataframe
    dfcorr1 = pd.DataFrame(columns=['RENOJ2vsSTN', 'RENOJ1vsSTN'], index=dfSTN.columns) 

    # [2.2] find correlation
    for i in td(range(26), desc='Finding correlation'):
        dfcorr1.iloc[i,0] = df1.iloc[:,i].corr(dfSTN.iloc[:,i])
        dfcorr1.iloc[i,1] = df2.iloc[:,i].corr(dfSTN.iloc[:,i])

    # [2.3] round off and sort accoring to difference
    dfcorr1 = (dfcorr1.astype(float)*100).round(2)
    dfcorr1['Diff'] = (dfcorr1['RENOJ2vsSTN'] - dfcorr1['RENOJ1vsSTN']).abs()
    dfcorr1.sort_values(by='Diff', inplace=True)

    return dfcorr1 
dfcorr1 = corr1()


# %% Plots for monthly mean comparison - month wise
def plots2():
    for i in td(range(12), desc='MM plots 2'):
        plt.figure(dpi=300)
        dfStnMM.iloc[i].plot(label='Station Data', kind='bar', edgecolor='k', color='gainsboro', hatch='//')
        plt.plot(df1MM.iloc[i], label='RENOJ-1', color='blue')
        plt.plot(df2MM.iloc[i], label='RENOJ-2', color='green')
        plt.xticks(np.arange(0,26,1), labels=dfStnMM.columns, rotation=90)
        if i==0:
            plt.legend(prop={'size': 8}, loc=1, ncol=1)
        # plt.ylim([0,700])
        plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
        plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
        plt.title("Monthly mean precipitation - {}".format(months[i])) 
        plt.xlabel("Stations")  
        plt.ylabel("Precipitation (mm/month)")
        plt.savefig("../../5_Images/08_Validation/04_RENOJ1vs2_MM2/{}_{}.png".format(str(i+1).zfill(2), months[i]), bbox_inches='tight', facecolor='w')
        plt.close()
plots2()


# %% Correlation for the above cell 
def corr2():
    # [1] firstly change dtype from 'object' to 'float' or it will raise error 
    dfSTN = dfStnMM.astype('float32')
    df1 = df1MM.astype('float32')
    df2 = df2MM.astype('float32')

    # [2] find correlation
    # [2.1] template dataframe
    dfcorr2 = pd.DataFrame(columns=['RENOJ2vsSTN', 'RENOJ1vsSTN', 'RENOJvsRENOJ2'], index=dfSTN.index) 

    # [2.2] find correlation
    for i in td(range(12), desc='Finding correlation'):
        dfcorr2.iloc[i,0] = df2.iloc[i].corr(dfSTN.iloc[i])
        dfcorr2.iloc[i,1] = df1.iloc[i].corr(dfSTN.iloc[i])
        dfcorr2.iloc[i,2] = df2.iloc[i].corr(df1.iloc[i])

    # [2.3] round off and sort accoring to difference
    dfcorr2 = (dfcorr2.astype(float)*100).round(2)
    dfcorr2['Diff'] = (dfcorr2['RENOJ2vsSTN'] - dfcorr2['RENOJ1vsSTN']).abs()
    # dfcorr2.sort_values(by='Diff', inplace=True)
    # dfcorr2.reset_index(drop=True, inplace=True)

    return dfcorr2
dfcorr2 = corr2()


# %% Differnce plots w.r.t above two cells 
def plots3():
    for i in td(range(1), desc='Difference plots'):
        plt.figure(dpi=300)
        (df1MM.iloc[i] - df2MM.iloc[i]).plot(color='gainsboro', kind='bar', edgecolor='black', hatch='//', ylim=[-14,14])
        plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
        plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
        plt.title("Precipitation offset - {}".format(months[i])) 
        plt.xlabel("Stations")  
        plt.ylabel("Precipitation (mm/month)")
        # plt.savefig("../../5_Images/08_Validation/05_RENOJ1vs2_Diff/{}_{}.png".format(str(i+1).zfill(2), months[i]), bbox_inches='tight', facecolor='w')
        # plt.close()
plots3()


# %% A summary plot of all correlation plots of the above two cells i.e. dfcorr2
def plots4():
    plt.figure(dpi=300)
    dfcorr2.iloc[:,0].plot(label='HiROX-2 vs. STN', color='tab:blue')
    dfcorr2.iloc[:,1].plot(label='HiROX-1 vs. STN', color='tab:green')
    dfcorr2.iloc[:,2].plot(label='HiROX-2 vs. HiROX-1', color='tab:red')
    plt.xticks(np.arange(0,12,1), labels=months)
    plt.legend(prop={'size': 6}, loc=3, ncol=3)
    plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
    plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
    plt.title("Correlation between HiROX-1/2 and stations") 
    plt.xlabel("Months")  
    plt.ylabel("Correlation (%)")
    plt.ylim([0,110])
    plt.savefig("../../5_Images/08_Validation/Correlation_Summary.png", bbox_inches='tight', facecolor='w')
    plt.close()
plots4()


# %% Plots for monthly mean comparison - monthly average
def plots5():
    plt.figure(dpi=300)
    dfStnMM.mean(axis=1).plot(label='Station Data', kind='bar', color='gainsboro', edgecolor='k', hatch='////')
    df1MM.mean(axis=1).plot(label='RENOJ-1', color='blue')
    df2MM.mean(axis=1).plot(label='RENOJ-2', color='green')
    plt.xticks(np.arange(0,12,1), labels=months, rotation=90)
    plt.legend(prop={'size': 8}, loc=1, ncol=1)
    plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
    plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
    plt.title("Comparision of RENOJ-1/2 with station data - all stations") 
    plt.xlabel("Stations")  
    plt.ylabel("Monthly mean precipitation (mm/month)")
    plt.savefig("../../5_Images/08_Validation/MM_all_stations.png", bbox_inches='tight', facecolor='w')
    plt.close()
plots5()



# %%
