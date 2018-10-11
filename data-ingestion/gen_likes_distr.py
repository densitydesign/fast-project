import pandas as pd
import numpy as np
from numpy.random import poisson
import random 
from datetime import datetime
from datetime import timedelta
from pymongo import MongoClient

brands = ['daftcollectionofficial','loupcharmant','muzungusisters','heidikleinswim','lisamariefernandez',
		  'zeusndione','dodobaror','athenaprocopiou','miguelinagambaccini', 'emporiosirenuse']

datapath = '../../csv/'
N_days = 20

client = MongoClient('mongodb://localhost:27017/')
db = client['FaST']

for b in brands:
	print 'Computing timeseries of ' + b
	posts = pd.read_csv(datapath + b + '/post.csv')
	
	perc = 0
	for index, p in posts.iterrows():
		#print p['taken_at_time'], p['likes_count']
		pid = p['id_post']
		likes = int(p['likes_count'])
		date = datetime.strptime(p['taken_at_time'], '%Y-%m-%d %H:%M:%S')
		
		date_range = pd.date_range(date, date+timedelta(days=N_days), freq='H').tolist()
		
		# distribution definition
		sum_distr = 0
		while sum_distr != likes:
			lam = random.uniform(0.05, 6.8)
			dist = poisson(lam, len(date_range))
			sum_distr = sum(dist)
		
		# dataframe distribution with datetime
		df = pd.DataFrame(dist, columns=['value'])
		df['timestamp'] = date_range
		
		# dict to store in the DB
		likes_obj = [row.to_dict() for index, row in df.iterrows()]
		#print likes_obj
		
		# update objects in the DB
		result = db.post.update_one({'id_post': pid},
				   {'$set': {'likes': likes_obj}},
				   upsert=False)
		print 'ACK: ' + result['acknowledged'] + ' ,matched ' + str(result['matchedCount']) + ' ,updated ' + str(result['modifiedCount'])
		# percentage of completion
		perc += 1
		print 'Completion: {:.1f}%'.format(float(perc)*100/posts.shape[0])