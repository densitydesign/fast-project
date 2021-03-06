#!/usr/bin/env bash

#,username,profile_pic_url,followers_count,following_count,num_posts,biography,isPrivate

# indexes (automatically drop duplicates)
echo "Creating indexes"
mongo 127.0.0.1:27017/FaST indexes_user.js

# insert followers user data
for i in `ls -d ../../csv/*/followers/`; do
    echo "Converting $i..."
    
    if [[ $i == *"lisamariefernandez"* ]]
    then
        mongoimport --db FaST --collection user --type csv --mode insert --headerline --columnsHaveTypes  --file $i/user.csv 
    else
        sed 's/\\\"//g' < $i/user.csv > $i/user_fixed.csv
        mongoimport --db FaST --collection user --type csv --mode insert --headerline --columnsHaveTypes --file $i/user_fixed.csv  
        rm $i/user_fixed.csv
    fi
    
    rm -rf ../../json
done;