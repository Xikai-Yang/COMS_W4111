from pymongo import MongoClient
from .base_data_service import BaseDataService


class MongoDBDataService(BaseDataService):
    def __init__(self, config_info):
        super(MongoDBDataService, self).__init__(config_info)

    def _get_connection(self):
        if self.connection is None:
            db_url = self.config_info.db_url
            self.connection = MongoClient(db_url)
        return self.connection


    def _close_connection(self):
        pass

    def _get_collection(self, collection_name):
        conn = self._get_connection()
        coll = conn[self.config_info.db_name][collection_name]
        return coll

    def _get_db(self):
        conn = self._get_connection()
        result = conn[self.config_info.db_name]
        return result

    def get_by_template(self, collection_name, template=None, field_list=None):
        project_c = None
        if field_list:
            project_c = dict()
            for f in field_list:
                project_c[f] = 1
        coll = self._get_collection(collection_name)
        result = coll.find(template, project_c)
        result = list(result)
        return result


    def list_resources(self):
        db = self._get_db()
        result = list(db.list_collection_names())
        return result

    def run_aggregation(self,
                        collection_name,
                        pipeline):
        coll = self._get_collection(collection_name)
        result = coll.aggregate(pipeline)
        result = list(result)
        return result



