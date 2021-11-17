# %% [markdown]
# # About
# This notebook generates the aspect and slope maps from dem, following [this](https://www.earthdatascience.org/tutorials/get-slope-aspect-from-digital-elevation-model/) and [this](https://richdem.readthedocs.io/en/latest/python_api.html#richdem.TerrainAttribute) link.



# %% [markdown]
# # Libs
import richdem as rd, matplotlib.pyplot as plt, gdal



# %% [markdown]
# # Read DEM
dem = rd.LoadGDAL("../../3_RSData/1_Rasters/DEM/02_srtm_epsg_32644.tif")  
plt.figure(dpi=150)  # visualize dem 
plt.imshow(dem, cmap='gist_earth')
plt.colorbar(extend='both')
plt.title("DEM of Uttarakhand")



# %% [markdown]
# # Find aspect
aspect = rd.TerrainAttribute(dem, attrib='aspect')  # aspect map generated
plt.figure(dpi=150)  # visualize aspect 
plt.imshow(aspect, cmap='magma')
plt.colorbar(extend='both')
plt.title("Aspect Map of Uttarakhand")
# rd.SaveGDAL(filename="../../3_RSData/1_Rasters/DEM/03_srtm_epsg_32644_aspect.tif", rda=aspect)  # map saved



# %% [markdown]
# # Find slope
slope = rd.TerrainAttribute(dem, attrib='slope_percentage')  # slope map generated (can use other options too)
# slope = rd.TerrainAttribute(dem, attrib='slope_riserun')  # other options 
# slope = rd.TerrainAttribute(dem, attrib='slope_degrees')
# slope = rd.TerrainAttribute(dem, attrib='slope_radians')
plt.figure(dpi=150)  # visualize slope
plt.imshow(slope, cmap='jet')
plt.colorbar(extend='both')
plt.title("Slope Map of Uttarakhand")
# rd.SaveGDAL(filename="../../3_RSData/1_Rasters/DEM/04_srtm_epsg_32644_slope.tif", rda=slope)  # slope map saved



# %%



