import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Set pandas setting to print more columns
pd.set_option('display.max_columns', 500)

# Read in data
df = pd.read_csv('data/gatekeeping_data.csv')

# Remove unwanted features
#   TotalKarma - was too biased towards one sub-reddit; replaced with an average karma value
#   post id - is just an id to look up posts in future; not relevant
#   sub - target value
to_remove = ['TotalKarma', 'post id', 'sub']
features = df.columns.values[np.logical_not(np.in1d(df.columns.values, to_remove))]

# Split inputs and outputs
x = df[features]
y = df['sub']

# Standardize data for PCA
x_standardize = StandardScaler().fit_transform(x)

# Run complete PCA
pca = PCA()
pca.fit(x_standardize)

variance_data = {
    'Variance': pca.explained_variance_,
    'Variance Ratio': pca.explained_variance_ratio_,
    'VR Cumulative Sum': np.cumsum(pca.explained_variance_ratio_)
}

varianceDf = pd.DataFrame(data=variance_data,
                          index=['PC {}'.format(i) for i in range(len(features))]).transpose()

print('\nHow much variance is explained?\n')
print(varianceDf)
print('\n')
print('Which features matter most?\n')
componentsDf = pd.DataFrame(data=abs(pca.components_),
                            columns=features,
                            index=['PC {}'.format(i) for i in range(len(features))]).transpose()
print(componentsDf)
print()

completeDf = pd.concat([componentsDf, varianceDf], axis=0)
completeDf.to_csv('results/pca_data.csv')
