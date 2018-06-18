import requests
import re
import pandas as pd
import time

locations = pd.read_csv('data/all-locations.csv') # query to the DB for distinct locations

N = locations.shape[0]
perc = 0

with open('locations-lookup.csv', 'a') as lookupfile:
	lookupfile.write('id_location,lat,long\n')
	for index,loc in locations.iterrows():
		id_location = loc['id_location']
		url = "https://www.instagram.com/explore/locations/{}/".format(id_location)
		page = requests.get(url)
		response_code = page.status_code
		
		while response_code != 200:
			print ('Error: {}'.format(response_code))
			print ('Waiting...')
			time.sleep(60)
			page = requests.get(url)
			response_code = page.status_code
		
		try:
			longitude = re.search(r'\"place:location:longitude\" content=\"((-)?(\d)+.(\d)+)', page.text).group(1)
			latitude = re.search(r'\"place:location:latitude\" content=\"((-)?(\d)+.(\d)+)', page.text).group(1)
			
			lookupfile.write('{},{},{}\n'.format(id_location, latitude, longitude))
			
		except Exception as e:
			print 'Error with location: '+loc['location']
			print 'URL: '+url
			print e
		
		perc = perc + 1
		print 'Completion: {:.1f}%...'.format(float(perc)*100/N)