import pandas as pd
from datetime import datetime

from pymongo import UpdateOne

from brand import union, dateGroupByKey, get_date
from brand.parsers import get_data, add_logging_arguments, add_data_arguments, parse_arguments_with, setup_logger

from bson import ObjectId

def convert_to_id(x):
	return ObjectId.from_datetime(
		datetime.fromtimestamp((str(x.name) + x["brand"]).__hash__() % 2147483647)
	)

def contentRatio(content):
    return {"$cond": [ {"$gt": ["$TOT", 0]}, {"$divide": [content, "$TOT"] }, 0.0 ]}
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

	hashtags_count = [
		matchBrand,
		{"$addFields": {
			"time": {"$dateFromString": {"dateString": "$taken_at_time"}}
		}},
		{"$unwind": "$hashtags"},
		{"$group":
			{
				"_id": union(dateGroupByKey("$time"),{"hashtag": "$hashtags"}),
			  	"count": {"$sum": 1}
			}
		},
		{"$sort": {"count": -1}},
	]


	posts = pd.DataFrame( list( coll.aggregate(post_count) ) )
	likes = pd.DataFrame( list( coll.aggregate(likes_count) ) )
	hashtags = pd.DataFrame( list( coll.aggregate(hashtags_count) ) )

	posts["date"] = get_date(posts)
	likes["date"] = get_date(likes)

	hashtags["date"] = get_date(hashtags)
	hashtags["hashtag"] = hashtags["_id"].apply(lambda x: x["hashtag"])

	hashtags = hashtags.groupby("date")\
		.apply(lambda x: {row["hashtag"]: row["count"] for _, row in x.iterrows()})\
		.to_frame("hashtags")

	posts = posts.drop("_id", axis=1).set_index("date", verify_integrity=True)
	likes = likes.drop("_id", axis=1).set_index("date", verify_integrity=True)


	metrics = pd.concat([posts, likes, hashtags], axis=1).sort_index().fillna(0)

	metrics["brand"] = brand
	metrics["_id"] = metrics.apply(convert_to_id, axis=1)

	metrics = metrics.reset_index().set_index("_id", verify_integrity=True)

	return stats_coll.bulk_write([UpdateOne({'_id': _id}, {"$set": row.to_dict()}, upsert=True) for _id, row in metrics.iterrows()])


def custom_parser(parser):

	parser.add_argument('--batch-size',
                        default=1000,
                        type=int,
                        help="Batch size to be used when performing bulk enrich")
	return parser

if __name__ == "__main__":

	from settings import brands

	args = parse_arguments_with([add_data_arguments, add_logging_arguments, custom_parser])

	logger = setup_logger(args)

	data = get_data(args)

	posts_coll = data["posts"]
	stats_coll = data["stats"]

	batch_size = args.batch_size

	for brand in brands:

		print("Writing of brand %s" % brand)
		print( brand_stats(brand, post_coll=posts_coll, stats_coll=stats_coll).bulk_api_result)

