#!/usr/bin/env bash

# indexes
echo "Creating indexes..."
mongo 127.0.0.1:27017/FaST indexes.js

# importing brands in db
echo "Importing data in db..."
sed 's/\\\"//g' <../../../csv/brand.csv >../../../csv/brand_fixed.csv
mongoimport --db FaST --collection brand --type csv --mode insert --headerline --file ../../../csv/brand_fixed.csv
rm ../../../csv/brand_fixed.csv

# importing posts in db
for i in `ls -d ../../../csv/*/`; do
    echo "Converting $i..."
    ./convert.py $i
    mongoimport --db FaST --collection post  --mode insert --file ../../../json/post.json  --jsonArray
    rm -rf ../../../json
done;