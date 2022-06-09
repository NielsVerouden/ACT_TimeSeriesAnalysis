# Import packages
import rasterio
import matplotlib.pyplot as plt
import pandas as pd
from os import chdir, getcwd

# Set working directory
wd=getcwd()
chdir('C:\Users\me\Documents')

C:\Users\markb\OneDrive - Wageningen University & Research

# Open dataset
water_data = rasterio.open(r'act/data/water_data.tif')

whole = rasterio.open(r'data/occurrence_80W_20Nv1_3_2020.tif')

# PLot data
plt.imshow(water_data.read(1), cmap='pink')

# Create an array
water_data_read = water_data.read(1)

# PLot the water data
plt.imshow(water_data_read)

water = water_data_read

# PLot the threshold wherin the water bodies are different from the land
plt.imshow(water, cmap='pink')

# Create dataframe
water = pd.DataFrame(water_data_read)

# Mask values greater than 10
water = water.mask(water < 1, None)

# PLot the water bodies
plt.imshow(water)



caphaitien_coords = [-72.273903,19.671135,-72.159233,19.798714]
