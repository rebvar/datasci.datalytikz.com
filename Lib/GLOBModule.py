from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, ExtraTreeClassifier, ExtraTreeRegressor
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor, BaggingClassifier, BaggingRegressor, GradientBoostingClassifier, RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.gaussian_process import GaussianProcessClassifier, GaussianProcessRegressor
from sklearn.mixture import BayesianGaussianMixture, GaussianMixture
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor, RadiusNeighborsClassifier, RadiusNeighborsRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.svm import SVC, SVR, LinearSVC, LinearSVR

class GLOB(object):

    """
    Plenned: Global Optimization for Learner Hyper-Parameters. 
    Current: Unified training a testing model for prediction models.
    """


    binLrnrNames = {"Naive Bayes":GaussianNB, "Multinomial Naive Bayes":MultinomialNB, "Bernoulli Naive Bayes":BernoulliNB, 
                 "Logistic Regression":LogisticRegression, "Decision Tree": DecisionTreeClassifier, "Extra Tree Classifier":ExtraTreeClassifier,
                 "AdaBoost Classifier":AdaBoostClassifier, "Bagging Classifier" : BaggingClassifier, "Gradient Boosting Classifier":GradientBoostingClassifier,
                 "Random Forest Classifier": RandomForestClassifier, "Gaussian Process Classifier": GaussianProcessClassifier,
                 "K Neighbors Classifier":KNeighborsClassifier, "Radius Neighbors Classifier": RadiusNeighborsClassifier, "Support Vector Classfifier": SVC, "Linear Support Vector Classfifier": LinearSVC, 
                 }

    regLrnrNames = {"Linear Regression":LinearRegression,"Decision Tree Regressor": DecisionTreeRegressor, "Extra Tree Regressor":ExtraTreeRegressor,
                     "AdaBoost Regressor":AdaBoostRegressor, "Bagging Regressor": BaggingRegressor, "Gradient Boosting Regressor": GradientBoostingRegressor,
                     "Random Forest Regressor": RandomForestRegressor, "Gaussian Process Regressor": GaussianProcessRegressor,
                     "K Neighbors Regressor": KNeighborsRegressor, "Radius Neighbors Regressor": RadiusNeighborsRegressor
                     , "Support Vector Regressor": SVR, "Linear Support Vector Regressor": LinearSVR, 
                     }




    def __init__(self, clfName, tunelrn = False):
        self.clfName = clfName
        self.predType = 'Bin'


    def getClassifier(self):
        if self.clfName in GLOB.binLrnrNames.keys():
            self.predType = "Bin"
            clf = GLOB.binLrnrNames[self.clfName]
            self.clf = clf()
        elif self.clfName in GLOB.regLrnrNames.keys():
            self.predType = "Cont"
            clf = GLOB.regLrnrNames[self.clfName]
            self.clf = clf()                            
        
        return self

    def buildClassifier(self, trSet, actual = None):
        if actual == None:
            self.actual = trSet[:,-1]
            self.clf.fit(trSet[:,1:-1], self.actual.astype(int))
        else:
            self.actual = actual
            self.clf.fit(trSet[:,1:], self.actual.astype(int))

    def evaluateModel(self, targetSet):
        if self.predType == 'Bin':
            p = self.clf.predict_proba(targetSet[:,1:-1])
            if len(p[0])<2:
                return p[:,0]            
            return p[:,1]
        else:            
            p = self.clf.predict(targetSet[:,1:-1])
            return p

    def getTunedCLF(self, *args):
        return self

    def getCLFOptions(self, *args):
        return []


    def evalMultiModel(self, vSets, trSet):
        all_predictions = []
        for vSet in vSets:
            all_predictions.append(self.evaluateModel(vSet))
        return all_predictions