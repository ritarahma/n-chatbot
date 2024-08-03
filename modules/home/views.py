import json
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
# import mysql


class Root(Resource):
    parser = RequestParser()
    parser.add_argument(
        'data', type=str, location='json',
        help="data required", required=True)

    def get(self):
        return {
            "version": "v1 - Development",
            "description": "NChatbot"
        }