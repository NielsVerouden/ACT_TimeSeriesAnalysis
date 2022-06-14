# Train a machine learning model

from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

#### GaussianNaiveBayes Classifier
def GaussianNaiveBayes(X,y):
    print("Fitting GaussianNaiveBayes Classifier to input data ... ")
    gnb = GaussianNB()
    gnb.fit(X, y)
    return gnb
#credit: http://patrickgray.me/open-geo-tutorial/chapter_5_classification.html
#https://towardsdatascience.com/land-cover-classification-in-satellite-imagery-using-python-ae39dbf2929


#### Random Forest
def RandomForest(X,y, n_estimators=100, criterion="gini",max_depth=None):
    print("Fitting Random Forest to input data ... ")
    rf = RandomForestClassifier(n_estimators=n_estimators,
                                criterion=criterion,        #"gini", "entropy", "log_loss"
                                max_depth=max_depth)        #None or an integer value
    rf.fit(X,y)
    return rf                            
#see the following link for all random forest options:
#https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
    

### K-nearest neighbours
def knn(X,y,n_neighbours=6):
    print("Fitting K-Nearest Neighbours to input data ... Takes a few minutes")
    knn = KNeighborsClassifier(n_neighbors=n_neighbours)
    knn.fit(X, y)
    print("Training finished)")
    return knn
#https://towardsdatascience.com/land-cover-classification-in-satellite-imagery-using-python-ae39dbf2929


### Support vector machine
def svm(X,y,C=3, kernel="rbf", degree=6):
    print("Fitting Support Vector Machine to input data ... Takes a few minutes")
    svm = SVC(C=C, kernel=kernel, degree=degree, cache_size=1024)
    svm.fit(X, y)
    return svm
#https://towardsdatascience.com/land-cover-classification-in-satellite-imagery-using-python-ae39dbf2929