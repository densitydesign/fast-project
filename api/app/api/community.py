from pymongo import DESCENDING
from flask_restful.reqparse import RequestParser

class CommunityGraphRequests(object):

    parser = RequestParser()

    DEFAULT_THRES=0.1
    DEFAULT_LIMIT=10

    parser.add_argument('thres', type=float)
    parser.add_argument('communities', type=str, required=True)
    parser.add_argument('limit', type=int)

    def parse_args(self):
        args = self.parser.parse_args()

        args.thres = args.thres if args.thres is not None else self.DEFAULT_THRES
        args.limit = args.limit if args.limit is not None else self.DEFAULT_LIMIT
        args.communities = args.communities.split(",")

        return args



class CommunityStorage(object):

    def __init__(self, collection):
        self.colleciton = collection
        try:
            self.reload()
        except:
            self.__communities__ = None

    @property
    def communities(self):
        if self.__communities__ is None:
            self.reload()
        return self.__communities__

    @property
    def json(self):
        return [ {"id": k, "hashtags": self.get_hashtags(k, 5), "posts": self.get_posts(k, 5)}
                 for k, v in self.communities.items() ]

    def reload(self):
        cursor = self.colleciton.find(
            {},
            {
                "_id": 0,
                "id": 1,
                "core_hashtags": 1,
                "top_posts": 1
            })
        self.__communities__ = {item["id"]: {"hashtags": item["core_hashtags"], "posts": item["top_posts"]} for item in list(cursor)}
        return self

    def get_community(self, id):
        return self.communities[id]

    def get_hashtags(self, id, n=None):
        return self.get_community(id)["hashtags"][:n]

    def get_posts(self, id, n=None):
        return self.get_community(id)["posts"][:n]


class CommunityGraph(object):

    fields = {"_id": 0, "username": 1, "id_user": 1, "communities": 1,
              "num_posts": 1, "activity": 1, "followers_count": 1}

    def __init__(self, collection, communities=[]):
        self.colleciton = collection
        self.communities = communities

    @property
    def query_exists(self):
        return { "$or": [{"communities.%s" % str(id): {"$exists":True}} for id in self.communities]}

    def query_thres(self, thres):
        return { "$or": [{"communities.%s" % str(id): {"$gte": thres}} for id in self.communities]}


    def __clean_communities__(self, user, thres):
        for community, score in user["communities"].items():
            if (community not in self.communities) or (score < thres):
                _ = user["communities"].pop(community)
        return user

    def graph(self, n=10, thres=0, field="num_posts"):

        users = list(self.colleciton.find(self.query_thres(thres), self.fields).sort([(field, DESCENDING)]).limit(n))

        nodes = [{"label": "community", "id": CommunityGraph.community_id(community)} for community in self.communities]
        edges = []

        for user in users:

            user["label"] = "user"
            user["id"] = CommunityGraph.user_id( user.pop("id_user") )

            communities = user.pop("communities")

            for community, score in communities.items():
                if (community in self.communities) and (score > thres):
                    edges.append( {
                        "source": user["id"],
                        "target": CommunityGraph.community_id(community),
                        "weight": score
                    } )

            nodes.append( user )

        return nodes, edges

    @staticmethod
    def user_id(id):
        return "u" + str(id)

    @staticmethod
    def community_id(id):
        return "c" + str(id)

