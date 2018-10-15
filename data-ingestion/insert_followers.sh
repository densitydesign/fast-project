#!/usr/bin/env bash

./convert.py followers
mongoimport --db FaST --collection post  --mode insert --file ../../../json/post.json  --jsonArray
rm -rf ../../../json