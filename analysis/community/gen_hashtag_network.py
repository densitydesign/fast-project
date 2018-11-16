import pandas as pd
import snap

def generateTables(targetpath, netfile, net):
	#split file into node and edge file
	net_file = open(targetpath+netfile+'.csv', 'r') 
	nodes_file = open(targetpath+netfile+'_nodes.csv', 'w')
	nodes_file.write('id\tcontent\ttype\tid_node\n')
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
		
datapath = 'raw-data/'

corenodes = pd.DataFrame()
coreedges = pd.DataFrame()

tagnetnodes = pd.DataFrame()
tagnetedges = pd.DataFrame()

## USER DATA ##
outpath = 'network_data/'

users = pd.read_csv(datapath+'user.csv', quotechar='"', escapechar='\\', dtype='object')
userNodes = users[['id_user', 'username']]
userNodes.columns = ['id', 'content']
userNodes['type'] = 'user'
corenodes = pd.concat([corenodes, userNodes])


## POST DATA ##
postdata = pd.read_csv(datapath+'post.csv', sep='\t', dtype='object')
postdata = postdata[['id_post','owner', 'taken_at_timestamp']]

# filter to keep only target users data
postdata = postdata[postdata['owner'].isin(list(userNodes['id']))]

postnodes = postdata[['id_post', 'taken_at_timestamp']]
postnodes.columns = ['id', 'content']
postnodes['type'] = 'post'
corenodes = pd.concat([corenodes, postnodes])
print '{} post nodes added.'.format(postnodes.shape[0])

#add post-user relationship
postedges = postdata[['id_post','owner']]
postedges.columns = ['target', 'source']
postedges['e_type'] = 'post'
coreedges = pd.concat([coreedges, postedges])
print '{} post edges added.'.format(postedges.shape[0])

## TAG DATA ##
tagdata = pd.read_csv(datapath+'tag.csv', dtype='object')

# filter to keep only target users data and tags that are relevant (separate analysis)
relevant_tags = list(pd.read_csv('raw-data/relevant_tags.csv')['tag'])

tagdata = tagdata[tagdata['tag'].isin(relevant_tags)]
tagdata = tagdata[tagdata['id_post'].isin(list(postnodes['id']))]

tagnodes = tagdata[['tag']].drop_duplicates()
tagnodes.columns = ['id']
tagnodes['content'] = tagdata['tag']
tagnodes['type'] = 'tag'
tagnetnodes = pd.concat([corenodes, tagnodes])
print '{} tag nodes added.'.format(tagnodes.shape[0])

#add post-tag relationship
print 'Add tag-post relationship...'
tagedges = tagdata[['id_post', 'tag']]
tagedges.columns = ['source', 'target']
tagedges['e_type'] = 'tag'
tagnetedges = pd.concat([coreedges, tagedges])
print '{} tag edges added.'.format(tagedges.shape[0])

## TAG NETWORK FILES ##
nodefile = 'temp/tagnodes.csv'
edgefile = 'temp/tagedges.csv'
tagnetnodes.to_csv(nodefile, index=None)
tagnetedges.to_csv(edgefile, index=None)

## NETWORK CONSTRUCTION ##
e_schema = snap.Schema()
e_schema.Add(snap.TStrTAttrPr("e_type", snap.atStr))
e_schema.Add(snap.TStrTAttrPr("source", snap.atStr))
e_schema.Add(snap.TStrTAttrPr("target", snap.atStr)) 

n_schema = snap.Schema()
n_schema.Add(snap.TStrTAttrPr("id", snap.atStr))
n_schema.Add(snap.TStrTAttrPr("content", snap.atStr))
n_schema.Add(snap.TStrTAttrPr("type", snap.atStr))

#define TTable objects of edges and nodes
context = snap.TTableContext()
edgetable = snap.TTable.LoadSS(e_schema, edgefile, context, ",", snap.TBool(True))
nodetable = snap.TTable.LoadSS(n_schema, nodefile, context, ",", snap.TBool(True))

#define (if any) attribute names using SNAP string vectors
edgeattrv = snap.TStrV()
edgeattrv.Add("e_type")

nodeattrv = snap.TStrV()
nodeattrv.Add("content")
nodeattrv.Add("type")
nodeattrv.Add("id")

#build SNAP network using the two TTable objects
net = snap.ToNetwork(snap.PNEANet, edgetable, "source", "target", edgeattrv, nodetable, "id", nodeattrv, snap.aaFirst)
print '|V| = {}'.format(net.GetNodes())
print '|E| = {}'.format(net.GetEdges()) 

# NB: complete == complete hashtag network
networkname = 'hashtag_network'

# visualization and metadata
snap.SaveEdgeListNet(net, outpath+networkname+'.csv', 'Hashtag Community Network - Filtered')
generateTables(outpath, networkname, net)

# node2vec input
snap.SaveEdgeList(net, outpath+networkname+'.edgelist')