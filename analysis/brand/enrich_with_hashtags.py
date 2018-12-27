#!/usr/bin/env python
import re
from brand import groupIterable
from pymongo import UpdateOne

from brand.parsers import parse_arguments_with, add_data_arguments, add_logging_arguments, setup_logger, get_data

def get_hashtags(text):
    return [hashtag.lower() for hashtag in re.findall(r"#(\w+)", text)]

def get_mentions(text):
    return [mention.lower() for mention in re.findall(r"(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9_]+)", text)]


def custom_parser(parser):

    parser.add_argument('--collection',
                        default="followers",
                        choices=["followers", "posts"],
                        help="Which collection to enrich")

    parser.add_argument('--batch-size',
                        default=10000,
                        type=int,
                        help="Batch size to be used when performing bulk enrich")

    return parser

if __name__ == "__main__":

    args = parse_arguments_with([add_data_arguments, add_logging_arguments, custom_parser])

    logger = setup_logger(args)

    data = get_data(args)

    collection = data[args.collection]

    batch_size = args.batch_size

    cursor = collection.find({"$or": [{"hashtags": {"$exists": False}}, {"mentions": {"$exists": False}}]}, {"caption": 1})
    # cursor = post_coll.find({}, {"caption": 1})

    for ibatch, posts in enumerate(groupIterable(cursor, batch_size)):

        # text = post["caption"]
        # hashtags = [hashtag.lower() for hashtag in get_hashtags(text)]

        logger.info("Batch %d: Processing %d posts" % (ibatch, len(posts)))

        documents = []
        for post in posts:
            try:
                documents.append(UpdateOne(
                    {'_id': post["_id"]},
                    {"$set": {"hashtags": get_hashtags(post["caption"]), "mentions": get_mentions(post["caption"])}}
                ))
            except Exception as e:
                logger.error("Error for post id %s" % post["_id"])
                logger.error("Exception: %s" % e.message)

        if len(documents)>0:
            collection.bulk_write(documents)


