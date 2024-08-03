## Cassandra to Elasticsearch Index Mapping generator
## Reference: https://elassandra.readthedocs.io/en/latest/mapping.html

from nflask.mixins.elastic import settings as settings_elastic, settings_elassandra

def get_model_columns(Model):
    colkey = Model._columns.keys()
    fields = []
    for col in colkey:
        fields.append({'name' : col, 'type' : Model._columns.get(col).db_type})
    return fields

def cql_to_elastic_type_mapping(name, coltype, elassandra = False):
    if coltype == 'text':
        if elassandra:
            return {name : {"type": "text","cql_collection":"singleton"}}
        else:
            return {name : {"type": "text"}}
    elif coltype == 'timestamp':
        if elassandra:
            return {name : {"type": "date","format": "yyyy-MM-dd HH:mm:ss","cql_collection":"singleton"}}
        else:
            return {name : {"type": "date","format": "yyyy-MM-dd HH:mm:ss"}}
    elif coltype == 'date':
        if elassandra:
            return {name : {"type": "date","format": "yyyy-MM-dd","cql_collection":"singleton"}}
        else:
            return {name : {"type": "date","format": "yyyy-MM-dd"}}
    elif coltype == 'boolean':
        if elassandra:
            return {name : {"type": "boolean","cql_collection":"singleton"}}
        else:
            return {name : {"type": "boolean"}}
    elif coltype == 'uuid':
        if elassandra:
            return {name : {"type": "keyword","cql_collection":"singleton"}}
        else:
            return {name : {"type": "keyword"}}
    elif coltype == 'int':
        if elassandra:
            return {name : {"type": "integer","cql_collection":"singleton"}}
        else:
            return {name : {"type": "integer"}}
    elif coltype == 'bigint':
        if elassandra:
            return {name : {"type": "long","cql_collection":"singleton"}}
        else:
            return {name : {"type": "long"}}
    elif coltype == 'tinyint':
        if elassandra:
            return {name : {"type": "byte","cql_collection":"singleton"}}
        else:
            return {name : {"type": "byte"}}
    elif coltype == 'smallint':
        if elassandra:
            return {name : {"type": "short","cql_collection":"singleton"}}
        else:
            return {name : {"type": "short"}}
    elif coltype == 'double':
        if elassandra:
            return {name : {"type": "double","cql_collection":"singleton"}}
        else:
            return {name : {"type": "double"}}
    elif coltype == 'float':
        if elassandra:
            return {name : {"type": "float","cql_collection":"singleton"}}
        else:
            return {name : {"type": "float"}}
    elif coltype == 'decimal':
        if elassandra:
            return {name : {"type": "keyword","cql_collection":"singleton"}}
        else:
            return {name : {"type": "keyword"}}
    elif coltype == 'inet':
        if elassandra:
            return {name : {"type": "ip","cql_collection":"singleton"}}
        else:
            return {name : {"type": "ip"}}
    elif coltype == 'blob':
        if elassandra:
            return {name : {"type": "binary","cql_collection":"singleton"}}
        else:
            return {name : {"type": "binary"}}
    elif coltype == 'keyword':
        if elassandra:
            return {name : {"type": "keyword","cql_collection":"singleton"}}
        else:
            return {name : {"type": "keyword"}}
    else:
        if elassandra:
            return {name : {"type": "keyword","cql_collection":"singleton"}}
        else:
            return {name : {"type": "keyword"}}

def generate_index_mapping(Model, properties_only = False):
    columns = get_model_columns(Model)
    if Model.__use_elassandra__:
        doc_type = Model.__elastic_index__
        settings = settings_elassandra
    elif Model.__use_elastic__:
        doc_type = Model.__elastic_doc_type__
        settings = settings_elastic
    else:
        return None
    custom_mappings = Model.__elastic_custom_mappings__
    properties = {}
    for col in columns:
        types = cql_to_elastic_type_mapping(col['name'],col['type'],Model.__use_elassandra__)
        properties = {**properties,**types}
    if custom_mappings is not None and isinstance(custom_mappings,dict):
        print("masuk custom mappings")
        for k,v in custom_mappings.items():
            types = cql_to_elastic_type_mapping(k,v,Model.__use_elassandra__)
            if k in properties:
                properties[k] = types[k]
            else:
                properties = {**properties,**types}
    print("masuk custom mappings")
    if properties_only:
        elastic_mappings = {"properties": properties}
    else:
        elastic_mappings = {
                "settings": settings,
                "mappings": {
                    doc_type: {
                        "properties": properties
                    }
                }
            }
    return elastic_mappings