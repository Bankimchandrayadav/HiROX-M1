# %% [markdown]
# # About 
# This notebook is a small demo of slicing a dataframe by date range 



# %% [markdown]
# # Import libs 
import pandas as pd 



# %% [markdown]
# # Read station files 
dfStn = pd.read_csv("../../2_ExcelFiles/01_StationData/04_daily.csv")  # station data read 
dfStn.Date = pd.to_datetime(dfStn.Date)  # data type of date chanegd



# %% [markdown]
# ## Show df
dfStn



# %% [markdown]
# # Slice within any date range
dfStn = dfStn[(dfStn.Date>='2006-06-01') & (dfStn.Date<='2007-12-31')]  



# %% [markdown]
# ## Show df now
dfStn


# %%



