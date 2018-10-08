#!/usr/bin/env python
import csv
import os
import json
import sys


def load_data(folder, collection, delimiter=","):
    file_path = folder + "/" + collection + ".csv"
    with open(file_path) as data_file:
        return list(csv.DictReader(data_file, delimiter=delimiter))


# main
folder = sys.argv[1]

# load followers posts in same collection of brands posts
output = []
post_data_list = load_data(folder, "post")
for current_post in post_data_list:
    id_post = current_post["id_post"]

    # useless field
    del current_post["shortcode"]

    output.append(current_post)


# dump output
OUT_DIR = "../../../json/"
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)
with open(OUT_DIR + "post.json", "w") as outfile:
    json.dump(output, outfile) #indent=2