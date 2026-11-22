# Базовые действия с таблицами.

import psycopg2
import psycopg2.errorcodes as pgcodes
import psycopg2.extras


class DbError(Exception):
    """Ошибка базы данных с понятным пользователю текстом."""

_MESSAGES = {
    pgcodes.UNIQUE_VIOLATION: "такая запись уже есть",
    pgcodes.FOREIGN_KEY_VIOLATION: "запись используется в другой таблице",
    pgcodes.CHECK_VIOLATION: "значение не проходит проверку базы данных",
    pgcodes.NOT_NULL_VIOLATION: "обязательное поле не заполнено",
    pgcodes.STRING_DATA_RIGHT_TRUNCATION: "слишком длинное значение",
    pgcodes.NUMERIC_VALUE_OUT_OF_RANGE: "число вне допустимого диапазона",
    pgcodes.INVALID_TEXT_REPRESENTATION: "значение не соответствует типу поля",
    pgcodes.UNDEFINED_TABLE: "таблица не найдена — выполните пункт 2 меню",
}


def describe_db_error(exc):
    base = _MESSAGES.get(getattr(exc, "pgcode", None), "ошибка базы данных")
    detail = ""
    if getattr(exc, "diag", None) is not None:
        detail = (exc.diag.message_primary or exc.diag.message_detail or "").strip()
    if detail:
        return base + ": " + detail
    return base


class DbTable:
    """Базовый класс таблицы: создание, удаление, выборка и изменение строк."""

    dbconn = None
    display_name = "запись"

    def table_name(self):
        raise NotImplementedError

    def columns(self):
        raise NotImplementedError

    def serial_columns(self):
        return []

    def primary_key(self):
        if self.serial_columns():
            return list(self.serial_columns())
        return [next(iter(self.columns()))]

    def table_constraints(self):
        return []

    def select_columns(self):
        return list(self.columns().keys())

    def writable_columns(self):
        return [c for c in self.columns() if c not in self.serial_columns()]

    def _run(self, sql, params=None, fetch=None):
        conn = self.dbconn.conn
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute(sql, params)
            if fetch == "one":
                result = cur.fetchone()
            elif fetch == "all":
                result = cur.fetchall()
            elif fetch == "scalar":
                row = cur.fetchone()
                result = None if row is None else list(row.values())[0]
            else:
                result = cur.rowcount
            conn.commit()
            return result
        except psycopg2.Error as exc:
            conn.rollback()
            raise DbError(describe_db_error(exc)) from exc
        finally:
            cur.close()

    def create(self):
        definitions = [name + " " + " ".join(definition)
                       for name, definition in self.columns().items()]
        definitions += self.table_constraints()
        self._run("CREATE TABLE " + self.table_name()
                  + " (" + ", ".join(definitions) + ")")

    def drop(self):
        self._run("DROP TABLE IF EXISTS " + self.table_name() + " CASCADE")

    def insert_one(self, values):
        columns = [c for c in self.writable_columns() if c in values]
        placeholders = ", ".join("%(" + c + ")s" for c in columns)
        sql = ("INSERT INTO " + self.table_name()
               + " (" + ", ".join(columns) + ") VALUES (" + placeholders + ")")
        self._run(sql, {c: values[c] for c in columns})

    def update_one(self, values, where):
        assignments = ", ".join(c + " = %(v_" + c + ")s" for c in values)
        conditions = " AND ".join(c + " = %(w_" + c + ")s" for c in where)
        params = {"v_" + c: v for c, v in values.items()}
        params.update({"w_" + c: v for c, v in where.items()})
        sql = ("UPDATE " + self.table_name() + " SET " + assignments
               + " WHERE " + conditions)
        return self._run(sql, params)

    def delete_one(self, where):
        conditions = " AND ".join(c + " = %(w_" + c + ")s" for c in where)
        params = {"w_" + c: v for c, v in where.items()}
        sql = ("DELETE FROM " + self.table_name() + " WHERE " + conditions)
        return self._run(sql, params)

    def count(self, where=None):
        sql = "SELECT COUNT(*) AS cnt FROM " + self.table_name()
        params = None
        if where:
            conditions = " AND ".join(c + " = %(w_" + c + ")s" for c in where)
            params = {"w_" + c: v for c, v in where.items()}
            sql += " WHERE " + conditions
        return self._run(sql, params, fetch="scalar")

    def all(self, limit=None, offset=0):
        sql = ("SELECT " + ", ".join(self.select_columns())
               + " FROM " + self.table_name()
               + " ORDER BY " + ", ".join(self.primary_key()))
        params = None
        if limit is not None:
            sql += " LIMIT %(limit)s OFFSET %(offset)s"
            params = {"limit": limit, "offset": offset}
        return self._run(sql, params, fetch="all")

    def page(self, limit, offset):
        return self.all(limit, offset)

    def find_by_position(self, num):
        sql = ("SELECT " + ", ".join(self.select_columns())
               + " FROM " + self.table_name()
               + " ORDER BY " + ", ".join(self.primary_key())
               + " LIMIT 1 OFFSET %(offset)s")
        return self._run(sql, {"offset": num - 1}, fetch="one")