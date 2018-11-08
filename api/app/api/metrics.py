import pandas as pd
from datetime import datetime
from flask_restful.reqparse import RequestParser

class MetricsRequests(object):

    parser = RequestParser()

    DEFAULT_LIMIT=10

    parser.add_argument('start', type=int)
    parser.add_argument('end', type=int)

    def parse_args(self):
        return self.parser.parse_args()

def build_query(args, query=None):

    query = query if query is not None else {}

    time_query = {}
    if (args.start):
        time_query["$gte"] = args.start
    if (args.end):
        time_query["$lte"] = args.end
    if len(time_query) > 0:
        query["date"] = time_query

    return query

def aggregate_response(json):

    print(json)

    df = pd.DataFrame(json).sort_values("date")

    s = df[["ambient", "lifestyle", "fashion"]]

    content = (s.sum() / s.sum().sum()).to_dict()

    return {
        "dates": [datetime.fromtimestamp(x).strftime("%Y-%m-%d") for x in df["date"].values],
        "posts": [int(x) for x in df["posts"].values],
        "likes": [int(x) for x in df["likes"].values],
        "content": content
    }


