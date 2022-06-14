# Train a machine learning model

from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier


#Train a GaussianNaiveBayes Classifier (just for trying)
#In later stages we can add different types of classifications (eg Random Forest)
def GaussianNaiveBayes(X,y):
    gnb = GaussianNB()
    gnb.fit(X, y)
    return gnb
#credit: http://patrickgray.me/open-geo-tutorial/chapter_5_classification.html
#https://towardsdatascience.com/land-cover-classification-in-satellite-imagery-using-python-ae39dbf2929

def RandomForest(X,y, n_estimators=100, criterion="gini",max_depth=None):
    rf = RandomForestClassifier(n_estimators=n_estimators,
                                criterion=criterion,        #"gini", "entropy", "log_loss"
                                max_depth=max_depth)        #None or an integer value
    rf.fit(X,y)
    return rf                            
#see the following link for all random forest options:
#https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
    