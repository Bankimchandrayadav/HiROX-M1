# %% [markdown]
# # About
# This code plots the comparisons between the monthly means (1998-2009) of sat and modelled data w.r.t the monthly means of station data. 


# %% Libraries
from tqdm.notebook import tqdm as td
import pandas as pd, matplotlib.pyplot as plt, numpy as np, shutil, geopandas as gpd, time, os, glob, rasterio as rio, seaborn as sns, string
start = time.time()




# %% Station Key
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

# [0] remove duplicates from stnKey
# [4.1] get the row, cols in a list 
rowcols = [(x,y) for x, y in zip(stnKey.row, stnKey.col)]

# [4.2] get the ids of duplicates (taken from: https://stackoverflow.com/a/23645631)
result=[idx for idx, item in enumerate(rowcols) if item in rowcols[:idx]]
stnKey.drop(index=result, inplace=True)  # duplicates removed 
stnKey.reset_index(drop=True, inplace=True)  # index reset [now 26 stations in total]




# %% Read station, sat and modelled data
# [1] station mean monthly data
dfStn = pd.read_csv("../../2_ExcelFiles/01_StationData/05_monthly_mean.csv").drop(columns='Unnamed: 0')  

# [2] csv files of sat and modelled data at stations 
dfSat = {} # empty dict 
csvFiles = sorted(glob.glob("../../2_ExcelFiles/02_SatDataAtSations/*.csv"))  
for i in td(range(len(csvFiles)), desc='Reading Sat and Modelled data'):
    dfSat[i] = pd.read_csv(csvFiles[i]).drop(columns=["Unnamed: 0"])




# %% Find errors
dfError = {}  # dictionary to store all error files
for i in td(range(len(csvFiles)), desc='Saving error files'):
    dfError[i] = dfStn-dfSat[i]
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']  # to change index 
    dfError[i].index = months  # index set
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------



# %% [markdown]
# # Sort the error matrix by station elevation
# %% [code]
# [1] new index with elevation values 
newIndex = ['Narendrangar_569', 'Rishikesh_672', 'Bhogpur_726', 'Sringar_733', 'Rudraprayag_839', 'CWC_Sringar_860', 'Deoprayag_919', 'Dunda_1042', 'Koteswar_1056', 'Pauri_1236', 'Okhimath_1244', 'Marora_1353', 'Uttarkashi_1369', 'TehriGarhwal_1394', 'Joshimath_1431', 'Keertinagar_1439', 'Nandkeshari_1558', 'Bironkhol_1607', 'Landsdown_1627', 'Bhatwari_1713', 'Karanprayag_1766', 'Tehri_1820', 'Mukhim_1950', 'Dhanolti_2494', 'Chamoli_2761', 'Badrinath_3446' ]

# [2] take transpose and sort by elevation
for i in range(len(csvFiles)):
    dfError[i] = dfError[i].T
    dfError[i].insert(0, column='srtm', value=stnKey.srtm.values)
    dfError[i].sort_values('srtm', inplace=True)

    # [3] replace index with 'newIndex' 
    dfError[i].index = newIndex
    dfError[i].drop(columns=['srtm'], inplace=True)




# %% [markdown]
## [A] Find the min-max of absolute error, MSEs and MMEs
# absolute erro
# dfError[2].abs().style.background_gradient(cmap='Wistia')  # absolute 
dfError[0].style.background_gradient(cmap='Wistia')  # actual 
dfError[0].abs().min(axis=1).to_frame().style.background_gradient(cmap='Wistia') # abs min 
dfError[0].abs().min(axis=1).to_frame().min()
dfError[0].abs().max(axis=1).to_frame().style.background_gradient(cmap='Wistia') # abs max 
dfError[0].abs().max(axis=1).to_frame().max()


# MSEs and MMes
dfError[0].abs().mean(axis=1).to_frame().style.background_gradient(cmap='Wistia') # MEE 
dfError[0].abs().mean(axis=0).to_frame().style.background_gradient(cmap='Wistia') # MME 

# relate MSEs with quartiles
stnKey.srtm.quantile([0.25,0.5,0.75])



# %% [markdown]
## [B] Finding count and average of postives and negatives  
np.sum((dfError[14] < 0).values.ravel())/312 * 100  # negatives count 
dfError[14][dfError[14]<0].abs().mean().mean() # mean of negatives
dfError[14][dfError[14]>0].abs().mean().mean() # mean of positives
dfError[14].abs().mean().mean()  # mean of all 




# %% [markdown]
## [C] Making figures 
### Figures are made by changing parts of this cell - firstly plotting for sat datasets and then for modelled one
# %% [code]

# MSE strip figures [0-12]
plt.rcParams["font.family"] = "Century Gothic"
for i in td(range(len(csvFiles)), desc='MSE Strips'):
    dfError[i].index = stnKey.sort_values('srtm').srtm.values  # indices renamed
    plt.figure(dpi=300)
    cmap = sns.color_palette("Blues", as_cmap=True)
    if i<14:
        sns.heatmap(dfError[i].abs().mean(axis=1).to_frame().T, cmap=cmap, linewidths=0.3, cbar=False, square=True, robust=True, vmin=5, vmax=135, annot=False, yticklabels=False, xticklabels=0)
        plt.tight_layout()
        outName = csvFiles[i].split('\\')[1].split('.csv')[0].upper()
        plt.savefig("../../5_Images/02_StnVsSat/06_errorElevationWise/estrip_{}.png".format(outName), bbox_inches='tight')
        plt.close()
    else:
        sns.heatmap(dfError[i].abs().mean(axis=1).to_frame().T, cmap=cmap, linewidths=0.3, cbar=False, square=True, robust=True, vmin=5, vmax=135, annot=False, yticklabels=False, xticklabels=1)
        plt.tight_layout()
        outName = csvFiles[i].split('\\')[1].split('.csv')[0].upper()
        plt.savefig("../../5_Images/02_StnVsSat/06_errorElevationWise/estrip_{}.png".format(outName), bbox_inches='tight')
        plt.close()

# %%

# visualize MSEs as a regular bar plot apart from the above heatmap 
dfError[14].abs().mean(axis=1).to_frame().plot(kind='bar', legend=0, color='gray', edgecolor='k', hatch='//////',ylim=[0,100])
plt.title("Mean station error (MSE) in Modelled data") 
plt.xlabel("Stations with elevations (m a.s.l.) ")  
plt.ylabel("Error (mm/month)")
plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
plt.tight_layout()
# plt.minorticks_on()
# plt.savefig("../../5_Images/02_StnVsSat/07_modelledErrors/modelled_03_MSE_bars.png", facecolor='w', bbox_inches='tight')


# check the range of MSEs to verify the vmin, vmax range in above 
print(dfError[14].abs().mean(axis=1).min())
print(dfError[14].abs().mean(axis=1).max()) 




# %% [markdown]
## [D1] Visualizing all of these together for a comprehensive analysis
# Get the mean of MSE strips
dataSets = ['BKGN', 'GPM', 'ERA5', 'ERA5LAND', 'TRMM', 'V1101', 'V1101EXR1', 'V1801R1', 'V1901', 'CRUTSV4', 'CHIRPS', 'HAR10', 'HAR30', 'HICHAP']
temp = pd.DataFrame(index=dfError[0].index, columns=dataSets)
for i in range(14):
    temp['{}'.format(dataSets[i])] = dfError[i].abs().mean(axis=1)
temp.index = newIndex



# %% [markdown]
## [D1] Plot
plt.rcParams["figure.dpi"] = 300
temp.mean(axis=1).to_frame().plot(kind='bar', legend=0, color='gray', hatch='//////', edgecolor='k', ylim=[0,100])
plt.title("Mean station error for all datasets") 
plt.xlabel("Stations with elevations (m a.s.l.) ")  
plt.ylabel("Error (mm/month)")
# plt.xticks(ticks=range(0,len(dfError[0].columns)), labels=np.arange(1, len(dfError[0].columns)+1))
plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
# plt.tight_layout()
# plt.minorticks_on()
# plt.savefig("../../5_Images/02_StnVsSat/06_errorElevationWise/estrip_all_datasets.png", facecolor='w', bbox_inches='tight')





# %% [markdown]
## [D2] Visualizing all of these together for a comprehensive analysis
# Get the mean of MEE strips
temp1 = pd.DataFrame(index=dfError[0].columns, columns=dataSets)
for i in range(14):
    temp1['{}'.format(dataSets[i])] = dfError[i].abs().mean(axis=0)



#%% [Markdown]
## [D2] Plot
plt.rcParams["figure.dpi"] = 300
temp1.mean(axis=1).to_frame().plot(kind='bar', legend=0, color='gray', hatch='//', edgecolor='k', ylim=[0,175], width=0.7)
plt.title("Mean monthly error for all datasets") 
plt.xlabel("Month")
plt.ylabel("Error (mm/month)")  
# plt.xticks(ticks=range(0,len(dfError[0].columns)), labels=np.arange(1, len(dfError[0].columns)+1))
plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
plt.tight_layout()
# plt.minorticks_on()
plt.savefig("../../5_Images/02_StnVsSat/06_errorElevationWise/estrip_all_datasets1.png", facecolor='w', bbox_inches='tight')




# %% [markdown]
## Plot between CWC Uttarkashi and Uttarkashi 
dfTemp = pd.read_csv("../../2_ExcelFiles/01_StationData/04_daily.csv")
plt.plot(dfTemp['CWC(UTTARKASHI)'])
plt.plot(dfTemp['UTTARKASHI'])
plt.title("Comparison of weather data at Uttarkashi from CWC and IMD") 
plt.xlabel("Days")  
plt.ylabel("Precipitation (mm/day)")
plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
plt.savefig("../../5_Images/02_StnVsSat/06_errorElevationWise/estrip_Uttarkashi.png", bbox_inches='tight', facecolor='w')


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------




# %% [markdown]
# # Error plot1
dfPlot1 = {}
for i in td(range(len(csvFiles))):
    dfPlot1[i] = dfError[i].abs().T
    colors = ['b', 'b', 'w', 'w', 'w', 'r', 'r', 'r', 'r', 'w', 'w', 'b']  # color classes as per DJF=b, JJAS=r, rest=w
    plt.rcParams["figure.dpi"] = 300
    dfPlot1[i].plot(kind='bar', stacked='True', legend=True, color=colors, edgecolor='k')
    plt.legend(loc=2, prop={'size': 4})
    dataName = csvFiles[i].split('/')[-1].split('_')[-1].split('.')[0].upper()  # extracted out data name
    plt.title("Error in {} data distributed over months ".format(dataName)) 
    plt.xlabel("Stations")  # title, labels and grid
    plt.ylabel("Error (mm/year)")
    plt.xticks(ticks=range(0,len(dfError[0].columns)), labels=np.arange(1, len(dfError[0].columns)+1))
    plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
    plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
    plt.tight_layout()
    # plt.savefig("../../5_Images/02_StnVsSat/01_errorPlot1/{}_{}.png".format(str(i+1).zfill(2), dataName), bbox_inches='tight', facecolor='w')
    # plt.close()




# %% Error plot2
dfPlot2 = {} 
for i in td(range(len(csvFiles)), desc='Saving plots'):
    # [1] read and format error dataframe 
    dfPlot2[i] = dfError[i].abs().T  # sort cols by elevation
    dfPlot2[i]['SRTM'] = list(stnKey.srtm)  
    dfPlot2[i].sort_values(by='SRTM', inplace=True)
    dfPlot2[i] = dfPlot2[i].T
    # [2] add elevation values to col header   
    newNames = []  
    for j in range(0, len(dfPlot2[0].columns)):
        newNames.append(dfPlot2[0].columns[j] + " ({})".format(int(dfPlot2[0].iloc[-1,j])))  
    dfPlot2[i].columns = newNames  # new names assigned
    dfPlot2[i] = dfPlot2[i][:-1]  # elevation row removed afer use
    # [3] plot
    colors = ['gray']*12 + ['blue']*8 + ['red']*6 + ['lime']*2 + ['green'] + ['magenta']  
    plt.rcParams["figure.dpi"] = 300
    dfPlot2[i].plot(kind='bar', stacked='True', legend=True, color=colors, edgecolor='k')
    plt.legend(prop={'size': 3}, loc=2, ncol=2)
    dataName = csvFiles[i].split('/')[-1].split('_')[-1].split('.')[0].upper()  # data name
    plt.title("Error in {} data distributed over elevation".format(dataName)) 
    plt.xlabel("Months")  # title, labels and grid
    plt.ylabel("Error (mm/year)")
    plt.xticks(ticks=range(0,len(dfPlot2[i])), labels=dfPlot2[i].index, rotation=45)
    plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
    plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
    plt.tight_layout()
    plt.savefig("../../5_Images/02_StnVsSat/02_errorPlot2/{}_{}.png".format(str(i+1).zfill(2), dataName), bbox_inches='tight', facecolor='w')
    plt.close()




# %% [markdown]
# #  Error plot3
# %% [code]
dfPlot3 = {} 
plt.rcParams["font.family"] = "Century Gothic"  # font of all plots set
for i in td(range(len(csvFiles)), desc='Saving plots'):
    # [1] read and format error dataframe 
    dfPlot3[i] = dfError[i]
    # [2] plot
    plt.figure(dpi=300)
    for j in range(0, len(dfPlot3[i].columns)):
        dataName = csvFiles[i].split('/')[-1].split('_')[-1].split('.')[0].upper() # data name
        plt.plot(dfPlot3[i].iloc[:,j])
        # plt.title("Error in {} data at stations".format(dataName))
        plt.ylim((-550,550))
        # plt.xlabel("Months")  # title, labels and grid
        plt.ylabel("Error (mm/month)")
        plt.xticks(ticks=range(0,12), labels=dfPlot3[i].index, rotation=45)
        # plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
        # plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
        plt.tight_layout()
    # plt.savefig("../../5_Images/02_StnVsSat/03_errorPlot3/{}_{}.png".format(str(i+1).zfill(2), dataName), bbox_inches='tight', facecolor='w', edgecolor='w')
    # plt.close()




# %% Error plot 3 for MS1-partA
import string
def plotsMS1PartA():

    dfPlot31 = {} 
    plt.rcParams["font.family"] = "Century Gothic"  # font of all plots set
    for i in td(range(6), desc='Saving plots'):
        # [1] read and format error dataframe 
        dfPlot31[i] = dfError[i]
        # [2] plot
        plt.figure(dpi=300)
        for j in range(0, len(dfPlot31[i].columns)):
            dataName = csvFiles[i].split('/')[-1].split('_')[-1].split('.')[0].upper() 
            plt.plot(dfPlot31[i].iloc[:,j])
            plt.ylim((-550,550))
            # plt.ylabel("Error (mm/month)")
            plt.xticks(ticks=range(0,12), labels=dfPlot31[i].index, rotation=45)
            plt.yticks(ticks=np.arange(-550,600,100), labels=np.arange(-550,600,100))
            plt.tight_layout()


        # 2 Add annotation
        x0, xmax = plt.xlim()
        y0, ymax = plt.ylim()
        data_width = xmax - x0
        data_height = ymax - y0
        plt.text(x0+data_width-0.3, y0 + data_height,'({})'.format(string.ascii_lowercase[i]), size=10, bbox=dict(boxstyle="square",ec='k',fc='white'))

        # Change xlabels, ylabels as per image position
        # https://www.geeksforgeeks.org/how-to-hide-axis-text-ticks-or-tick-labels-in-matplotlib/
        if i==0:
            ax = plt.gca()  # get current axes
            xax = ax.axes.get_xaxis()
            xax.set_visible(False)
        elif i==1 or i==2:
            ax = plt.gca()  # get current axes
            yax = ax.axes.get_yaxis()
            yax.set_visible(False)
            xax = ax.axes.get_xaxis()
            xax.set_visible(False)
        elif i==4 or i==5:
            ax = plt.gca()  # get current axes
            yax = ax.axes.get_yaxis()
            yax.set_visible(False)


        plt.savefig("../../5_Images/02_StnVsSat/03_errorPlot3/For_MS/Fig_Part_A/{}_{}.png".format(str(i+1).zfill(2), dataName), bbox_inches='tight', facecolor='w', edgecolor='w')
        plt.close()

    return None 
plotsMS1PartA()


# %% Error plot 3 for MS1-partB
def plotsMS1PartB():

    dfPlot31 = {} 
    plt.rcParams["font.family"] = "Century Gothic"  # font of all plots set
    for i in td(range(6,15), desc='Saving plots'):
        # [1] read and format error dataframe 
        dfPlot31[i] = dfError[i]
        # [2] plot
        plt.figure(dpi=300)
        for j in range(0, len(dfPlot31[i].columns)):
            dataName = csvFiles[i].split('/')[-1].split('_')[-1].split('.')[0].upper() 
            plt.plot(dfPlot31[i].iloc[:,j])
            plt.ylim((-550,550))
            # plt.ylabel("Error (mm/month)")
            plt.xticks(ticks=range(0,12), labels=dfPlot31[i].index, rotation=45)
            plt.yticks(ticks=np.arange(-550,600,100), labels=np.arange(-550,600,100))
            plt.tight_layout()


        # 2 Add annotation
        x0, xmax = plt.xlim()
        y0, ymax = plt.ylim()
        data_width = xmax - x0
        data_height = ymax - y0
        plt.text(x0+data_width-0.3, y0 + data_height,'({})'.format(string.ascii_lowercase[i]), size=10, bbox=dict(boxstyle="square",ec='k',fc='white'))

        # Change xlabels, ylabels as per image position
        # https://www.geeksforgeeks.org/how-to-hide-axis-text-ticks-or-tick-labels-in-matplotlib/
        if i in [7,8,10,]:
            ax = plt.gca()  # get current axes
            xax = ax.axes.get_xaxis()
            xax.set_visible(False)
            yax = ax.axes.get_yaxis()
            yax.set_visible(False)
        elif i in [6,9]:
            ax = plt.gca()  # get current axes
            xax = ax.axes.get_xaxis()
            xax.set_visible(False)
        elif i in [11,13]:
            ax = plt.gca()  # get current axes
            yax = ax.axes.get_yaxis()
            yax.set_visible(False)

        plt.savefig("../../5_Images/02_StnVsSat/03_errorPlot3/For_MS/Fig_Part_B/{}_{}.png".format(str(i+1).zfill(2), dataName), bbox_inches='tight', facecolor='w', edgecolor='w')
        plt.close()

    return None 
plotsMS1PartB()


# %% Error plot 3 for MS1-part A and B together
def plotsMS1PartsAB():

    dfPlot312 = {} 
    plt.rcParams["font.family"] = "Century Gothic"  # font of all plots set
    for i in td(range(14), desc='Saving plots'):

        # [1] read and format error dataframe 
        dfPlot312[i] = dfError[i]

        # [2] plot
        plt.figure(dpi=300)
        for j in range(0, len(dfPlot312[i].columns)):
            dataName = csvFiles[i].split('/')[-1].split('_')[-1].split('.')[0].upper() 
            plt.plot(dfPlot312[i].iloc[:,j])
            plt.ylim((-550,550))
            # plt.ylabel("Error (mm/month)")
            plt.xticks(ticks=range(0,12,1), labels=dfPlot312[i].index[::1], rotation=45, fontsize=18)
            plt.yticks(ticks=np.arange(-500,750,250), labels=np.arange(-500,750,250), fontsize=18)
            plt.tight_layout()

        # 2 Add annotation
        x0, xmax = plt.xlim()
        y0, ymax = plt.ylim()
        data_width = xmax - x0
        data_height = ymax - y0
        plt.text(x0+data_width-0.5, y0 + data_height,'({})'.format(string.ascii_lowercase[i]), size=20, bbox=dict(boxstyle="square",ec='k',fc='white'))

        # Change xlabels, ylabels as per image position
        # https://www.geeksforgeeks.org/how-to-hide-axis-text-ticks-or-tick-labels-in-matplotlib/
        if i in [0,3,6,9]:
            ax = plt.gca()  # get current axes
            xax = ax.axes.get_xaxis()
            xax.set_visible(False)
        elif i in [1,2,4,5,7,8,10]:
            ax = plt.gca()  # get current axes
            yax = ax.axes.get_yaxis()
            yax.set_visible(False)
            xax = ax.axes.get_xaxis()
            xax.set_visible(False)
        elif i in [11,13]:
            ax = plt.gca()  # get current axes
            yax = ax.axes.get_yaxis()
            yax.set_visible(False)

        plt.savefig("../../5_Images/02_StnVsSat/03_errorPlot3/For_MS/Fig_Part_AB/{}_{}.png".format(str(i+1).zfill(2), dataName), bbox_inches='tight', facecolor='w', edgecolor='w')
        plt.close()

    return None 
plotsMS1PartsAB()



# %% [markdown]
# # Error plot4
dfPlot4 = {}
for i in td(range(len(csvFiles)), desc='Saving plots'):
    dfPlot4[i] = dfError[i].abs().mean(axis=1)
    plt.figure(dpi=300)
    plt.bar(x=range(0,12), height=dfPlot4[i], color='gray', edgecolor='k', hatch='//')
    dataName = csvFiles[i].split('/')[-1].split('_')[-1].split('.')[0].upper()  # data name
    plt.title("Average absolute error in {} data".format(dataName)) 
    plt.ylim((0,175))
    plt.xlabel("Months")  # title, labels and grid
    plt.ylabel("Error (mm/month)")
    plt.xticks(ticks=range(0,12), labels=dfPlot4[i].index, rotation=45)
    plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
    plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
    plt.tight_layout()
    plt.savefig("../../5_Images/02_StnVsSat/04_errorPlot4/{}_{}.png".format(str(i+1).zfill(2), dataName), bbox_inches='tight', facecolor='w')
    plt.close()
print('Time elapsed: {} secs'.format(np.round(time.time()-start,2)))




# %%


