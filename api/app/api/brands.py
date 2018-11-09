import pandas as pd
from datetime import datetime
from flask_restful.reqparse import RequestParser


class BrandsStorage(object):

    def __init__(self, collection):
        self.colleciton = collection
        try:
            self.reload()
        except:
            self.__brands__ = None

    @property
    def brands(self):
        if self.__brands__ is None:
            self.reload()
        return self.__brands__

    @property
    def inverse_brands(self):
        return {v: k for k, v in self.brands.items()}

    @property
    def json(self):
        return [ {"id_user": k, "username": v} for k, v in self.brands.items() ]

    def reload(self):
        cursor = self.colleciton.find(
            {},
            {
                "_id": 0,
                "id_user": 1,
                "username": 1
            })
        self.__brands__ = {item["id_user"]: item["username"] for item in list(cursor)}
        return self

    def get_name(self, id):
        return self.brands[id]

    def get_id(self, name):
        return self.inverse_brands[name]
