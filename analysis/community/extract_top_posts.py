import pandas as pd
import requests
import re
from pymongo import MongoClient
import pymongo

def get_img_url(postUrl):
    page = requests.get(url)
    try:
        return re.findall(r'=[\S]*.jpg', page.text)[0][2:]
    except Exception as e:
        print e, postUrl
        return None

TOP_IMG = 5
MAX_POSTS = 30
cluster_pic_path = '../../../img/followers/'

# connect to DB
client = MongoClient('mongodb://localhost:27017/')
mongodb = client['FaST']

n_clusters = mongodb.community.count()

# count the effective retrieved images (some may be missing from Instagram, too)
# also, write as top posts in the community the ones that have the images
# iterate over the top posts, trying to extract from different users
print 'Set top posts for {} clusters and download images...'.format(n_clusters)
for c in range(n_clusters):
    print 'Cluster ' + str(c)
    top_img_cluster = mongodb.post_followers.find({"communities.{}".format(c): {"$exists": True}})\
                                       .sort("communities.{}".format(c), pymongo.DESCENDING)\
                                       .limit(MAX_POSTS)
    
    img_found = 0
    top_posts_ids = []
    for post in top_img_cluster:
        pid = post['id_post']
        url = post['link_post']
        username = post['username']
        image_url = get_img_url(url)
        
        if image_url is not None:
            img_data = requests.get(image_url).content
            with open(cluster_pic_path + '{}.jpg'.format(pid), 'wb') as handler:
                handler.write(img_data)
            
            top_posts_ids.append(pid)
            img_found += 1
            
        if img_found == TOP_IMG:
            break
     
    res = mongodb.community.update_one({'id': c}, {'$set': {'top_posts': top_posts_ids}}, upsert=False)