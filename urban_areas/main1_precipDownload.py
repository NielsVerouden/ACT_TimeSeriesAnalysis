import time
start_time = time.time()

# =============================================================================
# INFORMATION ABOUT THE SCRIPT
# =============================================================================
"""
_______________________________________________________________________________

INFO: 
This script downloads daily climate data with the POWER API provided by NASA. 
The Application Programming Interfaces (API) allows temporal data requests of 
POWER Analysis Ready Data (ARD), which is in this script set to daily climate data. 
Even though climate data is downloaded from the POWER API, only precipitation 
for each day is saved to a .CSV file. 

PARAMETERS:
The start and end variables define the start and end date from which the precipitation
per day should be downloaded. Precipitation data is exported with 'dest_name' as 
file name to the "precipitation_data" folder. If 'precipitation_data' folder does 
not exist yet, it will be created by the script. The parameters as set in this 
script are a boundingbox around Cap Haitiën (Haïti), and the time interval 
from 2020-01-01 to 2022-06-23. Hence, the 'dest_name' is in this case set to 
"CapHaitien_Jan2020Jun2022". This name should be changed when running the script 
again, otherwise the final CSV file will be overwritten. Besides, the 'grid'
variable is used to calculate the average precipitation within the boundingbox.
A larger grid will result in a more accurate average precipitation of the area
of interest, but also in longer computation times since data is downloaded for 
more lon/lat combinations. Hence, a large grid (5+) should only be selected whenever 
the AOI is also large. However, this is often not the case so a grid of 3 or 4 is
often accurate enough.

Moreover, sum_days defines the nr. of days for which the precipitation data should 
be summed. For instance, sum_days = 14 means that the precipitation per day between 
6 and 20 March are summed and saved to 20 March in the column 'sum_14days'.
   
It is also possible to view the coordinate combinations from which the precipitation
data is downloaded. This is only possible whenever the SAR data has first been 
downloaded and saved to the 'data/SAR_data/' directory. The SAR_path variable
corresponds to the folder within the 'SAR_data' directory which should contains 
the SAR images. Only the first image within this directory is taken for plotting. 
_______________________________________________________________________________

Source; https://power.larc.nasa.gov/
_______________________________________________________________________________
    
"""
# =============================================================================
# IMPORT FUNCTIONS
# =============================================================================
from urban_areas.py.s11ClimateDataAPI import climateDataAPI, visualiseCoordinates
from urban_areas.py.s12CombinePrecipData import combinePrecipData
from urban_areas.py.s13CalculatePrecipSum import calculatePrecipSum

# =============================================================================
# DEFINE INPUT PARAMETERS
# =============================================================================
start = '2021-01-01'
end = '2021-07-31'
coordinates = (-72.304390,19.668729,-72.112816,19.805822)
dest_name = "CapHaitien_Jan2021Jul2021"
grid = 3
sum_days = 14

# Visualise coordinates (y/n)? If so, define SAR_path
visualise = "y"
SAR_path = 'CapHaitien_Jan2021Jul2021'

# =============================================================================
# EXECUTE STEPS
# =============================================================================
# STEP 0: VISUALISE COORDINATES ON SAR DATA
coordinates_list, request_list = visualiseCoordinates(coordinates, grid, start, end, visualise, SAR_path)

# STEP 1: DOWNlOAD CLIMATE DATA WITH POWER API
file_names = climateDataAPI(request_list, start, end)

# STEP 2: COMBINE PRECIPITATION DATA INTO ONE DATAFRAME
df_combi = combinePrecipData(file_names, dest_name)

# STEP 3: ADD SUM OF AVERAGES TO DATAFRAME
df_total, csv_path = calculatePrecipSum(dest_name, df_combi, sum_days)



print(f"----- {round((time.time() - start_time), 2)} seconds -----")
