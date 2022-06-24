import time
start_time = time.time()

# =============================================================================
# IMPORT FUNCTIONS
# =============================================================================
from urban_areas.py.s11ClimateDataAPI import climateDataAPI
from urban_areas.py.s12CombinePrecipData import combinePrecipData
from urban_areas.py.s13CalculatePrecipSum import calculatePrecipSum

# =============================================================================
# DEFINE INPUT PARAMETERS
# =============================================================================
"""
The data is downloaded with 'dest_name' as file name in the "data" folder. If 
folder 'data' does not exist yet, it will be created by the script. The parameters 
as set in this script are the longitude and latitude of Cap Haitiën (Haïti), and 
the time interval from 2020-01-01 to 2022-06-23. Hence, the 'dest_name' is in this 
case set to "CapHaitien_Jan2020Jun2022". This name should be changed when running 
the script again, otherwise the final CSV file will be overwritten. Besides, the 
sum of the last 14 days is taken, which also influences the name of the final CSV
file

"""

longitude = -72.206768
latitude =  19.737036
start = '2020-01-01'
end = '2022-06-23'
dest_name = "CapHaitien_Jan2020Jun2022"
sum_days = 14

# =============================================================================
# EXECUTE STEPS
# =============================================================================
# STEP 1: DOWNlOAD CLIMATE DATA WITH POWER API (see py.s1ClimateDataAPI for more info)
file_names, coordinates = climateDataAPI(longitude, latitude, start, end)

# STEP 2: COMBINE PRECIPITATION DATA INTO ONE DATAFRAME
df_combi = combinePrecipData(file_names, dest_name)

# STEP 3: ADD SUM OF AVERAGES TO DATAFRAME
df_total, csv_path = calculatePrecipSum(dest_name, df_combi, sum_days)



print(f"----- {round((time.time() - start_time), 2)} seconds -----")