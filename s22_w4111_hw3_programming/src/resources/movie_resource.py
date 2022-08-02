from src.resources.base_resource import Base_Resource


class MovieResource(Base_Resource):

    def __init__(self, config):
        super(MovieResource, self).__init__(config)
        self.data_service = None

    def _get_project_fields(self):
        pass

    def get_full_collection_name(self):
        return self.config.collection_name

    def _get_relationship_name(self):
        return self.config.relationship_name

    def get_resource_by_id(self, id):
        pass

    def get_data_service(self):
        if self.data_service is None:
            self.data_service = self.config.data_service
        return self.data_service


    def _map_template(self, in_template:dict):
        new_template = {}
        for k,v in in_template.items():
            if k in ['released']:
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
        # if field_list:
        #     full_field_list = self._get_project_fields().intersection(field_list)
        # else:
        #     full_field_list = self._get_project_fields()
        final_template = self._map_template(template)
        self.get_data_service().set_relationship_name(self._get_relationship_name())

        result = super().get_by_template(relative_path, path_parameters, final_template, field_list,
                                         limit, offset, order_by)
        return result

    def create(self, new_resource):
        pass

    def update_resource_by_id(self, id, new_values):
        pass

    def delete_resource_by_id(self, id):
        pass