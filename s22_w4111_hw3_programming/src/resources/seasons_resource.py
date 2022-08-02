from src.resources.base_resource import Base_Resource


class SeasonsResource(Base_Resource):


    def __init__(self, config):
        super(SeasonsResource, self).__init__(config)
        self.data_service = None

    def _get_project_fields(self):
        # result = set(["episodeNum", "episodeAirDate", "episodeTitle"])
        result = set(["episodeAirDate","episodeTitle"])
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
        if in_template is None:
            return None

        new_template = {}
        for k,v in in_template.items():
            if k in ['seasonNum', 'episodeNum']:
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
        result = super().get_by_template(relative_path, path_parameters, final_template, full_field_list,
                                         limit, offset, order_by)
        return result

    def create(self, new_resource):
        pass

    def update_resource_by_id(self, id, new_values):
        pass

    def delete_resource_by_id(self, id):
        pass