import pandas as pd
import requests
import re
from pymongo import MongoClient
import pymongo

# connect to DB
client = MongoClient('mongodb://localhost:27017/')
mongodb = client['FaST']

n_clusters = mongodb.community.count()


print 'Set numerics for each community...'.format(n_clusters)
for c in range(n_clusters):
    print 'Cluster ' + str(c)
    n_posts = mongodb.post_followers.find({"communities.{}".format(c): {"$exists": True}}).count()
    
    n_users = mongodb.user.find({"communities.{}".format(c): {"$exists": True}}).count()
    resp = mongodb.user.aggregate([ {"$match": {"communities.{}".format(c): {"$exists": True}}}, 
                                            {"$group": {"_id": None, "weight": {"$sum": "$communities.{}".format(c)}}}])
    dim_weighted = list(resp)[0]['weight']
     
    res = mongodb.community.update_one({'id': c}, {'$set': {'num_posts': n_posts,
                                                            'num_users': n_users,
                                                            'sum_weights': dim_weighted                                                             
                                                           }
                                                    }, upsert=False)