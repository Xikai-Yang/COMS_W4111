from src.resources.mongo_data_service import MongoDBDataService
from src.resources.seasons_resource import SeasonsResource
from src.resources.neo4j_data_service import Neo4jDataService
from src.resources.episodes_resource import EpisodesResource
from src.resources.scenes_resource import ScenesResource
from src.resources.person_resource import PersonResource
from src.resources.movie_resource import MovieResource


class MongoDBDataServiceConfig:
    def __init__(self, db_url, db_name):
        self.db_url = db_url
        self.db_name = db_name


class Neo4jDataServiceConfig:
    def __init__(self, db_url, auth):
        self.db_url = db_url
        self.auth = auth

class PersonResourceConfig:
    def __init__(self, data_service, collection_name, relationship_name=None):
        self.data_service = data_service
        self.collection_name = collection_name
        self.relationship_name = relationship_name

class MovieResourceConfig:
    def __init__(self, data_service, collection_name, relationship_name=None):
        self.data_service = data_service
        self.collection_name = collection_name
        self.relationship_name = relationship_name

class SeasonResourceConfig:
    def __init__(self, data_service, collection_name):
        self.data_service = data_service
        self.collection_name = collection_name

class EpisodesResourceConfig:
    def __init__(self, data_service, collection_name):
        self.data_service = data_service
        self.collection_name = collection_name

class ScenesResourceConfig:
    def __init__(self, data_service, collection_name):
        self.data_service = data_service
        self.collection_name = collection_name


class ServiceFactory:
    def __init__(self):
        self.mongo_db_svc_config = MongoDBDataServiceConfig(
            "mongodb+srv://mongodb:WaaJt2wO9oARr3Sp@cluster0.jfvxi.mongodb.net/mongodb?retryWrites=true&w=majority",
            "GoT"
        )
        self.mongo_db_service = MongoDBDataService(self.mongo_db_svc_config)
        self.season_service_config = SeasonResourceConfig(self.mongo_db_service, "episodes")
        self.season_resource = SeasonsResource(self.season_service_config)

        self.episodes_service_config = EpisodesResourceConfig(self.mongo_db_service, "episodes")
        self.episodes_resource = EpisodesResource(self.episodes_service_config)

        self.scenes_service_config = ScenesResourceConfig(self.mongo_db_service, "episodes")
        self.scenes_resource = ScenesResource(self.scenes_service_config)

        self.neo4j_db_svc_config = Neo4jDataServiceConfig(
            "neo4j+s://ab499b93.databases.neo4j.io:7687",
            ("neo4j", "RQ_kEnQW6IywSy8hYw0BDytdvb4fXsYq6OeGj3c3pmc")
        )
        self.neo4j_db_service = Neo4jDataService(self.neo4j_db_svc_config)

        self.person_service_config = PersonResourceConfig(self.neo4j_db_service, "Person")
        self.person_resource = PersonResource(self.person_service_config)

        self.movie_service_config = MovieResourceConfig(self.neo4j_db_service, "Movie")
        self.movie_resource = MovieResource(self.movie_service_config)

        self.acted_in_service_config = MovieResourceConfig(self.neo4j_db_service, "Movie", "ACTED_IN")
        self.acted_in_resource = MovieResource(self.acted_in_service_config)

    def get(self, resource_name, default=None):
        if resource_name == "seasons":
            result = self.season_resource
        elif resource_name == "episodes":
            result = self.episodes_resource
        elif resource_name == "scenes":
            result = self.scenes_resource
        elif resource_name == "person":
            result = self.person_resource
        elif resource_name == "movie":
            result = self.movie_resource
        elif resource_name == "acted_in":
            result = self.acted_in_resource
        else:
            result = None
        return result

if __name__ == "__main__":
    s_factory = ServiceFactory()
    res = s_factory.neo4j_db_service._get_relationship_set()
    res
    print(res)
