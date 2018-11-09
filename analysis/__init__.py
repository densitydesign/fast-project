from pymongo.mongo_client import MongoClient

client = MongoClient()

db = client["FaST"]

posts_coll = db["post"]
stats_coll = db["stats"]

brands = ['daftcollectionofficial','loupcharmant','muzungusisters','heidikleinswim','lisamariefernandez',
		  'zeusndione','dodobaror','athenaprocopiou','miguelinagambaccini', "emporiosirenuse"]

datapath = '../../../csv'
