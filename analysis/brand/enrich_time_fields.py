#!/usr/bin/env python
from datetime import datetime

from brand import groupIterable
from pymongo import UpdateOne

from brand.parsers import parse_arguments_with, add_data_arguments, add_logging_arguments, setup_logger, get_data

def get_time(timestamp):
    return datetime.fromtimestamp(int(float(timestamp)))


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

    cursor = collection.find({"timestamp": {"$exists": False}}, {"taken_at_timestamp": 1})

    processed = 0

    for ibatch, posts in enumerate(groupIterable(cursor, batch_size)):

        logger.info("Batch %d: Processing %d posts" % (ibatch, len(posts)))

        documents = []
        for post in posts:
            try:
                documents.append(UpdateOne(
                    {'_id': post["_id"]},
                    {"$set": {"timestamp": get_time(post["taken_at_timestamp"])}}
                ))
            except Exception as e:
                logger.error("Error for post id %s" % post["_id"])
                logger.error("Exception: %s" % e.message)

        if (len(documents)>0):
            processed += len(documents)
            collection.bulk_write(documents)

    logger.info("Total documents processed: %d" % processed)