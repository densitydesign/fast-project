import pandas as pd
import numpy as np
from sklearn.manifold import TSNE

from settings import datapath, brands
from brand.parsers import get_data, add_logging_arguments, add_data_arguments, parse_arguments_with, setup_logger

def manipulateVector(v):
	outVector = []
	listVector = v.split(',')
    
	for string in listVector:
		outVector.append(string.strip())
    
	return np.array(outVector)

def perform_tsne(input, learning_rate):
	N = input.shape[0]

	X1 = np.concatenate(input['X']).reshape([N, 1024])

	X_embedded = TSNE(n_components=2, learning_rate=learning_rate).fit_transform(X1)

	tsne_out = pd.DataFrame(X_embedded)
	tsne_out.columns = ['x', 'y']
	tsne_out['id_post'] = input['id_post']
	return tsne_out[['id_post', 'x', 'y']].set_index("id_post")


def pair_coordinates(target_b_data, competitors, learning_rate):
	dict_coord = {}

	for c in competitors:
		data = pd.read_csv('{}/{}/imagevector.tsv'.format(datapath, c), sep='\t', dtype=object)

		input = pd.concat([target_b_data, data], axis=0)
		input['X'] = input['vector'].apply(lambda x: manipulateVector(x))
		input = input.reset_index()

		db_data = perform_tsne(input, learning_rate).loc[target_b_data["id_post"].values]

		dict_coord[c] = {pid: row.to_dict() for pid, row in db_data.iterrows()}

	return pd.DataFrame(dict_coord).T.to_dict()
	
def single_coordinates(data, learning_rate):

	input = data.copy(deep=True)
	input['X'] = input['vector'].apply(lambda x: manipulateVector(x))
	input = input.reset_index()

	return {pid: {"base": row.to_dict()} for pid, row in perform_tsne(input, learning_rate).iterrows()}


def generate_tuples(brands):
	for brand in brands:
		yield (brand, set(brands).difference([brand]) )


def custom_parser(parser):
	parser.add_argument('--learning-rate',
                        default=50,
                        help="""
                        parameter to tune in order to have a better distribution of data points; 
                        too high value: "ball effect"
                        too low value: too much overlap between pointsWhich collection to enrich
                        """)
	return parser

if __name__ == "__main__":
	args = parse_arguments_with([add_data_arguments, add_logging_arguments, custom_parser])

	logger = setup_logger(args)

	data = get_data(args)

	collection = data["posts"]

	L_RATE = args.learning_rate

	for target_b, competitors in generate_tuples(brands):

		print("Execution for brand: %s" % target_b)

		target_b_data = pd.read_csv('{}/{}/imagevector.tsv'.format(datapath, target_b), sep='\t', dtype=object)

		# TSNE coordinates computation
		print("Single coordinates computing...")
		single_dict = single_coordinates(target_b_data, learning_rate=L_RATE)

		print("Pair coordinates computing...")
		pair_dict = pair_coordinates(target_b_data=target_b_data, competitors=competitors, learning_rate=L_RATE)

		print("DB updates of %d documents" % len(pair_dict))
		# DB updates
		for pid in pair_dict.keys():
			coords = {}
			coords.update(pair_dict[pid])
			coords.update(single_dict[pid])
			#print coords

			collection.update_one({'id_post': pid},
								  {'$unset': {'postcoord': ""},
								   '$set': {'pair_coord': coords}},
								  upsert=False)

