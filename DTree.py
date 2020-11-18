import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.model_selection import train_test_split 
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn import preprocessing
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import plot_confusion_matrix

data = pd.read_csv('Revised Dataset 425.csv')

del data['post id']

Y = data['sub']
del data['sub']

#total karma is not a good indicator since we pulled only top posts and gatekeeping is more popular (so it has more high karma posts in the dataset)
del data['TotalKarma']

X = data

#randomly split our data into 33% test and 66% train
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=321)

scores = ['precision', 'recall', 'f1']

tree_params = {
    'criterion' : ['entropy', 'gini'],
    'max_depth' : list(range(2, 15)),
    }

#find best tree for each metric
for score in scores:

    #find best tree for our given metric, uses 10 fold cross validation
    print("Metrics for best classifier for %s scoring" % score)    
    clf = GridSearchCV(DecisionTreeClassifier(), tree_params, scoring = '%s_macro' % score, n_jobs = -2, cv = 10)
    clf.fit(x_train, y_train)

    #print individual scores for each tree
    print("Grid scores on development set:")
    print()
    means = clf.cv_results_['mean_test_score']
    stds = clf.cv_results_['std_test_score']
    for mean, std, params in zip(means, stds, clf.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r"
              % (mean, std * 2, params))

    #print best parameters for scoring and tree 
    print()
    print("Best Tree: ", clf.best_params_)
    print()
    
    #print metrics and graphs for best tree
    y_true, y_pred = y_test, clf.predict(x_test)
    fig = plot_confusion_matrix(clf.best_estimator_, x_test, y_test, display_labels = ('gatekeeping', 'gatesopencomeonin'), cmap = plt.cm.Blues)
    plt.title("Confusion Matrix for %s scoring" % score)
    plt.savefig("%s_CM.png" % score)
    
    print(classification_report(y_true, y_pred))

    fig = plt.figure(figsize=(25,20))
    _ = tree.plot_tree(clf.best_estimator_, 
                   feature_names=X.columns,  
                   class_names= ('gatekeeping', 'gatesopencomeonein'),
                   filled=True)
    
    fig.savefig("%s_tree.png" % score, dpi = 200)
