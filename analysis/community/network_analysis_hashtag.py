import snap
import pandas as pd
import numpy as np

network = snap.LoadEdgeListNet('data/emporiosirenuse_network_filtered.csv', '\t')

result = []
for NI in network.Nodes(): 
    nid =NI.GetId()
    ntype = network.GetStrAttrDatN(nid, 'type')
    if ntype == 'tag':
        tagname = network.GetStrAttrDatN(nid, 'content')
        #closeness = snap.GetClosenessCentr(network, nid)
        degree = NI.GetInDeg()
        result.append(tuple((tagname, degree)))

df = pd.DataFrame(result, columns=['hashtag', 'degree'])
df.to_csv('output/hashtag_distribution.csv', index=None)