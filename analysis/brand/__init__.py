
from itertools import islice

def groupIterable(iterable, batch_size=10000):
    iterable = iter(iterable)
    return iter(lambda: list(islice(iterable, batch_size)), [])
