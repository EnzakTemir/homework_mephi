from dbtable import *


class CategoriesTable(DbTable):
    display_name = "категория"

    def table_name(self):
        return self.dbconn.prefix + "categories"

    def columns(self):
        return {"category_id": ["serial", "PRIMARY KEY"],
                "name": ["varchar(100)", "NOT NULL", "UNIQUE"]}

    def serial_columns(self):
        return ["category_id"]

    def primary_key(self):
        return ["category_id"]

    def find_by_name(self, name):
        """Категория по названию (нужно при заполнении тестовыми данными)."""
        sql = "SELECT " + ", ".join(self.select_columns())
        sql += " FROM " + self.table_name()
        sql += " WHERE name = %(name)s"
        return self._run(sql, {"name": name}, fetch="one")

    def delete_with_medicines(self, category_id):
        """Удалить категорию вместе с её лекарствами в одной транзакции."""
        from medicines_table import MedicinesTable

        medicines = MedicinesTable()
        conn = self.dbconn.conn
        cur = conn.cursor()
        try:
            # Сначала строки второй таблицы, потом сама категория.
            cur.execute("DELETE FROM " + medicines.table_name()
                        + " WHERE category_id = %s", (category_id,))
            cur.execute("DELETE FROM " + self.table_name()
                        + " WHERE category_id = %s", (category_id,))
            conn.commit()
        except psycopg2.Error as exc:
            conn.rollback()
            raise DbError(describe_db_error(exc)) from exc
        finally:
            cur.close()
