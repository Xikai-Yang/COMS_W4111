from abc import ABC, abstractmethod
import copy


class BaseDataService(ABC):
    """
    need to implement two sub-classes for it, one for mongo, one for neo4j
    """
    def __init__(self, config_info):
        self.config_info = copy.deepcopy(config_info)
        self.connection = None

    @abstractmethod
    def _get_connection(self):
        pass

    @abstractmethod
    def _close_connection(self):
        pass

    @abstractmethod
    def get_by_template(self,
                        collection_name,
                        template = None,
                        field_list = None):
        pass

    @abstractmethod
    def list_resources(self):
        pass