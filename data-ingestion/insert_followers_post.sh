#!/usr/bin/env bash

# insert followers posts
./convert_2.py followers
mongoimport --db FaST --collection post_followers --type csv  --mode insert --headerline --file ../../csv/followers/post.csv
#rm -rf ../../json
