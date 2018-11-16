#!/bin/bash
../../../snap/examples/node2vec/node2vec -i:"network_data/hashtag_network.edgelist" -o:"network_data/hashtag_network_16.emb" -d:16 -p:1 -q:0.5 -k:30 -l:20 -v