#!/usr/bin/env bash

# insert followers posts
sed 's/\\\"//g' <../../csv/post.csv >../../csv/post_fixed.csv
./convert_2.py followers
mongoimport --db FaST --collection post_followers --mode insert --file ../../../json/post.json  --jsonArray
rm -rf ../../json
