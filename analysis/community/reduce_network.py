import snap
import time

def getLen2Paths(net, sourceid, targetid):
	nodeIt = net.GetNI(sourceid)
	
	NbrV = snap.TIntV()
	NbrV.Reserve(nodeIt.GetOutDeg())
	
	for e in range(nodeIt.GetDeg()):
		MidNI = net.GetNI(nodeIt.GetOutNId(e))
		if MidNI.IsNbrNId(targetid): # modify to consider the graph undirected --> neighbour node instead of out node
			NbrV.Add(MidNI.GetId())

	return NbrV.Len()
			
def generateTables(targetpath, netfile, net):
	#split file into node and edge file
	net_file = open(netfile, 'r') 
	nodes_file = open(targetpath+'reduced_nodes.csv', 'w')
	nodes_file.write('id\tid_post\n')
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
		
#print graph info ##		
def graphInfo(net):
	print '|V| = {}'.format(net.GetNodes())
	print '|E| = {}'.format(net.GetEdges())

	DegToCntV = snap.TIntPrV()
	snap.GetDegCnt(net, DegToCntV)
	overallDeg = 0
	for item in DegToCntV:
		overallDeg = overallDeg + item.GetVal2()*item.GetVal1()

	print 'Average degree: {:.1f}'.format(float(overallDeg)/net.GetNodes())
	print 'Graph connected: {}'.format(snap.IsConnected(net))

temppath = 'temp/'
path = 'data/'

tempnodefile = temppath+'nodes.csv'
tempedgefile = temppath+'edges.csv'

t_net = snap.LoadEdgeListNet(path+'test_network.csv', '\t')

start = time.time()

# remove user nodes to avoid that path between posts
it = t_net.BegNI()
for i in range(t_net.GetNodes()):
	nid = it.GetId()
	type = t_net.GetStrAttrDatN(nid, 'type')
	
	if type == 'user':
		t_net.DelNode(nid)
	it.Next()

with open(tempnodefile, 'w') as nodefile:
	with open(tempedgefile, 'w') as edgefile:
		nodefile.write('id\n')
		edgefile.write('source,target,weight\n')
		
		it = t_net.BegNI()
		V = t_net.GetNodes()
		perc = 0
		prev_perc = -1
		for i in range(V):
			sourcenid = it.GetId()
			type = t_net.GetStrAttrDatN(sourcenid, 'type')
			sourcestringid = t_net.GetStrAttrDatN(sourcenid, 'id')
			
			if type == 'post':
				nodefile.write('{}\n'.format(sourcestringid))
				posts = snap.TIntV()
				snap.GetNodesAtHop(t_net, sourcenid, 2, posts, False)

				for targetnid in posts:
					stringid = t_net.GetStrAttrDatN(targetnid, 'id')
					count = getLen2Paths(t_net, sourcenid, targetnid)
					edgefile.write('{},{},{}\n'.format(sourcestringid, stringid, count))
					
				#remove post to avoid repetition of same paths
				t_net.DelNode(sourcenid)
			it.Next()
			perc = perc + 1
			curr_perc = float(perc)*100/V
			if curr_perc >= prev_perc+1:
				print 'Completion: {:.1f}%...'.format(curr_perc)
				prev_perc = curr_perc

print 'Graph building...'

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
edgetable = snap.TTable.LoadSS(e_schema, tempedgefile, context, ",", snap.TBool(True))
nodetable = snap.TTable.LoadSS(n_schema, tempnodefile, context, ",", snap.TBool(True))

#define (if any) attribute names using SNAP string vectors
edgeattrv = snap.TStrV()
edgeattrv.Add("weight")

nodeattrv = snap.TStrV()
nodeattrv.Add("id")

#build SNAP network using the two TTable objects
net = snap.ToNetwork(snap.PNEANet, edgetable, "source", "target", edgeattrv, nodetable, "id", nodeattrv, snap.aaFirst)
graphInfo(net)

snap.SaveEdgeListNet(net, 'post_reduced_network.csv', 'Reduced Post Network - Emporio Le Sirenuse')
generateTables('./', 'post_reduced_network.csv', net)

print 'Time needed: {} s'.format(time.time() - start)