# %% [markdown]
# # About
# This notebook reprojects, resamples and clips the BKGN files to the extent of study area. The files are also saved as images for quick visualization.



# %% [markdown]
# # Libs
# %% [code]
from tqdm.notebook import tqdm as td 
from osgeo import gdal
import glob, os, time, numpy as np, matplotlib.pyplot as plt, rasterio as rio, string 
start = time.time()



# %% [markdown]
# # Read files and set vars
# %% [code]
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/2_BKGN/02_tiff/*.tif"))
outDir = "../../3_RSData/1_Rasters/2_BKGN/03_resampled/"  # out directory
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']



# %% [markdown]
# # Reproject, resample and clip
# %% [code]
a=1
if a == 0:
    for i in td(range(0, len(rasters)), desc='Warping'):
        outName = outDir + "{}_{}.tif".format(str(i+1).zfill(2), months[i])  # outfile name
        gdal.Warp(
        destNameOrDestDS=outName,
        srcDSOrSrcDSTab=rasters[i],
        dstSRS="epsg:32644",  # reprojection
        xRes = 5000,  # resampling
        yRes=5000,
        outputBounds = [159236.23230056558, 3170068.6251568096, 509236.2323005656, 3500068.6251568096]  # clipping
        )



# %% [markdown]
# # Also save as images
# %% [code]
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/2_BKGN/03_resampled/*.tif"))
outDir = "../../5_Images/00_BKGNData/01_original/"  # out directory


# %% [markdown]
### All plots
# %% [code]
for i in td(range(len(rasters)), desc='Saving images'):  
    plt.figure(dpi=300)  # plotting
    plt.imshow(rio.open(rasters[i]).read(1), cmap='jet')
    plt.colorbar(extend='both')
    plt.title('Precipitation in {}'.format(rasters[i].split('/')[-1][3:6]))
    # plt.savefig(outDir + rasters[i].split('/')[-1], bbox_inches='tight', facecolor='w')
    plt.close()



# %% [markdown]
### Only JJAS plots
# %% [code]

rasters1 = rasters[5:9]
plt.rcParams["font.family"] = "Century Gothic"  # font of all plots set
for i in td(range(1), desc='Saving images'):  
    plt.figure(dpi=300)  # plotting
    plt.imshow(rio.open(rasters1[i]).read(1), cmap='jet')
    cbar = plt.colorbar(extend='both')
    cbar.set_label('mm/month', rotation=90)
    # plt.title('Precipitation in {}'.format(rasters[i].split('/')[-1][3:6]))


    # 2 Add annotation
    x0, xmax = plt.xlim()
    y0, ymax = plt.ylim()
    data_width = xmax - x0
    data_height = ymax - y0
    plt.text(x0, y0 + data_height,'({})'.format(string.ascii_lowercase[i:i+1]), size=10, bbox=dict(boxstyle="square",ec='k',fc='white'))
    # plt.savefig(outDir + rasters[i].split('/')[-1], bbox_inches='tight', facecolor='w')
    # plt.close()


# %% [code]
print('Time elapsed: {} secs'.format(np.round(time.time()-start,2)))


# %%



