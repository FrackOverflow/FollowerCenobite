"""
FC_DataClasses

Contains Model classes for interacting with the database
"""

from datetime import datetime
from functools import total_ordering
import json


# region Abstract Types
class dbObj():
    """
    Abstract superclass for all database objects.
    Adds meta fields and functions for database interactions.
    """
    # Name of the database table
    TABLE = "TABLE-NAME"

    # ID Column names
    ID_COLS = ["id"]

    # Fields that aren't saved to the database
    filter_fields = ["TABLE", "ID_COLS", "filter_fields", "json_fields"]

    # Fields that have to be converted to/from json
    json_fields = []

    @classmethod
    def get_id_cols(cls):
        """ Gets the name of the ID column(s) for a dbObj."""
        return list(cls.ID_COLS)

    @classmethod
    def _get_filter_fields(cls):
        """ Gets the fields to filter out when saving to the database."""
        return list(cls.filter_fields)

    @classmethod
    def get_json_fields(cls):
        """ Gets the fields to convert to/from json."""
        return list(cls.json_fields)

    @classmethod
    def get_table(cls):
        """Gets the DB table name."""
        return str(cls.TABLE)

    def _get_filtered_fields(self, filt) -> dict:
        # Get filtered fields prepped for database
        obj_type = type(self)
        fields = dict(vars(self))

        # Dump any json/dicts/arrays to strings
        for field in obj_type.get_json_fields():
            if field in fields:
                fields[field] = json.dumps(fields[field])

        # Filter non DB fields
        for field in filt:
            fields.pop(field, None)
        return fields

    def get_row_data(self) -> dict:
        """
        Gets the row data for saving to the database.
        Includes ID if [ID is present and ID != -1]).

        Args:
            self: A dbObj instance

        Returns:
            dict: a set of (field name [key], field value) pairs
        """
        obj_type = type(self)
        has_id = True
        id_cols = obj_type.get_id_cols()

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
            return self._get_filtered_fields(obj_type._get_filter_fields())
        else:
            return self._get_filtered_fields(obj_type._get_filter_fields()
                                             + id_cols)

    def get_display_data(self):
        """
        Gets the row data for saving to the database.
        Filters ID even when it is present.

        Args:
            self: A dbObj instance

        Returns:
            dict: a set of (field name [key], field value) pairs
        """
        obj_type = type(self)
        return self._get_filtered_fields(obj_type._get_filter_fields()
                                         + obj_type.get_id_cols())


# region Comparison Types
@total_ordering
class DateComparable(dbObj):
    """
    Abstract superclass with comparable datetime property.
    """
    filter_fields = dbObj.filter_fields + ["date_format", "date_prop"]

    # Date property name
    date_prop = "date"

    def __init__(self,
                 date_format):
        super(DateComparable, self).__init__()
        self.date_format = date_format

    # Gets datetime property for comparison
    def _get_datetime(self):
        return datetime.strptime(getattr(self, self.date_prop),
                                 self.date_format)

    # Checks if "other" has the appropriate comparison fields
    def _is_valid_op(self, other):
        return (hasattr(other, "date_prop")
                and hasattr(other, other.date_prop)
                and hasattr(other, "date_format"))

    def __eq__(self, other):
        if not self._is_valid_op(other):
            return NotImplemented
        return self._get_datetime() == other._get_datetime()

    def __lt__(self, other):
        if not self._is_valid_op(other):
            return NotImplemented
        return self._get_datetime() < other._get_datetime()
# endregion
# endregion


# region Real Types
# region Meta Types
class preference(dbObj):
    """
    User Preference settings for FC.
    Represents a preference record from the database.
    """
    TABLE = "preferences"

    def __init__(self,
                 id,
                 default_acc_id,
                 progress_dir,
                 data_dir,
                 ig_url,):
        super(preference, self).__init__()
        self.id = id
        self.default_acc_id = default_acc_id
        self.progress_dir = progress_dir
        self.data_dir = data_dir
        self.ig_url = ig_url
# endregion


# region Entity Classes
class follow(DateComparable):
    """
    FC Follow datapoint
    Represents a follow record from the database
    """
    TABLE = "follow"

    def __init__(self,
                 id,
                 username,
                 acc_id, date,
                 follower,
                 following,
                 date_format):
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
    """
    FC Instagram Account
    Represents an ig_account record from the database
    """
    TABLE = "ig_account"
    date_field = "last_update"

    def __init__(self,
                 id,
                 username,
                 abbrv,
                 last_update,
                 date_format):
        super(ig_account, self).__init__(date_format)
        self.id = id
        self.username = username
        self.abbrv = abbrv
        self.last_update = last_update


class last_follow(dbObj):
    """
    FC Instagram Account
    Represents an last_follows record from the database
    """
    TABLE = "last_follows"
    ID_COLS = ["username", "acc_id"]

    def __init__(self,
                 username: str,
                 acc_id: int,
                 last_following_id: int,
                 last_follower_id: int):
        super(last_follow, self).__init__()
        self.username = username
        self.acc_id = acc_id
        self.last_following_id = last_following_id
        self.last_follower_id = last_follower_id
# endregion
# endregion


class dbObjFactory():
    """
    Factory for creating dbObj using active prefs and dateformat
    """
    def __init__(self,
                 prefs: preference,
                 date_format: str):
        self.set_new_prefs(prefs, date_format)

    def set_new_prefs(self, prefs: preference, date_format: str):
        """ Updates active Preferences and Date Format."""
        self.active_prefs = prefs
        self.db_date_format = date_format

    def mk_dbo(self, T: type[dbObj], fields):
        """Creates dbObj with type & fields."""
        return getattr(self, T.__name__)(*fields)

    # region Typing Methods
    # - Names must match corresponding class
    # - Args must match ordered column names from corresponding DB table
    def follow(self, id, username, acc_id, date, follower, following):
        """ Create a follow from data."""
        return follow(id, username, acc_id, date, follower, following, self.db_date_format)

    def last_follow(self, username, acc_id, last_following_id, last_follower_id):
        """ Create a last follow from data."""
        return last_follow(username, acc_id, last_following_id, last_follower_id)

    def ig_account(self, id, username, abbrv, last_update):
        """ Create an ig_account from data."""
        return ig_account(id, username, abbrv, last_update, self.db_date_format)

    def preference(self, id, default_acc_id, progress_dir, data_dir, ig_url):
        """ Create a preference from data."""
        return preference(id, default_acc_id, progress_dir, data_dir, ig_url)
    # endregion


if __name__ == "__main__":
    d8 = datetime.today().strftime("%b%D_%Y")
    lf = last_follow("Babar", 56, 21, 21)
    iga = ig_account(56, "Barbossa", "BRBSA", d8)
    f = follow(21, "Babar", 56, datetime.today().strftime("%b%D_%Y"), 1, 1, d8, "%b%D_%Y")

    testArray = [lf, iga, f]

    for db_o in testArray:
        t_obj = type(db_o)
        print(f"> {t_obj.__name__} ---------------")
        print(f"Table Name = {t_obj.get_table()}")
        print(f"ID Col(s) = {t_obj.get_id_cols()}")
        print(f"Filter Fields = {t_obj._get_filter_fields()}")
        print(f"Json Fields = {t_obj._get_filter_fields()}")

        """
        values = vars(db_o)
        print(f"Additional Values:")
        for var in values:
            if values[var] not in t_obj.GetFilterFields():
                print(f"{var} = {values[var]}")
        """
