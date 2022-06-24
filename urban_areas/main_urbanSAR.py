import time
start_time = time.time()

# =============================================================================
# INFORMATION ABOUT THE SCRIPT
# =============================================================================
"""
_______________________________________________________________________________

This script extracts the mean VV backscatter values from areas that are classed 
as 'built-up' in the Global Human Settlement Layer (GHSL). A CSV file is returned
that contain the mean VV backscatter values per date for urban areas as defined
by the parameters and the SAR extent. 

For SAR_path, insert the name of the folder containing unzipped and stacked SAR 
files. For the urban_raster, the name of urban raster that should be loaded should 
be defined. Both the SAR_path and urban_raster read from the 'data' folder, so be
sure that the SAR images and the urban tif file are saved in the main 'data' folder

A tuple of (xmin, ymin, xmax, and ymax) should be defined for the 'coordinates' 
variable. This variable is used to mask the urban raster. It is advised to make 
the boundingbox similar as or larger than the extent of the SAR data. The
"built_lowerbound" variable corresponds to the multi-temporal classification of 
built-up presence. To select built-up, a value between 3 and 6 should be chosen
(default is 3). 

Finally, there is an option to show the extent of the boundingbox (from coordinates)
on the first SAR image. It visualises whether the boundingbox has correctly been
defined according to the SAR extent. Be aware of the following: (1) If the bbox is 
larger than the SAR extent, all urban areas in the SAR extent will be taken, (2) if
the bbox is smaller than the SAR extent, only the urban areas within the bbox will
be taken (even though the SAR extent is larger). Advisable to check the bbox extent
first before running the whole script.

_______________________________________________________________________________

Multi-temporal classification of built-up presence;
_______________________________________________________________________________
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

# =============================================================================
# DEFINE INPUT PARAMETERS (for more info, see above)
# =============================================================================
SAR_path = 'SAR_CapHaitien'
urban_raster = 'GHS_built_globe/GHS_BUILT_LDSMT_GLOBE_R2018A_3857_30_V2_0_8_10.tif' 
coordinates = (-72.262286,19.680749,-72.155731,19.817650)  
built_lowerbound = 3

# Show boundingbox in map? (y/n)
show_bbox = 'y'

# =============================================================================
# EXECUTE STEPS
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
df_vv = exportToCSV(mean_values, dates, SAR_path)

# =============================================================================
# VISUALISE RESULTS
# =============================================================================

#########################
# print(f"\nMean values of the urban areas are: \n{mean_values}")
# # Plot the clipped SAR data
# f, ax = plt.subplots(figsize=(10, 10))
# ax.set(title="SAR imagery - Cap-Haitiën")
# ax.set_axis_off()
# plt.imshow(SAR_im, cmap='CMRmap_r')
# plt.show()
#########################







# =============================================================================
# READ RAINFALL AND MEAN VV DATA FROM FILES
# =============================================================================
# Create path names
# sum_days = 14       # VERWIJDEREN STRAKS !!!

# csv_mean_vv = 'data/meanVV_2020-01-02_2022-03-28.csv'
# csv_urban = 'data/daily_precipitation_avg14days_CapHaitien_Jan2020Jun2022.CSV'
# sumdays_name = f"sum_{sum_days}days"

# # Read dataframe from files
# df_vv = pd.read_csv(csv_mean_vv)
# df_precip = pd.read_csv(csv_urban)

# # Combine dataframes
# df_total = pd.merge(df_precip, df_vv, on ='date')

# fig_dims = (50, 10)
# fig, ax = plt.subplots(figsize=fig_dims)
# ax.set_xticklabels(df_total.date, rotation=90)
# ax1 = sns.lineplot(x = "date", y = "mean_VV", ax=ax, data=df_total)
# ax2 = ax1.twinx()
# sns.lineplot(x = "date", y = "average_(mm/day)", ax=ax2, data=df_total, color='r')
# plt.title('Mean VV & average precipitation (in mm/day)', fontdict={'fontsize': 30})
# plt.show()

# fig_dims = (50, 10)
# fig, ax = plt.subplots(figsize=fig_dims)
# ax.set_xticklabels(df_total.date, rotation=90)
# ax1 = sns.lineplot(x = "date", y = "mean_VV", ax=ax, data=df_total)
# ax2 = ax1.twinx()
# sns.lineplot(x = "date", y = sumdays_name, ax=ax2, data=df_total, color='r')
# plt.title('Mean VV & sum_14days (in mm)', fontdict={'fontsize': 30})
# plt.show()

# # =============================================================================
# # VISUALISING RESULTS
# # =============================================================================
# nr1 = rxr.open_rasterio("data/SAR/2021-11-25_vv_vh_vvvhratio_Stack.tiff", masked=True).squeeze()
# nr2 = rxr.open_rasterio("data/SAR/2021-04-05_vv_vh_vvvhratio_Stack.tiff", masked=True).squeeze()
# nr3 = rxr.open_rasterio("data/SAR/2022-02-01_vv_vh_vvvhratio_Stack.tiff", masked=True).squeeze()
# nrlast = rxr.open_rasterio("data/SAR/2021-09-02_vv_vh_vvvhratio_Stack.tiff", masked=True).squeeze()

# # Visualise raster
# f, ax = plt.subplots(figsize=(10, 10))
# ax.set(title="2021-11-25 - Cap-Haitiën")
# ax.set_axis_off()
# plt.imshow(nr1[0], cmap='CMRmap_r')
# plt.show()

# # Visualise raster
# f, ax = plt.subplots(figsize=(10, 10))
# ax.set(title="2021-04-05 - Cap-Haitiën")
# ax.set_axis_off()
# plt.imshow(nr2[0], cmap='CMRmap_r')
# plt.show()

# # Visualise raster
# f, ax = plt.subplots(figsize=(10, 10))
# ax.set(title="2022-02-01 - Cap-Haitiën")
# ax.set_axis_off()
# plt.imshow(nr3[0], cmap='CMRmap_r')
# plt.show()

# # Visualise raster
# f, ax = plt.subplots(figsize=(10, 10))
# ax.set(title="2021-09-02 - Cap-Haitiën")
# ax.set_axis_off()
# plt.imshow(nrlast[0], cmap='CMRmap_r')
# plt.show()


print(f"----- {round((time.time() - start_time), 2)} seconds -----")
