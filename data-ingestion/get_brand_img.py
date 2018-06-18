import pandas as pd
import requests
import sys
import re

def solveImgUrl(postUrl):
	page = requests.get(url)
	try:
		return re.findall(r'\"[\S]*.jpg', page.text)[0][1:]
	except Exception as e:
		print 'Error with post: {}'.format(postUrl)
		print e
		return None

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