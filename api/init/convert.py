#!/usr/bin/env python
import csv
import os
import json
import sys
import numpy as np
import pandas as pd

def key_value(line):
    return line.split(":")

def load_content_mapping(filename):
    d = {}
    with open(filename, "r") as fid:
        for line in fid.readlines():
            key, value = key_value(line)
            d[key] = value.replace("\n", "").split(",")
    return pd.Series({kw: k for k, v in d.items() for kw in v})\
             .to_frame("content")
    

def load_data(folder, collection, delimiter=","):
    file_path = folder + "/" + collection + ".csv"
    with open(file_path, encoding='utf-8') as data_file:
        return list(csv.DictReader(data_file, delimiter=delimiter))


# main
indexed_collections = {"imagetag": {}, "geo_location": {}, "postcoord": {}}
folder = sys.argv[1]

content_mapping = load_content_mapping("content_dictionary.csv")
contents = content_mapping["content"].unique()

# index imagetag
imagetag_data_list = load_data(folder, "imagetag")
for item in imagetag_data_list:
    indexed_collections["imagetag"].setdefault(item["id_post"], [])\
        .append({"concept": item["concept"], "confidence": item["confidence"]})

# index geo location
location_data_list = load_data(folder, "location_geo")
for item in location_data_list:
    indexed_collections["geo_location"][item["id_post"]] = {
        "id_location": item["id_location"],
        "location": item["location"],
        "lat": item["lat"],
        "long": item["long"]
    }

# index postcoord
postcoord_data_list = load_data(folder, "postcoord")
for item in postcoord_data_list:
    indexed_collections["postcoord"][item["id_post"]] = [item["x"], item["y"]]

# convert
output = []
post_data_list = load_data(folder, "post")
for current_post in post_data_list:
    id_post = current_post["id_post"]

    # useless field
    del current_post["shortcode"]

    # postcoord
    if id_post in indexed_collections["postcoord"]:
        current_post["postcoord"] = indexed_collections["postcoord"][id_post]

    # imagetag
    if id_post in indexed_collections["imagetag"]:
        keywords = pd.merge(content_mapping,
                          pd.DataFrame( indexed_collections["imagetag"][id_post] ),
                          right_on="concept", left_index=True, how="right")\
                   .fillna("OTHER")
        keywords["confidence"] = keywords["confidence"].apply(float)

        grouped = keywords.groupby("content")
       
        current_post["imagetag"] = \
            grouped\
                .apply(lambda x: [
                    {"concept": key, "confidence": str(value)} 
                    for key, value in x.set_index("concept")["confidence"].items()]).to_dict()

        post_contents = grouped["confidence"].sum()
        
        current_post["content"] = post_contents.apply(str).to_dict()
        current_post["main_content"] = post_contents.reindex(contents).idxmax() if len(post_contents)>1 else "OTHER"

    # location
    if id_post in indexed_collections["geo_location"]:
        current_post["location"] = indexed_collections["geo_location"][id_post]

    current_post["taken_at_timestamp"] = int(current_post["taken_at_timestamp"])
        
    output.append(current_post)


# dump output
OUT_DIR = "../../../json/"
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)
with open(OUT_DIR + "post.json", "w") as outfile:
    json.dump(output, outfile) #indent=2
