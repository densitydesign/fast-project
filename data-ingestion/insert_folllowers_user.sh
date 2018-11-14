#!/usr/bin/env bash

# insert followers user data
mongoimport --db FaST --collection user --type csv --mode insert --headerline --file ../../csv/followers/user.csv