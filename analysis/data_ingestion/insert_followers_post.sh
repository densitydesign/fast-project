#!/usr/bin/env bash

# insert followers posts
echo "Converting $1..."
mongoimport --db FaST --collection post_followers --type csv --mode insert --headerline --columnsHaveTypes  --parseGrace skipRow --file "../../csv/$1/followers/post_fixed.csv"


