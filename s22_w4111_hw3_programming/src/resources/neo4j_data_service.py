from py2neo import Graph
from .base_data_service import BaseDataService


class Neo4jDataService(BaseDataService):
    def __init__(self, config_info):
        super(Neo4jDataService, self).__init__(config_info)
        self.properties = {}
        self.labels = None
        self.relationship_name = None
        self.relationship_table = None
        self.relationship_set = None

    def _get_connection(self):
        if self.connection is None:
            db_url = self.config_info.db_url
            db_auth = self.config_info.auth
            self.connection = Graph(db_url, auth=db_auth)
        return self.connection

    def _get_relationship_set(self):
        q = """
        match (n)-[r]->(m) return distinct type(r) as relationship
        """
        if self.relationship_set is None:

            result = self._get_connection().run(q)
            result = result.data()
            relationship_set = set()
            for item in result:
                relationship_set.add(item['relationship'])
            self.relationship_set = relationship_set
        return self.relationship_set

    def _get_relationships(self):
        q = """
        match (n)-[r]->(m) return distinct labels(n) as initiate, type(r) as relationship, labels(m) as target
        """
        if self.relationship_table is None:
            relationship = self._get_connection().run(q)
            relationship = relationship.data()
            result = []
            for item in relationship:
                for initiate in item["initiate"]:
                    for target in item["target"]:
                        relationship_item = {}
                        relationship_item["initiate"] = initiate
                        relationship_item["target"] = target
                        relationship_item["relationship"] = item["relationship"]
                        result.append(relationship_item)
            self.relationship_table = result
        return self.relationship_table



    def _get_properties(self, collection_name):
        if collection_name not in self.properties:
            q = """
            MATCH(p: {}) WITH DISTINCT keys(p) AS keys
            UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
            return allfields
            """.format(collection_name)
            allfields = self._get_connection().run(q)
            properties = allfields.data()
            self.properties[collection_name] = [item['allfields'] for item in properties]
        return self.properties[collection_name]

    def set_relationship_name(self, relationship_name):
        if relationship_name is not None:
            self.relationship_name = relationship_name

    def _get_labels(self):
        q = """
        MATCH (p) with distinct labels(p) as labelCollection
        UNWIND labelCollection as labelList 
        with distinct labelList as distinctLabels
        return distinctLabels
        """
        if self.labels is None:
            labels_cursor = self._get_connection().run(q)
            labels_list = labels_cursor.data()
            self.labels = [item['distinctLabels'] for item in labels_list]

        return self.labels

    def _close_connection(self):
        pass

    def _get_collection(self, collection_name):
        pass

    def _get_db(self):
        pass

    def _collection_to_property(self, template=None):
        new_template = {}
        if template is not None:
            key_list = list(template.keys())
            for key in key_list:
                value = template[key]
                if key.capitalize() == "Person":
                    key = "name"
                new_template[key] = value
        return new_template

    def construct_q_with_relationship(self,
                         initiate_collection_name,
                         target_collection_name,
                         template=None,
                         field_list=None):

        relationship_name = self.relationship_name
        q = """
            match (initiate:{})-[r:{}]->(target:{})
        """.format(initiate_collection_name, relationship_name, target_collection_name)

        initiate_property_list = self._get_properties(initiate_collection_name)
        target_property_list = self._get_properties(target_collection_name)
        new_template = {}
        if template is not None:
            for k, v in template.items():
                if k in initiate_property_list or k in target_property_list:
                    new_template[k] = v
                if k.capitalize() == initiate_collection_name or k.capitalize() == target_collection_name:
                    new_template[k.capitalize()] = v
                else:
                    continue
        new_template = self._collection_to_property(new_template)

        if len(new_template) != 0:
            q += " where "
            key_list = list(new_template.keys())
            for i in range(len(key_list)):
                key = key_list[i]
                if key in initiate_property_list:
                    q += "initiate." + str(key) + " = " + "$" + str(key)
                elif key in target_property_list:
                    q += "target." + str(key) + " = " + "$" + str(key)
                if i != len(key_list) - 1:
                    q += ", "

        if field_list is None:
            q += " return initiate,r,target"

        else:
            q += " return "
            for j in range(len(field_list)):
                if field_list[j] in initiate_property_list:
                    q += ("initiate." + field_list[j])
                else:
                    q += ("target." + field_list[j])
                if j != len(field_list) - 1:
                    q += ", "
        return q, new_template

    def construct_q_without_relationship(self,
                        collection_name,
                        template=None,
                        field_list=None):

        q = """match (n:{})""".format(collection_name)
        property_list = self._get_properties(collection_name)
        new_template = {}
        if template is not None:
            for k, v in template.items():
                if k in property_list:
                    new_template[k] = v
                else:
                    continue

        if len(new_template) != 0:
            q += " where "
            key_list = list(new_template.keys())
            for i in range(len(key_list)):
                key = key_list[i]
                q += "n." + str(key) + " = " + "$" + str(key)
                if i != len(key_list) - 1:
                    q += ", "
        if field_list is None:
            q += " return n"
        else:
            q += " return "
            for j in range(len(field_list)):
                q += ("n." + field_list[j])
                if j != len(field_list) - 1:
                    q += ", "
        return q, new_template

    def parse_template(self,
                       collection_name,
                       template=None,
                       field_list=None):

        need_relationship = False
        if self.relationship_name is not None and self.relationship_name in self._get_relationship_set():
            need_relationship = True

        init = None
        targ = None
        if template is not None:
            if need_relationship:
                for k,v in template.items():
                    k = k.capitalize()
                    for item in self._get_relationships():
                        if (k == item['initiate']) and (collection_name == item['target']) and (self.relationship_name == item['relationship']):
                            init, targ = k, collection_name
                            break
                        if (k == item['target']) and (collection_name == item['initiate']) and (self.relationship_name == item['relationship']):
                            init, targ = collection_name, k
                            break

        if not need_relationship:
            q, new_template = self.construct_q_without_relationship(collection_name, template, field_list)
        else:
            if init is None or targ is None:
                raise Exception("relationship not found")
            q, new_template = self.construct_q_with_relationship(init, targ, template, field_list)

        return q,new_template

    def get_by_template(self,
                        collection_name,
                        template=None,
                        field_list=None):

        q, final_template = self.parse_template(collection_name, template, field_list)
        res = self._get_connection().run(q, final_template)
        return list(res)

    def list_resources(self):
        q = "MATCH (n) RETURN DISTINCT LABELS(n)"
        result = self._get_connection().run(q)
        return result.data()

    def run_aggregation(self,
                        collection_name,
                        pipeline):
        pass





