import pandas as pd
import numpy as np

import sys

from sklearn.manifold import TSNE

datapath = '../../../csv'
L_RATE = 50 # parameter to tune in order to have a better distribution of data points
			# too high value: "ball effect"
			# too low value: too much overlap between points

def manipulateVector(v):
    outVector = []
    listVector = v.split(',')
    
    for string in listVector:
        outVector.append(string.strip())
    
    return np.array(outVector)

brand = sys.argv[1]
data = pd.read_csv('{}/{}/imagevector.tsv'.format(datapath, brand), sep='\t')

N = data.shape[0]

X = []
for index, x in data.iterrows():
    X.append(manipulateVector(x['vector']))

X1 = np.concatenate(X).reshape([N, 1024])
X_embedded = TSNE(n_components=2, learning_rate=L_RATE).fit_transform(X1)
tsne_out = pd.DataFrame(X_embedded)
tsne_out.columns = ['x','y']
tsne_out['id_post'] = data['id_post']
tsne_out = tsne_out[['id_post', 'x', 'y']]

tsne_out.to_csv('{}/{}/postcoord.csv'.format(datapath, brand), index=None)