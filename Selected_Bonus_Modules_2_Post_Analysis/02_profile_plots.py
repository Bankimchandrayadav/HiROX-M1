# %% [markdown]
# # About
#  This notebook was used to get profile plots at station locations for all the satellite data and modelled data




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




# %% [markdown]
## Read files
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




# %% [markdown]
# # Profile plots
for j in range(len(months)):
    for i in td(range(len(stnKey)), desc='{}'.format(months[j])):
        plt.figure(dpi=300)
        # [1] plotting - satellite and modelled data
        plt.plot(dsAPHROV1101[j][:,stnKey.col[i]], label='APHRO-V1101', color='blue') 
        plt.plot(dsAPHROV1101EXR1[j][:,stnKey.col[i]], label='APHRO-V1101EXR1', color='blue', linestyle='dashed')
        plt.plot(dsAPHROV1801R1[j][:,stnKey.col[i]], label='APHRO-V1801R1', color='blue', linestyle='dotted')
        plt.plot(dsAPHROV1901[j][:,stnKey.col[i]], label='APHRO-V1901', color='blue', marker='o', markersize=2) 
        plt.plot(dsERA5Land[j][:,stnKey.col[i]], label='ERA5Land', color='magenta')   
        plt.plot(dsERA5[j][:,stnKey.col[i]], label='ERA5', color='magenta', linestyle='dashed')   
        plt.plot(dsGPM[j][:,stnKey.col[i]], label='GPM', color='red')  
        plt.plot(dsTRMM[j][:,stnKey.col[i]], label='TRMM', color='red', linestyle='--')   
        plt.plot(dsHAR10[j][:,stnKey.col[i]], label='HAR10', color='tab:brown') 
        plt.plot(dsHAR30[j][:,stnKey.col[i]], label='HAR30', color='tab:brown', linestyle='--') 
        plt.plot(dsCHIRPS[j][:,stnKey.col[i]], label='CHIRPS', color='gold', linestyle='-') 
        plt.plot(dsHICHAP[j][:,stnKey.col[i]], label='HICHAP', color='gold', linestyle='--')   
        plt.plot(dsCRUTSV4[j][:,stnKey.col[i]], label='CRUTSV4', color='gold', linestyle='-', marker='o', markersize=2 ) 
        plt.plot(dsBKGN[j][:,stnKey.col[i]], label='BKGN', color='lime')   
        plt.plot(dsModelled[j][:,stnKey.col[i]], label='MODELLED', color='black')

        # envelope around modelled data
        mod = dsModelled[j][:,stnKey.col[i]]
        plt.fill_between(np.arange(0,66), mod*1.2, mod*0.8, color='k', alpha=0.5)

        # [2] add station data
        plt.scatter(x=stnKey.row[i], y=dfStn['{}'.format(stnKey.Station[i])][j], color='k', s=40, zorder=20, label=stnKey.Station[i])  # station data

        # [3] set other plot properties 
        plt.gca().invert_xaxis()  # now x axis = south to north
        plt.legend(loc=2, prop={'size': 5})
        plt.title("Profile plots for {}".format(months[j]))
        plt.xlabel("South to North" +  r"$\rightarrow $")
        plt.ylabel("Precipitation (mm/month)")
        plt.tight_layout()
        plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
        plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
        plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 
        plt.minorticks_on()
        plt.savefig("../../5_Images/03_StnVsSat_profiles/{}_{}/{}_{}.png".format(str(j+1).zfill(2), months[j], str(i+1).zfill(2), stnKey.Station[i]), facecolor='w')
        plt.close()
print('Time elapsed: {} mins'.format(np.round((time.time()-start)/60, 2)))




# %%



