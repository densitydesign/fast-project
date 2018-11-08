import pandas as pd
from datetime import datetime

from pymongo import UpdateOne

from analysis import brands, posts_coll, stats_coll
from bson import ObjectId

def convert_to_id(x):
	return ObjectId.from_datetime(
		datetime.fromtimestamp((str(x.name) + x["brand"]).__hash__() % 2147483647)
	)

def dateGroupByKey(field):
    return { 
	"year" : {"$year": field} , 
	"month": {"$month": field}, 
	"day"  : {"$dayOfMonth": field}
    }

def contentRatio(content):
    return {"$cond": [ {"$gt": ["$TOT", 0]}, {"$divide": [content, "$TOT"] }, 0.33 ]}
    # return { "$divide": [content, "$TOT"] }

def brand_stats(brand, post_coll, stats_coll):
	coll = post_coll

	matchBrand = {"$match": {"username": brand}}

	likes_count = [
		matchBrand,
		{"$unwind": "$likes"},
		{ "$group": {
			"_id": dateGroupByKey("$likes.time"),
			"likes": {"$sum": 1}
			}
		}]

	post_count = [
		matchBrand,
			{"$addFields": {
			"content.AMBIENT": { "$ifNull": [ "$content.AMBIENT", 0 ] },
			"content.FASHION": { "$ifNull": [ "$content.FASHION", 0 ] },
			"content.LIFESTYLE": { "$ifNull": [ "$content.LIFESTYLE", 0 ] },
		}},
		{"$addFields": {"TOT": {"$add": ["$content.AMBIENT", "$content.FASHION", "$content.LIFESTYLE"]}}},
		# {"$match": {"TOT": {"$gt": 0}}},
		{"$addFields": {
			"time": {"$dateFromString": {"dateString": "$taken_at_time"}},
			"ambientRatio": contentRatio("$content.AMBIENT"),
			"fashionRatio": contentRatio("$content.FASHION"),
			"lifestyleRatio": contentRatio("$content.LIFESTYLE"),
			}
		},
		{"$group":
			{ "_id": dateGroupByKey("$time"),
			  "posts": {"$sum": 1},
			  "ambient": {"$sum": "$ambientRatio"},
			  "fashion": {"$sum": "$fashionRatio"},
			  "lifestyle": {"$sum": "$lifestyleRatio"}
			}
		}]

	posts = pd.DataFrame( list( coll.aggregate(post_count) ) )
	likes = pd.DataFrame( list( coll.aggregate(likes_count) ) )

	def get_date(df):
		return df["_id"].apply(lambda x: datetime.strptime("%04d%02d%02d" % (x["year"], x["month"],x["day"]), "%Y%m%d"))

	posts["date"] = get_date(posts)
	likes["date"] = get_date(likes)

	posts = posts.drop("_id", axis=1).set_index("date", verify_integrity=True)
	likes = likes.drop("_id", axis=1).set_index("date", verify_integrity=True)

	metrics = pd.concat([posts, likes], axis=1).sort_index().fillna(0)

	metrics["brand"] = brand
	metrics["_id"] = metrics.apply(convert_to_id, axis=1)

	metrics = metrics.reset_index().set_index("_id", verify_integrity=True)

	return stats_coll.bulk_write([UpdateOne({'_id': _id}, {"$set": row.to_dict()}, upsert=True) for _id, row in metrics.iterrows()])


if __name__ == "__main__":

	for brand in brands:

		print("Writing of brand %s" % brand)
		print( brand_stats(brand, post_coll=posts_coll, stats_coll=stats_coll).bulk_api_result)

