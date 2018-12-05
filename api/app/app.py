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

from api.community import CommunityStorage, CommunityGraph, CommunityGraphRequests, \
    CommunityMetricsRequests, CommunityMetrics

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

from abc import abstractproperty

class CommunitiesMetrics(CommunityMetricsRequests):

    @abstractproperty
    def type(self):
        return ""

    def get(self, community_id, brand_id):
        args = self.parse_args()

        metrics = CommunityMetrics(mongo.db.stats)

        storage = BrandsStorage(mongo.db.brand)

        if (args.start):
            metrics.set_start(args.start)\

        if (args.end):
            metrics.set_end(args.end)

        brand_name = storage.get_name(brand_id)

        entities = metrics.get_entities(community=community_id,
                                        type=self.type,
                                        brand=brand_name,
                                        top=args.limit, filter_size=args.complexity)

        size = metrics.size(brand=brand_name)

        return {"posts": size, self.type: dict(entities)}

class CommunitiesHashtags(Resource, CommunitiesMetrics):

    @property
    def type(self):
        return "hashtags"

class CommunitiesMentions(Resource, CommunitiesMetrics):

    @property
    def type(self):
        return "mentions"

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

        cursor = mongo.db.stats.find(query,{"_id": 0, "communities": 0})

        return jsonify( aggregate_response( list( cursor ), args.window ) )


api = Api(app)
api.add_resource(Brand, "/brands")
api.add_resource(Community, "/communities")
api.add_resource(CommunitiesGraph, "/communities/graph")

api.add_resource(CommunitiesHashtags, "/communities/<community_id>/<brand_id>/hashtags",
                 "/communities/<string:community_id>/<int:brand_id>/hashtags")
api.add_resource(CommunitiesMentions, "/communities/<community_id>/<brand_id>/mentions",
                 "/communities/<string:community_id>/<int:brand_id>/mentions")

api.add_resource(Post, "/posts/<brand_id>", "/posts/<string:brand_id>")
api.add_resource(Metrics, "/metrics/<brand_id>", "/metrics/<string:brand_id>")

if __name__ == "__main__":
    app.run(debug=True)
