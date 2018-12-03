from pymongo import MongoClient
import pymongo
import pandas as pd
import os

path = '../../csv/'

client = MongoClient('mongodb://localhost:27017/')
mongodb = client['FaST']

# get brands list
brands = mongodb.brand.find({}, {'id_user':1, 'username':1, '_id':0})

# create index
mongodb.user.create_index([('following', pymongo.TEXT)])

for b in brands:
    brand_id = b['id_user']
    brandname = b['username']
    print brand_id,brandname
    
    # conversion needed because mongo does not recognize numpy.int64 as type
    followers = [int(i) for i in pd.read_csv(path + brandname + '/followers/user.csv')['id_user'].drop_duplicates()]
    res = mongodb.user.update_many({'id_user': {'$in': followers}}, {'$addToSet': {'following': brand_id}})
    