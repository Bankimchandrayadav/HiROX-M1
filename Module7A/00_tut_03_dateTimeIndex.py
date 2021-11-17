# %% [markdown]
# # About
# Hints about how to get dates to timestamps to datetimeindex, useful for conversion of a timeseries geotiff data to a netcdf file, though an easier solution is given in "1_codes/07_ModelledPrecipitation/04_daily_maps_2000_2018.ipynb". Still, this format of dates can prove useful in other yet unidentified scenarios. 
# *For usage in geotiff stack to netcdf see [this link](https://stackoverflow.com/a/46900324)



# %% [markdown]
# # Libs
import glob, pandas as pd 



# %% [markdown]
## Read files 
rasOut = sorted(glob.glob("../../3_RSData/1_Rasters/GeneratedRasters/03_Daily/*.tif"))  # 1 out rasters read

dates = []
for i in range(len(rasOut)):  # 2 get dates from file names
    date = rasOut[i].split('/')[-1].split('.')[0]  # date extracted from filename
    date = date.replace('_','')  # underscore removed from date
    dates.append(pd.Timestamp(date))  # converted to timestamp format
datesPandas = pd.DatetimeIndex(dates)  # converted to pd.datetimeindex format



# %% [markdown]
# # Dates as pd.DatetimeIndex
datesPandas


# %%



