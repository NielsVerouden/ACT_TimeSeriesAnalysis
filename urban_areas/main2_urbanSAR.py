import time
start_time = time.time()

# =============================================================================
# INFORMATION ABOUT THE SCRIPT
# =============================================================================
"""
_______________________________________________________________________________

INFO:
This script extracts the mean VV backscatter values from areas that are classed 
as 'built-up' in the Global Human Settlement Layer (GHSL). At the current moment,
a CSV file is exported that contains the mean VV backscatter values per date, as
well as the average precipitation per date and the sum of the last x days. Moreover
several outlier detection methods are done to find outliers in the dataset. The
outliers, which are linked to the dates in the dataset, are both plotted and exported
to the same CSV file as the mean VV backscatter. This CSV file is saved in the 
following directory -> 'urban_areas/output/outlierDetection/___.CSV'

PARAMETERS:
For SAR_path, insert the name of the folder containing unzipped and stacked SAR 
files. All SAR directories should be placed in 'data/SAR_data/...' whenever you
download the data from the EO Browser website. The EO Learn API saves the SAR 
images automatically to the correct directory. For the urban_raster, the name of 
urban raster that should be loaded should be defined. In our case, all GHSL files 
are saved to a folder called 'GHS_built_globe' inside the 'data' folder. Moreover,
the name of the GHSL has been changed somewhat so it becomes easier to know which
file should be imported (raster for Haiti -> "GHS_BUILT_LDSMT_GLOBE_R2018A_HAITI.tif")

A tuple of (xmin, ymin, xmax, and ymax) should be defined for the 'coordinates' 
variable. This variable is used to mask the urban raster. It is also possible to 
leave the coordinates variable empty (i.e. assign an empty tuple). In this case, 
the exact extent of the SAR images will be taken. Be aware of the following: 
(1) If the bbox is larger than the SAR extent, all urban areas in the SAR extent 
will be taken, (2) if the bbox is smaller than the SAR extent, only the urban areas 
within the bbox will be taken (even though the SAR extent is larger). Advisable 
to check the bbox extent first before running the whole script (this is done by
only running STEP 1 of EXECUTE RASTER CLIPPING). 

The "built_lowerbound" variable corresponds to the multi-temporal classification of 
built-up presence. To select built-up, a value between 3 and 6 should be chosen
(default is 3). There is also an option to show the extent of the boundingbox 
(from coordinates) on the first SAR image. It visualises how the boundingbox has
been defined relative to the SAR extent. Finally, the file name of the precipitation 
csv should be defined. This file should be saved in the 'precipitation_data' folder 
inside the main 'data' folder. Do not forget to add '.CSV' behind the file name. 
_______________________________________________________________________________

Multi-temporal classification of built-up presence;
0 = no data
1 = water surface
2 = land no built-up in any epoch
3 = built-up from 2000 to 2014 epochs
4 = built-up from 1990 to 2000 epochs
5 = built-up from 1975 to 1990 epochs
6 = built-up up to 1975 epoch
_______________________________________________________________________________

Source; https://ghsl.jrc.ec.europa.eu/documents/GHSL_Data_Package_2019.pdf?t=1637939855 (Table 2)
_______________________________________________________________________________
"""

# =============================================================================
# IMPORT FUNCTIONS
# =============================================================================
from urban_areas.py.s21UrbanClipping import createBbox
from urban_areas.py.s21UrbanClipping import maskUrban
from urban_areas.py.s21UrbanClipping import rasterToPolygon
from urban_areas.py.s21UrbanClipping import clipSAR
from urban_areas.py.s21UrbanClipping import exportToCSV
from urban_areas.py.s22VisualiseData import visualiseData
from urban_areas.py.s23OutlierDetection import visualOutlierDetection
from urban_areas.py.s23OutlierDetection import statisticalOutlierDetection
from urban_areas.py.s23OutlierDetection import visualiseStatisticalOutliers
from urban_areas.py.s23OutlierDetection import exportOutlierDetection

# =============================================================================
# DEFINE INPUT PARAMETERS (for more info, see above)
# =============================================================================
# PARAMETERS FOR RASTER CLIPPING
# Make 'coordinates' an empty tuple to take SAR image as extent 
SAR_path = 'ValkenburgMar2021Sep2021'
urban_raster = 'GHS_built_globe/GHS_BUILT_LDSMT_GLOBE_R2018A_NETHERLANDS.tif' 
coordinates = (5.812265,50.853351,5.851490,50.879097)
built_lowerbound = 3

# Show boundingbox in map? (y/n)
show_bbox = 'y'

# =============================================================================
# PARAMETERS FOR VISUALISATION
# Add file name of the precipitation data that should be linked to the mean vv (including '.CSV')
precipitation_csv = 'daily_precipitation_avg14days_ValkenburgMar2021Dec2021.CSV'

# =============================================================================
# EXECUTE RASTER CLIPPING
# =============================================================================
# STEP 1: CREATE BOUNDING BOX AROUND URBAN AREA
bbox = createBbox(coordinates, SAR_path, show_bbox)

# STEP 2: MASK URBAN RASTER BY BBOX
temp_path_masked = maskUrban(urban_raster, bbox)

# STEP 3: CONVERT MASKED RASTER TO POLYGON
urban_polygon_masked = rasterToPolygon(temp_path_masked, SAR_path, built_lowerbound)

# STEP 4: CLIP POLYGON WITH SAR IMAGES
mean_values, dates = clipSAR(SAR_path, urban_polygon_masked)

# STEP 5: EXPORT MEAN VALUES AS CSV FILE
file_name, path_mean_vv = exportToCSV(mean_values, dates, SAR_path)

# =============================================================================
# VISUALISE RESULTS AND OUTLIER DETECTION
# =============================================================================
# STEP 1: LINEPLOTS OF MEAN VV BACKSCATTER, AVG PRECIPITATION, AND SUM PRECIPITATION
df_total, days, mean_VV, sum_xdays = visualiseData(SAR_path, precipitation_csv, file_name, path_mean_vv)

# STEP 2: VISUAL OUTLIER DETECTION
visualOutlierDetection(SAR_path, df_total, days, mean_VV, sum_xdays)

# STEP 3: STATISTICAL OUTLIER DETECTION
df_outlier, LR_columns = statisticalOutlierDetection(df_total, mean_VV, sum_xdays)
visualiseStatisticalOutliers(SAR_path, df_outlier, LR_columns, mean_VV, sum_xdays, days)

# STEP 4: EXPORT OUTLIER DETECTION DF
exportOutlierDetection(df_outlier, SAR_path)


print(f"----- {round((time.time() - start_time), 2)} seconds -----")
