import math
from flask import current_app
from flask_restful.reqparse import RequestParser
from nflask.exceptions import APIError
import base64
from flask import Response
import json
from nflask.utils import node


class ElasticListResourceMixin(object):
    _query_parser = RequestParser()
    query = None
    queryset = None
    payload = None

    def __init__(self):
        # Define elastic instance
        self.elastic_instance = current_app.elastic
        # Define request parser
        self._search_param = getattr(self, 'search_param', 'search')
        self._page_param = getattr(self, 'page_param', 'page')
        self._page_size_param = getattr(self, 'page_size_param', 'pageSize')

        self._query_parser.add_argument(
            self._search_param, type=str, location="args")
        self._query_parser.add_argument(
            self._page_param, type=int, location="args")
        self._query_parser.add_argument(
            self._page_size_param, type=int, location="args")

        # Define initial pagination cursor
        self.cursor = {
            "total": 0,
            "start": 0,
            "pageSize": current_app.config['DEFAULT_PAGE_LIMIT'],
            "page": 1
        }

    def get_total_count(self):
        # Get all data count
        if self.queryset is not None:
            total = self.queryset['hits']['total']
        else:
            all_data = self.elastic_instance.count(
                index=self.elastic_index,
                doc_type=self.elastic_doc_type,
                # body={
                #     "query": self.query
                # }
            )
            # Get total row count
            total = all_data['count']
        self.cursor["total"] = total

        return total

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        else:
            # Define default search query
            self.query = {
                "match_all": {}
            }
            # Define request arguments
            args = self._query_parser.parse_args()
            # Define query when search param is not null
            if args[self._search_param] is not None and args[self._search_param] != '':
                query_param = {
                    "query": "{}".format(args[self._search_param]),
                    "default_operator": "and",
                    "fields": [i for i in self.elastic_search_fields]
                }

                self.query = {
                    "query_string": query_param
                }

            if args[self._page_size_param]:
                self.cursor["pageSize"] = args[self._page_size_param]

            if args[self._page_param] is not None:
                page = args[self._page_param]
                if page == 0:
                    page = 1
                self.cursor["start"] = ((page - 1) * self.cursor["pageSize"])

            # Get data from elastic index
            self.queryset = self.elastic_instance.search(
                index=self.elastic_index,
                doc_type=self.elastic_doc_type,
                body={
                    "from": self.cursor["start"],
                    "size": self.cursor["pageSize"],
                    "query": self.query,
                    "sort": [
                        {
                            "_uid": {
                                "order": "asc"
                            }
                        }
                    ]
                }
            )

            return self.queryset

    def get_payload(self):
        if self.payload:
            return self.payload
        else:
            return None

    # data elasticsearch yang telah diolah akan langsung di paginasi
    def paginator2(self):
        queryset = self.get_queryset()
        total = self.get_total_count()
        payload = self.get_payload()
        # Define filtered count
        filtered = queryset['hits']['total']
        # Define total pages
        #print(filtered)
        pageCount = math.ceil(filtered / self.cursor['pageSize'])

        # Define results
        results = self.queryset['hits']['hits']
        results = results[self.cursor['start']:self.cursor['start']+self.cursor['pageSize']]


        # Raise error if page is greater than total page count
        if pageCount > 0 and self.cursor['page'] > pageCount:
            raise APIError(
                code=400,
                status="PaginationError",
                message="Page exceed total page count")

        return {
            "payload":payload,
            "total": total,
            "filtered": filtered,
            "page": self.cursor['page'],
            "pageCount": pageCount,
            "pageSize": self.cursor['pageSize'],
            "results": results
        }
    def paginator(self):
        queryset = self.get_queryset()
        total = self.get_total_count()
        payload = self.get_payload()
        # Define filtered count
        filtered = queryset['hits']['total']
        # Define total pages
        #print(filtered)
        pageCount = math.ceil(filtered / self.cursor['pageSize'])

        # Define results
        results = list(
            item['_source'] for item in self.queryset['hits']['hits'] if item.get('_source'))
        
        total = len(results)

        # Raise error if page is greater than total page count
        if pageCount > 0 and self.cursor['page'] > pageCount:
            raise APIError(
                code=400,
                status="PaginationError",
                message="Page exceed total page count")

        return {
            "payload":payload,
            "total": total,
            "filtered": filtered,
            "page": self.cursor['page'],
            "pageCount": pageCount,
            "pageSize": self.cursor['pageSize'],
            "results": results
        }

    def get_object(self):
        queryset = self.get_queryset()

        results = list(
            item['_source'] for item in self.queryset['hits']['hits'])

        return {
            "results": results
        }

    def tree_klasifikasi(self):
        queryset = self.get_queryset()

        match_query = {"match_all": {}}

        query = {
            "bool": {
                "must": match_query,
            }
        }

        all_data = self.elastic_instance.search(
            index=self.elastic_index,
            doc_type=self.elastic_doc_type,
            body={
                "from": 0,
                "size": 1000,
                "query": query,
            }
        )

        raw = list(
            item['_source'] for item in all_data['hits']['hits'])

        nodes = dict((e["id"], node(e)) for e in raw)
        for e in raw:
            if e["parent_id"] is not None:
                nodes[e["parent_id"]].add_child(nodes[e["id"]])

        roots = [n for n in nodes.values() if n.value["parent_id"] is None]

        raw = json.dumps(roots, default=lambda o: o.__dict__,
            sort_keys=False, indent=4)

        result = json.loads(raw)

        args = self._query_parser.parse_args()
        hasil = []

        if args[self._search_param] is not None:
            for data in result:
                if args[self._search_param] in data['value']['nama'].lower():
                    hasil.append(data)
                else:
                    hasil = hasil
        else:
            hasil = result

        return hasil


class ElasticDetailResourceMixin(object):

    def __init__(self):
        # Define elastic instance
        self.elastic_instance = current_app.elastic

    def get_object(self, id=None):
        # Get single data from elastic search
        data = self.elastic_instance.get(
            index=self.elastic_index,
            doc_type=self.elastic_doc_type,
            id=id
        )
        # Return data
        return data['_source']

    def get_image(self, id=None):
        # Get single data from elastic search
        data = self.elastic_instance.get(
            index=self.elastic_index,
            doc_type=self.elastic_doc_type,
            id=id
        )
        # Return data
        raw = base64.b64decode(data['_source']['blob'])
        r = Response(response=raw, status=200, mimetype="image/jpg")
        r.headers["Content-Type"] = "image/jpg"

        return r


class PaginatorResourceMixin(object):
    _query_parser = RequestParser()
    query = None
    queryset = None
    payload = None

    def __init__(self):
        self._search_param = getattr(self, 'search_param', 'search')
        self._page_param = getattr(self, 'page_param', 'page')
        self._page_size_param = getattr(self, 'page_size_param', 'pageSize')

        self._query_parser.add_argument(
            self._search_param, type=str, location="args")
        self._query_parser.add_argument(
            self._page_param, type=int, location="args")
        self._query_parser.add_argument(
            self._page_size_param, type=int, location="args")

        self.cursor = {
            "total": 0,
            "start": 0,
            "pageSize": current_app.config['DEFAULT_PAGE_LIMIT'],
            "page": 1
        }

    def get_count(self):
        if self.queryset is not None:
            total = len(self.queryset)

        return total

    def paginator(self):
        total = self.get_count()
        payload = self.payload if self.payload else None
        # Define filtered count
        #filtered = queryset['hits']['total']
        # Define total pages
        #print(filtered)
        pageCount = math.ceil(total / self.cursor['pageSize'])

        # Define results
        results = self.queryset[self.cursor['start']:self.cursor['start']+self.cursor['pageSize']]

        # Raise error if page is greater than total page count
        if pageCount > 0 and self.cursor['page'] > pageCount:
            raise APIError(
                code=400,
                status="PaginationError",
                message="Page exceed total page count")
        return {
            "total": total,
            "payload":payload,
            # "filtered": filtered,
            "page": self.cursor['page'],
            "pageCount": pageCount,
            "pageSize": self.cursor['pageSize'],
            "results": results
        }


# class AllSourceMixin(ElasticListResourceMixin):

#     def __init__(self):
#         # Define request parser
#         self.elastic_instance = current_app.elastic
#         # Define request parser
#         self._search_param = getattr(self, 'search_param', 'search')
#         self._page_param = getattr(self, 'page_param', 'page')
#         self._page_size_param = getattr(self, 'page_size_param', 'pageSize')
#         self._start_date_param = getattr(self, 'start_date_param', 'startDate')
#         self._end_date_param = getattr(self, 'end_date_param', 'endDate') 

#         self._query_parser.add_argument(
#             self._search_param, type=str, location="args")
#         self._query_parser.add_argument(
#             self._page_param, type=int, location="args")
#         self._query_parser.add_argument(
#             self._page_size_param, type=int, location="args")
#         self._query_parser.add_argument(
#             self._start_date_param, type=str, location="args")
#         self._query_parser.add_argument(
#             self._end_date_param, type=str, location='args')
        
#         # Define initial pagination cursor
#         self.cursor = {
#             "total": 0,
#             "start": 0,
#             "pageSize": current_app.config['DEFAULT_PAGE_LIMIT'],
#             "page": 1
#         }



#     def get_queryset(self):
#         if self.queryset is not None:
#             return self.queryset
#         else:
#             # Define default search query
#             self.query = {
#                 "match_all": {}
#             }
#             # Define request arguments
#             args = self._query_parser.parse_args()
#             # Define query when search param is not null
#             if args[self._search_param] is not None and args[self._search_param] != '':
#                 query_param = {
#                     "query": "{}".format(args[self._search_param]),
#                     "default_operator": "and",
#                     "fields": [i for i in self.elastic_search_fields]
#                 }

#                 self.query = {
#                     "query_string": query_param
#                 }

#             if args[self._page_size_param]:
#                 self.cursor["pageSize"] = args[self._page_size_param]

#             if args[self._page_param] is not None:
#                 page = args[self._page_param]
#                 if page == 0:
#                     page = 1
#                 self.cursor["start"] = ((page - 1) * self.cursor["pageSize"])

#             # Get data from elastic index
#             self.queryset = self.elastic_instance.search(
#                 index=self.elastic_twitter_index,
#                 doc_type=self.elastic_doc_type,
#                 body={
#                     "from": self.cursor["start"],
#                     "size": self.cursor["pageSize"],
#                     "query": self.query,
#                     # "sort": [
#                     #     {
#                     #         "_uid": {
#                     #             "order": "asc"
#                     #         }
#                     #     }
#                     # ]
#                 }
#             )['hits']['hits']

#             self.queryset.append(
#                 self.elastic_instance.search(
#                 index=self.elastic_instagram_index,
#                 doc_type=self.elastic_doc_type,
#                 body={
#                     "from": self.cursor["start"],
#                     "size": self.cursor["pageSize"],
#                     "query": self.query,
#                 }
#                 )['hits']['hits']
#             )

#             self.queryset.append(
#                 self.elastic_instance.search(
#                 index=self.elastic_news_index,
#                 doc_type=self.elastic_doc_type,
#                 body={
#                     "from": self.cursor["start"],
#                     "size": self.cursor["pageSize"],
#                     "query": self.query,
#                     # "sort": [
#                     #     {
#                     #         "_uid": {
#                     #             "order": "asc"
#                     #         }
#                     #     }
#                     # ]
#                 }
#             )['hits']['hits']
            
#             )

#             self.queryset = [item for sublist in self.queryset for item in sublist]

#             return self.queryset
    
#     def get_total_count(self):
#         # Get all data count
#         if self.queryset is not None:
#             total = len(self.queryset)
#         else:
#             twitter_count = self.elastic_instance.count(
#                 index=self.elastic_twitter_index,
#                 doc_type=self.elastic_doc_type,
#                 # body={
#                 #     "query": self.query
#                 # }
#             )['count']
#             # Get total row count
#             instagram_count = self.elastic_instance.count(
#                 index=self.elastic_instagram_index,
#                 doc_type=self.elastic_doc_type,
#                 # body={
#                 #     "query": self.query
#                 # }
#             )['count']
#             news_count = self.elastic_instance.count(
#                 index=self.elastic_news_index,
#                 doc_type=self.elastic_doc_type,
#                 # body={
#                 #     "query": self.query
#                 # }
#             )['count']

#             total = twitter_count + instagram_count + news_count
#         self.cursor["total"] = total

#         return total


#     def paginator(self):
#         queryset = self.get_queryset()
#         total = self.get_total_count()
#         # Define filtered count
#         filtered = len(queryset)
#         # Define total pages
#         #print(filtered)
#         pageCount = math.ceil(filtered / self.cursor['pageSize'])

#         # Define results
#         results = [item['_source'] for item in self.queryset]

#         # Raise error if page is greater than total page count
#         if pageCount > 0 and self.cursor['page'] > pageCount:
#             raise APIError(
#                 code=400,
#                 status="PaginationError",
#                 message="Page exceed total page count")

#         return {
#             "total": total,
#             "filtered": filtered,
#             "page": self.cursor['page'],
#             "pageCount": pageCount,
#             "pageSize": self.cursor['pageSize'],
#             "results": results
#         }
