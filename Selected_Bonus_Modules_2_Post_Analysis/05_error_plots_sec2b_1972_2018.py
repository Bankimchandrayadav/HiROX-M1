# %% [markdown]
# # About
# > This code plots the comparisons between the monthly means (1972-2018) of modelled data w.r.t the monthly means of station data. 




# %% [markdown]
# # Libraries
from tqdm.notebook import tqdm as td
import pandas as pd, matplotlib.pyplot as plt, numpy as np, shutil, geopandas as gpd, time, os, glob, rasterio as rio
start = time.time()




# %% [markdown]
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

# [5] keep only stations with Zone=HELT
result = []
for i in range(len(stnKey)):
    if not stnKey.Zone[i] == 'HELT':
        result.append(i)
stnKey.drop(index=result, inplace=True)  # duplicates removed 
stnKey.reset_index(drop=True, inplace=True)  # index reset [now 3 stations in total (sec2b)]




# %% [markdown]
# # Read station, sat and modelled data
# [1] station mean monthly data
dfStn = pd.read_csv("../../2_ExcelFiles/01_StationData/06_monthly_mean_1972_2018.csv").drop(columns='Unnamed: 0')  
dfStn = dfStn[stnKey.Station]

# [2] csv files of sat and modelled data at stations 
dfMod =  pd.read_csv("../../2_ExcelFiles/03_ModelledData/01_monthly_mean_1972_2018.csv").drop(columns='Unnamed: 0')  
dfMod = dfMod[stnKey.Station]






# %% [markdown]
# # Find errors
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']  # to change index 
dfError = dfStn - dfMod
dfError.index = months  # index set




# %% [markdown]
# # Error plot1
# dfPlot1 = {}
# for i in td(range(len(csvFiles))):
#     dfPlot1[i] = dfError[i].abs().T
#     colors = ['b', 'b', 'w', 'w', 'w', 'r', 'r', 'r', 'r', 'w', 'w', 'b']  # color classes as per DJF=b, JJAS=r, rest=w
#     plt.rcParams["figure.dpi"] = 300
#     dfPlot1[i].plot(kind='bar', stacked='True', legend=True, color=colors, edgecolor='k')
#     plt.legend(loc=2, prop={'size': 4})
#     dataName = csvFiles[i].split('/')[-1].split('_')[-1].split('.')[0].upper()  # extracted out data name
#     plt.title("Error in {} data distributed over months ".format(dataName)) 
#     plt.xlabel("Stations")  # title, labels and grid
#     plt.ylabel("Error (mm/year)")
#     plt.xticks(ticks=range(0,len(dfError[0].columns)), labels=np.arange(1, len(dfError[0].columns)+1))
#     plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
#     plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
#     plt.tight_layout()
#     plt.savefig("../../5_Images/02_StnVsSat/01_errorPlot1/{}_{}.png".format(str(i+1).zfill(2), dataName), bbox_inches='tight', facecolor='w')
#     plt.close()




# %% [markdown]
# # Error plot2
# dfPlot2 = {} 
# for i in td(range(len(csvFiles)), desc='Saving plots'):
#     # [1] read and format error dataframe 
#     dfPlot2[i] = dfError[i].abs().T  # sort cols by elevation
#     dfPlot2[i]['SRTM'] = list(stnKey.srtm)  
#     dfPlot2[i].sort_values(by='SRTM', inplace=True)
#     dfPlot2[i] = dfPlot2[i].T
#     # [2] add elevation values to col header   
#     newNames = []  
#     for j in range(0, len(dfPlot2[0].columns)):
#         newNames.append(dfPlot2[0].columns[j] + " ({})".format(int(dfPlot2[0].iloc[-1,j])))  
#     dfPlot2[i].columns = newNames  # new names assigned
#     dfPlot2[i] = dfPlot2[i][:-1]  # elevation row removed afer use
#     # [3] plot
#     colors = ['gray']*12 + ['blue']*8 + ['red']*6 + ['lime']*2 + ['green'] + ['magenta']  
#     plt.rcParams["figure.dpi"] = 300
#     dfPlot2[i].plot(kind='bar', stacked='True', legend=True, color=colors, edgecolor='k')
#     plt.legend(prop={'size': 3}, loc=2, ncol=2)
#     dataName = csvFiles[i].split('/')[-1].split('_')[-1].split('.')[0].upper()  # data name
#     plt.title("Error in {} data distributed over elevation".format(dataName)) 
#     plt.xlabel("Months")  # title, labels and grid
#     plt.ylabel("Error (mm/year)")
#     plt.xticks(ticks=range(0,len(dfPlot2[i])), labels=dfPlot2[i].index, rotation=45)
#     plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
#     plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
#     plt.tight_layout()
#     plt.savefig("../../5_Images/02_StnVsSat/02_errorPlot2/{}_{}.png".format(str(i+1).zfill(2), dataName), bbox_inches='tight', facecolor='w')
#     plt.close()




# %% [markdown]
# # #  Error plot3
# plt.figure(dpi=300)
# for j in range(len(dfError.columns)):
#     plt.plot(dfError.iloc[:,j])
#     plt.ylim((-400,400))
#     plt.xlabel("Months")  # title, labels and grid
#     plt.ylabel("Error (mm/month)")
#     plt.xticks(ticks=range(0,12), labels=dfError.index, rotation=45)
#     plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
#     plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
#     plt.tight_layout()




# %% [markdown]
# # Error plot4
dfError1 = dfError.abs().mean(axis=1)
plt.rcParams["figure.dpi"] = 300
plt.figure(dpi=300)
plt.bar(x=range(0,12), height=dfError1, color='gray', edgecolor='k', hatch='/////')
plt.title("Mean absolute error in Section 2B in RENOJ-2") 
plt.xlabel("Months")  # title, labels and grid
plt.ylabel("Error (mm/month)")
plt.legend(loc=2, prop={'size': 4})
plt.xticks(ticks=range(0,12), labels=dfError.index, rotation=45)
plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
plt.tight_layout()
plt.savefig("../../5_Images/02_StnVsSat/05_errorsForSec2B/Overall.png", bbox_inches='tight', facecolor='w')





# %%


