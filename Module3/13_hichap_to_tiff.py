# %% [markdown]
# # About
# This notebook converts HICHAP netcdf data to tiff format and then reprojects, resamples and clips it to study area's extent



# %% [markdown]
# # Libraries
from tqdm.notebook import tqdm as td 
from pyproj import crs
import xarray as xr, gdal, rioxarray, glob, numpy as np, time
start = time.time()



# %% [markdown]
# # Read files
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/10_HICHAP/1981-2010/*.nc"))
ds = xr.open_mfdataset(rasters)  
ds = ds.sel(time=slice('1998-01','2009-12'))
ds = ds.resample(time="MS").sum()
ds = ds.groupby('time.month').mean()



# %% [markdown]
# # Save as individual netcdf files
outDir = "../../3_RSData/1_Rasters/10_HICHAP/1981-2010/monthly_means/01_netcdf/"
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
for i in td(range(0, len(ds.month)), desc='Converting to netcdf'):
    outName = outDir + "{}_{}.nc".format(str(i+1).zfill(2), months[i])  # outfile name
    ds.isel(month=i).to_netcdf(outName)  # saved as individual netcdf files



# %% [markdown]
# # Convert to tiff
#  Dropping dims or variables taken from http://xarray.pydata.org/en/stable/howdoi.html
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/10_HICHAP/1981-2010/monthly_means/01_netcdf/*.nc"))   
outDir = "../../3_RSData/1_Rasters/10_HICHAP/1981-2010/monthly_means/02_tiff/"
for i in td(range(0, len(rasters)), desc='Converting to tiff'):
    outName = outDir + "{}_{}.tif".format(str(i+1).zfill(2), months[i])  # outfile name
    ds = rioxarray.open_rasterio(rasters[i])
    # following projection copied from ds attributes 
    projWKT = 'PROJCS["WGS 84 / UTM zone 45N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",87],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32645"]]'
    proj = crs.CRS.from_wkt(projWKT)  # crs read 
    ds = ds.rio.write_crs(proj)  # original crs set 
    ds = ds.rio.reproject("epsg:4326")  # reprojected to wgs84
    ds['P'].rio.to_raster(outName) # saved as tif



# %% [markdown]
# # Reproject, resample and clip
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/10_HICHAP/1981-2010/monthly_means/02_tiff/*.tif"))
outDir = '../../3_RSData/1_Rasters/10_HICHAP/1981-2010/monthly_means/03_resampled/'
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



