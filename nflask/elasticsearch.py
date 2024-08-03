from elasticsearch import Elasticsearch
from nflask.index_generator import generate_index_mapping


def init_elastic(app):
    # Setup elastic search connection
    app.logger.info("Initializing Elasticsearch connection...")

    # Get elastic configuration
    config = app.config['ELASTICSEARCH']

    # Elastic search configurations
    if 'elastic' not in app.__dict__.keys():
        elastic = Elasticsearch(
            hosts=[{'host': config['HOSTS'][0], 'port': config['PORT']}],
            http_compress=config['HTTP_COMPRESS'])

        setattr(app, "elastic", elastic)


def create_index(app, model):
    # Detect index in elastic search
    #print(app.elastic, dir(app.elastic))
    if model.__use_elassandra__:
        index = model.__table_name__
        doc_type = index
    else:
        if model.__elastic_index__ is not None:
            index = model.__elastic_index__
        else:
            index = model.__table_name__
        if model.__elastic_doc_type__ is not None:
            doc_type = model.__elastic_doc_type__
        else:
            doc_type = "_doc"
    
    if not app.elastic.indices.exists(index):
        print(index)
        app.logger.info(
            "Elastic: Index {} not found, creating index...".format(
                index))
        
        settings = generate_index_mapping(model,False)
        
        # Create index
        app.elastic.indices.create(
            index=index,
            ignore=400,
            body=settings)
        
    else:
        app.logger.info(
            "Elastic: Updating index...".format(
                index))
        
        mappings = generate_index_mapping(model,True)
                
        # Update index
        app.elastic.indices.put_mapping(
            index=index,
            doc_type=doc_type,
            ignore=400,
            body=mappings)
