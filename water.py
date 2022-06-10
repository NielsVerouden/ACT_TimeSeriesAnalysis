# Import packages
import rasterio
import matplotlib.pyplot as plt
import pandas as pd


# Open dataset
water_data = rasterio.open(r'data/really_small_area/really_small.tif')

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

# Mask values lower than 1
water = water.mask(water < 1, None)

# PLot the water bodies
plt.imshow(water)

# Convert to array again
water = water.to_numpy()

# Create metadata about the file to save it
metadata = water_data.profile


metadata.update(
        dtype=rasterio.uint8,
        count=1,
        compress='lzw')

# Set the land values to None
metadata['nodata'] = None

water = water.mask(water > water.quantile(0))



    
plt.imshow(water_data_read)

for i in range(0,11):
    for j in range(0,10):
        if water_data_read[i][j] < 1:
            water_data_read[i][j] = 0
        else:
            water_data_read[i][j] = 1

# Save as tif
with rasterio.open('water.tif', 'w', **metadata) as dst:
    dst.write(water_data_read)


caphaitien_coords = [-72.273903,19.671135,-72.159233,19.798714]
