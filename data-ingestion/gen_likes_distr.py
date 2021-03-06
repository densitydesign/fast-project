
import pandas as pd
import numpy as np
from numpy.random import poisson
import random 
from datetime import datetime
from datetime import timedelta
from pymongo import MongoClient

brands = ['lisamariefernandez','zeusndione','dodobaror','athenaprocopiou','miguelinagambaccini', 'emporiosirenuse','daftcollectionofficial','loupcharmant','muzungusisters','heidikleinswim']

datapath = '../../csv/'
N_days = 20

client = MongoClient('mongodb://localhost:27017/')
db = client['FaST']

for b in brands:
	print 'Computing timeseries of ' + b
	posts = pd.read_csv(datapath + b + '/post.csv')
	likes = pd.read_csv(datapath + b + '/' + b + '_likes.csv')
	
	perc = 0
	for index, p in posts.iterrows():
		pid = str(p['id_post'])
		shortcode = p['shortcode']
		likes_list = list(likes[likes['shortcode'] == shortcode]['username'])

		date = datetime.strptime(p['taken_at_time'], '%Y-%m-%d %H:%M:%S')
		date_range = pd.date_range(date, date+timedelta(days=N_days), freq='D').tolist()
		
		# distribution definition
		r = []
		for u in likes_list:
			random.shuffle(date_range)
			d = date_range[4]
			s = random.randint(0, 81400)
			
			date = d + timedelta(seconds = s)
			r.append(tuple((date, u)))
		
		# dataframe distribution with datetime
		df = pd.DataFrame(r, columns=['time','user'])
		
		# dict to store in the DB
		likes_obj = [row.to_dict() for index, row in df.iterrows()]
		#print likes_obj
		
		# update objects in the DB
		result = db.post.update_one({'id_post': pid},
					{'$set': {'likes': likes_obj}},
				   upsert=False)
		print 'ACK: ' + str(result.acknowledged) + ' ,matched ' + str(result.matched_count) + ' ,updated ' + str(result.modified_count)

		# percentage of completion
		perc += 1
		print 'completion: {:.1f}%'.format(float(perc)*100/posts.shape[0])
