import time
start_time = time.time()

# =============================================================================
# IMPORT FUNCTIONS
# =============================================================================
from py.s1ClimateDataAPI import climateDataAPI
from py.s2CombinePrecipData import combinePrecipData
from py.s3CalculatePrecipSum import sumAverages

# =============================================================================
# DEFINE INPUT PARAMETERS
# =============================================================================
"""
The data is downloaded with 'dest_name' as file name in the "data" folder. If 
folder 'data' does not exist yet, it will be created by the script. The parameters 
as set in this script are the longitude and latitude of Cap Haitiën (Haïti), and 
the time interval from 2020-01-01 to 2022-06-23. Hence, the 'dest_name' is in 
this case set to "avg_daily_precipitation_CapHaitien_Jan2020Jun2022". This name 
should be changed when running the script again, otherwise the final CSV file will 
be overwritten.

"""

longitude = -72.206768
latitude =  19.737036
start = '2020-01-01'
end = '2022-06-23'
dest_name = "CapHaitien_Jan2020Jun2022"
sum_days = 28

# =============================================================================
# EXECUTE STEPS
# =============================================================================
# STEP 1: DOWNlOAD CLIMATE DATA WITH POWER API (see py.s1ClimateDataAPI for more info)
file_names, coordinates = climateDataAPI(longitude, latitude, start, end)

# STEP 2: COMBINE PRECIPITATION DATA INTO ONE DATAFRAME
df_combi = combinePrecipData(file_names, dest_name)

# STEP 3: ADD SUM OF AVERAGES TO DATAFRAME
df_total, csv_path = sumAverages(dest_name, df_combi, sum_days)



print(f"----- {round((time.time() - start_time), 2)} seconds -----")


# =============================================================================
# EXTRA
# =============================================================================
# # Plot list of climate data coordinates 
# import pandas as pd
# import geopandas as gpd
# from shapely.geometry import Point
# import matplotlib.pyplot as plt
# import rioxarray as rxr

# df = pd.DataFrame(coordinates, columns=['longitude', 'latitude'])
# geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]

# # urban = gpd.read_file('data/cap_haitien_polygons/urban_areas_polygon.shp')
# # urban.to_crs(crs='epsg:4326')
# mean_vv = rxr.open_rasterio("data/SAR/2021-11-25_vv_vh_vvvhratio_Stack.tiff", masked=True).squeeze()
# geo_df = gpd.GeoDataFrame(df, crs='epsg:4326', geometry=geometry)

# # Visualise raster
# f, ax = plt.subplots(figsize=(10, 10))
# ax.set(title="2021-11-25 - Cap-Haitiën")
# ax.set_axis_off()
# plt.imshow(mean_vv[0], cmap='CMRmap_r')
# plt.imshow(geo_df)
# plt.show()
