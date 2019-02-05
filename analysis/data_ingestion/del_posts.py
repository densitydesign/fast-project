from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['FaST']

post_to_delete = ["1622756415428740088", "1621859932835884702", "1542173212951335701"]

for pid in post_to_delete:
    res = db.post.delete_one({"id_post": pid})
    print res.deleted_count