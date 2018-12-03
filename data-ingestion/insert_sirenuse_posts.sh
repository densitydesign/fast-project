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
        
        # if this command does not work, substitute ./ with local path of python 3 installation (e.g.: C:\\Anaconda3\\python)
        ./convert_f.py $i
        mongoimport --db FaST --collection post_followers --mode insert --file ../../json/post.json  --jsonArray
        
        rm -rf ../../json
    fi

done;
done;