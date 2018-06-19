import snap
import pandas as pd
import numpy as np

network = snap.LoadEdgeListNet('data/followers_network.csv', '\t')

result = []
for NI in network.Nodes(): 
    nid =NI.GetId()
    ntype = network.GetStrAttrDatN(nid, 'type')
    if ntype == 'tag':
        tagname = network.GetStrAttrDatN(nid, 'content')
        closeness = snap.GetClosenessCentr(network, nid)
        degree = NI.GetInDeg()
        result.append(tuple((tagname, degree, closeness)))

df = pd.DataFrame(result, columns=['hashtag', 'degree', 'closeness'])

deg_sorted = df.sort_values(by='degree', ascending=False)
print deg_sorted[:20]

clos_sorted = df.sort_values(by='closeness', ascending=False)
print clos_sorted[:20]