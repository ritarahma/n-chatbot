import os
from flask import Flask
from flask_cors import CORS
from nflask.api import Api
from nflask.elasticsearch import init_elastic
from nflask.redis import init_redis
from nflask.lemmatizer import init
from nflask.mysqlconn import init_db
#from nflask.cassandra import init_db, sync_db

import json


class Nflask(Flask):
    def __init__(self, import_name=__package__, *args, **kwargs):
        # Initialize default flask __init__
        super(Nflask, self).__init__(import_name, *args, **kwargs)
        # Initialize flask config
        self.config.from_object("config")
        self.logger.info("Initializing nflask...")
        # Initialize CORS
        CORS(self)
        # Initialize Flask Restful
        self.Api = Api(self)
        # Initialize Elasticsearch
        init_elastic(self)
        # Initialize Redis
        init_redis(self)
        # Initialize modules from configured modules dir
        self.init_modules(self.config['MODULES_DIR'])
        #initialize mysql
        init_db(self)

    def init_modules(self, prefix):
        # Method to read modules dir
        # Don't load if it ends with .py and folder name
        # is __pycache__ and .gitkeep
        # self.logger.info("Initializing Modules...")
        filelist = list(
            '{}/{}'.format(
                prefix, folder
            ) for folder in os.listdir(prefix)
            if not folder.endswith('.py') and
            folder != "__pycache__" and
            folder != ".gitkeep" and
            folder != ".DS_Store")

        # Register into app blueprint
        self.register_modules(filelist, prefix)

    def register_modules(self, files, base):
        # Method to register into app blueprint
        from nflask.loaders import import_modules
        from nflask.routes import register_resources
        # from nflask.elasticsearch import create_index
        # Load imported modules
        imported_modules = list(import_modules(self, file) for file in files)

        for module in imported_modules:
            # Only load module if it is not None and don't have subfolder
            if module is not None:
                # Get module name for prefix
                name = module.__name__.replace("_", "-")
                prefix = "/api/{}".format(name)
                # Get module resources
                resources = getattr(
                    module, self.config['RESOURCES_OBJECT'], None)

                # Load resources if resources it's found in module
                if resources is not None:
                    # Register into Root Blueprint
                    register_resources(
                        self, self.Api, resources, prefix=prefix)
                else:
                    # module have subfolder
                    sub_filelist = list(
                    '{}/{}/{}'.format(
                        base, name, folder
                    ) for folder in os.listdir('{}/{}'.format(base, name))
                    if not folder.endswith('.py') and
                    folder != "__pycache__" and
                    folder != ".gitkeep" and
                    folder != ".DS_Store")
                    
                    self.register_sub_modules(sub_filelist, name)

    def register_sub_modules(self, files, base):
        # Method to register into app blueprint
        from nflask.loaders import import_modules
        from nflask.routes import register_resources

        # Load imported modules
        imported_modules = list(import_modules(self, file) for file in files)

        for module in imported_modules:
            # Only load module if it is not None
            if module is not None:
                # Get module name for prefix
                name = module.__name__.replace("_", "-")
                prefix = "/api/{}/{}".format(base,name)
                # print(name, base)
                # Get module resources
                resources = getattr(
                    module, self.config['RESOURCES_OBJECT'], None)

                # Load resources if resources it's found in module
                if resources is not None:
                    # Register into Root Blueprint
                    register_resources(
                        self, self.Api, resources, prefix=prefix)


    def run(self, *args, **kwargs):
        self.logger.info("nflask is running...")
        super(Nflask, self).run(*args, **kwargs)
