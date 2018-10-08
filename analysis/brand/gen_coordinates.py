import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
from pymongo import MongoClient

competitors = ['daftcollectionofficial','loupcharmant','muzungusisters','heidikleinswim','lisamariefernandez',
              'zeusndione','dodobaror','athenaprocopiou','miguelinagambaccini']
target_b = 'emporiosirenuse'
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

def pair_coordinates():
	dict_coord = {}
	for c in competitors:
		data = pd.read_csv('{}/{}/imagevector.tsv'.format(datapath, c), sep='\t', dtype=object)
		meta = pd.read_csv('{}/{}/post.csv'.format(datapath, c), dtype=object)

		input = pd.concat([target_b_data, data], axis=0)
		input['X'] = input['vector'].apply(lambda x: manipulateVector(x))
		input = input.reset_index()
		
		N = input.shape[0]

		X1 = np.concatenate(input['X']).reshape([N, 1024])
		X_embedded = TSNE(n_components=2, learning_rate=L_RATE).fit_transform(X1)
		tsne_out = pd.DataFrame(X_embedded)
		tsne_out.columns = ['x','y']
		tsne_out['id_post'] = input['id_post']
		tsne_out = tsne_out[['id_post', 'x', 'y']]
		
		post = pd.concat([target_b_meta, meta], axis=0)
		
		outdata = post.merge(tsne_out, on='id_post')[['id_post', 'x', 'y', 'url_img']].drop_duplicates(subset='id_post')
		#with open('data/{}_{}.json'.format(target_b, c), 'w') as outfile:
		#	outfile.write(outdata.to_json(orient='index'))
		
		db_data = outdata[['id_post', 'x', 'y']]
		db_data.set_index('id_post', inplace=True)
		
		temp_dict = db_data.to_dict(orient='index')
		for pid in temp_dict.keys():
			val = temp_dict[pid]
			temp_dict[pid] = {c: val}
		
		dict_coord.update(temp_dict)
	return dict_coord
	
def single_coordinates(brand_list):
	dict_coord = {}
	for brand in brand_list:
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
		tsne_out.set_index('id_post', inplace=True)
		
		temp_dict = tsne_out.to_dict(orient='index')
		for pid in temp_dict.keys():
			val = temp_dict[pid]
			temp_dict[pid] = {'base': val}
			
		dict_coord.update(temp_dict)
	return dict_coord
	
target_b_data = pd.read_csv('{}/{}/imagevector.tsv'.format(datapath, target_b), sep='\t', dtype=object)
target_b_meta = pd.read_csv('{}/{}/post.csv'.format(datapath, target_b), dtype=object)

# TSNE coordinates computation
pair_dict = pair_coordinates()
single_dict = single_coordinates(competitors+[target_b])

print len(pair_dict)
print len(single_dict)

# DB updates
client = MongoClient('mongodb://localhost:27017/')
db = client['FaST']
for pid in pair_dict.keys():
	coords = {}
	coords.update(pair_dict[pid])
	coords.update(single_dict[int(pid)])
	#print coords
	
	db.post.update_one({'id_post': pid}, {'$set': {'pair_coord': coords}}, upsert=False)

