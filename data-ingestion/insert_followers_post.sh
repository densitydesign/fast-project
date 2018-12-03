#!/usr/bin/env bash

# insert followers posts
for i in `ls -d ../../csv/*/followers/`; do
    if [[ $i == *"daftcollectionofficial"* ]] || [[ $i == *"miguelinagambaccini"* ]] || [[ $i == *"heidikleinswim"* ]]
    then
        echo "Converting $i..."
        #sed 's/\\\"//g' < $i/post.csv > $i/post_fixed.csv
        mongoimport --db FaST --collection post_followers --type csv --mode insert --headerline --file $i/post_fixed.csv
    fi

done;
