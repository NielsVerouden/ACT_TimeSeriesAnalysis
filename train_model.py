# Train a machine learning model

from sklearn.naive_bayes import GaussianNB


#Train a GaussianNaiveBayes Classifier (just for trying)
#In later stages we can add different types of classifications (eg Random Forest)
def GaussianNaiveBayes(X,y):
    gnb = GaussianNB()
    gnb.fit(X, y)
    return gnb
#credit: http://patrickgray.me/open-geo-tutorial/chapter_5_classification.html
#https://towardsdatascience.com/land-cover-classification-in-satellite-imagery-using-python-ae39dbf2929