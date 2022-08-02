from abc import ABC, abstractmethod


class Base_Resource(ABC):

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get_full_collection_name(self):
        pass

    @abstractmethod
    def get_resource_by_id(self, id):
        """

        :param id: The 'primary key' of the resource instance relative to the collection.
        :return: The resource or None if not found.
        """
        pass

    @abstractmethod
    def get_data_service(self):
        pass

    @abstractmethod
    def get_by_template(self,
                        relative_path=None,
                        path_parameters=None,
                        template=None,
                        field_list=None,
                        limit=None,
                        offset=None,
                        order_by=None):
        if path_parameters is None:
            final_path_parameters = {}
        else:
            final_path_parameters = path_parameters

        if template is None:
            final_template = {}
        else:
            final_template = template

        full_template = {**final_path_parameters, **final_template}

        d_service = self.get_data_service()
        result = d_service.get_by_template(
            self.get_full_collection_name(),
            full_template,
            field_list
        )
        return result


    @abstractmethod
    def create(self, new_resource):
        """

        Assume that
            - new_resource is {'customerNumber': 101, 'status': 'Shipped'}
            - self.get_full_table_name() returns 'classicmodels.orders'

        This function would logically perform

        insert into classicmodels.orders(customerNumber, status)
            values(101, 'Shipped')

        :param new_resource: A dictionary containing the data to insert.
        :return: Returns the values of the primary key columns in the order defined.
            In this example, the result would be [101]
        """
        pass

    @abstractmethod
    def update_resource_by_id(self, id, new_values):
        """
        This is a logical abstraction of an SQL UPDATE statement.

        Assume that
            - id is 30100
            - new_values is {'customerNumber': 101, 'status': 'Shipped'}
            - self.get_full_table_name() returns 'classicmodels.orders'

        This method would logically execute.

        update classicmodels.orders
            set customerNumber=101, status=shipped
            where
                orderNumber=30100


        :param id: The 'primary key' of the resource to update
        :new_values: A dictionary defining the columns to update and the new values.
        :return: 1 if a resource was updated. 0 otherwise.
        """
        pass

    @abstractmethod
    def delete_resource_by_id(self, id):
        """
        This is a logical abstraction of an SQL DELETE statement.

        Assume that
            - id is 30100
            - new_values is {'customerNumber': 101, 'status': 'Shipped'}

        This method would logically execute.

        delete from classicmodels.orders
            where
                orderNumber=30100


        :param id: The 'primary key' of the resource to delete
        :return: 1 if a resource was deleted. 0 otherwise.
        """
        pass
