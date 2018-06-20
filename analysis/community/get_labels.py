import pandas as pd

import snap

import sys
import time
import itertools

def rebuildContent(graph, subgraph):

    it = subgraph.BegNI()

    for i in range(subgraph.GetNodes()):
        nid = it.GetId()
        type = graph.GetStrAttrDatN(nid, 'type')
        content = graph.GetStrAttrDatN(nid, 'content')

        if type == 'user' or type == 'tag':
            subgraph.AddStrAttrDatN(nid, content,'content')
        else:
            subgraph.AddStrAttrDatN(nid, ' ','content')

        subgraph.AddStrAttrDatN(nid, type,'type')

        it.Next()

    ite = subgraph.BegEI()

    for j in range (subgraph.GetEdges()):
        sourceid = ite.GetSrcNId()
        targetid = ite.GetDstNId()
        eid = graph.GetEI(sourceid, targetid)

        subgraph.AddStrAttrDatE(ite.GetId(), graph.GetStrAttrDatE(eid, 'e_type'), 'e_type')
        ite.Next()

path = 'data/'		

# read input network (hashtag filtered)		
t_net = snap.LoadEdgeListNet(path+'followers_network.csv', '\t')

# read cluster file
clusters = pd.read_csv('output/clustering_users.csv')
n_clusters = len(clusters['cluster'].unique())

# rebuild network only with cluster users and keep the top 10 hashtags by frequency
with open('output/cluster_users_labels.txt', 'w') as outfile:
    for c in range(n_clusters):
        print 'Cluster {}'.format(c)
        outfile.write(str(c))
        outfile.write('\t')
        
        #Since network complete is used, then the vector of ids is already defined for users
        clusterV = snap.TIntV()
        clusterVusers = snap.TIntV()
        cluster_users = list(clusters[clusters['cluster'] == c]['id'])
        for n in cluster_users:
            clusterVusers.Add(int(n))
        
        outfile.write(str(len(cluster_users)))
        outfile.write('\t')
        
        for v in clusterVusers:
            # add posts to subnetwork
            nodeIt = t_net.GetNI(v)
            for e in range(nodeIt.GetOutDeg()):
                clusterV.Add(nodeIt.GetOutNId(e))
                # add tags to subnetwork
                tags = snap.TIntV()
                snap.GetNodesAtHop(t_net, v, 2, tags, True)
                clusterV.AddV(tags)
    
        clusterV.AddV(clusterVusers)
        clusterV.Merge() 

        cluster_graph = snap.GetSubGraph(t_net, clusterV)
        rebuildContent(t_net, cluster_graph)

        #cluster_tags = result[c]

        it = cluster_graph.BegNI()
        V = cluster_graph.GetNodes()

        tag_deg = []
        for i in range(V):
            nid = it.GetId()
            type = cluster_graph.GetStrAttrDatN(nid, 'type')
            tagname = cluster_graph.GetStrAttrDatN(nid, 'content')

            if type == 'tag':
                indegree = it.GetInDeg()
                tag_deg.append((tagname, indegree))

            it.Next()
    
		# NB: resulting labels are the TOP 10 HASHTAGS
        topTags_df = pd.DataFrame(tag_deg, columns=['tag', 'indegree']).sort_values(by='indegree', ascending=False)
        topTags = list(topTags_df['tag'][:10])
        outfile.write(",".join(topTags))
        outfile.write('\n')