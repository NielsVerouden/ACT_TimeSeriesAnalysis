# Train a machine learning model
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.utils import class_weight
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit, GridSearchCV
import pandas as pd

# =============================================================================
#Helper function for random forest to create a dict with class weights
def constructDict(arr):
    #Create a dictionary with the class weights
    dict = {"Dry":arr[0],
            "Flooded":arr[1],
            "FloodedUrban":arr[2]}
    return dict
# =============================================================================
# Linear Support Vector Classifier
def Linear_SVC(training_data):
    predictor_cols = ['mean_VV','mean_VH','mean_VV/VH_ratio','mean_Population','mean_DEM']
    X = training_data[predictor_cols].values.tolist()  #X are the stats/predictor data
    y = training_data['Label'].tolist() #The 3 classes
    
    svc = LinearSVC(random_state=0, tol=1e-3)
    svc.fit(X, y)
    return(svc)
# =============================================================================
# GaussianNaiveBayes Classifier
def GaussianNaiveBayes(training_data):
    predictor_cols = ['mean_VV','mean_VH','mean_VV/VH_ratio','mean_Population','mean_DEM']
    X = training_data[predictor_cols].values.tolist()  #X are the stats/predictor data
    y = training_data['Label'].tolist() #The 3 classes
    gnb = GaussianNB()
    gnb.fit(X, y)
    return gnb
# =============================================================================
# Random forest
def RandomForest(training_data, n_estimators=100, criterion="gini",max_depth=None,min_samples_split=4):
    predictor_cols = ['mean_VV','mean_VH','mean_VV/VH_ratio','mean_Population','mean_DEM']
    X = training_data[predictor_cols].values.tolist()  #X are the stats/predictor data
    y = training_data['Label'].tolist() #The 3 classes
    
    parameters= {'class_weight': None,      #Add class weights (dict or 'balanced' or None)
                    'criterion': 'gini',
                    'max_depth': 15,
                    'max_features': 0.5,
                    'min_samples_leaf': 3}
    rf = RandomForestClassifier(**parameters)     
    rf.fit(X,y)
    return rf 
# =============================================================================
# K-nearest neighbours
def knn(training_data,n_neighbours=3):
    predictor_cols = ['mean_VV','mean_VH','mean_VV/VH_ratio','mean_Population','mean_DEM']
    X = training_data[predictor_cols].values.tolist()  #X are the stats/predictor data
    y = training_data['Label'].tolist() #The 3 classes
    knn = KNeighborsClassifier(n_neighbors=n_neighbours)
    knn.fit(X, y)
    print("Training finished")
    return knn
# =============================================================================
# Support vector machine
def svm(training_data,C=3, kernel="poly", degree=4):
    predictor_cols = ['mean_VV','mean_VH','mean_VV/VH_ratio','mean_Population','mean_DEM']
    X = training_data[predictor_cols].values.tolist()  #X are the stats/predictor data
    y = training_data['Label'].tolist() #The 3 classes
    
    svm = SVC(C=C, kernel=kernel, degree=degree, cache_size=1024)
    svm.fit(X, y)
    return svm
# =============================================================================
# Random Forest: Finding optimal parameters using a cross-validation approach
def RandomForest_FindParams(training_data):
    print("Finding the best parameters for Random Forest ... ")
    predictor_cols = ['mean_VV','mean_VH','mean_VV/VH_ratio','mean_Population','mean_DEM']
    X = training_data[predictor_cols].values.tolist()  #X are the stats/predictor data
    y = training_data['Label'].tolist() #The 3 classes
    
    #Class weights to balance for the different amounts of pixels in each class
    class_weights = class_weight.compute_class_weight('balanced',
                                                 classes=np.unique(y),
                                                 y=y)
    #Manuall increase the class weights of the flooded classes since they are more important
    class_weights_mod = class_weights* [1, 5, 5]
    class_weights_extr = class_weights* [1, 10, 10]
    
    class_dict_mod = constructDict(class_weights_mod)
    class_dict_extr = constructDict(class_weights_extr)
    
    param_grid = {'min_samples_leaf':[1,3],'max_features':[0.5,'sqrt','log2'],
              'max_depth':[10,15,20],
              'class_weight':[None, 'balanced', class_dict_mod, class_dict_extr],
              'criterion':['gini']}
    
    sss = StratifiedShuffleSplit(n_splits=5)
    grid = GridSearchCV(RandomForestClassifier(),param_grid,cv=sss,verbose=1,n_jobs=-1,return_train_score=True)
    grid.fit(X,y) 
    
    results_dict = grid.cv_results_
    results=pd.DataFrame.from_dict(results_dict)
    best_params = grid.best_params_
    pd.DataFrame.to_csv(results,"./data/RandomForestCV_Results.csv",mode='w+')
    
    rf=RandomForestClassifier(**best_params)
    best_model=rf.fit(X,y)
    return best_model, results, best_params

#credit: http://patrickgray.me/open-geo-tutorial/chapter_5_classification.html
#https://towardsdatascience.com/land-cover-classification-in-satellite-imagery-using-python-ae39dbf2929
#https://gis.stackexchange.com/questions/373720/performing-supervised-classification-on-sentinel-images
      
#see the following link for all random forest options:
#https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html

  
        