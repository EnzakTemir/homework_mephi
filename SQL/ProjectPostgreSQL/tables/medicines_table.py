from dbtable import *


class MedicinesTable(DbTable):
    display_name = "лекарство"

    def table_name(self):
        return self.dbconn.prefix + "medicines"

    def columns(self):
        return {
            "medicine_id": ["serial", "PRIMARY KEY"],
            "name": ["varchar(150)", "NOT NULL"],
            "dosage": ["varchar(50)", "NOT NULL"],
            "quantity_or_volume": ["varchar(50)", "NOT NULL"],
            "manufacturer": ["varchar(150)", "NOT NULL"],
            "prescription_required": ["boolean", "NOT NULL", "DEFAULT FALSE"],
            "category_id": ["integer", "NOT NULL",
                            "REFERENCES " + self.dbconn.prefix
                            + "categories(category_id)"],
            "price": ["numeric(10,2)", "NOT NULL", "CHECK (price > 0)"],
        }

    def serial_columns(self):
        return ["medicine_id"]

    def primary_key(self):
        return ["medicine_id"]

    def count_by_category(self, category_id):
        return self.count(where={"category_id": category_id})

    def page_by_category(self, category_id, limit, offset):
        sql = "SELECT " + ", ".join(self.select_columns())
        sql += " FROM " + self.table_name()
        sql += " WHERE category_id = %(category_id)s"
        sql += " ORDER BY " + ", ".join(self.primary_key())
        sql += " LIMIT %(limit)s OFFSET %(offset)s"
        params = {"category_id": category_id,
                  "limit": limit, "offset": offset}
        return self._run(sql, params, fetch="all")

    def find_by_position_in_category(self, category_id, num):
        sql = "SELECT " + ", ".join(self.select_columns())
        sql += " FROM " + self.table_name()
        sql += " WHERE category_id = %(category_id)s"
        sql += " ORDER BY " + ", ".join(self.primary_key())
        sql += " LIMIT 1 OFFSET %(offset)s"
        params = {"category_id": category_id, "offset": num - 1}
        return self._run(sql, params, fetch="one")
