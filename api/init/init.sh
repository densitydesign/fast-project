#!/usr/bin/env bash

# indexes
echo "Creating indexes..."
mongo 127.0.0.1:27017/FaST indexes.js

# convert
echo "Converting data..."
./convert.py

# import
echo "Importing data in db..."
sed 's/\\\"//g' <../../../csv/brand.csv >../../../csv/brand_fixed.csv
mongoimport --db FaST --collection brand --type csv --mode insert --headerline --file ../../../csv/brand_fixed.csv
mongoimport --db FaST --collection post  --mode insert --file ../../../json/post.json  --jsonArray

# clean
echo "Cleaning..."
rm ../../../csv/brand_fixed.csv
rm -rf ../../../json