#!/usr/bin/env python
import csv
import os
import json


def load_data(collection, delimiter=","):
    file_path = "../../../csv/" + collection + ".csv"
    with open(file_path) as data_file:
        return list(csv.DictReader(data_file, delimiter=delimiter))


# main
indexed_collections = {"imagevector": {}, "imagetag": {}, "location": {}, "postcoord": {}}

# index imagetag
imagetag_data_list = load_data("imagetag")
for item in imagetag_data_list:
    indexed_collections["imagetag"].setdefault(item["id_post"], [])\
        .append({"concept": item["concept"], "confidence": item["confidence"]})

# index imagevector
imagevector_data_list = load_data("imagevector", delimiter=";")
for item in imagevector_data_list:
    indexed_collections["imagevector"][item["id_post"]] = item["vector"]

# index location
location_data_list = load_data("location")
for item in location_data_list:
    indexed_collections["location"][item["id_post"]] = {"id_location": item["id_location"], "location": item["location"]}

# index postcoord
postcoord_data_list = load_data("postcoord")
for item in postcoord_data_list:
    indexed_collections["postcoord"][item["id_post"]] = [item["x"], item["y"]]

# convert
output = []
post_data_list = load_data("post")
for current_post in post_data_list:
    current_post["imagetag"] = indexed_collections["imagetag"][current_post["id_post"]]
    current_post["imagevector"] = indexed_collections["imagevector"][current_post["id_post"]]
    current_post["postcoord"] = indexed_collections["postcoord"][current_post["id_post"]]

    if current_post["id_post"] in indexed_collections["location"]:
        current_post["location"] = indexed_collections["location"][current_post["id_post"]]

    output.append(current_post)

# dump output
OUT_DIR = "../../../json/"
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)
with open(OUT_DIR + "post.json", "w") as outfile:
    json.dump(output, outfile) #indent=2
