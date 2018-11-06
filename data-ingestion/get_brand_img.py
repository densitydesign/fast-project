import pandas as pd
import requests
import sys
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

collection_ids = [str(id) for id in db.post.find().distinct('_id')]

for mongo_id in collection_ids:
    p = db.post.find_one({"_id": mongo_id})
    url = p['link_post']
    
    new_url = solveImgUrl(url)
    print(new_url)
    if new_url == -1:
        new_url = url
        
    res = db.post.update_one({'_id': mongo_id},
					{'$set': {'url_img': new_url}},
				   upsert=False)
    
'''
datapath = '../../csv/'
		
brand = sys.argv[1]
path = '../../img/{}/'.format(brand)
posts = pd.read_csv(datapath+'post.csv'.format(brand)) # susbstitue with query to MongoDB
N = posts.shape[0]

perc = 0
for index, p in posts.iterrows():
	post_id = p['id_post']
	url = p['link_post']
	image_url = solveImgUrl(url)
	
	if image_url is not None:
		img_data = requests.get(image_url).content
		with open(path+'{}.jpg'.format(post_id), 'wb') as handler:
			handler.write(img_data)
	perc = perc + 1
	print 'Completion: {:.1f}%...'.format(float(perc)*100/N)
'''