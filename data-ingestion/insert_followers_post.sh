#!/usr/bin/env bash

# insert followers posts
sed 's/\\\"//g' <../../csv/followers/post.csv >../../csv/followers/post_fixed.csv
./convert_f.py followers
mongoimport --db FaST --collection post_followers --mode insert --file ../../json/post.json  --jsonArray
rm -rf ../../json
