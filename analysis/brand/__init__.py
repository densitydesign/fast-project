from copy import deepcopy as copy
from collections import Mapping

from datetime import datetime
from itertools import islice

def groupIterable(iterable, batch_size=10000):
    iterable = iter(iterable)
    return iter(lambda: list(islice(iterable, batch_size)), [])


def dateGroupByKey(field):
    return {
        "year" : {"$year": field} ,
        "month": {"$month": field},
        "day"  : {"$dayOfMonth": field}
    }


def get_date(df):
    return df["_id"].apply(
        lambda x: int(datetime.strptime("%04d%02d%02d" % (x["year"], x["month"], x["day"]), "%Y%m%d").strftime("%s"))
    )

def union(*dicts):
    def __dict_merge(dct, merge_dct):
        merged = copy(dct)
        for k, v in merge_dct.iteritems():
            if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], Mapping)):
                merged[k] = __dict_merge(dct[k], merge_dct[k])
            else:
                merged[k] = merge_dct[k]
        return merged

    return reduce(__dict_merge, dicts)
