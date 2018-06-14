from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from


app = Flask(__name__)
swagger = Swagger(app)
app.config["MONGO_DBNAME"] = "FaST"
mongo = PyMongo(app, config_prefix='MONGO')
APP_URL = "http://127.0.0.1:5000"


class Brand(Resource):
    @swag_from("yamls/brands.yml")
    def get(self):
        cursor = mongo.db.brand.find(
            {},
            {
             "_id": 0,
             "id_user": 1,
             "username": 1
            })
        result = list(cursor)
        return jsonify(result)


class Post(Resource):
    @swag_from("yamls/post.yml")
    def get(self, brand_id):
        cursor = mongo.db.post.find(
            {
                "owner": brand_id
            },
            {
                "_id": 0
            })
        result = list(cursor)
        return jsonify(result)


api = Api(app)
api.add_resource(Brand, "/brands")
api.add_resource(Post, "/posts/<string:brand_id>")


if __name__ == "__main__":
    app.run(debug=True)
