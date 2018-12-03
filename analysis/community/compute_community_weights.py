import pandas as pd
import snap
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
mongodb = client['FaST']
path = 'network-data/'

# data import
print ('Import clusters...')
clusters = pd.read_csv('complete_analysis/output/final/1_step_tags_clusters.txt', sep='\t')

# extract list of tags for each cluster
clusterTags = {}
for c in range(clusters.shape[0]-1):
    c_tags = clusters[clusters['n_cluster'] == c]['hashtags'].values[0].split(',')
    clusterTags[c] = set(c_tags)


# read input network to extract tags frequency
print ('Load network to compute post-tag distribution...')
t_net = snap.LoadEdgeListNet(path+'hashtag_network.csv', '\t')

usedtags = {}
userposts = {}

it = t_net.BegNI()
V = t_net.GetNodes()
for i in range(V):
    nid = it.GetId()
    type = t_net.GetStrAttrDatN(nid, 'type')

    if type == 'post':
        id_post = t_net.GetStrAttrDatN(nid, 'id')
        
        taglist = []
        nodeIt = t_net.GetNI(nid)
        for t in range(nodeIt.GetOutDeg()):
            tid = nodeIt.GetOutNId(t)
            tagname = t_net.GetStrAttrDatN(tid, 'content')
            taglist.append(tagname)
            
        usedtags[id_post] = set(taglist)
        
    elif type == 'user':
        id_user = int(t_net.GetStrAttrDatN(nid, 'id'))
        username = t_net.GetStrAttrDatN(nid, 'content')
        postlist = []
        nodeIt = t_net.GetNI(nid)
        for t in range(nodeIt.GetOutDeg()):
            pid = nodeIt.GetOutNId(t)
            id_post = t_net.GetStrAttrDatN(pid, 'id')
            postlist.append(id_post)
            
        userposts[id_user] = set(postlist)
    it.Next()

# compute participation of each post in each cluster 
print ('Compute participation for each post in each cluster...')
postPart = {}
for p in usedtags.keys():
    p_vector = usedtags[p]
    
    if len(p_vector)>0:
        postPart[p] = {}
        for c in range(clusters.shape[0]-1):
            c_vector = clusterTags[c]
            participation = float(len(p_vector.intersection(c_vector)))/len(c_vector)
            c = str(c) # needed because in mongodb only string keys can be used
            if participation > 0: # threshold tbd
                postPart[p][c] = participation
        if not postPart[p]:
            del postPart[p]

# update followers post collection with this information
post_followers_db = mongodb["post_followers"]
i = 1
for post in postPart.keys():
    result = post_followers_db.update_one({'id_post': post}, {'$set': {'communities': postPart[post]}}, upsert=False)
    
    perc = float(i)*100/len(postPart)
    print str(perc)+'%'
        
    i = i+1
    
# compute user participation
print ('Compute participation of each user based on post participation...')
userPart = {}
for u in userposts.keys():
    u_posts = userposts[u]
    userPart[u] = {}
    for c in range(clusters.shape[0]-1):
        c = str(c) # needed because of post have string keys
        userPart[u][c] = 0.0
        n_relevant_posts = len(u_posts)
        for p in u_posts:
            try:
                userPart[u][c] = userPart[u][c] + postPart[p][c]
            except KeyError:
                n_relevant_posts -= 1 # post without hashtags
        
        if n_relevant_posts > 0 and userPart[u][c] > 0.0:
            userPart[u][c] = userPart[u][c]/n_relevant_posts
        else:
            del userPart[u][c]
            
    if not userPart[u]:
        del userPart[u]

# update followers user collection with this information
user_db = mongodb["user"]
for user in userPart.keys():
    result = user_db.update_one({'id_user': user}, {'$set': {'communities': userPart[user]}}, upsert=False)
    print 'user: ' + str(user) + ' matched ' + str(result.matched_count) + ' ,updated ' + str(result.modified_count)