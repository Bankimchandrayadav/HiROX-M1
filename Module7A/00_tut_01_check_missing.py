# %% [markdown]
# # About
# This notebook is a demonstration of how to to check for missing data when reading time series data - here GPM and GLADS data taken for example



# %% [markdown]
# # Libs
import glob, datetime



# %% [markdown]
# # GPM data
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/1_GPM/daily/*.nc4"))  # 1 read files 
c=0

for i in range(0, len(rasters)-1):  # 2 Fix missing data    
    date1Str = rasters[i].split('3IMERG.')[-1].split('-')[0]  # read first date (dtype=string)    
    date1 = datetime.datetime.strptime(date1Str, '%Y%m%d')  # change dtype to datetime format
    date2Str = rasters[i+1].split('3IMERG.')[-1].split('-')[0]  # read consecutive date 
    date2 = datetime.datetime.strptime(date2Str, '%Y%m%d')  # change its dtype
    if (date2-date1).days == 1:  # checking for missing data
        pass
    else:
        print('Missing data between {} and {}'.format(date1Str, date2Str))
        c+=1

if c==0:  # 3 Success message if everything is ok   
    dateInitial = datetime.datetime.strptime(rasters[0].split('3IMERG.')[-1].split('-')[0], '%Y%m%d')
    dateLast = datetime.datetime.strptime(rasters[-1].split('3IMERG.')[-1].split('-')[0], '%Y%m%d')    
    print('First date =', dateInitial) 
    print('Last Date =', dateLast)
    print('Interval in days =', (dateLast-dateInitial).days)
    print('No. of files =', len(rasters))
    print('Hence, no missing files')
# Note: In prior runs of this function there were 4 missing files and I downloaded them mannually using the url links file 



# %% [markdown]
# # GLADS data
rasters = sorted(glob.glob("../../3_RSData/1_Rasters/12_GLDAS/*.nc4"))  # 1 read GLADS data
c=0
for i in range(0, len(rasters)-1):  # 2 fix missing data
    date1Str = rasters[i].split('.A')[-1].split('.')[0]  # got first date
    date1 = datetime.datetime.strptime(date1Str, '%Y%m%d')       
    date2Str = rasters[i+1].split('.A')[-1].split('.')[0]  # got second date
    date2 = datetime.datetime.strptime(date2Str, '%Y%m%d')
    if (date2-date1).days == 1:
        pass
    else:
        # print('Missing data between {} and {}'.format(date1Str, date2Str))
        c+=1

if c==0:  # Message if there is no missing data
    dateInitial = datetime.datetime.strptime(rasters[0].split('.A')[-1].split('.')[0], '%Y%m%d')
    dateLast = datetime.datetime.strptime(rasters[-1].split('.A')[-1].split('.')[0], '%Y%m%d')    
    print('First date =', dateInitial) 
    print('Last Date =', dateLast)
    print('Interval in days =', (dateLast-dateInitial).days)
    print('No. of files =', len(rasters))
    print('Hence, no missing files')
# Note: In prior runs of this function there were several missing files and I downloaded them mannually using url links file



# %%



