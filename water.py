# Import packages
import rasterio
import matplotlib.pyplot as plt
import pandas as pd


# Open dataset
test = rasterio.open(r'data/really_small_area/really_small.tif')

whole = rasterio.open(r'data/occurrence_80W_20Nv1_3_2020.tif')

# PLot data
plt.imshow(test.read(1), cmap='pink')

# Create an array
test_arr = test.read(1)

# PLot the water data
plt.imshow(test_arr)


# Create metadata about the file to save it
metadata = test.profile


metadata.update(
        dtype=rasterio.uint8,
        count=1,
        compress='lzw')

# Set the land values to None
metadata['nodata'] = None

# Create only 0 and 1 values
def create_mask (water_data): 
    for i in range(0,len(water_data)):
        for j in range(0, len(water_data)):
            if water_data[i][j] < 1:
                water_data[i][j] = 0
            else:
                water_data[i][j] = 1
    return(water_data)

create_mask(test_arr)
            
# Plot the result
plt.imshow(test_arr)

# Save as tif
with rasterio.open('water.tif', 'w', **metadata) as dst:
    dst.write(test_arr)
    
    
    




caphaitien_coords = [-72.273903,19.671135,-72.159233,19.798714]
