from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from flasgger import Swagger


app = Flask(__name__)
swagger = Swagger(app)
app.config["MONGO_DBNAME"] = "FaST"
mongo = PyMongo(app, config_prefix='MONGO')
APP_URL = "http://127.0.0.1:5000"


class Brand(Resource):
    def get(self):
        """
        Returns a list of available brands
        ---
        responses:
          200:
            description: A list of available brands
            schema:
              id: Brand
              properties:
                username:
                  type: string
                  description: The name of the brand
                id_user:
                  type: number
                  description: The id of the brand
         """
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
    def get(self, brand_id):
        """
        Returns all the Posts of the given brand
        ---
        parameters:
          - name: brand_id
            in: path
            type: number
            required: true
        responses:
          200:
            description: A list of Posts of the given brand
            schema:
              id: Post
              properties:
                id_post:
                  type: string
                  description: The id of the post
                caption:
                  type: string
                  description: The caption of the post
                comment_count:
                  type: integer
                  description: The number of comments on the post
                imagetag:
                  type: array
                  description: An array of tags along with their confidence
                  items:
                    type: object
                    properties:
                      concept:
                        type: string
                        description: A concept
                      confidence:
                        type: string
                        description: the confidence of this concept
                imagevector:
                  type: string
                  description: A string including the vector representing the k-dimensional embedding of this post
                "is_video":
                  type: string
                  description: A string "True" or "False" including a boolean value of whether this post includes a video
                "likes_count":
                  type: string
                  description: The number of likes given to this post
                "link_post":
                  type: string
                  description: The url to this post
                "location":
                  type: object
                  properties:
                    id_location:
                      type: string
                      description: The id of the location of this post
                    location:
                      type: string
                      description: The location of this post
                "owner":
                  type: string
                  description: A string including a number that represnts the user_id
                "postcoord":
                  type: array
                  description: The pair of coordinates to embed this post into the plane
                  items:
                    type: string
                  minItems: 2
                  maxItems: 2
                "shortcode":
                  type: string
                  description: No idea
                "taken_at_time":
                  type: string
                  description: The date and time at which this post was taken from the web
                "taken_at_timestamp":
                  type: string
                  description: The timestamp at which this post was taken from the web
                "url_img":
                  type: string
                  description: The url of the image embedded in this post
                "username":
                  type: string
                  description: The username of the brand
                "video_count":
                  type: string
                  description: The number of videos
         """
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
