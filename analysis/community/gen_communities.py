import pandas as pd
from sklearn.cluster import DBSCAN
import snap
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
mongodb = client['FaST']
path = 'network-data/'

# data import
print ('Import data...')
features = pd.read_csv(path + 'hashtag_network_16.emb', sep=' ',header=None,skiprows=1)
nodes = pd.read_csv(path + 'hashtag_network_nodes.csv', sep='\t')
data = nodes.merge(features, left_on='id', right_on=0)
tags = data[data['type'] == 'tag'].drop(['type',0,'id','content'], axis=1)

# DBSCAN clustering over tags features
print ('Computation of DBSCAN clustering on tags features...')
epsilon = 0.5
minPts = 7
db = DBSCAN(eps = epsilon, min_samples = minPts, n_jobs = -1).fit(tags[range(1,17)])
labels = db.labels_
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
tags['cluster_dbscan'] = labels
core_samples_idx = db.core_sample_indices_ 

print ('Estimated number of clusters: {}'.format(n_clusters))

# read input network to extract tags frequency
print ('Load network to compute tag frequencies...')
t_net = snap.LoadEdgeListNet(path+'hashtag_network.csv', '\t')

tagfreq = {}
it = t_net.BegNI()
V = t_net.GetNodes()
for i in range(V):
    nid = it.GetId()
    type = t_net.GetStrAttrDatN(nid, 'type') 
    if type == 'tag':
        tagname = t_net.GetStrAttrDatN(nid, 'content')
        freq = t_net.GetNI(nid).GetInDeg()
        tagfreq[tagname] = freq
        
    it.Next()
    
tfreq_df = pd.DataFrame.from_dict(tagfreq, orient='index')
tfreq_df.columns = ['freq']

# define community object in a JSON file as a set of core hashtags and non core hashtags
# ordered by overall frequency
print ('Extract tags groups and write in DB...')

communities = []
for n in range(n_clusters):
    curr_comm = {'id': n}
    
    c = tags[tags['cluster_dbscan'] == n]
    
    core_idx = set(c.index).intersection(set(core_samples_idx))
    core_hashtags = c[c.index.isin(core_idx)][['id_node']].merge(tfreq_df,  right_index=True, left_on='id_node')
    non_core_hashtags = c[~c.index.isin(core_idx)][['id_node']].merge(tfreq_df,  right_index=True, left_on='id_node')
    
    core_hashtags = list(core_hashtags.sort_values(by='freq', ascending=False)['id_node'])
    non_core_hashtags = list(non_core_hashtags.sort_values(by='freq', ascending=False)['id_node'])
    
    curr_comm['core_hashtags'] = core_hashtags
    curr_comm['non_core_hashtags'] = non_core_hashtags
    
    communities.append(curr_comm)

# write resulting communities (clusters) in the DB, in a separate collection
# including the ordered list of core and non-core hashtags

# create the collection if does not exist, otherwise do nothing to avoid overwrite data
collections = mongodb.list_collection_names()
if "community" not in collections:
    comm_db = mongodb["community"]
    result = comm_db.insert_many(communities)
    print (result.inserted_ids)
else:
    print ("Collection \"community\" already in MongoDB: verify before inserting!")
