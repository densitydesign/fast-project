#!/usr/bin/env bash

# insert followers posts
./convert.py followers
mongoimport --db FaST --collection post_followers  --mode insert --file ../../json/post.json  --jsonArray
rm -rf ../../json

# insert followers user data
mongoimport --db FaST --collection user --type csv --mode insert --headerline --file ../../csv/followers/user.csv