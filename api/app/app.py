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

from api.brands import BrandsStorage

class Brand(Resource):

    @swag_from("yamls/brands.yml")
    def get(self):
        storage = BrandsStorage(mongo.db.brand)
        return jsonify(storage.reload().json)

from api.community import CommunityStorage, CommunityGraph, CommunityGraphRequests

class Community(Resource):

    def get(self):
        storage = CommunityStorage(mongo.db.community)
        return jsonify(storage.reload().json)


class CommunitiesGraph(Resource, CommunityGraphRequests):

    def get(self):
        args = self.parse_args()

        nodes, edges = CommunityGraph(mongo.db.user, args.communities).graph(args.limit, args.thres)

        return jsonify({
            "nodes": nodes,
            "edges": edges
        })


from api.posts import PostRequests, build_query as post_query, parse_coords

class Post(Resource, PostRequests):

    @swag_from("yamls/post.yml")
    def get(self, brand_id):

        args = self.parse_args()

        query = post_query(args, {"owner": brand_id})
            
        print(query)

        cursor = mongo.db.post.find(query, {"_id": 0}).limit(args.limit)
        storage = BrandsStorage(mongo.db.brand)

        f = parse_coords(storage.get_name(args.competitor) if (args.competitor) else None)

        return jsonify([ f(x) for x in cursor])

from api.metrics import MetricsRequests, build_query as metric_query, aggregate_response

class Metrics(Resource, MetricsRequests):

    def get(self, brand_id):
        args = self.parse_args()

        storage = BrandsStorage(mongo.db.brand)
        print(storage.brands)
        query = metric_query(args, {"brand": storage.get_name(int(brand_id))})

        print(query)

        cursor = mongo.db.stats.find(query,{"_id": 0})

        return jsonify( aggregate_response( list( cursor ) ) )


api = Api(app)
api.add_resource(Brand, "/brands")
api.add_resource(Community, "/communities")
api.add_resource(CommunitiesGraph, "/communities/graph")
api.add_resource(Post, "/posts/<brand_id>", "/posts/<string:brand_id>")
api.add_resource(Metrics, "/metrics/<brand_id>", "/metrics/<string:brand_id>")

if __name__ == "__main__":
    app.run(debug=True)
