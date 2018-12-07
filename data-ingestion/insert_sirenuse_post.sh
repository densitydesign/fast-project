#!/usr/bin/env bash

# indexes (automatically drop duplicates)
echo "Creating index for id_post and timestamp..."
mongo 127.0.0.1:27017/FaST indexes_post.js

# insert sirenuse followers posts
mongoimport --db FaST --collection post_followers --type csv --mode insert --headerline --columnsHaveTypes --parseGrace skipRow --file ../../csv/emporiosirenuse/followers/post_fixed.csv
        
