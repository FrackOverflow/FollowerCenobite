from os import remove, getcwd
from os.path import isfile, join
from datetime import datetime
import json
import sqlite3
import FC_DataClasses as dc


class fcdb():
    def __init__(self, about="FC_About.json"):
        # Load About.json (DB constants)
        about = json.load(open(about))
        self.date_format = about["DateFormat"]
        self.cmd_delim = about["DBCmdDelim"]
        self.data_folder = about["DataFolder"]
        self.db_name = about["DataFolder"] + about["DBName"]
        self.SetDBAndPrefs()

    def SetNewPrefs(self, prefs, date_format = ""):
        self.active_prefs = prefs
        if date_format:
            self.date_format = date_format
        self.obj_f.SetNewPrefs(prefs, date_format)

    def SetDBAndPrefs(self):
        if not isfile(self.db_name):
            print(f"No FCDB was found, initializing a new database at: \n\t---> {join(getcwd(), self.db_name)}")
            self.CreateNewDB()
            startup_data = self.LoadStartupData()
            self.obj_f = dc.dbObj_factory(dc.preference(*startup_data["startup_prefs"][0]), self.date_format)
            self.PopulateStartupData(startup_data)
        else:
            self.active_prefs = self.sselect(dc.preference, suffix="ORDER BY id DESC")[0]
            self.obj_f = dc.dbObj_factory(self.active_prefs, self.date_format)

    #region Helpers
    # Gets the first value from a list or if its empty returns None
    @staticmethod
    def FirstOr(default, result):
        return result[0] if result else default

    # Returns a string in format (?, ?, ?) where num = number of question marks
    @staticmethod
    def MakeValueString(num: int) -> str:
        qs = []
        for i in range(0, num):
            qs.append("?")
        return f'({",".join(qs)})'
    
    @staticmethod
    def colData(value):
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, int):
            return str(value)
        if isinstance(value, list) or isinstance(value, dict):
            return json.dumps(value)
        
    @staticmethod
    def MakeColSet(cols: dict):
        return ", ".join([f"{c} = ?" for c in cols])

    @staticmethod
    def MakeUpsertColset(cols: dict):
        return ", ".join([f"{c} = excluded.{c}" for c in cols])

    @staticmethod
    def TypeList(rows, db_obj: dc.dbObj):
        objs = []
        for row in rows:
            objs.append(db_obj(*row))
        return objs
    #endregion

    #region Run
    def RunQuery(self, statement):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(statement)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(e)

    def RunValueStatement(self, statement, values):
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

    def RunStatement(self, statement):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(statement)
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(e)

    def RunCommands(self, statements):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                for statement in statements:
                    cursor.execute(statement)
                conn.commit()
        except sqlite3.Error as e:
            print(e)
    #endregion

    #region Query Strings
    # Each method makes a corresponding query statment string from supplied data
    def mkQInsert(self, table, row_data):
        fields = ",".join(row_data.keys())
        return (f"INSERT INTO {table} ({fields}) VALUES{self.MakeValueString(len(row_data))};", tuple(row_data.values()))
    
    def mkQUpdate(self, table, row_data):
        row_id = row_data.pop("id")
        return (f"UPDATE {table} SET {self.MakeColSet(row_data)} WHERE id = {row_id};", tuple(row_data.values()))
    
    def mkQUpsert(self, table, row_data, id_cols): 
        # Unwrap the query string and remove trailing semicolon
        qinsert = self.mkQInsert(table, row_data)[0][:-1]
        # Create Upsert query from supplied data and insert query
        return (f'{qinsert} ON CONFLICT({", ".join(id_cols)}) DO UPDATE SET {self.MakeUpsertColset(row_data)};', tuple(row_data.values()))
    #endregion

    #region Query Methods
    # Startup select, manually types returned records with no factory (dbObj_factory is not available until prefs are loaded)
    def sselect(self, db_obj_type: type[dc.dbObj], fields = "*", suffix = ""):
        qSelect = "SELECT {1} FROM {0}{2};"
        if suffix and suffix[0] != " ":
            suffix = f" {suffix}"
        rows = self.RunQuery(qSelect.format(db_obj_type.GetTable(), fields, suffix))
        return [db_obj_type(*x) for x in rows]
    
    # Run a select statement and return a list of dbObjs created with the active factory
    def select(self, db_obj_type: type[dc.dbObj], fields = "*", suffix = ""):
        qSelect = "SELECT {1} FROM {0}{2};"
        if suffix and suffix[0] != " ":
            suffix = f" {suffix}"
        rows = self.RunQuery(qSelect.format(db_obj_type.GetTable(), fields, suffix))
        return [self.obj_f.mk_dbo(db_obj_type, x) for x in rows]
    
    # Insert
    def insert(self, db_obj: dc.dbObj):
        qInsert = self.mkQInsert(db_obj.GetTable(), db_obj.GetRowData())
        return self.RunValueStatement(*qInsert)

    # Bulk Insert
    def binsert(self, db_objs: list[dc.dbObj]):
        values = []
        for db_obj in db_objs:
            qinsert = self.mkQInsert(db_obj.GetTable(), db_obj.GetRowData())
            values.append(qinsert[1])
        return self.RunValueStatement(qinsert[0], values)

    # Update
    def update(self, db_obj: dc.dbObj):
        if not db_obj.id or db_obj.id == -1:
            print("When updating a db obj id must be set!")
        else:
            qupdate = self.mkQUpdate(db_obj.GetTable(), db_obj.GetRowData())
            return self.RunValueStatement(*qupdate)
    
    # Bulk Update
    def bupdate(self, db_objs: list[dc.dbObj]):
        values = []
        for db_obj in db_objs:
            if not db_obj.id or db_obj.id == -1:
                print("When updating a db obj id must be set!")
            else:
                qupdate = self.mkQUpdate(db_obj.GetTable(), db_obj.GetRowData())
                values.append(qupdate[1])
        return self.RunValueStatement(qupdate[0], values)
    
    # Upsert
    def upsert(self, db_obj: dc.dbObj):
        return self.RunValueStatement(*self.mkQUpsert(db_obj.GetTable(), db_obj.GetRowData()))

    # Bulk Upsert
    def bupsert(self, db_objs: list[dc.dbObj]):
        values = []
        for db_obj in db_objs:
            qupsert = self.mkQUpsert(db_obj.GetTable(), db_obj.GetRowData(), db_obj.GetIdCols())
            values.append(qupsert[1])
        return self.RunValueStatement(qupsert[0], values)
    #endregion

    #region Create
    def PrepareStaments(self, fname):
        f = open(fname)
        return "".join(f.readlines()).split(self.cmd_delim)

    def RunDbScript(self, fname):
        create = self.PrepareStaments(fname)
        self.RunCommands(create)

    def CreateNewDB(self):
        # Create New DB
        self.RunDbScript(f"{self.data_folder}dbCreationScript.txt")

    def LoadStartupData(self):
        f = open(f"{self.data_folder}FC_Startup_Data.json")
        return json.load(f)

    def PopulateStartupData(self, startup_data):
        startup_objs = []
        ui_data = startup_data["ui_data"]

        for acc in startup_data["startup_acc"]:
            c_acc = self.obj_f.ig_account(*acc)
            startup_objs.append(c_acc)

        for pref in startup_data["startup_prefs"]:
            c_pref = dc.preference(*pref)
            startup_objs.append(c_pref)
            
        for menu in ui_data["menus"]:
            c_menu = dc.fc_menu(
                menu.get("id", -1),
                menu.get("name", None),
                menu.get("menu_def", None)
            )
            startup_objs.append(c_menu)

        for subtype in ui_data["window_subtypes"]:
            c_st = dc.fc_window_subtype(
                subtype.get("id", -1),
                subtype.get("subtype_id", None),
                subtype.get("subtype", None),
                subtype.get("data", None)
            )
            startup_objs.append(c_st)

        for window in ui_data["windows"]:
            c_win = dc.fc_window(
                window.get("id", -1),
                window.get("title", None),
                window.get("nickname", None),
                window.get("menu_id", None),
                window.get("subtype_id", None),
                window.get("onExit", None),
                window.get("onClose", None),
                window.get("onCapture", None),
                window.get("closeEvents", None),
                window.get("captureEvents", None)
            )
            startup_objs.append(c_win)
        
        for db_obj in startup_objs:
            self.insert(db_obj)
    #endregion

class struct(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

if __name__ == "__main__":
    dbname = "ProgramData\TestData\TESTFC.db"
    try:
        db = fcdb("ProgramData/TestData/TEST_FC_About.json")
        # db.MunchFollowData("ProgramData\FollowerJson\OF_Flwg_May30_2024.json", "ProgramData\FollowerJson\OF_Flwr_May30_2024.json", 0, datetime.today().strftime("%b%d_%Y"))
    finally:
        if isfile(dbname):
            remove(dbname)