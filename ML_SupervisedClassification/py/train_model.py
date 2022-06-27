# Below you find various functions to train a Machine Learning algorithm to detect floods
# The functions are aranged from least to most complex
# All except GNB perform 5-fold cross-validation and a grid search to find the optimal parameters
# This may take a while, esp. if the amount of training data is very large
import os
import numpy as np
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.utils import class_weight
from sklearn.model_selection import StratifiedShuffleSplit, GridSearchCV
from sklearn.metrics import make_scorer, fbeta_score

if not os.path.exists("./ML_SupervisedClassification/output/GridSearch_Results"): 
    os.makedirs("./ML_SupervisedClassification/output/GridSearch_Results")

# =============================================================================
# Set random seed to ensure reproducability
np.random.seed(123)
# =============================================================================
#Helper function for random forest to create a dict with class weights
def constructDict(arr):
    #Create a dictionary with the class weights
    dict = {"Dry":arr[0],
            "Flooded":arr[1],
            "FloodedUrban":arr[2]}
    return dict
# =============================================================================
# Helper function to obtain x and y from a dataset
def getXY(data):
    predictor_cols = ['mean_VV','mean_VH','mean_VV/VH_index','mean_Population','mean_DEM']
    X = data[predictor_cols].values.tolist()  #X are the stats/predictor data
    y = data['Label'].tolist() #The 3 classes
    return X,y
# =============================================================================
# GaussianNaiveBayes Classifier (No cross validation needed)
def GaussianNaiveBayes(training_data):
    """
    Parameters
    ----------
    training_data: pd.DataFrame: dataframe containing X and y variables
    -------
    Trains a GNB model on the dataset.
    It uses values from 'mean_VV','mean_VH','mean_VV/VH_index','mean_Population' and 'mean_DEM'
    to predict 'Label'
    -------
    """
    X,y = getXY(training_data)
    gnb = GaussianNB()
    gnb.fit(X, y)
    return gnb
# =============================================================================
# K-nearest neighbours (Simple cross validation with different N of neighbors)
def knn(training_data):
    """
    Parameters
    ----------
    training_data: pd.DataFrame: dataframe containing X and y variables
    -------
    Performs 5-fold cross-validation and a grid search with different parameter settings.
    It returns a trained KNN model with the best parameter settings, based on the f2 score of
    the lables "Flooded" and "FloodedUrban"
    It uses values from 'mean_VV','mean_VH','mean_VV/VH_index','mean_Population' and 'mean_DEM'
    to predict 'Label'.
    -------
    """
    
    X,y = getXY(training_data)
    
    #Define grid of parameters
    param_grid = {'n_neighbors': [3,4,5,6,7]}
    
    #Define loss function
    #this loss function computes the mean of precision and recall for the two
    #labels that we are interested in
    f2_score = make_scorer(fbeta_score, beta=2, labels=["Flooded","FloodedUrban"], average= "micro")
    sss = StratifiedShuffleSplit(n_splits=5)
    
    grid = GridSearchCV(KNeighborsClassifier(),param_grid,cv=sss,verbose=1,n_jobs=-1,return_train_score=True, scoring=f2_score)
    grid.fit(X,y) 
    
    results_dict = grid.cv_results_
    results=pd.DataFrame.from_dict(results_dict)
    best_params = grid.best_params_
    pd.DataFrame.to_csv(results,"./ML_SupervisedClassification/output/GridSearch_Results/KNN_GS_Results.csv",mode='w+')
    
    knn=KNeighborsClassifier(**best_params)
    best_model=knn.fit(X,y)

    return best_model, results, best_params
# =============================================================================
# Support vector machine (More complex algorithm, hence more parameters for the crossvalidation)
def svm(training_data):
    """
    Parameters
    ----------
    training_data: pd.DataFrame: dataframe containing X and y variables
    -------
    Performs 5-fold cross-validation and a grid search with different parameter settings.
    It returns a trained svm model with the best parameter settings, based on the f2 score of
    the lables "Flooded" and "FloodedUrban"
    It uses values from 'mean_VV','mean_VH','mean_VV/VH_index','mean_Population' and 'mean_DEM'
    to predict 'Label'.
    -------
    """
    
    X,y = getXY(training_data)
    
    #Define grid of parameters
    param_grid = {'C':[1,1.5,2],
                  'kernel':['linear', 'poly', 'rbf'],
                  'degree':[2,3,4]}
    
    #Define loss function
    #this loss function computes the mean of precision and recall for the two
    #labels that we are interested in
    f2_score = make_scorer(fbeta_score, beta=2, labels=["Flooded","FloodedUrban"], average= "micro")
    sss = StratifiedShuffleSplit(n_splits=5)
    
    grid = GridSearchCV(SVC(),param_grid,cv=sss,verbose=1,n_jobs=-1,return_train_score=True, scoring=f2_score)
    grid.fit(X,y) 
    
    results_dict = grid.cv_results_
    results=pd.DataFrame.from_dict(results_dict)
    best_params = grid.best_params_
    pd.DataFrame.to_csv(results,"./ML_SupervisedClassification/output/GridSearch_Results/SVM_GS_Results.csv",mode='w+')
    
    svm=SVC(**best_params)
    best_model=svm.fit(X,y)
    return best_model, results, best_params
# =============================================================================
# Random Forest: Finding optimal parameters using a cross-validation approach
def RandomForest(training_data):
    """
    Parameters
    ----------
    training_data: pd.DataFrame: dataframe containing X and y variables
    -------
    Performs 5-fold cross-validation and a grid search with different parameter settings.
    It returns a trained Random Forest model with the best parameter settings, based on the f2 score of
    the lables "Flooded" and "FloodedUrban"
    It uses values from 'mean_VV','mean_VH','mean_VV/VH_index','mean_Population' and 'mean_DEM'
    to predict 'Label'.
    -------
    """
    X,y = getXY(training_data)
    
    #Class weights to balance for the different amounts of pixels in each class
    class_weights = class_weight.compute_class_weight('balanced',
                                                 classes=np.unique(y),
                                                 y=y)
    #Manuall increase the class weights of the flooded classes since they are more important
    class_weights_mod = class_weights* [1, 5, 5]
    class_weights_extr = class_weights* [1, 10, 10]
    
    class_dict_mod = constructDict(class_weights_mod)
    class_dict_extr = constructDict(class_weights_extr)
    
    #Define grid of parameters
    param_grid = {'min_samples_leaf':[1,3],'max_features':[0.5,'sqrt','log2'],
              'max_depth':[10,15,20],
              'class_weight':[None, 'balanced', class_dict_mod, class_dict_extr],
              'criterion':['gini']}
    
    #Define loss function
    #this loss function computes the mean of precision and recall for the two
    #labels that we are interested in
    f2_score = make_scorer(fbeta_score, beta=2, labels=["Flooded","FloodedUrban"], average= "micro")
    
    sss = StratifiedShuffleSplit(n_splits=5)
    grid = GridSearchCV(RandomForestClassifier(),param_grid,cv=sss,verbose=1,n_jobs=-1,return_train_score=True, scoring=f2_score)
    grid.fit(X,y) 
    
    results_dict = grid.cv_results_
    results=pd.DataFrame.from_dict(results_dict)
    best_params = grid.best_params_
    pd.DataFrame.to_csv(results,"./ML_SupervisedClassification/output/GridSearch_Results/RandomForestGS_Results.csv",mode='w+')
    
    rf=RandomForestClassifier(**best_params)
    best_model=rf.fit(X,y)
    return best_model, results, best_params

#credit: http://patrickgray.me/open-geo-tutorial/chapter_5_classification.html
#https://towardsdatascience.com/land-cover-classification-in-satellite-imagery-using-python-ae39dbf2929
#https://gis.stackexchange.com/questions/373720/performing-supervised-classification-on-sentinel-images
      
#see the following link for all random forest options:
#https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html

  
        