import seaborn as sns
import rasterio as rio
from rasterio.plot import show_hist
import matplotlib.pyplot as plt
import numpy as np
from rasterio.plot import reshape_as_image
import glob
import os
from sklearn import tree
import numpy as np
import pandas as pd
def show_histograms(folder):
    filenames = os.listdir(folder)
    filenames_sorted = sorted(filenames)
    
    for id, filename in enumerate(filenames_sorted):
        filepath=os.path.join(folder, filename)
        title = str(filename[0:10]) #date
        
        with rio.open(filepath,'r') as src:

            fig, axhist = plt.subplots(1, 1, figsize=(20, 20))
            show_hist(src, ax=axhist, bins=100, lw=0.0, stacked=False, 
                      alpha=0.3, histtype='stepfilled', density=True)
    
            axhist.set_title(title, size=60)
            axhist.legend(list(src.descriptions), prop={'size': 40})
            axhist.set_ylim([0,0.00005])
            plt.show()
            #optional: add code to save histograms in a folder

def show_backscatter(folder):
    filenames = os.listdir(folder)
    filenames_sorted = sorted(filenames)
    # Function to normalize bands into 0.0 - 1.0 scale
    def normalize(array):
        array_min, array_max = array.min(), array.max()
        return (array - array_min) / (array_max - array_min)
    
    for id, filename in enumerate(filenames_sorted):
        filepath=os.path.join(folder, filename)
        title = str(filename[0:10]) #select date as title
        with rio.open(filepath,'r') as src:
            #show(src,title=title, transform=src.transform, adjust='linear')
            
            #Read bands
            vv=src.read(1)
            vh=src.read(2)
            ratio=src.read(3)

            #Normalize values to enable RGB plotting
            vv_norm = normalize(vv)
            vh_norm = normalize(vh)
            ratio_norm = normalize(ratio)
            
            #Stack normalized arrays
            stck = np.dstack((vv_norm,vh_norm,ratio_norm))
            
            #Open new plotting device and show image
            plt.figure()
            plt.imshow(stck)
            plt.suptitle(title)
            plt.show()

######Visualize predictions:
def visualizePrediction(masked_predictions_names, input_folder):
    for filename in masked_predictions_names:
        date=filename[48:58]
        
        #search for files in the directory with stacked images
        pattern = '%s/*%s*.tiff' % (input_folder,date)
        for file in glob.glob(pattern):
            image_path = file
        
        with rio.open(filename) as prediction_src:
            prediction=prediction_src.read()
            
        with rio.open(image_path) as src:
            # may need to reduce this image size if your kernel crashes, takes a lot of memory
            img = src.read()
        
        # Take our full image and reshape into long 2d array (nrow * ncol, nband) for classification
        reshaped_img = reshape_as_image(img)
        reshaped_prediction = reshape_as_image(prediction)
        
        def color_stretch(image, index):
            colors = image[:, :, index].astype(np.float64)
            for b in range(colors.shape[2]):
                colors[:, :, b] = rio.plot.adjust_band(colors[:, :, b])
            return colors
            
        # find the highest pixel value in the prediction image
        n = int(np.max(reshaped_prediction))
        
        # next setup a colormap for our map
        colors = dict((
            (0, (139,69,19, 255)),      # Brown - dry area
            (1, (48, 156, 214, 255)),    # Blue - flooded
            (2, (96, 19, 134, 255)),    # Purple - flooded urban
            (100,(206, 224, 196, 255))  #Lime - water
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
        
        axs[1].imshow(reshaped_prediction, cmap=cmap, interpolation='none')
        fig.suptitle(date)
        fig.show()
    plt.close(fig)
    #credit: http://patrickgray.me/open-geo-tutorial/chapter_5_classification.html
    
###Visualize a tree from a Random Forest 
def visualizeTreeFromRF(rf,data):
    #fn=data.feature_names
    #cn=data.target_names
    plt.figure()
    fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (4,4), dpi=800)
    tree.plot_tree(rf.estimators_[0],
                   feature_names = ["VV","VH","Ratio","DEM","GHS"], 
                   class_names=["Dry","Flooded","FloodedUrban"],
                   filled = True,
                  proportion=False,
                  max_depth=5);
    plt.show()
    #fig.savefig('rf_individualtree.png')

def visualizeData(X,y):
    df = pd.DataFrame(columns=['VV', 'VH',"VV/VH","GHS","DEM"], data=X)
    df['Label'] = y
    plt.figure()
    sns.pairplot(df, height=2.5, hue='Label')
    plt.show()
    return
