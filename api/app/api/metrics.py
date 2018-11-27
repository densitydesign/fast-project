import pandas as pd
from datetime import datetime, timedelta
from flask_restful.reqparse import RequestParser

class MetricsRequests(object):

    parser = RequestParser()

    DEFAULT_LIMIT=10
    DEFAULT_WINDOW="week"

    parser.add_argument('start', type=int)
    parser.add_argument('end', type=int)
    parser.add_argument('window', type=str)

    def parse_args(self):
        args = self.parser.parse_args()

        args.window = args.window if args.window is not None else self.DEFAULT_WINDOW

        return args

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


def compact(*dd):
    return pd.concat([pd.Series(x) for x in dd], axis=1).sum(axis=1).sort_values(ascending=False).head(10).to_dict()

def getFirstWeekDay(ts):
    x = datetime.fromtimestamp(ts)
    return int( ( x.date() - timedelta(days=x.weekday()) ).strftime("%s") )

def getFirstMonthDay(ts):
    x = datetime.fromtimestamp(ts)
    return int((x.date() - timedelta(days=x.day)).strftime("%s"))

aggregation_window = {
    "week": getFirstWeekDay,
    "month": getFirstMonthDay
}

def aggregate_response(json, window="week"):

    df = pd.DataFrame(json).sort_values("date")

    s = df[["ambient", "lifestyle", "fashion"]]

    content = (s.sum() / s.sum().sum()).to_dict()

    agg_func = aggregation_window[window]

    hs = df[df["hashtags"] != 0].set_index("date")["hashtags"]\
        .groupby(lambda x: agg_func(x))\
        .apply(lambda x: compact(*x.values))

    return {
        "dates": [datetime.fromtimestamp(x).strftime("%s") for x in df["date"].values],
        "posts": [int(x) for x in df["posts"].values],
        "likes": [int(x) for x in df["likes"].values],
        "hashtags": {int( week ): hs.loc[week].to_dict() for week in hs.index.levels[0]},
        "content": content
    }


def concat_dicts(*dicts):
    return pd.concat([pd.Series(x) for x in dicts], axis=1).sum(axis=1).to_dict()


