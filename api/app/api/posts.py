
from flask_restful.reqparse import RequestParser

class PostRequests(object):

    parser = RequestParser()

    DEFAULT_LIMIT=10

    parser.add_argument('start', type=int)
    parser.add_argument('end', type=int)
    parser.add_argument('limit', type=int)
    parser.add_argument('content', type=str)
    parser.add_argument('competitor', type=int, required=False)

    def parse_args(self):
        args = self.parser.parse_args()

        args.limit = args.limit if args.limit is not None else self.DEFAULT_LIMIT

        return args


def build_query(args, query=None):

    query = query if query is not None else {}

    time_query = {}
    if (args.start):
        time_query["$gte"] = args.start
    if (args.end):
        time_query["$lte"] = args.end
    if len(time_query) > 0:
        query["taken_at_timestamp"] = time_query

    if (args.content):
        query["main_content"] = args.content

    return query


def parse_coords(competitor=None):
    def wrapper(json):
        json["postcoord"] = json.pop("pair_coord")[
            competitor if competitor is not None else "base"
        ]
        return json
    return wrapper