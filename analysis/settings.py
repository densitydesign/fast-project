import os
from pymongo.mongo_client import MongoClient

# Level of logging
LOG_LEVEL = "INFO"

# Name of the MongoDB database
MONGO_DB = "FaST"

# Name of the collections
STATS_COLLECTION = "stats"
POSTS_COLLECTION = "post"
FOLLOWERS_COLLECTION = "post_followers"
USERS_COLLECTION = "user"
BRANDS_COLLECTION = "brand"
COMMUNITY_COLLECTION = "community"

brands = ['daftcollectionofficial','loupcharmant','muzungusisters','heidikleinswim','lisamariefernandez',
		  'zeusndione','dodobaror','athenaprocopiou','miguelinagambaccini', "emporiosirenuse"]

# =================
# DO NOT EDIT BELOW
# =================

client = MongoClient()

db = client[MONGO_DB]

posts_coll     = db[POSTS_COLLECTION]
stats_coll     = db[STATS_COLLECTION]
followers_coll = db[FOLLOWERS_COLLECTION]
users_coll      = db[USERS_COLLECTION]
brands_coll    = db[BRANDS_COLLECTION]
community_coll = db[COMMUNITY_COLLECTION]

datapath = os.path.join(os.getcwd(), '..', '..', '..', 'csv')
