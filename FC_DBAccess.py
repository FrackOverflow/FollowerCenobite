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
    
#region Low Level
    def GetAllObj(self, T: type[dc.dbObj]):
        return self.select(T)
    
    def GetObjById(self, T: type[dc.dbObj], id):
        return self.FirstOr(None, self.select(T, suffix=f"WHERE id = {id}"))
    
    def GetLastRow(self, T: type[dc.dbObj]):
        return self.FirstOr(None, self.select(T, suffix=f"ORDER BY ({', '.join(T.GetIdCols())}) DESC LIMIT 1"))
    
    def GetLastId(self, T: type[dc.dbObj]):
        firstId = struct()
        firstId.id = 0
        return self.FirstOr(firstId, self.select(T, suffix=f"ORDER BY ({', '.join(T.GetIdCols())}) DESC LIMIT 1")).id
#endregion

#region Cached
    # Gets currently active preferences
    def GetActivePrefs(self) -> dc.preference:
        if not hasattr(self, "active_prefs"):
            self.active_prefs = self.FirstOr(None, self.select(dc.preference, suffix="ORDER BY id DESC"))
        return self.active_prefs
    
    # Updates prefs in DB and sets active prefs on DB connection and DB Obj factory
    def SaveActivePrefs(self, prefs):
        self.SetNewPrefs(prefs)
        return self.update(prefs)
    
    def GetIgAccounts(self):
        if not self.ig_accs:
            self.ig_accs = {x.id: x for x in self.GetAllObj(dc.ig_account)}
        return self.ig_accs
    
    def GetIgAccountById(self, id):
        if not self.ig_accs:
            self.GetIgAccounts()
        return self.ig_accs.get(id)
    
    def GetWindows(self):
        if not self.windows:
            self.windows = {x.id: x for x in self.GetAllObj(dc.fc_window)}
        return self.windows
    
    def GetWindowById(self, id):
        if not self.windows:
            self.GetWindows()
        return self.windows.get(id)
    
    def GetWindowByNickname(self, nickname):
        if not self.windows:
            self.GetWindows()
        # This comprehension looks weird cause it needs to parse the id: value format cache dicts.
        return next((v for k, v in self.windows.items() if v.nickname == nickname), None)

    def GetWSubtypes(self):
        if not self.w_subtypes:
            self.w_subtypes = {x.id: x for x in self.GetAllObj(dc.fc_window_subtype)}
        return self.w_subtypes
    
    def GetWSubtypeById(self, id):
        if not self.w_subtypes:
            self.GetWSubtypes()
        return self.w_subtypes.get(id)
    
    def GetMenus(self):
        if not self.menus:
            self.menus = {x.id: x for x in self.GetAllObj(dc.fc_menu)}
        return self.menus
    
    def GetMenuById(self, id):
        if not self.menus:
            self.GetMenus()
        return self.menus.get(id)
    
    def GetActiveIgAccount(self):
        if not self.active_prefs:
            self.GetActivePrefs()
        if not self.ig_accs:
            self.GetIgAccounts()
        return self.ig_accs.get(self.active_prefs.default_acc_id)
#endregion

#region Not Cached
    def GetFollowsByAcc(self, acc):
        return self.select(dc.follow, suffix=f"WHERE acc_id = {acc.id}")
    
    def GetLastFollowsByAcc(self, acc: dc.ig_account) -> list[dc.last_follow]:
        return self.select(dc.last_follow, suffix=f"WHERE acc_id = {acc.id}")
    
    def GetFlwsByLastFlw(self, lf: dc.last_follow):
        flws = []
        if lf.last_follower_id:
            flws.append(self.select(dc.follow, suffix=f"WHERE id = {lf.last_follower_id}"))
        if lf.last_following_id:
            if lf.last_follower_id != lf.last_following_id:
                flws.append(self.select(dc.follow, suffix=f"WHERE id = {lf.last_following_id}"))
        return flws
    
    def GetMostRecentFollowsByAcc(self, acc):
        lfs = self.GetLastFollowsByAcc(acc)
        recent_flws = []
        for lf in lfs:
            flws = self.GetFlwsByLastFlw(lf)
            if len(flws) == 1:
                recent_flws.append(flws[0])
            if len(flws) == 2:
                recent_flws.append(flws[0] if flws[0] > flws[1] else flws[1])
        return recent_flws
#endregion

#region JsonProcessing
    def MunchFollowData(self, follower_json, following_json, acc_id, date):
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
        last_id = self.GetLastId(dc.follow) 
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
            existing_lf = self.select(dc.last_follow, suffix=f"WHERE username = {self.colData(user)} AND acc_id = {acc_id}")
            if len(existing_lf) == 1:
                ex_lf = existing_lf[0]
                if ex_lf.last_follower_id:
                    f_lFlwr = self.select(dc.follow, suffix=f"WHERE id = {ex_lf.last_follower_id}")[0]
                    if f_lFlwr < follow:
                        ex_lf.last_follower_id = follow.id
                if ex_lf.last_following_id:
                    f_lFlwg = self.select(dc.follow, suffix=f"WHERE id = {ex_lf.last_following_id}")[0]
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
        
        self.binsert(commit_follows)
        self.bupsert(commit_last_follows) # We could make this quicker by determining which records are inserts vs updates and doing 2 bulk calls. 
    #endregion

if __name__ == "__main__":
    dbname = "ProgramData\TestData\TEST_FC.db"
    try:
        db = dbAccessor("ProgramData/TestData/TEST_FC_About.json")
        db.MunchFollowData("ProgramData\FollowerJson\OF_Flwg_May30_2024.json", "ProgramData\FollowerJson\OF_Flwr_May30_2024.json", 1, datetime.today().strftime("%b%d_%Y"))
        db.MunchFollowData("ProgramData\FollowerJson\OF_Flwg_May31_2024.json", "ProgramData\FollowerJson\OF_Flwr_May31_2024.json", 1, datetime.today().strftime("%b%d_%Y"))
    finally:
        if isfile(dbname):
            remove(dbname)

