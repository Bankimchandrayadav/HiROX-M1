# %% [markdown]
# # About
# This notebook converts TRMM netcdf data to tiff format and then reprojects, resamples and clips it to study area's extent



# %% [markdown]
# # Libraries
from tqdm.notebook import tqdm as td 
import xarray as xr, gdal, rioxarray, glob, numpy as np, time
start = time.time()



# %% [markdown]
# # Read files
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/5_TRMM/with_time_dim/*.nc"))[:144]
ds = xr.open_mfdataset(rasters)  
ds = ds*24*30
ds = ds.groupby('time.month').mean()



# %% [markdown]
# # Save as individual netcdf files
outDir = "../../3_RSData/1_Rasters/5_TRMM/with_time_dim/monthly_means/01_netcdf/"  # outdir
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
for i in td(range(0, len(ds.month)), desc='Converting to netcdf'):
    outName = outDir + "{}_{}.nc".format(str(i+1).zfill(2), months[i])  # outfile name
    ds.isel(month=i).to_netcdf(outName)  # saved as individual netcdf files



# %% [markdown]
# # Convert to tiff
#  Dropping dims or variables taken from http://xarray.pydata.org/en/stable/howdoi.html
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/5_TRMM/with_time_dim/monthly_means/01_netcdf/*.nc"))   
outDir = "../../3_RSData/1_Rasters/5_TRMM/with_time_dim/monthly_means/02_tiff/"
for i in td(range(0, len(rasters)), desc='Converting to tiff'):
    outName = outDir + "{}_{}.tif".format(str(i+1).zfill(2), months[i])  # outfile name
    ds = rioxarray.open_rasterio(rasters[i])  
    ds = ds.rename({'x': 'y','y': 'x'})  # renamed coz x and y were read interchanged
    ds = ds.transpose('band', 'y', 'x')  # set dim order to as expected by rioxarray i.e. (band,y,x)
    ds = ds.rio.write_crs("epsg:4326")  # crs set 
    ds['precipitation'].rio.to_raster(outName) # saved as tif



# %% [markdown]
# snowman2's reply: https://github.com/corteva/rioxarray/issues/47#issuecomment-740755254  
# ds.precipitation.squeeze().transpose('nlat', 'nlon').rio.set_spatial_dims(x_dim="nlon", y_dim="nlat").rio.to_raster("1998_01_01.tif")



# %% [markdown]
# # Reproject, resample and clip
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/5_TRMM/with_time_dim/monthly_means/02_tiff/*.tif"))
outDir = '../../3_RSData/1_Rasters/5_TRMM/with_time_dim/monthly_means/03_resampled/'
for i in td(range(0, len(rasters)), desc='Warping'):
    outName = outDir + "{}_{}.tif".format(str(i+1).zfill(2), months[i])  # outfile name
    gdal.Warp(
        destNameOrDestDS=outName,
        srcDSOrSrcDSTab=rasters[i],
        dstSRS="epsg:32644",  # reprojection
        xRes = 5000,  # resampling
        yRes=5000,
        outputBounds = [159236.23230056558, 3170068.6251568096, 509236.2323005656, 3500068.6251568096]  # clip
    )



# %%
print('Time elapsed: {} secs'.format(np.round(time.time()-start)))


# %%



