from config import CASSANDRA_KEYSPACE
settings = {
    "number_of_shards": 1,
    "number_of_replicas": 0
}
settings_elassandra = {
    "keyspace" : CASSANDRA_KEYSPACE,
    "number_of_shards": 1,
    "number_of_replicas": 0
}
analyzerSettings = {
     "number_of_shards": 1,
        "analysis": {
            "filter": {
                "autocomplete_filter": {
                    "type": "edge_ngram",
                    "min_gram": 1,
                    "max_gram": 50
                }
            },
            "analyzer": {
                "autocomplete": {
                    "type": "custom",
                    "tokenizer": "keyword",
                    "filter": [
                        "lowercase",
                        "autocomplete_filter"
                    ]
                },
                "patternmatch": {
                    "type": "custom",
                    "tokenizer": "pattern",
                    "pattern": "_"
                }
            }
        }
    }
mappings = {
    "id": {
        "type": "text"
    },
    "created_by_id": {
        "type": "text"
    },
    "created_by_email": {
        "type": "text"
    },
    "created_date": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss"
    },
    "updated_by_id": {
        "type": "text"
    },
    "updated_by_email": {
        "type": "text"
    },
    "updated_date": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss"
    },
    "deleted_by_id": {
        "type": "text"
    },
    "deleted_by_email": {
        "type": "text"
    },
    "deleted_date": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss"
    }
}
