#Predict flood/dry/flooded urban based on a model


import rasterio as rio
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.windows import Window
from rasterio.plot import reshape_as_raster, reshape_as_image
import numpy as np
from matplotlib import pyplot as plt

file_location = 'TrainingData\\2021_04_05\\TrainingSentinel_2021_04_05.tiff'
model = gnb
training_polys = polys

with rio.open(file_location) as src:
    # may need to reduce this image size if your kernel crashes, takes a lot of memory
    img = src.read()

# Take our full image and reshape into long 2d array (nrow * ncol, nband) for classification
print(img.shape)
reshaped_img = reshape_as_image(img)
print(reshaped_img.shape)

class_prediction = model.predict(reshaped_img.reshape(-1, 3))

# Reshape our classification map back into a 2D matrix so we can visualize it
class_prediction = class_prediction.reshape(reshaped_img[:, :, 0].shape)

#Helper function to convert numbers to string labels:
def str_class_to_int(class_array):
   class_array[class_array == np.unique(training_polys["Label"])[0]] = 0
   class_array[class_array == np.unique(training_polys["Label"])[1]] = 1
   class_array[class_array == np.unique(training_polys["Label"])[2]] = 2
   return(class_array.astype(int))

class_prediction = str_class_to_int(class_prediction)


######Visualize:
def color_stretch(image, index):
    colors = image[:, :, index].astype(np.float64)
    for b in range(colors.shape[2]):
        colors[:, :, b] = rio.plot.adjust_band(colors[:, :, b])
    return colors
    
# find the highest pixel value in the prediction image
n = int(np.max(class_prediction))

# next setup a colormap for our map
colors = dict((
    (0, (139,69,19, 255)),      # Brown - dry area
    (1, (48, 156, 214, 255)),    # Blue - flooded
    (2, (96, 19, 134, 255)),    # Purple - flooded urban
))

# Put 0 - 255 as float 0 - 1
for k in colors:
    v = colors[k]
    _v = [_v / 255.0 for _v in v]
    colors[k] = _v
    
index_colors = [colors[key] if key in colors else 
                (255, 255, 255, 0) for key in range(0, n+1)]

cmap = plt.matplotlib.colors.ListedColormap(index_colors, 'Classification', n+1)
fig, axs = plt.subplots(2,1,figsize=(10,7))

img_stretched = color_stretch(reshaped_img, [0,1,2])
axs[0].imshow(img_stretched)

axs[1].imshow(class_prediction, cmap=cmap, interpolation='none')

fig.show()