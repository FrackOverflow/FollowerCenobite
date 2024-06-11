"""
FC_DBAccess

Contains controller classes for abstracted interaction with the DB
"""
from datetime import datetime
import json
from os import remove
from os.path import isfile
import FC_DataClasses as dc
from FC_DBConnect import fcdb, Struct


class dbAccessor(fcdb):
    """
    FC Controller Class
    Contains high-level methods for updating model with dbObj classes
    """

    def __init__(self, about="FC_About.json"):
        super(dbAccessor, self).__init__(about)
        self.menus = {}
        self.windows = {}
        self.w_subtypes = {}
        self.ig_accs = {}

    # region Low Level
    def _get_all_obj(self, T: type[dc.dbObj]):
        return self._select(T)

    def _get_obj_by_id(self, T: type[dc.dbObj], id):
        return self.first_or(None, self._select(T, suffix=f"WHERE id = {id}"))

    def _get_last_row(self, T: type[dc.dbObj]):
        return self.first_or(None, self._select(T, suffix=f"ORDER BY ({', '.join(T.get_id_cols())}) DESC LIMIT 1"))

    def _get_last_id(self, T: type[dc.dbObj]):
        firstId = struct()
        firstId.id = 0
        return self.first_or(firstId, self._select(T, suffix=f"ORDER BY ({', '.join(T.get_id_cols())}) DESC LIMIT 1")).id
    # endregion

    # region Cached
    def get_active_prefs(self) -> dc.preference:
        """ Get currently active preferences."""
        if not hasattr(self, "active_prefs"):
            self.active_prefs = self.first_or(None, self._select(dc.preference, suffix="ORDER BY id DESC"))
        return self.active_prefs

    def save_active_prefs(self, prefs):
        """Updates prefs in DB and sets active prefs on DB connection."""
        self.set_new_prefs(prefs)
        return self._update(prefs)

    def get_ig_accounts(self):
        """ Get all registered IG accounts."""
        if not self.ig_accs:
            self.ig_accs = {x.id: x for x in self._get_all_obj(dc.ig_account)}
        return self.ig_accs

    def get_ig_account_by_id(self, id):
        """ Get an IG account using ID."""
        if not self.ig_accs:
            self.get_ig_accounts()
        return self.ig_accs.get(id)

    def save_ig_account(self, acc: dc.ig_account):
        """ Save an IG account to DB."""
        return self._insert(acc)

    def get_active_ig_account(self):
        """ Get the active IG account."""
        if not self.active_prefs:
            self.get_active_prefs()
        if not self.ig_accs:
            self.get_ig_accounts()
        return self.ig_accs.get(self.active_prefs.default_acc_id)
    # endregion

    # region Not Cached
    def get_follows_by_acc(self, acc):
        """ Get all follows by Account."""
        return self._select(dc.follow, suffix=f"WHERE acc_id = {acc.id}")

    def get_last_follows_by_acc(self, acc: dc.ig_account) -> list[dc.last_follow]:
        """ Get all last_follows by Account."""
        return self._select(dc.last_follow, suffix=f"WHERE acc_id = {acc.id}")

    def get_flws_by_last_flw(self, lf: dc.last_follow):
        """ Get follows referenced on a last_follow."""
        flws = []
        if lf.last_follower_id:
            flws.append(self._select(dc.follow, suffix=f"WHERE id = {lf.last_follower_id}"))
        if lf.last_following_id:
            if lf.last_follower_id != lf.last_following_id:
                flws.append(self._select(dc.follow, suffix=f"WHERE id = {lf.last_following_id}"))
        return flws

    def get_newest_follows_by_acc(self, acc) -> list[dc.follow]:
        """ Get all the newest follows for each user following an account."""
        lfs = self.get_last_follows_by_acc(acc)
        recent_flws = []
        for lf in lfs:
            flws = self.get_flws_by_last_flw(lf)
            if len(flws) == 1:
                recent_flws.append(flws[0])
            if len(flws) == 2:
                recent_flws.append(flws[0] if flws[0] > flws[1] else flws[1])
        return recent_flws
    # endregion

    # region JsonProcessing
    def munch_follow_data(self, follower_json, following_json, acc_id, date):
        """ Process json follower data into database."""
        # Load Json Data
        f_flwr = open(follower_json, encoding="utf-8-sig")
        f_flwg = open(following_json, encoding="utf-8-sig")
        flwr = next(iter(json.load(f_flwr).values()))
        flwg = next(iter(json.load(f_flwg).values()))

        # Get all users in Json
        s_flwr = set([x["username"] for x in flwr])
        s_flwg = set([x["username"] for x in flwg])
        all_known = s_flwg.union(s_flwr)

        # Initialize variables for parsing last follows
        commit_follows = []
        commit_last_follows = []
        last_id = self.get_last_id(dc.follow)
        for user in all_known:
            last_id += 1
            isflwr = False
            isflwg = False
            lFlwgId = None
            lFlwrId = None
            if user in s_flwr:
                isflwr = True
                lFlwrId = last_id
            if user in s_flwg:
                isflwg = True
                lFlwgId = last_id
            follow = self.obj_f.follow(last_id, user, acc_id, date, isflwr, isflwg)
            commit_follows.append(follow)

            # If last follow is found compare follow date with current
            existing_lf = self._select(dc.last_follow, suffix=f"WHERE username = {self._col_data(user)} AND acc_id = {acc_id}")
            if len(existing_lf) == 1:
                ex_lf = existing_lf[0]
                if ex_lf.last_follower_id:
                    f_lFlwr = self._select(dc.follow, suffix=f"WHERE id = {ex_lf.last_follower_id}")[0]
                    if f_lFlwr < follow:
                        ex_lf.last_follower_id = follow.id
                if ex_lf.last_following_id:
                    f_lFlwg = self._select(dc.follow, suffix=f"WHERE id = {ex_lf.last_following_id}")[0]
                    if f_lFlwg < follow:
                        ex_lf.last_following_id = follow.id

                # Only update if newer is found.
                if f_lFlwr < follow or f_lFlwg < follow:
                    commit_last_follows.append(ex_lf)

            # If no existing last follow the user is new
            if len(existing_lf) == 0:
                commit_last_follows.append(self.obj_f.last_follow(user, acc_id, lFlwgId, lFlwrId))
            if len(existing_lf) > 1:
                print(f"Constraint Violation: Multiple Last Follows were found for user/account pair {user}, {acc_id}")

        self._binsert(commit_follows)
        self._bupsert(commit_last_follows)
        # We could make this quicker by determining which records are inserts vs updates and doing 2 bulk calls.

        # We currently don't mark users as "unfollowed" if there is no record in follower/following, but this could happen if we both unfollow eachother
        # To track this we need to track when the last import for a user was, get it when we start the import, and look for any "follow" records with
        # the previous import date that don't show up in follower or following. IS THERE ANY BENEFIT TO TRACKING THIS??

        # When we import we should create a new GUID and save it in an "imports" table which will track when a follow record was imported
        # To roll back, we can show a list of imports and let the user select an import to rollback to. We should then delete the
    # endregion


if __name__ == "__main__":
    dbname = r"ProgramData\TestData\TEST_FC.db"
    try:
        db = dbAccessor(r"ProgramData/TestData/TEST_FC_About.json")
        db.munch_follow_data(r"ProgramData\FollowerJson\OF_Flwg_May30_2024.json", r"ProgramData\FollowerJson\OF_Flwr_May30_2024.json", 1, datetime.today().strftime("%b%d_%Y"))
        db.munch_follow_data(r"ProgramData\FollowerJson\OF_Flwg_May31_2024.json", r"ProgramData\FollowerJson\OF_Flwr_May31_2024.json", 1, datetime.today().strftime("%b%d_%Y"))
    finally:
        if isfile(dbname):
            remove(dbname)
