import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
from pymongo import MongoClient

from analysis import datapath, brands

L_RATE = 50 # parameter to tune in order to have a better distribution of data points
			# too high value: "ball effect"
			# too low value: too much overlap between points

def manipulateVector(v):
	outVector = []
	listVector = v.split(',')
    
	for string in listVector:
		outVector.append(string.strip())
    
	return np.array(outVector)

def perform_tsne(input):
	N = input.shape[0]

	X1 = np.concatenate(input['X']).reshape([N, 1024])

	X_embedded = TSNE(n_components=2, learning_rate=L_RATE).fit_transform(X1)

	tsne_out = pd.DataFrame(X_embedded)
	tsne_out.columns = ['x', 'y']
	tsne_out['id_post'] = input['id_post']
	return tsne_out[['id_post', 'x', 'y']].set_index("id_post")


def pair_coordinates(target_b_data, competitors):
	dict_coord = {}

	for c in competitors:
		data = pd.read_csv('{}/{}/imagevector.tsv'.format(datapath, c), sep='\t', dtype=object)

		input = pd.concat([target_b_data, data], axis=0)
		input['X'] = input['vector'].apply(lambda x: manipulateVector(x))
		input = input.reset_index()

		db_data = perform_tsne(input).loc[target_b_data["id_post"].values]

		dict_coord[c] = {pid: row.to_dict() for pid, row in db_data.iterrows()}

	return pd.DataFrame(dict_coord).T.to_dict()
	
def single_coordinates(data):

	input = data.copy(deep=True)
	input['X'] = input['vector'].apply(lambda x: manipulateVector(x))
	input = input.reset_index()

	return {pid: {"base": row.to_dict()} for pid, row in perform_tsne(input).iterrows()}


def generate_tuples(brands):
	for brand in brands:
		yield (brand, set(brands).difference([brand]) )


client = MongoClient('mongodb://localhost:27017/')
db = client['FaST']

for target_b, competitors in generate_tuples(brands):

	print("Execution for brand: %s" % target_b)

	target_b_data = pd.read_csv('{}/{}/imagevector.tsv'.format(datapath, target_b), sep='\t', dtype=object)

	# TSNE coordinates computation
	print("Single coordinates computing...")
	single_dict = single_coordinates(target_b_data)

	print("Pair coordinates computing...")
	pair_dict = pair_coordinates(target_b_data=target_b_data, competitors=competitors)

	print("DB updates of %d documents" % len(pair_dict))
	# DB updates
	for pid in pair_dict.keys():
		coords = {}
		coords.update(pair_dict[pid])
		coords.update(single_dict[pid])
		#print coords

		db.post.update_one({'id_post': pid},
						   {'$unset': {'postcoord': ""},
							'$set': {'pair_coord': coords}},
						   upsert=False)

