# %% [markdown]
# # About
# ## This notebook refines the resampled BKGN files based on standard deviation and also saves the tiff files as images for quick visualization


# %% Libraries
from tqdm.notebook import tqdm as td 
import rasterio as rio, matplotlib.pyplot as plt, time, glob, numpy as np, string
from osgeo import gdal
start = time.time()


# %% Read files and set vars
def readFiles():
    rasBKGN = sorted(glob.glob("../../3_RSData/1_Rasters/2_BKGN/03_resampled/*.tif"))  
    dfBKGN = {}  # dict to store rasters
    for i in range(len(rasBKGN)):
        dfBKGN[i] = rio.open(rasBKGN[i]).read(1)  # time slices read into a dict of numpy arrays
    
    return rasBKGN, dfBKGN
rasBKGN, dfBKGN = readFiles()


# %% Filter data
def filterData():
    for k in td((range(len(rasBKGN))), desc='Removing outliers'):  # 2 filter outliers
        data = dfBKGN[k].flatten('F')  # std and mean
        dataSD = np.std(data)
        dataMean = np.mean(data)
        lower = dataMean - (dataSD*3) # lower and upper limits of data within 3SDs
        upper = dataMean + (dataSD*3)
        outliers = []  # get outliers in a list
        for item in data:
            if item > upper or item < lower:
                outliers.append(item)
        row = dfBKGN[k].shape[0]  # remove outliers
        col = dfBKGN[k].shape[1]
        for i in range(0, 66):
            for j in range(0, 70):
                if dfBKGN[k][i,j] in outliers:
                    dfBKGN[k][i,j] = np.nan  # replace the outlier entry by np.nan
                    dfBKGN[k][i,j] = np.nanmean(dfBKGN[k][i-1:i+2, j-1:j+2])  # or 3x3 window avg
                else:
                    pass 

    return dfBKGN
dfBKGN = filterData()


# %% Save filtered data tiff files 
def filteredtoTiff():

    referenceRas = gdal.Open(rasBKGN[0])  
    outDir = "../../3_RSData/1_Rasters/2_BKGN/04_refined/"
    dsTiffBKGN = {}

    for i in td(range(len(rasBKGN)), desc='Saving as tiff'):
        date = rasBKGN[i].split('\\')[-1].split('.')[0]  
        dsTiffBKGN[i] = gdal.GetDriverByName('GTiff').Create(
            outDir + "{}.tif".format(date), 
            xsize=referenceRas.RasterXSize, 
            ysize=referenceRas.RasterYSize, 
            bands=1, 
            eType=gdal.GDT_Float32)  
        dsTiffBKGN[i].SetGeoTransform(referenceRas.GetGeoTransform())  # geotransform
        dsTiffBKGN[i].SetProjection(referenceRas.GetProjection())  # projection set
        dsTiffBKGN[i].GetRasterBand(1).WriteArray(dfBKGN[i])  # data written to tiff 
        dsTiffBKGN[i]=None  # file closed after creation

    return None 
filteredtoTiff()


# %% Save filtered data to images - all months
def filteredToImagesAll():

    outDir = "../../5_Images/00_BKGNData/02_refined/"  
    plt.rcParams["font.family"] = "Century Gothic"  # font of all plots set
    for i in td(range(len(rasBKGN)), desc='Saving images'):  
        plt.figure(dpi=300)  # plotting
        plt.imshow(dfBKGN[i], cmap='jet')
        cbar = plt.colorbar(extend='both')
        cbar.set_label('mm/month', rotation=90)
        plt.title("BKGN's Precipitation in {}".format(rasBKGN[i].split('\\')[-1][3:6]))
        plt.xlabel('Grid columns' + r"$\rightarrow$")
        plt.ylabel(r"$\leftarrow$"+'Grid rows')
        plt.savefig(outDir + rasBKGN[i].split('\\')[-1].split('.tif')[0], bbox_inches='tight', facecolor='w')
        plt.close()

    return None 
filteredToImagesAll()


# %% Save filtered data to images - JJAS
def filteredToImagesJJAS():

    outDir = "../../5_Images/00_BKGNData/02_refined/JJAS/"  
    plt.rcParams["font.family"] = "Century Gothic"  # font of all plots set
    for i in td(range(5,9), desc='Saving images'):  
        plt.figure(dpi=300)  # plotting
        plt.imshow(dfBKGN[i], cmap='jet')
        cbar = plt.colorbar(extend='both')
        # cbar.set_label('mm/month', rotation=90)

        # Change xlabels, ylabels as per image position
        # https://www.geeksforgeeks.org/how-to-hide-axis-text-ticks-or-tick-labels-in-matplotlib/
        ax = plt.gca()  # get current axes
        if i==5:
            xax = ax.axes.get_xaxis()
            xax = xax.set_visible(False)
        elif i==6:
            xax = ax.axes.get_xaxis()
            xax = xax.set_visible(False)
            yax = ax.axes.get_yaxis()
            yax = yax.set_visible(False)
        elif i==8:
            yax = ax.axes.get_yaxis()
            yax = yax.set_visible(False)

        # 2 Add annotation
        x0, xmax = plt.xlim()
        y0, ymax = plt.ylim()
        data_width = xmax - x0
        data_height = ymax - y0
        plt.text(x0+data_width-1, y0 + data_height,'({})'.format(string.ascii_lowercase[i-5]), size=10, bbox=dict(boxstyle="square",ec='k',fc='white'))
        plt.savefig(outDir + rasBKGN[i].split('\\')[-1].split('.tif')[0], bbox_inches='tight', facecolor='w')
        plt.close()
    print('Time elapsed: ', np.round(time.time()-start,2), 'secs')

    return None 
filteredToImagesJJAS()


# %% [code]