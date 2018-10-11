from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from
from flask_cors import CORS
from flask import request

app = Flask(__name__)
swagger = Swagger(app)
app.config["MONGO_DBNAME"] = "FaST"
mongo = PyMongo(app, config_prefix='MONGO')
APP_URL = "http://127.0.0.1:5000"

# Configure app
CORS(app)


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

from api.posts import PostRequests, build_query, parse_coords

class Post(Resource, PostRequests):

    @swag_from("yamls/post.yml")
    def get(self, brand_id):

        args = self.parse_args()

        query = build_query(args, {"owner": brand_id})
            
        print(query)

        cursor = mongo.db.post.find(query, {"_id": 0}).limit(args.limit)

        return jsonify(list(map(parse_coords(args.competitor), cursor)))

api = Api(app)
api.add_resource(Brand, "/brands")
api.add_resource(Post, "/posts/<brand_id>", "/posts/<string:brand_id>")

if __name__ == "__main__":
    app.run(debug=True)
