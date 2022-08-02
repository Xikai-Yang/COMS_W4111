from src.resources.base_resource import Base_Resource


class ScenesResource(Base_Resource):


    def __init__(self, config):
        super(ScenesResource, self).__init__(config)
        self.data_service = None

    def _get_project_fields(self):
        # result = ["seasonNum","episodeNum","sceneNum","sceneLocation","sceneSubLocation",
        #           "sceneStart","sceneEnd","episodeTitle","episodeLink","episodeAirDate","episodeDescription"]

        result = ["seasonNum","episodeNum","sceneNum","sceneLocation","sceneSubLocation",
                  "sceneStart","sceneEnd"]
        return result

    def get_full_collection_name(self):
        return self.config.collection_name

    def get_resource_by_id(self, id):
        template = {"seasonNum": id}
        result = self.get_by_template(template=template)
        return result

    def get_data_service(self):
        if self.data_service is None:
            self.data_service = self.config.data_service
        return self.data_service

    def _map_template(self, in_template:dict):
        mapping = {"seasons":"seasonNum", "episodes":"episodeNum","scenes":"sceneNum"}
        if in_template is None:
            return None

        new_template = {}
        for k,v in in_template.items():
            if k in list(mapping.keys()):
                k = mapping[k]
            new_template[k] = v

        for k,v in new_template.items():
            if k in ['seasonNum', 'episodeNum','sceneNum']:
                v = int(v)
            new_template[k] = v
        return new_template

    def get_by_template(self,
                        relative_path=None,
                        path_parameters=None,
                        template=None,
                        field_list=None,
                        limit=None,
                        offset=None,
                        order_by=None):
        if field_list:
            full_field_list = self._get_project_fields().intersection(field_list)
        else:
            full_field_list = self._get_project_fields()
        final_template = self._map_template(template)
        pipeline = [
            {
                '$unwind': {
                    'path': '$scenes',
                    'includeArrayIndex': 'sceneNum',
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$project': {
                    'seasonNum': 1,
                    'episodeNum': 1,
                    'episodeTitle': 1,
                    'episodeLink': 1,
                    'episodeAirDate': 1,
                    'episodeDescription': 1,
                    'sceneNum': {
                        '$add': [
                            '$sceneNum', 1
                        ]
                    },
                    'sceneLocation': '$scenes.location',
                    'sceneSubLocation': '$scenes.subLocation',
                    'sceneStart': '$scenes.sceneStart',
                    'sceneEnd': '$scenes.sceneEnd'
                }
            }, {
                '$match': final_template
            }
        ]
        full_field_dict = dict()
        for field in full_field_list:
            full_field_dict[field] = 1
        full_field_dict = \
        {
            '$project': full_field_dict
        }

        pipeline.append(full_field_dict)
        result = self.get_data_service().run_aggregation(self.get_full_collection_name(), pipeline)
        return list(result)

    def create(self, new_resource):
        pass

    def update_resource_by_id(self, id, new_values):
        pass

    def delete_resource_by_id(self, id):
        pass