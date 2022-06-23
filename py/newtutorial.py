from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import geopandas as gpd
import pandas as pd
from rasterstats import zonal_stats
import os
import numpy as np
import rasterio as rio
from rasterio.plot import reshape_as_raster, reshape_as_image
training_folder = "./data/TrainingDataHaiti"
date_folder= "2021_04_05"

def loadTrainingData(training_folder):
    #Retrieve all folders in the training_folder
    trainingDates = os.listdir(training_folder)
    dataframes = []
    #For each folder, we are going to extract the mean pixel values in the training polygons:
    for index, date_folder in enumerate(trainingDates):
        for file in os.listdir(os.path.join(training_folder,date_folder)):
            #Load shapefile using geopandas:
            if file.endswith(".shp"):
                pointfile=os.path.join(training_folder,date_folder,file)
        
            #Retrieve the filepath to get the raster file (used later to open the file)                   
            if file.endswith(".tiff") and file.startswith("TrainingSentinel"):
                sentinel_location = os.path.join(training_folder,date_folder,file)
        #sentinel_location = "./data/SentinelTimeSeriesStacked/2021-04-05_vv_vh_vvvhratio_Stack.tiff"
                
        df = gpd.read_file(pointfile) #Create geodataframe from the points
        stats = ['mean'] 
        
        with rio.open(sentinel_location) as src:
            transform = src.transform
            names=src.descriptions
            band_count = src.count
            
            #For each band, calculate the mean pixel values using zonal statistics
            #Put these means in a dataframe called df2
            #Then, join this dataframe to df, which contains the information from the shapefile
            for i in range(1,band_count+1):
                df2 = pd.DataFrame(zonal_stats(vectors=df['geometry'], raster=src.read(i),affine=transform,  stats=stats))
                df2.columns=['{0}_{1}'.format(stat, names[i-1]) for stat in stats]
                df = df.join(df2)
        dataframes.append(df) 
    #Now concatenate all dataframes in a single dataframe, containing all training data
    df = pd.concat(dataframes)
    #We now have:
    #df.columns.tolist()
    #['Shape_Leng','Shape_Area','Class','Label','geometry','mean_VV','mean_VH','mean_VV/VH_ratio','mean_Population','mean_DEM']
        
    #Split data into train and test (https://stackoverflow.com/questions/24147278/how-do-i-create-test-and-train-samples-from-one-dataframe-with-pandas)
    msk = np.random.rand(len(df)) < 0.8
    train = df[msk]
    test = df[~msk]
    return (train, test)


#Train the model
def TrainModel(training_data):
    predictor_cols = ['mean_VV','mean_VH','mean_VV/VH_ratio','mean_Population','mean_DEM']
    X = training_data[predictor_cols].values.tolist() #List of lists: [64.0, 33.0, 41.0, 43.0] #X are the stats/predictor data
    y = training_data['Label'].tolist() #y[:5]: [1, 1, 1, 1, 1] #y are the classes
    
    clf = make_pipeline(StandardScaler(),
                        LinearSVC(random_state=0, tol=1e-3)) #I have no idea what parameters to use, just copied from some example  :)
    clf.fit(X, y)
    return(clf)

def GetAccuracy(test_data,model):
    predictor_cols = ['mean_VV','mean_VH','mean_VV/VH_ratio','mean_Population','mean_DEM']
    #Test
    Xtest = test_data[predictor_cols].values.tolist()
    ytest = test_data['Label']
    p = model.predict(Xtest)
    model.score(Xtest,ytest) #81% accuracy

def predict(filepath, model):
    with rio.open(filepath) as src:
        meta=src.meta
        bands=src.read()

    #Reshape to (nrows, ncols, bands)
    bands_reshaped = reshape_as_image(bands)
    
    #Reshaope  to 2d array
    bands_ready_for_classification = bands_reshaped.reshape(int(np.prod(bands_reshaped.shape)/5),5)
    
    r = model.predict(bands_ready_for_classification) #Predict using the model and Sentinel2 bands
    r = r.reshape(bands[0].shape) #Reshape into a 2d array
    
    def str_class_to_int(class_array):
        class_array[class_array == 'Dry'] = 0
        class_array[class_array == 'Flooded'] = 1
        class_array[class_array == 'FloodedUrban'] = 2
        return(class_array.astype(int))
    
    r=str_class_to_int(r)
    #Write the r (result) array to a georeferenced image
    meta.update(dtype=rio.float32,
                count=1,
                compress='lzw')

    with rio.open('./data/Classed_image.tif', 'w', **meta) as dst:
        dst.write_band(1, r.astype(rio.float32))
    return
      
