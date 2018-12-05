#!/usr/bin/env bash

# indexes (automatically drop duplicates)
echo "Creating index for id_post and timestamp..."
mongo 127.0.0.1:27017/FaST indexes_post.js

# insert followers posts
for i in `ls -d ../../csv/*/followers/`; do
    if [[ $i == *"emporiosirenuse"* ]]
    then
        echo "Converting $i..."
        
        #sed 's/\\\"//g' < $i/post.csv > $i/post_fixed.csv
        
        # if this command does not work, substitute ./ with local path of python 3 installation 
        # e.g.: Local Windows -> C:\\Anaconda3\\python, Linux Server -> /home/anaconda2/envs/api_env/bin/python
        #C:\\Anaconda3\\python convert_f.py $i
        mongoimport --db FaST --collection post_followers --type csv --mode insert --headerline --columnsHaveTypes --parseGrace autoCast --file $i/post_fixed.csv
        
    fi

done;
