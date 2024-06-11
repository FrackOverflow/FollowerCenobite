from datetime import datetime
import json
from os import remove
from os.path import isfile
import FC_DataClasses as dc
from FC_DBConnect import fcdb, struct


class dbAccessor(fcdb):
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
    # Gets currently active preferences
    def get_active_prefs(self) -> dc.preference:
        if not hasattr(self, "active_prefs"):
            self.active_prefs = self.first_or(None, self._select(dc.preference, suffix="ORDER BY id DESC"))
        return self.active_prefs

    # Updates prefs in DB and sets active prefs on DB connection and DB Obj factory
    def save_active_prefs(self, prefs):
        self.set_new_prefs(prefs)
        return self._update(prefs)

    def get_ig_accounts(self):
        if not self.ig_accs:
            self.ig_accs = {x.id: x for x in self._get_all_obj(dc.ig_account)}
        return self.ig_accs

    def get_ig_account_by_id(self, id):
        if not self.ig_accs:
            self.get_ig_accounts()
        return self.ig_accs.get(id)

    def save_ig_account(self, acc: dc.ig_account):
        return self._insert(acc)

    def get_windows(self):
        if not self.windows:
            self.windows = {x.id: x for x in self._get_all_obj(dc.fc_window)}
        return self.windows

    def get_window_by_id(self, id):
        if not self.windows:
            self.get_windows()
        return self.windows.get(id)

    def get_window_by_bickname(self, nickname):
        if not self.windows:
            self.get_windows()
        # This comprehension looks weird cause it needs to parse the id: value format cache dicts.
        return next((v for k, v in self.windows.items() if v.nickname == nickname), None)

    def get_win_subtypes(self):
        if not self.w_subtypes:
            self.w_subtypes = {x.id: x for x in self._get_all_obj(dc.fc_window_subtype)}
        return self.w_subtypes

    def get_win_subtype_by_id(self, id):
        if not self.w_subtypes:
            self.get_win_subtypes()
        return self.w_subtypes.get(id)

    def get_menus(self):
        if not self.menus:
            self.menus = {x.id: x for x in self._get_all_obj(dc.fc_menu)}
        return self.menus

    def get_menuById(self, id):
        if not self.menus:
            self.get_menus()
        return self.menus.get(id)

    def get_active_ig_account(self):
        if not self.active_prefs:
            self.get_active_prefs()
        if not self.ig_accs:
            self.get_ig_accounts()
        return self.ig_accs.get(self.active_prefs.default_acc_id)
    # endregion

    # region Not Cached
    def get_follows_by_acc(self, acc):
        return self._select(dc.follow, suffix=f"WHERE acc_id = {acc.id}")

    def get_last_follows_by_acc(self, acc: dc.ig_account) -> list[dc.last_follow]:
        return self._select(dc.last_follow, suffix=f"WHERE acc_id = {acc.id}")

    def get_flws_by_last_flw(self, lf: dc.last_follow):
        flws = []
        if lf.last_follower_id:
            flws.append(self._select(dc.follow, suffix=f"WHERE id = {lf.last_follower_id}"))
        if lf.last_following_id:
            if lf.last_follower_id != lf.last_following_id:
                flws.append(self._select(dc.follow, suffix=f"WHERE id = {lf.last_following_id}"))
        return flws

    def get_newest_follows_by_acc(self, acc) -> list[dc.follow]:
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
        self._bupsert(commit_last_follows)  # We could make this quicker by determining which records are inserts vs updates and doing 2 bulk calls. 
    # endregion


if __name__ == "__main__":
    dbname = "ProgramData\TestData\TEST_FC.db"
    try:
        db = dbAccessor("ProgramData/TestData/TEST_FC_About.json")
        db.munch_follow_data("ProgramData\FollowerJson\OF_Flwg_May30_2024.json", "ProgramData\FollowerJson\OF_Flwr_May30_2024.json", 1, datetime.today().strftime("%b%d_%Y"))
        db.munch_follow_data("ProgramData\FollowerJson\OF_Flwg_May31_2024.json", "ProgramData\FollowerJson\OF_Flwr_May31_2024.json", 1, datetime.today().strftime("%b%d_%Y"))
    finally:
        if isfile(dbname):
            remove(dbname)
