#region FC Meta
from datetime import datetime
from functools import total_ordering
import json

#region Abstract Types
class dbObj():
#region Read-only Class Members
    TABLE = "TABLE-NAME"
    ID_COLS = ["id"]
    filter_fields = ["TABLE", "ID_COLS", "filter_fields","json_fields"]
    json_fields = []

    @classmethod
    def GetIdCols(cls):
        return list(cls.ID_COLS)
    
    @classmethod
    def GetFilterFields(cls):
        return list(cls.filter_fields)
    
    @classmethod
    def GetJsonFields(cls):
        return list(cls.json_fields)
    
    @classmethod
    def GetTable(cls):
        return str(cls.TABLE)
#endregion

#region Methods
    # Get filtered fields prepped for database
    def _getFilteredFields(self, filt) -> dict:
        obj_type = type(self)
        fields = dict(vars(self))

        # Dump any json/dicts/arrays to strings
        for field in obj_type.GetJsonFields():
            if field in fields:
                fields[field] = json.dumps(fields[field])

        # Filter non DB fields
        for field in filt:
            fields.pop(field, None)
        return fields
    
    # Get RowData (filters meta fields for saving to DB, does not filter ID if it is present and not -1)
    def GetRowData(self) -> dict:
        obj_type = type(self)
        has_id = True
        id_cols = obj_type.GetIdCols()

        for id_col in id_cols:
            if not hasattr(self, id_col):
                has_id = False
                break

            # Special case for id = -1
            if hasattr(self, "id") and self.id == -1:
                has_id = False
                break

        if has_id:
            print("Writing object with static ID, be careful!")
            return self._getFilteredFields(obj_type.GetFilterFields())
        else:
            return self._getFilteredFields(obj_type.GetFilterFields() + id_cols)
        
    # Get DisplayData (filters metafields for display, filters ID even when it is present)
    def GetDisplayData(self):
        obj_type = type(self)
        return self._getFilteredFields(obj_type.GetFilterFields() + obj_type.GetIdCols())
#endregion

#region Comparison Types
@total_ordering
class DateComparable(dbObj):
    filter_fields = dbObj.filter_fields + ["date_format", "date_field"]
    date_field = "date"

    def __init__(self, date_format):
        super(DateComparable, self).__init__()
        self.date_format = date_format

    def _get_datetime(self):
        return datetime.strptime(self.date, self.date_format)
    
    def _is_valid_op(self, other):
        return (hasattr(other, self.date_field) and hasattr(other, "date_format"))

    def __eq__(self, other):
        if not self._is_valid_op(other):
            return NotImplemented
        return self._get_datetime() == other._get_datetime()
    
    def __lt__(self, other):
        if not self._is_valid_op(other):
            return NotImplemented
        return self._get_datetime() < other._get_datetime()
#endregion
#endregion

#region Real Types
#region Meta Types
class preference(dbObj):
    TABLE = "preferences"

    def __init__(self, id, default_acc_id, progress_dir, data_dir, ig_url,):
        super(preference, self).__init__()
        self.id = id
        self.default_acc_id = default_acc_id
        self.progress_dir = progress_dir
        self.data_dir = data_dir
        self.ig_url = ig_url

class fc_window(dbObj):
    TABLE = "fc_window"
    json_fields = dbObj.json_fields + ["closeEvents","captureEvents"]

    def __init__(self, id, title, nickname, menu_id, subtype_id, onExit, onClose, onCapture, closeEvents, captureEvents):
        super(fc_window, self).__init__()
        self.id = id
        self.title = title
        self.nickname = nickname
        self.menu_id = menu_id
        self.subtype_id = subtype_id
        self.onExit = onExit
        self.onClose = onClose
        self.onCapture = onCapture
        if isinstance(closeEvents, str):
            self.closeEvents = json.loads(closeEvents)
        else:
            self.closeEvents = closeEvents
            
        if isinstance(captureEvents, str):
            self.captureEvents = json.loads(captureEvents)
        else:
            self.captureEvents = captureEvents

class fc_menu(dbObj):
    TABLE = "fc_menu"
    json_fields = dbObj.json_fields + ["menu_def"]

    def __init__(self, id, name, menu_def):
        super(fc_menu, self).__init__()
        self.id = id
        self.name = name
        if isinstance(menu_def, str):
            self.menu_def = json.loads(menu_def)
        else:
            self.menu_def = menu_def
    
    def raw_menu_def(self):
        return json.dumps(self.menu_def, [])

class fc_window_subtype(dbObj):
    TABLE = "window_subtype"
    json_fields = dbObj.json_fields + ["data"]
    
    def __init__(self, id, subtype_id, subtype, data):
        super(fc_window_subtype, self).__init__()
        self.id = id
        self.subtype_id = subtype_id
        self.subtype = subtype
        if isinstance(data, str):
            self.data = json.loads(data)
        else:
            self.data = data
    
    def raw_data(self):
        return json.dumps(self.data)
#endregion

#region FC Data
class follow(DateComparable):
    TABLE = "follow"

    def __init__(self, id, username, acc_id, date, follower, following, date_format):
        super(follow, self).__init__(date_format)
        self.id = id
        self.username = username
        self.acc_id = acc_id
        self.date = date
        
        # Is the user a Follower of the associated account?
        self.follower = follower

        # Is the associated account following the User?
        self.following = following
    
    # Dont follow back (Your account follows the user, the user does not follow back)
    def dfb(self):
        return (not self.follower and self.following)
    
    def idfb(self):
        return (self.follower and not self.following)

class ig_account(DateComparable):
    TABLE = "ig_account"
    date_field = "last_update"

    def __init__(self, id, username, abbrv, last_update, date_format):
        super(ig_account, self).__init__(date_format)
        self.id = id
        self.username = username
        self.abbrv = abbrv
        self.last_update = last_update

class last_follow(dbObj):
    TABLE = "last_follows"
    ID_COLS = ["username","acc_id"]

    def __init__(self, username: str, acc_id: int, last_following_id: int, last_follower_id: int):
        super(last_follow, self).__init__()
        self.username = username
        self.acc_id = acc_id
        self.last_following_id = last_following_id
        self.last_follower_id = last_follower_id
#endregion
#endregion

class dbObj_factory():
    def __init__(self, prefs: preference, date_format: str):
        self.SetNewPrefs(prefs, date_format)
    
    def SetNewPrefs(self, prefs: preference, date_format: str):
        self.active_prefs = prefs
        self.db_date_format = date_format

    def mk_dbo(self, T: type[dbObj], fields):
        return getattr(self, T.__name__)(*fields)

    def follow(self, id, username, acc_id, date, follower, following):
        return follow(id, username, acc_id, date, follower, following, self.db_date_format)
    
    def last_follow(self, username, acc_id, last_following_id, last_follower_id):
        return last_follow(username, acc_id, last_following_id, last_follower_id)
    
    def ig_account(self, id, username, abbrv, last_update):
        return ig_account(id, username, abbrv, last_update, self.db_date_format)
    
    def preference(self, id, default_acc_id, progress_dir, data_dir, ig_url):
        return preference(id, default_acc_id, progress_dir, data_dir, ig_url)
    
    def fc_window(self, id, title, nickname, menu_id, subtype_id, onExit, onClose, onCapture, closeEvents, captureEvents):
        return fc_window(id, title, nickname, menu_id, subtype_id, onExit, onClose, onCapture, closeEvents, captureEvents)
    
    def fc_menu(self, id, name, menu_def):
        return fc_menu(id, name, menu_def)
    
    def fc_window_subtype(self, id, subtype_id, subtype, data):
        return fc_window_subtype(id, subtype_id, subtype, data)
    
if __name__ == "__main__":
    d8 = datetime.today().strftime("%b%D_%Y")
    lf = last_follow("Babar", 56, 21, 21)
    iga = ig_account(56, "Barbossa", "BRBSA", d8)
    f = follow(21, "Babar", 56, datetime.today().strftime("%b%D_%Y"), 1, 1, d8, "%b%D_%Y")
    wsub = fc_window_subtype(5, 2, "Barbarossa", '{"foo":"baz"}')
    m = fc_menu(1, "Advanced", [])
    w = fc_window(6,"Main","Main",1,5,"","","",[],[])
    
    testArray = [lf, iga, f, wsub, m, w]

    for db_o in testArray:
        t_obj = type(db_o)
        print(f"> {t_obj.__name__} ---------------")
        print(f"Table Name = {t_obj.GetTable()}")
        print(f"ID Col(s) = {t_obj.GetIdCols()}")
        print(f"Filter Fields = {t_obj.GetFilterFields()}")
        print(f"Json Fields = {t_obj.GetJsonFields()}")
        
        """
        values = vars(db_o)
        print(f"Additional Values:")
        for var in values:
            if values[var] not in t_obj.GetFilterFields():
                print(f"{var} = {values[var]}")
        """
