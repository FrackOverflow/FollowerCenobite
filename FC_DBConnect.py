"""
FC_DBConnect

Low level DB access and setup logic
"""
from os import remove, getcwd
import os.path
import json
import sqlite3
import FC_DataClasses as dc


class fcdb():
    """
    FCDB Connection Class
    Provides DB setup and low level access
    """
    date_format: str
    cmd_delim: str
    db_name: str
    obj_f: dc.dbObjFactory

    def __init__(self,
                 about="FC_About.json"):
        # Load About.json (DB constants)
        about = json.load(open(about))
        self.date_format = about["DateFormat"]
        self.cmd_delim = about["DBCmdDelim"]
        self.data_folder = fcdb._fq_path(about["DataFolder"])
        self.db_name = fcdb._fq_path(self.data_folder, about["DBName"])
        self.image_path = fcdb._fq_path(self.data_folder, "images")
        self._set_db_and_prefs()

    def set_new_prefs(self, prefs, date_fmt=""):
        """ Set new preferences & date format on DB connection and object factory."""
        self.active_prefs = prefs
        if date_fmt:
            self.date_format = date_fmt
        self.obj_f.set_new_prefs(prefs, date_fmt)

    def _set_db_and_prefs(self):
        # sets DB connection and preferences, creates DB if it isn't found
        if not os.path.isfile(self.db_name):
            print(f"No FCDB was found, initializing a new database at: \n\t---> {os.path.join(getcwd(), self.db_name)}")
            self._create_new_db()
            startup_data = self._load_startup_data()
            self.obj_f = dc.dbObjFactory(dc.preference(*startup_data["startup_prefs"][0]), self.date_format)
            self._populate_startup_data(startup_data)
        else:
            self.active_prefs = self._sselect(dc.preference, suffix="ORDER BY id DESC")[0]
            self.obj_f = dc.dbObjFactory(self.active_prefs, self.date_format)

    # region Helpers
    @staticmethod
    def _fq_path(*paths):
        # Returns a path relative to the FC install folder
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), *paths)

    @staticmethod
    def first_or(default, result):
        """ Gets the first value from a list or if its empty returns None."""
        return result[0] if result else default

    @staticmethod
    def _mk_value_string(num: int) -> str:
        # Returns a string in format (?, ?, ?) where num = number of question marks
        qs = []
        for i in range(0, num):
            qs.append("?")
        return f'({",".join(qs)})'

    @staticmethod
    def _col_data(value):
        # Returns provided python data formatted to a SQL string
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, int):
            return str(value)
        if isinstance(value, list) or isinstance(value, dict):
            return json.dumps(value)

    @staticmethod
    def _mk_col_set(cols: dict):
        # Returns the provided columns in format "key1 = ?, key2 = ?,..., keyn = ?"
        return ", ".join([f"{c} = ?" for c in cols])

    @staticmethod
    def _mk_upsert_colset(cols: dict):
        # Returns the provided columns in format "key1 = excluded.key1, key2 = excluded.key2,..., keyn = excluded.keyn"
        return ", ".join([f"{c} = excluded.{c}" for c in cols])

    @staticmethod
    def _type_list(rows, db_obj: dc.dbObj):
        # Returns a list where each entry is an entry from rows typed to db_obj
        objs = []
        for row in rows:
            objs.append(db_obj(*row))
        return objs
    # endregion

    # region Run
    def _r_query(self, statement):
        # Run a query on the database and get all rows
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(statement)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(e)

    def _r_val_statement(self, statement, values):
        # Run a statement on the database repeatedly using entries in "values", return the last row ID
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if isinstance(values, list):
                    cursor.executemany(statement, values)
                else:
                    cursor.execute(statement, values)
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(e)

    def _r_statement(self, statement):
        # Run a query on the database and get the last row ID
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(statement)
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(e)

    def r_cmds(self, statements):
        # Run a set of statements on the database
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                for statement in statements:
                    cursor.execute(statement)
                conn.commit()
        except sqlite3.Error as e:
            print(e)
    # endregion

    # region Query Strings
    # Each method makes a corresponding query statment string from supplied data
    def mk_q_insert(self, table, row_data):
        """ Make insert query."""
        fields = ",".join(row_data.keys())
        return (f"INSERT INTO {table} ({fields}) VALUES{self._mk_value_string(len(row_data))};", tuple(row_data.values()))

    def mk_q_update(self, table, row_data):
        """ Make update query."""
        row_id = row_data.pop("id")
        return (f"UPDATE {table} SET {self._mk_col_set(row_data)} WHERE id = {row_id};", tuple(row_data.values()))

    def mk_q_upsert(self, table, row_data, id_cols):
        """ Make upsert query."""
        # Unwrap the query string and remove trailing semicolon
        qinsert = self.mk_q_insert(table, row_data)[0][:-1]
        # Create Upsert query from supplied data and insert query
        return (f'{qinsert} ON CONFLICT({", ".join(id_cols)}) DO UPDATE SET {self._mk_upsert_colset(row_data)};', tuple(row_data.values()))
    # endregion

    # region Query Methods
    def _sselect(self, db_obj_type: type[dc.dbObj], fields="*", suffix="") -> list[dc.dbObj]:
        """Startup select, manually types returned records with no factory (dbObjFactory is not available until prefs are loaded)"""
        qSelect = "SELECT {1} FROM {0}{2};"
        if suffix and suffix[0] != " ":
            suffix = f" {suffix}"
        rows = self._r_query(qSelect.format(db_obj_type.get_table(), fields, suffix))
        return [db_obj_type(*x) for x in rows]

    def _select(self, db_obj_type: type[dc.dbObj], fields="*", suffix="") -> list[dc.dbObj]:
        """Run a select statement and return a list of dbObjs"""
        qSelect = "SELECT {1} FROM {0}{2};"
        if suffix and suffix[0] != " ":
            suffix = f" {suffix}"
        rows = self._r_query(qSelect.format(db_obj_type.get_table(), fields, suffix))
        return [self.obj_f.mk_dbo(db_obj_type, x) for x in rows]

    def _insert(self, db_obj: dc.dbObj):
        """SQL Insert"""
        qInsert = self.mk_q_insert(db_obj.get_table(), db_obj.get_row_data())
        return self._r_val_statement(*qInsert)

    def _binsert(self, db_objs: list[dc.dbObj]):
        """SQL Bulk Insert"""
        values = []
        for db_obj in db_objs:
            qinsert = self.mk_q_insert(db_obj.get_table(), db_obj.get_row_data())
            values.append(qinsert[1])
        return self._r_val_statement(qinsert[0], values)

    def _update(self, db_obj: dc.dbObj):
        """SQL Update"""
        if not db_obj.id or db_obj.id == -1:
            print("When updating a db obj id must be set!")
        else:
            qupdate = self.mk_q_update(db_obj.get_table(), db_obj.get_row_data())
            return self._r_val_statement(*qupdate)

    def _bupdate(self, db_objs: list[dc.dbObj]):
        """SQL Bulk Update"""
        values = []
        for db_obj in db_objs:
            if not db_obj.id or db_obj.id == -1:
                print("When updating a db obj id must be set!")
            else:
                qupdate = self.mk_q_update(db_obj.get_table(), db_obj.get_row_data())
                values.append(qupdate[1])
        return self._r_val_statement(qupdate[0], values)

    def _upsert(self, db_obj: dc.dbObj):
        """SQL Upsert"""
        return self._r_val_statement(*self.mk_q_upsert(db_obj.get_table(), db_obj.get_row_data()))

    def _bupsert(self, db_objs: list[dc.dbObj]):
        """SQL Bulk Upsert"""
        values = []
        for db_obj in db_objs:
            qupsert = self.mk_q_upsert(db_obj.get_table(), db_obj.get_row_data(), db_obj.get_id_cols())
            values.append(qupsert[1])
        return self._r_val_statement(qupsert[0], values)
    # endregion

    # region Create
    def _prepare_staments(self, fname):
        # Prepare DB script using delemiter from About.json
        f = open(fname)
        return "".join(f.readlines()).split(self.cmd_delim)

    def _r_db_script(self, fname):
        # Run DB Script
        create = self._prepare_staments(fname)
        self.r_cmds(create)

    def _create_new_db(self):
        self._r_db_script(f"{self.data_folder}dbCreationScript.sql")

    def _load_startup_data(self):
        f = open(f"{self.data_folder}FC_Startup_Data.json")
        return json.load(f)

    def _populate_startup_data(self, startup_data):
        startup_objs = []

        for acc in startup_data["startup_acc"]:
            c_acc = self.obj_f.ig_account(*acc)
            startup_objs.append(c_acc)

        for pref in startup_data["startup_prefs"]:
            c_pref = dc.preference(*pref)
            startup_objs.append(c_pref)

        for db_obj in startup_objs:
            self._insert(db_obj)
    # endregion


class Struct(dict):
    """
    Struct is a dictionary you access like and object.
    Used for compatibility, to mock complex objects when default values are required, etc.
    """
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


if __name__ == "__main__":
    dbname = r"ProgramData\TestData\TESTFC.db"
    try:
        db = fcdb("ProgramData/TestData/TEST_FC_About.json")
        # db.munch_follow_data("ProgramData\FollowerJson\OF_Flwg_May30_2024.json", "ProgramData\FollowerJson\OF_Flwr_May30_2024.json", 0, datetime.today().strftime("%b%d_%Y"))
    finally:
        if os.path.isfile(dbname):
            remove(dbname)
