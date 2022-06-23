import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from shapely.geometry import mapping
import rioxarray as rxr
import geopandas as gpd
import rasterio as rio
import pandas as pd
import os
import time
from os import listdir
from os.path import isfile, join

start_time = time.time()
# =============================================================================
# STEP 1: DEFINE INPUT PARAMETERS
# =============================================================================
SAR_path = "data/SAR/"
urban_path = "data/cap_haitien_polygons/urban_areas_polygon.shp"

# =============================================================================
# STEP 2: DEFINE FUNCTIONS
# =============================================================================
def defineSARDates(SAR_path):
    # Add all SAR files to one variable and create list of dates
    file_names = [file for file in listdir(SAR_path) if isfile(join(SAR_path, file))]
    dates = []
    for i in file_names:
        dates.append(i[0:10])
    return file_names, dates

def changeCRS(SAR_path, file_names):
    # Open first SAR file as rasterio object
    raster = rio.open(os.path.join(SAR_path, file_names[0]))
    
    # Assign CRS of SAR image to variable
    epsg_code = int(raster.crs.data['init'][5:])

    return epsg_code

def meanCalculator(urban_path, epsg_code, SAR_path, file_names):
    # Read urban polygon as geopandas (gpd)
    urban_poly = gpd.read_file(urban_path)

    # Change CRS of urban polygon to CRS of SAR raster
    urban_poly = urban_poly.to_crs(epsg=epsg_code)
    
    # Create emply list for appending mean values of clipped SAR
    mean_values = []
    
    for file in file_names:
        # Create path to each file
        SAR_path = os.path.join(SAR_path, file)

        # Open raster as rioxarray (rxr) object and only select VV scatter (band 1)
        SAR_im = rxr.open_rasterio(SAR_path, masked=True).squeeze()[0]

        # Clip radar data to urban areas (This can take some time. This function 
        # makes a clip for each individual file. We have also looked at stacking 
        # the images as one tiff file before clipping but this does not speed up 
        # the process)
        SAR_clipped = SAR_im.rio.clip(urban_poly.geometry.apply(mapping))

        # Calculate mean value and append to list
        mean_values.append(int(SAR_clipped.mean()))
        
    return mean_values

def exportToCSV(mean_values, dates):
    # Create dataframe of mean VV values per date
    df_vv = pd.DataFrame({'mean_VV':mean_values, 'date':dates})

    # Create name for csv file based on dates, and write dataframe to csv file
    csv_name = f'data/meanVV_{dates[0]}_{dates[-1]}.csv'
    df_vv.to_csv(csv_name, encoding='utf-8', index=False)
    return df_vv

# =============================================================================
# STEP 3: EXECUTE FUNCTIONS
# =============================================================================
# Define dates of SAR images
file_names, dates = defineSARDates(SAR_path)

# Define EPSG code of SAR images
epsg_code = changeCRS(SAR_path, file_names)

# Clip SAR images to urban polygon extent and calculate mean values
mean_values = meanCalculator(urban_path, epsg_code, SAR_path)

# Create pandas DataFrame and export it as .csv file
df_vv = exportToCSV(mean_values, dates)












print(f"--- {round((time.time() - start_time), 2)} seconds ---")

##########################
# print(f"\nMean values of the urban areas are: \n{mean_values}")
# Plot the clipped SAR data
# f, ax = plt.subplots(figsize=(10, 10))
# ax.set(title="SAR imagery - Cap-Haitiën")
# ax.set_axis_off()
# plt.imshow(SAR_im, cmap='CMRmap_r')
# plt.show()
##########################

# # =============================================================================
# # READ RAINFALL AND MEAN VV DATA FROM FILES
# # =============================================================================
# # Create path names
# csv_mean_vv = 'data/meanVV_2020-01-02_2022-03-28.csv'
# csv_urban = csv_path

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
# sns.lineplot(x = "date", y = "sum_28days", ax=ax2, data=df_total, color='r')
# plt.title('Mean VV & sum_28days (in mm)', fontdict={'fontsize': 30})
# plt.show()


# plt.rcParams["figure.figsize"] = (30, 5)
# ax = df_total.plot(x="date", y="mean_VV", legend=False)
# ax2 = ax.twinx()
# df_total.plot(x="date", y="sum_14days", ax=ax2, legend=False, color='r')
# ax2.figure.legend(fancybox=True, framealpha=1, shadow=True, borderpad=1)
# plt.show()







# highest = df_total.sort_values('mean_VV', ascending=True)
# highest.head(10)

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


# # =============================================================================
# # CHECK FOR OUTLIERS WITHIN DATAFRAME
# # =============================================================================
# import scipy.stats as st
# import plotly.express as px
# import plotly.io as pio
# pio.renderers.default = 'browser'

# # VISUALY CHECK OUTLIERS
# hist = px.histogram(df, x='mean')
# hist.show()
# box = px.box(df, y='mean')
# box.show()

# # STATISTICALLY CHECK OUTLIERS
# def find_outliers_IQR(df):
#    q1=df.quantile(0.25)
#    q3=df.quantile(0.75)
#    IQR=q3-q1
#    outliers = df[((df<(q1-1.5*IQR)) | (df>(q3+1.5*IQR)))]
#    return outliers
# find_outliers_IQR(df['mean'])


# # Confidence interval
# x = df['mean'].mean()
# t = 1.96
# s = df['mean'].std()
# n = len(df)

# def confidence_interval(x, t, s, n):
#     CI_high = x + t*(s/(n*0.5))
#     CI_low = x - t*(s/(n*0.5))
#     return CI_high, CI_low

# CI_h, CI_l = confidence_interval(x, t, s, n)

# CI = st.norm.interval(alpha=0.95, loc=np.mean(df['mean']), scale=st.sem(df['mean']))