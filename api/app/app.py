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

from flask_restful.reqparse import RequestParser
        
class Post(Resource):
    parser = RequestParser()

    parser.add_argument('start', type=int)
    parser.add_argument('end'  , type=int)
    parser.add_argument('limit', type=int)
    parser.add_argument('content', type=str)
    
    @swag_from("yamls/post.yml")
    def get(self, brand_id):

        args = self.parser.parse_args()

        query = {
                "owner": brand_id
            }
            
        limit = args.limit if (args.limit) else 10

        time_query = {}
        if (args.start):
            time_query["$gte"] = args.start
        if (args.end):
            time_query["$lte"] = args.end
        if len(time_query)>0:
            query["taken_at_timestamp"] = time_query
            
        if (args.content):
            query["main_content"] = args.content

        print(query)
            
        cursor = mongo.db.post.find(query,{"_id": 0}).limit(limit)
        result = list(cursor)
        return jsonify(result)


api = Api(app)
api.add_resource(Brand, "/brands")
api.add_resource(Post, "/posts/<brand_id>", "/posts/<string:brand_id>")

if __name__ == "__main__":
    app.run(debug=True)
