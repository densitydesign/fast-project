import pandas as pd

import snap

import sys
import time
import ast

def rebuildContent(graph, subgraph):

    it = subgraph.BegNI()

    for i in range(subgraph.GetNodes()):
        nid = it.GetId()
        nodeid = graph.GetStrAttrDatN(nid, 'id')
        type = graph.GetStrAttrDatN(nid, 'type')
        content = graph.GetStrAttrDatN(nid, 'content')

        subgraph.AddStrAttrDatN(nid, nodeid,'id')
        subgraph.AddStrAttrDatN(nid, content,'content')
        subgraph.AddStrAttrDatN(nid, type,'type')

        it.Next()

    ite = subgraph.BegEI()

    for j in range (subgraph.GetEdges()):
        sourceid = ite.GetSrcNId()
        targetid = ite.GetDstNId()
        eid = graph.GetEI(sourceid, targetid)

        subgraph.AddStrAttrDatE(ite.GetId(), graph.GetStrAttrDatE(eid, 'e_type'), 'e_type')
        ite.Next()
	
def generateTables(targetpath, netfile, net):
	#split file into node and edge file
	net_file = open(targetpath+netfile+'.csv', 'r') 
	nodes_file = open(targetpath+netfile+'_nodes.csv', 'w')
	nodes_file.write('id\tcluster\tid_node\tcontent\ttype\n')
	edges_file = open(targetpath+netfile+'_edges.csv', 'w')
	edges_file.write('source\ttarget\ttype\n')
	
	n_nodes = net.GetNodes()
	n_edges = net.GetEdges()
	
	line_num = 0 
	for line in net_file:
		if line_num>=4 and line_num < (n_nodes+4) : # 4 headers
			nodes_file.write(line)
		elif line_num >= (n_nodes+6) and line_num < (n_nodes+6+n_edges): #skip #END
			edges_file.write(line)
		line_num = line_num + 1

datapath = 'data/'
outpath = 'output/'
# read input network (hashtag filtered)		

t_net = snap.LoadEdgeListNet(datapath+'followers_network.csv', '\t')

# read cluster output file
out_clusters = pd.read_csv(outpath+'1_step_consumers.csv', sep='\t')
clusters_id = out_clusters['n_cluster']

allclustersdict = {}

allClustersNodes = snap.TIntV()
for c in clusters_id:
	print 'Cluster {}'.format(c)
	
	cluster_dim = out_clusters[out_clusters['n_cluster'] == c]['n_users'].values[0]
	userlist = list(ast.literal_eval(out_clusters[out_clusters['n_cluster'] == c]['consumers_list'].values[0]))
	
	if cluster_dim > 1:
		cluster_users = [x[0] for x in userlist]
	else:
		cluster_users = [userlist[0]]
	
	it = t_net.BegNI()
	V = t_net.GetNodes()

	clusterV = snap.TIntV()
	for i in range(V):
		nid = it.GetId()
		type = t_net.GetStrAttrDatN(nid, 'type')
		username = t_net.GetStrAttrDatN(nid, 'content')

		if type == 'user' and username in cluster_users:
			# add user node to subnetwork
			clusterV.Add(nid)

			# add posts to subnetwork
			nodeIt = t_net.GetNI(nid)
			for e in range(nodeIt.GetOutDeg()):
				clusterV.Add(nodeIt.GetOutNId(e))
			# add tags to subnetwork
			tags = snap.TIntV()
			snap.GetNodesAtHop(t_net, nid, 2, tags, True)

			clusterV.AddV(tags)

		it.Next()

	clusterV.Merge() 
	allClustersNodes.AddV(clusterV)
	
	allclustersdict[c] = clusterV

print 'Merge all clusters...'
allClustersNodes.Merge()
allclusters_graph = snap.GetSubGraph(t_net, allClustersNodes)
rebuildContent(t_net, allclusters_graph)

print 'Add cluster attribute...'
allclusters_graph.AddIntAttrN('cluster')
for c in clusters_id:
	for nid in allclustersdict[c]:
		allclusters_graph.AddIntAttrDatN(nid, c, 'cluster')
		
net_name = 'focused_clusters'
snap.SaveEdgeListNet(allclusters_graph, outpath+'{}.csv'.format(net_name), 'All Clusters Hashtag Network - Only Consumers')
generateTables(outpath, net_name, allclusters_graph)
		