# general imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# sklearn imports
import sklearn.svm as svm
import sklearn.metrics as met
import sklearn.model_selection as ms
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Set pandas setting to print more columns
pd.set_option('display.max_columns', 500)

# Read in data
df = pd.read_csv('data/gatekeeping_data.csv')
features = np.delete(df.columns.values, [-1, -2])

# Split inputs and outputs
x = df[features]
y = df['sub']

#########
#  PCA  #
#########

# # Standardize data for PCA
# x_standardize = StandardScaler().fit_transform(x)
#
# # Run PCA to see how many features are required to explain 95% of variance
# pca = PCA(0.95)
# principal_components = pca.fit_transform(x_standardize)
# principalDf = pd.DataFrame(data=principal_components,
#                            columns=['PC {}'.format(i) for i in range(principal_components.shape[1])])
#
# finalDf = pd.concat([principalDf, df['sub']], axis=1)
#
# print('How much variance is explained?\n')
# print(pca.explained_variance_ratio_)
# print('\n')
# print('Which features matter most?\n')
# components = pd.DataFrame(data=abs(pca.components_), columns=features)
# print(components)

#########
#  SVC  #
#########

# Split training/validation/testing data
x_train, x_test, y_train, y_test = ms.train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
x_valid, x_test, y_valid, y_test = ms.train_test_split(x_test, y_test, test_size=0.5, random_state=42, stratify=y_test)

# --- Course Search --- #

# Define search parameters
C_coarse = np.logspace(-5, 15, 11, base=2)
degree_coarse = np.linspace(2, 12, 11, endpoint=False, dtype='int')
gamma_coarse = np.logspace(-15, 5, 11, base=2)
param_grid = [
    {
        'svc__kernel': ['linear'],
        'svc__C': C_coarse
    },
    {
        'svc__kernel': ['poly'],
        'svc__degree': degree_coarse,
        'svc__C': C_coarse
    },
    {
        'svc__kernel': ['rbf'],
        'svc__gamma': gamma_coarse,
        'svc__C': C_coarse
    }
]

# Define scorers
scores = ['precision_macro', 'recall_macro', 'f1_macro']

# Initialize standardization/SVC pipeline
pipe = Pipeline([('scalar', StandardScaler()), ('svc', svm.SVC())])

# Run grid search
clf = ms.GridSearchCV(pipe, param_grid, cv=10, n_jobs=-2, scoring=scores, refit='f1_macro', verbose=2)
clf.fit(x_train, y_train)

# Separate data based on kernel used and score type
params = np.array(clf.cv_results_['params'])
kernels = np.array(clf.cv_results_['param_svc__kernel'])

data_course = {
    'Linear': {
        'precision': {
            'mean': clf.cv_results_['mean_test_precision_macro'][kernels == 'linear'],
            'std': clf.cv_results_['std_test_precision_macro'][kernels == 'linear']
        },
        'recall': {
            'mean': clf.cv_results_['mean_test_recall_macro'][kernels == 'linear'],
            'std': clf.cv_results_['std_test_recall_macro'][kernels == 'linear']
        },
        'f1': {
            'mean': clf.cv_results_['mean_test_f1_macro'][kernels == 'linear'],
            'std': clf.cv_results_['std_test_f1_macro'][kernels == 'linear']
        },
        'params': params[kernels == 'linear']
    },
    'Polynomial': {
        'precision': {
            'mean': clf.cv_results_['mean_test_precision_macro'][kernels == 'poly'],
            'std': clf.cv_results_['std_test_precision_macro'][kernels == 'poly']
        },
        'recall': {
            'mean': clf.cv_results_['mean_test_recall_macro'][kernels == 'poly'],
            'std': clf.cv_results_['std_test_recall_macro'][kernels == 'poly']
        },
        'f1': {
            'mean': clf.cv_results_['mean_test_f1_macro'][kernels == 'poly'],
            'std': clf.cv_results_['std_test_f1_macro'][kernels == 'poly']
        },
        'params': params[kernels == 'poly']
    },
    'RBF': {
        'precision': {
            'mean': clf.cv_results_['mean_test_precision_macro'][kernels == 'rbf'],
            'std': clf.cv_results_['std_test_precision_macro'][kernels == 'rbf']
        },
        'recall': {
            'mean': clf.cv_results_['mean_test_recall_macro'][kernels == 'rbf'],
            'std': clf.cv_results_['std_test_recall_macro'][kernels == 'rbf']
        },
        'f1': {
            'mean': clf.cv_results_['mean_test_f1_macro'][kernels == 'rbf'],
            'std': clf.cv_results_['std_test_f1_macro'][kernels == 'rbf']
        },
        'params': params[kernels == 'rbf']
    }
}

print('\nBest parameter set found:\n\n{}'.format(clf.best_params_))
print('Score: {}\n'.format(clf.best_score_))

print('Detailed classification report:\n')
print('The model is trained on the partial training set.')
print('The scores are computed on the validation set.\n')
y_predict = clf.predict(x_valid)
print(met.classification_report(y_valid, y_predict))
print('Confusion matrix:\n')
labels = ['gatekeeping', 'gatesopencomeonin']
conf_mat = met.confusion_matrix(y_valid, y_predict, labels=labels)
conf_mat = pd.DataFrame(conf_mat, columns=['GK Predict', 'GOCOI Predict'], index=['GK True', 'GOCOI True'])
print(conf_mat)

# --- Fine Search --- #

# Define search parameters
C_fine = np.logspace(0, 8, 33, base=2)
gamma_fine = np.logspace(-10, -3, 29, base=2)
param_grid = {
    'svc__kernel': ['rbf'],
    'svc__gamma': gamma_fine,
    'svc__C': C_fine
}

# Define scorers
scores = ['precision_macro', 'recall_macro', 'f1_macro']

# Initialize standardization/SVC pipeline
pipe = Pipeline([('scalar', StandardScaler()), ('svc', svm.SVC())])

# Run grid search
clf = ms.GridSearchCV(pipe, param_grid, cv=10, n_jobs=-2, scoring=scores, refit='f1_macro', verbose=1)
clf.fit(x_train, y_train)

# Separate data based on kernel used and score type
params = np.array(clf.cv_results_['params'])
data_fine = {
    'precision': {
        'mean': clf.cv_results_['mean_test_precision_macro'],
        'std': clf.cv_results_['std_test_precision_macro']
    },
    'recall': {
        'mean': clf.cv_results_['mean_test_recall_macro'],
        'std': clf.cv_results_['std_test_recall_macro']
    },
    'f1': {
        'mean': clf.cv_results_['mean_test_f1_macro'],
        'std': clf.cv_results_['std_test_f1_macro']
    },
    'params': params
}

print('\nBest parameter set found:\n\n{}'.format(clf.best_params_))
print('Score: {}\n'.format(clf.best_score_))

print('Detailed classification report:\n')
print('The model is trained on the partial training set.')
print('The scores are computed on the validation set.\n')
y_predict = clf.predict(x_valid)
print(met.classification_report(y_valid, y_predict, digits=4))
print('Confusion matrix:\n')
labels = ['gatekeeping', 'gatesopencomeonin']
conf_mat = met.confusion_matrix(y_valid, y_predict, labels=labels)
conf_mat = pd.DataFrame(conf_mat, columns=['GK Predict', 'GOCON Predict'], index=['GK True', 'GOCON True'])
print(conf_mat)

##############
#  Plotting  #
##############

# --- Linear Coarse Plots --- #

fig_1, axes_1 = plt.subplots(1, 3, figsize=(15, 5))
for ax, (key, val) in zip(axes_1, data_course['Linear'].items()):
    ax.plot(C_coarse, val['mean'])
    ax.set_xlabel('C value')
    ax.set_ylabel(key.capitalize())
    ax.set_xscale('log')

fig_1.suptitle('Linear Kernel Scores versus C')
plt.tight_layout()

# --- Polynomial Coarse Contours --- #

X, Y = np.meshgrid(C_coarse, degree_coarse)

fig_2, axes_2 = plt.subplots(1, 3, figsize=(15, 5))
for ax, (key, val) in zip(axes_2, data_course['Polynomial'].items()):
    Z = val['mean'].reshape(len(degree_coarse), len(C_coarse))
    cont = ax.contourf(X, Y, Z, cmap='Blues', levels=10)
    fig_2.colorbar(cont, ax=ax)
    ax.set_title(key.capitalize())
    ax.set_xlabel('C Value')
    ax.set_ylabel('Degree')
    ax.set_xscale('log')

fig_2.suptitle('Polynomial Kernel Scores versus Degree and C')
plt.tight_layout()

# --- RBF Course Contours --- #

X, Y = np.meshgrid(C_coarse, gamma_coarse)

fig_3, axes_3 = plt.subplots(1, 3, figsize=(15, 5))
for ax, (key, val) in zip(axes_3, data_course['RBF'].items()):
    Z = val['mean'].reshape(len(gamma_coarse), len(C_coarse))
    cont = ax.contourf(X, Y, Z, cmap='Blues', levels=20)
    fig_3.colorbar(cont, ax=ax)
    ax.set_title(key.capitalize())
    ax.set_xlabel('C Value')
    ax.set_ylabel('Gamma Value')
    ax.set_xscale('log')
    ax.set_yscale('log')

fig_3.suptitle('RBF Kernel Scores versus Gamma and C')
plt.tight_layout()

# --- RBF Fine Contours --- #

X, Y = np.meshgrid(C_fine, gamma_fine)

fig_4, axes_4 = plt.subplots(1, 3, figsize=(15, 5))
for ax, (key, val) in zip(axes_4, data_fine.items()):
    Z = val['mean'].reshape(len(gamma_fine), len(C_fine))
    cont = ax.contourf(X, Y, Z, cmap='Blues')
    ax.scatter(clf.best_params_['svc__C'], clf.best_params_['svc__gamma'], c='r', edgecolors='black')
    fig_4.colorbar(cont, ax=ax)
    ax.set_title(key.capitalize())
    ax.set_xlabel('C Value')
    ax.set_ylabel('Gamma Value')
    ax.set_xscale('log')
    ax.set_yscale('log')

fig_4.suptitle('RBF Kernel Scores versus Gamma and C')
plt.tight_layout()

plt.show()

################
#  Final Test  #
################

# Combine training and validation sets into a complete training set
x_train = pd.concat([x_train, x_valid], axis=0)
y_train = pd.concat([y_train, y_valid], axis=0)

# Create standardize/SVC pipeline with hyper-parameters chosen through grid search
svc = svm.SVC(C=clf.best_params_['svc__C'], kernel='rbf', gamma=clf.best_params_['svc__gamma'])
pipe = Pipeline([('scalar', StandardScaler()), ('svc', svc)])

# Train svc on full training set
pipe.fit(x_train, y_train)

# Make predictions and get classification report and confusion matrix
y_predict = pipe.predict(x_test)

print('\n==========================================================\n')
print('Final Model Results\n')
print('The model is trained on the full development set.')
print('The scores are computed on the test set.\n')
print(met.classification_report(y_test, y_predict, digits=4))
print('Confusion matrix:\n')
labels = ['gatekeeping', 'gatesopencomeonin']
conf_mat = met.confusion_matrix(y_test, y_predict, labels=labels)
conf_mat = pd.DataFrame(conf_mat, columns=['GK Predict', 'GOCOI Predict'], index=['GK True', 'GOCOI True'])
print(conf_mat)

# Save final report and confusion matrix to csv's
report = met.classification_report(y_test, y_predict, output_dict=True)
reportDf = pd.DataFrame(report).transpose()
reportDf.to_csv('results/final_svc_classification_report.csv')
conf_mat.to_csv('results/final_svc_confusion_matrix.csv')
