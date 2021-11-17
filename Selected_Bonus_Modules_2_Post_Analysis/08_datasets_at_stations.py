# %% [markdown]
# # About
#  This code was used to extract the values of all 15 datasets at station locations for the 'Profile analysis' under 'Results' section of Ch6 in PhD Thesis. 




# %% [markdown]
# # Libraries
from tqdm.notebook import tqdm as td 
import rasterio as rio, geopandas as gpd , matplotlib.pyplot as plt, numpy as np, glob, pandas as pd, shutil, os, time, rasterio as rio
start = time.time()
def fresh(where):
    if os.path.exists(where):
        shutil.rmtree(where)
        os.mkdir(where)
    else:
        os.mkdir(where)  # function to make folders




# %% [markdown]
# # Remove old files
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']  # to change index 
# for i in range(0, 12):
#     fresh(where="../../5_Images/03_StnVsSat_profiles/{}_{}".format(str(i+1).zfill(2), months[i]))  




# %% [markdown]
# # Prepare station key
def stationKey():
    ## Station Key  
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
    coords = [(x,y) for x, y in zip(stnKey.geometry.x, stnKey.geometry.y)]  # x,y coords zippped
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

    return stnKey
stnKey = stationKey()




# %% [markdown]
## Read files
def readFiles():
    # [1] read station data
    dfStn = pd.read_csv("../../2_ExcelFiles/01_StationData/05_monthly_mean.csv").drop(columns='Unnamed: 0')  # station data 

    # [2] read satellite and modelled data
    p = "../../3_RSData/1_Rasters/"  # common path portion
    # rasBKGN = sorted(glob.glob(p+"2_BKGN/03_resampled/*.tif"))  # original bkgn data
    rasBKGN = sorted(glob.glob(p+"2_BKGN/04_refined/*.tif"))  # refined bkgn data
    rasGPM = sorted(glob.glob(p+"1_GPM/monthly_means/3_resampled/*.tif"))
    rasERA5Land = sorted(glob.glob(p+"3_ERA5Land/monthly_means/03_resampled/*.tif"))
    rasERA5 = sorted(glob.glob(p+"4_ERA5/monthly_means/03_resampled/*.tif"))
    rasTRMM = sorted(glob.glob(p+"5_TRMM/with_time_dim/monthly_means/03_resampled/*.tif"))
    rasCHIRPS = sorted(glob.glob(p+"8_CHIRPS/monthly_means/03_resampled/*.tif"))
    rasHICHAP = sorted(glob.glob(p+"10_HICHAP/1981-2010/monthly_means/03_resampled/*.tif"))
    rasCRUTSV4 = sorted(glob.glob(p+"9_CRUTSV4/monthly_means/03_resampled/*.tif"))
    rasAPHROV1101 = sorted(glob.glob(p+"6_APHRODITE/V1101/monthly_means/03_resampled/*.tif"))
    rasAPHROV1101EXR1 = sorted(glob.glob(p+"6_APHRODITE/V1101EXR1/monthly_means/03_resampled/*.tif"))
    rasAPHROV1801R1 = sorted(glob.glob(p+"6_APHRODITE/V1101EXR1/monthly_means/03_resampled/*.tif"))
    rasAPHROV1901 = sorted(glob.glob(p+"6_APHRODITE/V1901/monthly_means/03_resampled/*.tif"))
    rasHAR10 = sorted(glob.glob(p+"7_HAR10/monthly/d10/monthly_means/03_resampled/*.tif"))
    rasHAR30 = sorted(glob.glob(p+"7_HAR10/monthly/d30/monthly_means/03_resampled/*.tif"))
    rasModelled = sorted(glob.glob(p+"GeneratedRasters/03_MeanMonthly/40_2000_2009_GPM/02_Tiff/*.tif"))

    # [3] get the above data into the dicts of 12 dataframes each
    dsGPM, dsBKGN, dsERA5Land, dsERA5, dsTRMM, dsCHIRPS, dsHICHAP, dsCRUTSV4, dsAPHROV1101, dsAPHROV1101EXR1, dsAPHROV1801R1, dsAPHROV1901, dsHAR10, dsHAR30, dsModelled= {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

    for i in range(12):
        dsBKGN[i] = rio.open(rasBKGN[i]).read(1)  
        dsGPM[i] = rio.open(rasGPM[i]).read(1)  
        dsERA5Land[i] = rio.open(rasERA5Land[i]).read(1)
        dsERA5[i] = rio.open(rasERA5[i]).read(1)
        dsTRMM[i] = rio.open(rasTRMM[i]).read(1)
        dsCHIRPS[i] = rio.open(rasCHIRPS[i]).read(1)
        dsHICHAP[i] = rio.open(rasHICHAP[i]).read(1)
        dsCRUTSV4[i] = rio.open(rasCRUTSV4[i]).read(1)
        dsAPHROV1101[i] = rio.open(rasAPHROV1101[i]).read(1)
        dsAPHROV1101EXR1[i] = rio.open(rasAPHROV1101EXR1[i]).read(1)
        dsAPHROV1801R1[i] = rio.open(rasAPHROV1801R1[i]).read(1)
        dsAPHROV1901[i] = rio.open(rasAPHROV1901[i]).read(1)
        dsHAR10[i] = rio.open(rasHAR10[i]).read(1)
        dsHAR30[i] = rio.open(rasHAR30[i]).read(1)
        dsModelled[i] = rio.open(rasModelled[i]).read(1)

    return dsGPM, dsBKGN, dsERA5Land, dsERA5, dsTRMM, dsCHIRPS, dsHICHAP, dsCRUTSV4, dsAPHROV1101, dsAPHROV1101EXR1, dsAPHROV1801R1, dsAPHROV1901, dsHAR10, dsHAR30, dsModelled, dfStn
dsGPM, dsBKGN, dsERA5Land, dsERA5, dsTRMM, dsCHIRPS, dsHICHAP, dsCRUTSV4, dsAPHROV1101, dsAPHROV1101EXR1, dsAPHROV1801R1, dsAPHROV1901, dsHAR10, dsHAR30, dsModelled, dfStn = readFiles()




# %% [markdown]
## July Koteswar
def julyKoteswar():
    ## Extract values at Koteswar ([28,19] from stnKey) for month = 6 (July)
    # [1] Prepare dataframe
    datasetNames = ['dsGPM', 'dsBKGN', 'dsERA5Land', 'dsERA5', 'dsTRMM', 'dsCHIRPS', 'dsHICHAP', 'dsCRUTSV4', 'dsAPHROV1101', 'dsAPHROV1101EXR1', 'dsAPHROV1801R1', 'dsAPHROV1901', 'dsHAR10', 'dsHAR30', 'dsModelled']
    dfTemp = pd.DataFrame(index= datasetNames, columns=['Koteswar'])

    # [2] Get dataset values into dataframe
    dfTemp.loc['dsGPM'] = dsGPM[6][28,19]
    dfTemp.loc['dsBKGN'] = dsBKGN[6][28,19]
    dfTemp.loc['dsERA5Land'] = dsERA5Land[6][28,19]
    dfTemp.loc['dsERA5'] = dsERA5[6][28,19]
    dfTemp.loc['dsTRMM'] = dsTRMM[6][28,19]
    dfTemp.loc['dsCHIRPS'] = dsCHIRPS[6][28,19]
    dfTemp.loc['dsHICHAP'] = dsHICHAP[6][28,19]
    dfTemp.loc['dsCRUTSV4'] = dsCRUTSV4[6][28,19]
    dfTemp.loc['dsAPHROV1101'] = dsAPHROV1101[6][28,19]
    dfTemp.loc['dsAPHROV1101EXR1'] = dsAPHROV1101EXR1[6][28,19]
    dfTemp.loc['dsAPHROV1801R1'] = dsAPHROV1801R1[6][28,19]
    dfTemp.loc['dsAPHROV1901'] = dsAPHROV1901[6][28,19]
    dfTemp.loc['dsHAR10'] = dsHAR10[6][28,19]
    dfTemp.loc['dsHAR30'] = dsHAR30[6][28,19]
    dfTemp.loc['dsModelled'] = dsModelled[6][28,19]

    # [3] Find difference from station value and sort the differences
    dfTemp['Difference'] = dfStn.loc[6]['CWC(KOTESWAR)'] - dfTemp.Koteswar
    dfTemp.sort_values(by='Difference', inplace=True)

    print('Staion value at Koteswar:', dfStn.iloc[6]['CWC(KOTESWAR)'], 'mm')

    return datasetNames, dfTemp
datasetNames, dfTemp = julyKoteswar()




# %% [markdown]
## July Pauri
def julyPauri():
    ## Extract values at Pauri ([32,25] from stnKey) for month = 6 (July)
    # [1] Prepare dataframe
    datasetNames = ['dsGPM', 'dsBKGN', 'dsERA5Land', 'dsERA5', 'dsTRMM', 'dsCHIRPS', 'dsHICHAP', 'dsCRUTSV4', 'dsAPHROV1101', 'dsAPHROV1101EXR1', 'dsAPHROV1801R1', 'dsAPHROV1901', 'dsHAR10', 'dsHAR30', 'dsModelled']
    dfTemp = pd.DataFrame(index= datasetNames, columns=['Pauri'])

    # [2] Get dataset values into dataframe
    dfTemp.loc['dsGPM'] = dsGPM[6][32,25]
    dfTemp.loc['dsBKGN'] = dsBKGN[6][32,25]
    dfTemp.loc['dsERA5Land'] = dsERA5Land[6][32,25]
    dfTemp.loc['dsERA5'] = dsERA5[6][32,25]
    dfTemp.loc['dsTRMM'] = dsTRMM[6][32,25]
    dfTemp.loc['dsCHIRPS'] = dsCHIRPS[6][32,25]
    dfTemp.loc['dsHICHAP'] = dsHICHAP[6][32,25]
    dfTemp.loc['dsCRUTSV4'] = dsCRUTSV4[6][32,25]
    dfTemp.loc['dsAPHROV1101'] = dsAPHROV1101[6][32,25]
    dfTemp.loc['dsAPHROV1101EXR1'] = dsAPHROV1101EXR1[6][32,25]
    dfTemp.loc['dsAPHROV1801R1'] = dsAPHROV1801R1[6][32,25]
    dfTemp.loc['dsAPHROV1901'] = dsAPHROV1901[6][32,25]
    dfTemp.loc['dsHAR10'] = dsHAR10[6][32,25]
    dfTemp.loc['dsHAR30'] = dsHAR30[6][32,25]
    dfTemp.loc['dsModelled'] = dsModelled[6][32,25]

    # [3] Find difference from station value and sort the differences
    dfTemp['Difference'] = dfStn.loc[6]['PAURI'] - dfTemp.Pauri
    dfTemp.sort_values(by='Difference', inplace=True)

    print('Staion value at Pauri:', dfStn.iloc[6]['PAURI'], 'mm')


    return datasetNames, dfTemp
datasetNames, dfTemp1 = julyPauri()




# %% [markdown]
## July Srinagar
def julySrinagar():
    ## Extract values at Srinagar ([31, 24] from stnKey) for month = 6 (July)
    # [1] Prepare dataframe
    datasetNames = ['dsGPM', 'dsBKGN', 'dsERA5Land', 'dsERA5', 'dsTRMM', 'dsCHIRPS', 'dsHICHAP', 'dsCRUTSV4', 'dsAPHROV1101', 'dsAPHROV1101EXR1', 'dsAPHROV1801R1', 'dsAPHROV1901', 'dsHAR10', 'dsHAR30', 'dsModelled']
    dfTemp = pd.DataFrame(index= datasetNames, columns=['Srinagar'])

    # [2] Get dataset values into dataframe
    dfTemp.loc['dsGPM'] = dsGPM[6][31,24]
    dfTemp.loc['dsBKGN'] = dsBKGN[6][31,24]
    dfTemp.loc['dsERA5Land'] = dsERA5Land[6][31,24]
    dfTemp.loc['dsERA5'] = dsERA5[6][31,24]
    dfTemp.loc['dsTRMM'] = dsTRMM[6][31,24]
    dfTemp.loc['dsCHIRPS'] = dsCHIRPS[6][31,24]
    dfTemp.loc['dsHICHAP'] = dsHICHAP[6][31,24]
    dfTemp.loc['dsCRUTSV4'] = dsCRUTSV4[6][31,24]
    dfTemp.loc['dsAPHROV1101'] = dsAPHROV1101[6][31,24]
    dfTemp.loc['dsAPHROV1101EXR1'] = dsAPHROV1101EXR1[6][31,24]
    dfTemp.loc['dsAPHROV1801R1'] = dsAPHROV1801R1[6][31,24]
    dfTemp.loc['dsAPHROV1901'] = dsAPHROV1901[6][31,24]
    dfTemp.loc['dsHAR10'] = dsHAR10[6][31,24]
    dfTemp.loc['dsHAR30'] = dsHAR30[6][31,24]
    dfTemp.loc['dsModelled'] = dsModelled[6][31,24]

    # [3] Find difference from station value and sort the differences
    dfTemp['Difference'] = dfStn.loc[6]['CWC(SRINAGAR)'] - dfTemp.Srinagar
    dfTemp.sort_values(by='Difference', inplace=True)

    print('Staion value at CWC(SRINAGAR):', dfStn.iloc[6]['CWC(SRINAGAR)'], 'mm')


    return datasetNames, dfTemp
datasetNames, dfTemp2 = julySrinagar()

# %%
