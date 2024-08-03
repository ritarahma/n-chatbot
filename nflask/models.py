"""Models."""

from flask import current_app as app
from cassandra.cqlengine.models import Model as CassandraModel


class Model(CassandraModel):
    """Models."""

    __abstract__ = True
    __use_elastic__ = False
    __use_elassandra__ = False
    __elastic_index__ = None
    __elastic_doc_type__ = None
    __elastic_settings__ = None
    __elastic_custom_mappings__ = None
    __elastic_query_by_id__ = True

    def __init__(self, *args, **kwargs):
        """Models."""
        super(Model, self).__init__(*args, **kwargs)
        _use_elastic = getattr(self, "__use_elastic__", False)
        _use_elassandra = getattr(self, "__use_elassandra__", False)
        _elastic_index = getattr(self, "__elastic_index__", None)
        _elastic_doc_type = getattr(self, "__elastic_doc_type__", None)
        self.elastic_ops = _use_elastic is not False and \
            _elastic_index is not None and \
            _elastic_doc_type is not None
        self.elassandra_ops = _use_elassandra is not False and \
            _elastic_index is not None

    def save(self):
        """Save model to db."""
        saved = super(Model, self).save()
        if self.elastic_ops:
            self.create_index()

        return saved

    def update(self, **kwargs):
        """Update model to db."""
        elastic_query = kwargs.pop("elastic_query", None)
        saved = super(Model, self).update(**kwargs)
        is_deleted = getattr(saved, "is_deleted", False)
        if self.elastic_ops or self.elassandra_ops:
            if is_deleted:
                if self.__elastic_query_by_id__:
                    self.delete_index(id=saved.id)
                else:
                    self.delete_index_by_query(
                        query=elastic_query)
        if self.elastic_ops:
            if not is_deleted:
                self.update_index(id=saved.id)

        return saved

    def delete(self, **kwargs):
        """Delete data in elasticsearh."""
        elastic_query = kwargs.pop("elastic_query", None)
        # Delete model from db
        super(Model, self).delete()
        if self.elastic_ops:
            if self.__elastic_query_by_id__:
                # Get model id
                id = self.id
                self.delete_index(id=id)
            else:
                self.delete_index_by_query(query=elastic_query)

    def create_index(self):
        """Method to create elasticsearch index."""
        app.logger.debug("Creating {} index".format(
            self.__elastic_index__))
        if self.__use_elassandra__:
            doc_type = self.__elastic_index__
        else:
            doc_type = self.__elastic_doc_type__
        if self.__elastic_query_by_id__:
            app.elastic.index(
                refresh=True,
                index=self.__elastic_index__,
                doc_type=doc_type,
                id=str(self.id),
                body=self.to_dict())
        else:
            app.elastic.index(
                refresh=True,
                index=self.__elastic_index__,
                doc_type=doc_type,
                body=self.to_dict())

    def update_index(self, id=None):
        """Method to update elasticsearch index."""
        if self.__use_elassandra__:
            doc_type = self.__elastic_index__
        else:
            doc_type = self.__elastic_doc_type__
        if id is not None:
            app.logger.debug("Updating {} index".format(
                self.__elastic_index__))
            app.elastic.update(
                refresh=True,
                index=self.__elastic_index__,
                doc_type=doc_type,
                id=str(id),
                body=dict(
                    doc=self.to_dict()))

    def delete_index(self, id=None):
        """Method to delete elasticsearch index."""
        if self.__use_elassandra__:
            doc_type = self.__elastic_index__
        else:
            doc_type = self.__elastic_doc_type__
        if id is not None:
            app.logger.debug("Deleting {} index".format(
                self.__elastic_index__))
            app.elastic.delete(
                refresh=True,
                index=self.__elastic_index__,
                doc_type=doc_type,
                id=str(id))

    def delete_index_by_query(self, query=None):
        """Method to delete elasticsearch index by query."""
        if self.__use_elassandra__:
            doc_type = self.__elastic_index__
        else:
            doc_type = self.__elastic_doc_type__
        if query is not None:
            app.logger.debug("Deleting {} index by query".format(
                self.__elastic_index__))
            app.elastic.delete_by_query(
                refresh=True,
                index=self.__elastic_index__,
                doc_type=doc_type,
                body=query)

    # @classmethod
    def to_dict(self):
        """"To dict."""
        return {}
