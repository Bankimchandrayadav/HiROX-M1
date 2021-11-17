# %% [markdown]
# # About
# > 1. This code divides the the study area into 4-5 vertical bands based on similarity in topography  
# > 2. The criteria for band demarcation is minimum correlation b/w all the columns/profiles of a band should be greater than 90%




# %% [markdown]
# # Libs
# %% [code]
from tqdm.notebook import tqdm as td 
import rasterio as rio, matplotlib.pyplot as plt, time, pandas as pd, numpy as np, geopandas as gpd, shutil, os
from osgeo import gdal
start = time.time()
def fresh(where):
    if os.path.exists(where):
        shutil.rmtree(where)
        os.mkdir(where)
    else:
        os.mkdir(where)  # function to make folders



# %% [markdown]
# # Remove old files
# fresh(where=r"../../5_Images/04_StnVsSat_band_profiles/00_GettingBands")



# %% [markdown]
# # Prepare station key
# %% [code]
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

# [5] sort by cols
stnKey.sort_values('col', inplace=True)
stnKey.reset_index(drop=True, inplace=True)  # reset index 




# %% [markdown]
## Finding demarcations
# %% [code]
# [1] read the dem of the study area
df = pd.DataFrame(data=ds.read(1))  

# [2] view the col nos. of the stations
# [14, 15, 15, 16, 17, 18, 19, 19, 19, 19, 21, 21, 21, 22, 23, 23, 24, 25, 25, 29, 29, 30, 31, 33, 39, 39, 40, 40, 40, 46]  
[14, 15, 15, 16, 17, 18, 19, 19, 19, 21, 21, 22, 23, 23, 24, 25, 25, 29, 30, 31, 33, 39, 39, 40, 40, 46]


# [2] now find the limits (a,b,c...) based on hit and trials 
a,b,c,d,e,f = 14,18,26,39,43,47  
print(np.round(df.iloc[:,a:b].corr().min().min(),3))  
print(np.round(df.iloc[:,b:c].corr().min().min(),3))
print(np.round(df.iloc[:,c:d].corr().min().min(),3))
print(np.round(df.iloc[:,d:e].corr().min().min(),3))
print(np.round(df.iloc[:,e:f].corr().min().min(),3))




# %% [markdown]
# # Plot the profiles of bands
# %% [code]
bL = [a,b,c,d,e,f]  # 6 demarcations, hence 5 bands

# [1] Plot the profiles in bands
plt.rcParams["font.family"] = "Century Gothic"  # font of all plots set
for i in td(range(5), desc='Saving plots'):
    plt.figure(dpi=300)
    plt.plot(df.iloc[:,bL[i]:bL[i+1]])  

    # plot envelope (mean+-20%) around mean
    mean = df.iloc[:,bL[i]:bL[i+1]].mean(axis=1)
    plt.plot(mean, color='k', label='Band mean', linewidth=1.5)
    plt.fill_between(np.arange(0,66), mean*1.2, mean*0.8, color='k', alpha=0.5, hatch="//////", linewidth=0.0)

    # state correlation on each plot
    correlation = df.iloc[:,bL[i]:bL[i+1]].corr().min().min()  
    correlation = np.round(correlation,2)
    plt.plot([], [], "", alpha=0, label="Correlation: {}".format(correlation))

    # other plot properties
    # plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
    # plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
    plt.minorticks_on()
    plt.xlabel("South to North" +  r"$\rightarrow $")
    plt.ylabel("Elevation (m a.s.l.)")
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 
    # plt.title('Precipitation profiles on band {}'.format(i+1))
    plt.legend(loc=2, prop={'size': 8})
    plt.gca().invert_xaxis()  # now x axis = south to north
    plt.savefig("../../5_Images/04_StnVsSat_band_profiles/00_GettingBands/Band_{}.png".format(str(i+1).zfill(2)), facecolor='w', bbox_inches='tight')
    plt.close()



# %% [markdown]
# # Show bands on study area
# %% [code]
xcoords = bL 
band1 = np.arange(14,18, 0.1)
band2 = np.arange(18,26, 0.1)
band3 = np.arange(26,39, 0.1)
band4 = np.arange(39,43, 0.1)
band5 = np.arange(43,47, 0.1)

plt.rcParams["font.family"] = "Century Gothic"  # font of all plots set
plt.figure(dpi=300)  # plotting and filling bands
plt.imshow(ds.read(1), cmap='jet')
cbar = plt.colorbar(extend='both')
cbar.set_label('metres', rotation=90)

for xc in band1:
    plt.axvline(x=xc, alpha=0.2, color='r')
for xc in band2:
    plt.axvline(x=xc, alpha=0.2, color='g')
for xc in band3:
    plt.axvline(x=xc, alpha=0.2, color='y')
plt.axvline(x=39, color='k', linewidth=0.5)
for xc in band4:
    plt.axvline(x=xc, alpha=0.2, color='b')
for xc in band5:
    plt.axvline(x=xc, alpha=0.2, color='c')

plt.axvline(x=14, color='k', linewidth=0.5)  # seperation lines 
plt.axvline(x=18, color='k', linewidth=0.5)
plt.axvline(x=26, color='k', linewidth=0.5)
plt.axvline(x=43, color='k', linewidth=0.5)
plt.axvline(x=47, color='k', linewidth=0.5)


plt.plot([],[],"", color='r', label='Band1')  # other plot properties 
plt.plot([],[],"", color='g', label='Band2')
plt.plot([],[],"", color='y', label='Band3')
plt.plot([],[],"", color='b', label='Band4')
plt.plot([],[],"", color='c', label='Band5')
plt.legend(loc=2, prop={'size': 5})
# plt.grid(b=True, which='major', color='k', linestyle='--', alpha=0.50)
# plt.grid(b=True, which='minor', color='k', linestyle='--', alpha=0.50)
plt.xlabel("Grid columns" +  r"$\rightarrow $")
plt.ylabel(r"$\leftarrow $"+"Grid rows")
# plt.title('Profiles grouped into bands')
plt.tight_layout()
plt.savefig("../../5_Images/04_StnVsSat_band_profiles/00_GettingBands/AllBands.png", facecolor='w', bbox_inches='tight')
plt.close()




# %% [code]
print('Time elapsed: {} secs'.format(np.round(time.time()-start,2)))



# %%



