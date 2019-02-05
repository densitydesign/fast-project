def parse_arguments_with(parsers=[], namespace=None):
    import argparse
    from functools import reduce

    return reduce(lambda x, f: f(x), parsers, argparse.ArgumentParser()).parse_args(namespace=namespace)

def add_data_arguments(parser):

    from settings import MONGO_DB, STATS_COLLECTION, POSTS_COLLECTION, FOLLOWERS_COLLECTION, USERS_COLLECTION, \
        BRANDS_COLLECTION, COMMUNITY_COLLECTION, datapath

    parser.add_argument('--db',
                        default=MONGO_DB,
                        help="Name of the MongoDB Database")

    parser.add_argument('--stats-collection',
                        default=STATS_COLLECTION,
                        help="Collection with the stats")
    parser.add_argument('--posts-collection',
                        default=POSTS_COLLECTION,
                        help="Collection with the posts")
    parser.add_argument('--followers-collection',
                        default=FOLLOWERS_COLLECTION,
                        help='Collection for the followers posts')
    parser.add_argument('--users-collection',
                        default=USERS_COLLECTION,
                        help='Collection for all the users')
    parser.add_argument('--brands-collection',
                        default=BRANDS_COLLECTION,
                        help='Collection for all the brands')
    parser.add_argument('--community-collection',
                        default=COMMUNITY_COLLECTION,
                        help='Collection for all the communities that have been identified by clustering')
    parser.add_argument('--use-default-data',
                        action="store_true",
                        help='If used, use the default data binding according to settings.py')

    parser.add_argument('--data-path',
                        default=datapath,
                        help='Path where the data is stored')

    return parser


def add_logging_arguments(parser):

    parser.add_argument('--log-level',
                        choices=["INFO", "WARN", "ERROR", "DEBUG"],
                        default="INFO",
                        help='Set the log level of the logging')

    parser.add_argument('--log-conf',
                        default='logging.yaml',
                        help="Configuration file for the logging")

    return parser

def setup_logger(args):
    """
    Setup logging configuration

    :param args: arguments

    :type args: instance of argparse.ArgumentParser

    :return: logger setted depending on configuration file given in args
    """
    from loggers import getLogger, getDefaultLogger, configFromFile

    getDefaultLogger(level=args.log_level)

    if args.log_conf is not None:
        configFromFile(args.log_conf)

    return getLogger("brand")


def get_data(args):

    if (args.use_default_data is True):

        from settings import db, posts_coll, stats_coll, followers_coll, users_coll, brands_coll, community_coll
    else:
        from settings import client

        db = client[args.db]

        posts_coll = db[args.posts_collection]
        stats_coll = db[args.stats_collection]
        followers_coll = db[args.followers_collection]
        users_coll = db[args.users_collection]
        brands_coll = db[args.brands_collection]
        community_coll = db[args.community_collection]

    return {
        "db": db,
        "posts": posts_coll,
        "stats": stats_coll,
        "followers":followers_coll,
        "users": users_coll,
        "brands": brands_coll,
        "community": community_coll
    }


