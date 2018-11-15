import requests
import re
from pymongo import MongoClient

def solveImgUrl(postUrl):
	page = requests.get(url)
	try:
		return re.findall(r'\"[\S]*.jpg', page.text)[0][1:]
	except Exception as e:
		print('Error with: ' + postUrl)
		print(e)
		return -1

client = MongoClient('mongodb://localhost:27017/')
db = client['FaST']

collection_ids = [id for id in db.post.find().distinct('_id')]

for mongo_id in collection_ids:
    p = db.post.find_one({"_id": mongo_id})
    url = p['link_post']
    
    new_url = solveImgUrl(url)
    if new_url == -1:
        new_url = url
        
    res = db.post.update_one({'_id': mongo_id},
					{'$set': {'url_img': new_url}},
				   upsert=False)
