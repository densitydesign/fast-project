import numpy as np
import pandas as pd
import snap

import sys
import itertools
import time

def getLen2Paths(net, sourceid, targetid):
	nodeIt = net.GetNI(sourceid)
	
	NbrV = snap.TIntV()
	NbrV.Reserve(nodeIt.GetOutDeg())
	
	for e in range(nodeIt.GetOutDeg()):
		MidNI = net.GetNI(nodeIt.GetOutNId(e))
		if MidNI.IsOutNId(targetid):
			NbrV.Add(MidNI.GetId())

	return NbrV.Len()
			
def generateTables(targetpath, netfile, net):
	#split file into node and edge file
	net_file = open(netfile, 'r') 
	nodes_file = open(targetpath+'reduced_nodes.csv', 'w')
	nodes_file.write('id\tcontent\n')
	edges_file = open(targetpath+'reduced_edges.csv', 'w')
	edges_file.write('source\ttarget\tweight\n')
	
	n_nodes = net.GetNodes()
	n_edges = net.GetEdges()
	
	line_num = 0 
	for line in net_file:
		if line_num>=4 and line_num < (n_nodes+4) : # 4 headers
			nodes_file.write(line)
		elif line_num >= (n_nodes+6) and line_num < (n_nodes+6+n_edges): #skip #END
			edges_file.write(line)
		line_num = line_num + 1

temppath = 'temp/'
path = 'data/'
	
t_net = snap.LoadEdgeListNet(path+'followers_network.csv', '\t')

start = time.time()

it = t_net.BegNI()
V = t_net.GetNodes()

tagsPerPost = {}	
with open(temppath+'reduced_nodes.csv', 'w') as nodefile:
	nodefile.write('id\n')	
	for i in range(V):
		nid = it.GetId()
		type = t_net.GetStrAttrDatN(nid, 'type')
		id_post = t_net.GetStrAttrDatN(nid, 'id')
		timestamp = t_net.GetStrAttrDatN(nid, 'content')
		
		if type == 'post':
			nodefile.write('{}\n'.format(id_post))
			
			tags = snap.TIntV()
			snap.GetNodesAtHop(t_net, nid, 1, tags, True)
			
			tags.Merge()
			tagsPerPost[id_post] = tags
		it.Next()

t_net.Clr()
		
with open(temppath+'reduced_edges.csv', 'w') as edgefile:
	edgefile.write('source,target,weight\n')
	
	for posttuple in list(itertools.combinations(tagsPerPost.keys(), 2)):
		p0 = posttuple[0]
		p1 = posttuple[1]
		
		tags0 = tagsPerPost[p0]
		tags1 = tagsPerPost[p1]
	
		commonT = snap.TIntV()
		tags0.Intrs(tags1, commonT)
		Ntags = commonT.Len()

		if Ntags > 0:
			edgefile.write('{},{},{}\n'.format(p0,p1,Ntags))

#upload these saved tables using TTable object
context = snap.TTableContext()

#define schema using columns of the files
e_schema = snap.Schema()
e_schema.Add(snap.TStrTAttrPr("source", snap.atStr))
e_schema.Add(snap.TStrTAttrPr("target", snap.atStr)) 
e_schema.Add(snap.TStrTAttrPr("weight", snap.atInt))

n_schema = snap.Schema()
n_schema.Add(snap.TStrTAttrPr("id", snap.atStr))

#define TTable objects of edges and nodes
edgetable = snap.TTable.LoadSS(e_schema, temppath+'reduced_edges.csv', context, ",", snap.TBool(True))
nodetable = snap.TTable.LoadSS(n_schema, temppath+'reduced_nodes.csv', context, ",", snap.TBool(True))

#define (if any) attribute names using SNAP string vectors
edgeattrv = snap.TStrV()
edgeattrv.Add("weight")

nodeattrv = snap.TStrV()
nodeattrv.Add("id")


#build SNAP network using the two TTable objects
net = snap.ToNetwork(snap.PNEANet, edgetable, "source", "target", edgeattrv, nodetable, "id", nodeattrv, snap.aaFirst)

snap.SaveEdgeListNet(net, 'post_reduced_network.csv', 'Reduced Post Network - Emporio Le Sirenuse')

#input for visualization
generateTables('./', 'post_reduced_network.csv', net)

print 'Time needed: {} s'.format(time.time() - start)