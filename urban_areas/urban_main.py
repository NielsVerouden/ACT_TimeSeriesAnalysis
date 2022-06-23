import time
start_time = time.time()

# =============================================================================
# IMPORT FUNCTIONS
# =============================================================================
from py.downloadClimateData import downloadClimateData




# =============================================================================
# STEP 1: DEFINE INPUT PARAMETERS
# =============================================================================
# Possible time intervals are "hourly", "daily", or "monthly". The data is 
# downloaded to the 'dest_name' folder in the "data" folder. The standard 
# dest_name is "climate_data", so data is stored in "./data/climate_date/___.csv".
longitude = -72.206768
latitude =  19.737036
start = '2020-01-01'
end = '2022-04-25'
dest_name = "climate_data"  
time_interval =  'daily'

# =============================================================================
# STEP 2: DOWNlOAD CLIMATE DATA WITH POWER API (see script for more info)
# =============================================================================
df_rain = downloadClimateData(lon=longitude, lat=latitude, start=start, end=end, dest_name=dest_name, time_interval=time_interval)






print(f"----- {round((time.time() - start_time), 2)} seconds -----")