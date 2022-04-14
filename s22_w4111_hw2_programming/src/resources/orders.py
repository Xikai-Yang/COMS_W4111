from .base_resource import Base_Resource
import pymysql
import json

class Orders(Base_Resource):

    def __init__(self):
        super().__init__()
        self.db_schema = 'classicmodels'
        self.db_table = 'orders'
        self.db_table_full_name = self.db_schema + "." + self.db_table
        self.primary_key_fields = "orderNumber"
        self.conn = self._get_connection()

    def _get_connection(self):
        conn = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="dbuserdbuser",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True                             # this attribute is important
        )
        return conn

    def get_resource_by_id(self, id):
        sql = "select * from " + self.db_table_full_name + " where orderNumber=%s"
        # conn = self._get_connection()
        cursor = self.conn.cursor()
        res = cursor.execute(sql, (id))

        if res == 1:
            result = cursor.fetchone()
        else:
            result = None

        return result

    def get_by_template(self, path=None, template=None, field_list=None, limit=None, offset=None):

        sql = "select" + " " + ','.join(field_list) + " from " + self.get_full_table_name()
        argument_list = []
        if template is not None:
            where_condition = "where "
            key_list = list(template.keys())
            for i in range(len(key_list)):
                key = key_list[i]
                where_condition += (str(key) + "=%s")
                argument_list.append(template[key])
                if i != len(key_list) - 1:
                    where_condition += ' and '
            sql = sql + " " + where_condition

        cursor = self.conn.cursor()
        res = cursor.execute(sql, tuple(argument_list))
        if res > 0:
            result = cursor.fetchall()
        else:
            result = None
        return result

    def create(self, new_resource):
        new_resource = eval(new_resource)
        sql = "insert into" + " " + str(self.get_full_table_name()) +"(" + ",".join(list(new_resource.keys())) + ")"
        sql = sql + " " + "values" + "(" + ','.join(["%s"]*len(new_resource.keys())) + ")"

        cursor = self.conn.cursor()
        try:
            res = cursor.execute(sql, tuple(list(new_resource.values())))
            if res > 0:
                res = new_resource[self.primary_key_fields]
        except Exception as e:
            res = e

        return res

    def update_resource_by_id(self, id, new_values):
        new_values = eval(new_values)
        sql = "update " + str(self.get_full_table_name()) + " " + "set" + " "
        key_list = list(new_values.keys())
        update_info = ""
        value_list = []
        for i in range(len(key_list)):
            key = key_list[i]
            value_list.append(new_values[key])
            update_info = update_info + (str(key) + "=%s")
            if i != len(key_list) - 1:
                update_info += ", "

        where_condition = "where " + self.primary_key_fields + "=%s"
        value_list.append(id)
        sql = sql + update_info + " " + where_condition
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, (value_list))
            res = cursor.rowcount
        except Exception as e:
            res = e
        return res

    def delete_resource_by_id(self, id):
        sql = "delete from " + self.get_full_table_name() + " where " + self.primary_key_fields + "=%s"
        cursor = self.conn.cursor()
        cursor.execute(sql, (id))
        res = cursor.rowcount
        return res
