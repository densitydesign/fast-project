#!/usr/bin/env python
import csv
import os
import json
import sys


def load_data(folder, collection, delimiter=","):
    file_path = folder + "/" + collection + ".csv"
    with open(file_path, 'rU') as data_file:
        return list(csv.DictReader(data_file, delimiter=delimiter))


# main
folder = sys.argv[1]
path = '../../csv/'

# load followers posts NOT in same collection of brands posts
# for now use a test table post_followers
output = []
post_data_list = load_data(path + folder, "post")
for current_post in post_data_list:
    try:
        id_post = current_post["id_post"]

        # useless field
        del current_post["shortcode"]

        output.append(current_post)
    except:
        print ("No id found, skipping!")

# dump output
OUT_DIR = "../../json/"
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)
with open(OUT_DIR + "post.json", "w") as outfile:
    json.dump(output, outfile) #indent=2
