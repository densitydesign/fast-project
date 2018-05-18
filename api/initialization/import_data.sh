#!/usr/bin/env bash

# Look for occurrences of \", namely \\\" and replace them with nothing
sed 's/\\\"//g' <../../../csv/brand.csv >../../../csv/brand_fixed.csv
mongoimport --db FaST --collection brand --type csv --mode insert --headerline --file ../../../csv/brand_fixed.csv

# Use tabs insted of semicolons (only csv and tsv are accepted by mongo)
tr ";" "\t" <../../../csv/imagevector.csv > ../../../csv/imagevector_fixed.tsv
mongoimport --db FaST --collection imagevector --type tsv --mode insert --headerline --file ../../../csv/imagevector_fixed.tsv

# Regulars
mongoimport --db FaST --collection post --type csv --mode insert --headerline --file ../../../csv/post.csv
mongoimport --db FaST --collection imagetag --type csv --mode insert --headerline --file ../../../csv/imagetag.csv
mongoimport --db FaST --collection postcoord --type csv --mode insert --headerline --file ../../../csv/postcoord.csv
mongoimport --db FaST --collection location --type csv --mode insert --headerline --file ../../../csv/location.csv


