from datetime import datetime
import PySimpleGUI as sg
from sys import exit as sysexit
from FC_UIBuilder import ui_builder, TitledContent
from FC_DBAccess import dbAccessor
import FC_DataClasses as dc

class fc_present(ui_builder):
    def __init__(self):
        self.dba = dbAccessor()
    
    #region DBA Aliases
    # DBAccessor Methods have long names, these make things a bit pretties
    def get_w(self, nickname):
        return self.dba.GetWindowByNickname(nickname)
    #endregion

    #region Layout Factories
    # Setup Window
    def mk_lSetup(self):
        lSetup = [[sg.Text("Welcome to FollowerCenobite, register an account to get started:")]]
        lSetup.append(self.MakeTextInput('Instagram Username:',))
        lSetup.append(self.MakeTextInput('IG Nickname:', tip="Used for data file names"))
        lSetup.append([sg.Button('Start')])
        return lSetup
    
    def mk_lPrefs(self, prefs):
        lInit = [[sg.Text("Edit Prefereneces")]]
        
        # Add default acc dropdown!
        lInit.append(self.MakeTextInput('Path to Progress Folder:', prefs.progress_dir))
        lInit.append(self.MakeTextInput('Path to JSON Folder:', prefs.data_dir))
        lInit.append(self.MakeTextInput('Instagram URL:', prefs.ig_url))

        lInit.append([sg.Button('Overwrite')])
        lInit.append([sg.Button('Cancel')])

        return lInit

    def mk_lMain(self, win):
        # Get required data
        selectedAcc = self.dba.GetActiveIgAccount()
        follows = self.dba.GetMostRecentFollowsByAcc(selectedAcc)
        if len(follows) > 0:
            dfb = [f for f in follows if f.dfb()]
            idfb = [f for f in follows if f.idfb()]
            flwr = [f for f in follows if f.follower]
            flwg = [f for f in follows if f.following]
        else:
            
            headings = dc.follow.GetRowData()


        # Make Layout
        lMain = [self.MakeWindowMenu(win)]
        tabset = []
        tab_content = []
        tab_content.append(TitledContent("Don't Follow Back", self.MakeTable()))
        tab_content.append(TitledContent("I Don't Follow Back", self.MakeTable()))
        tab_content.append(TitledContent("Followers", self.MakeTable()))
        tab_content.append(TitledContent("Followings", self.MakeTable()))

        mainTg = self.MakeTabGroup(tabset)
        lMain.append(mainTg)
        lMain.append([sg.Button('Ok')])
        return lMain

    def mk_lCrawl(self, rsrc, subTypeId):
        lCrawl = []
        userList = self.userDict[subTypeId]
        # Tab Group
        tabData = [
            TitledContent(self.subTypeData[rsrc["subType"]][subTypeId]["MainTab"], userList), 
            TitledContent("Processed Users", [])
            ]
        for tab in tabData:
            tab.content = self.MakeTable(tab.content)
        mainTg = self.MakeTabGroup(tabData)
        lCrawl.append(mainTg)
        
        # Progress Bar
        progBar = self.MakeProgBar("crawlProg", len(userList))
        lCrawl.append(progBar)
        
        # Controls
        # Slider for number of windows to open
        # Consider how to open the next set of users and 
        return lCrawl
    #endregion

    #region Event Logic
    def wMainCapture(self, res):
        if "::" in res.event:
            rawEvent = res.event.split("::")
            eventName = rawEvent[1]
        else:
            eventName = res.event
        if eventName == "quit":
            sysexit("User quit from Menu")
    
        #Display defaults window, then reload main with new prefs!
        #if eventName == "dPrefs":
        #    dInit(defaults)

        if eventName.startswith("dCrawl_"):
            subType = eventName.split("_")[1]
            self.dCrawl(subType)
    #endregion

    #region Display Logic
    # Display a window, return window response for expected events
    def Display(self, win: dc.fc_window, layout: list[list]) -> ui_builder.WindowResponse | None:
        onClose = self.UserExit
        onExit = self.UserExit
        onCapture = self.UserCapture

        if win.onClose:
            onClose = getattr(self, win.onClose)
        if win.onExit:
            onExit = getattr(self, win.onExit)
        if win.onCapture:
            onCapture = getattr(self, win.onCapture)

        window = sg.Window(win.title, layout)
        while True:
            res = self.WindowResponse(*window.read())

            # User Closes Window
            if res.event == sg.WIN_CLOSED:
                onExit(win.nickname, res)

            # Close Event Fired
            if res.event in win.closeEvents:
                window.Close()
                onClose(win.nickname, res)
                return res
            
            # Capture Event Fired
            if onCapture and res.event in win.captureEvents:
                onCapture(win.nickname, res)
    
    def dPrefs(self):
        wPrefs = self.get_w("Pref")
        lPrefs = self.mk_lPrefs(self.prefs)
        return self.Display(wPrefs, lPrefs)

    def dSetup(self):
        wSetup = self.get_w("Setup")
        lSetup = self.mk_lSetup()
        return self.Display(wSetup, lSetup)

    def dMain(self):
        wMain = self.get_w("Main")
        lMain = self.mk_lMain(wMain)
        return self.Display(wMain, lMain)

    def dCrawl(self, subTypeId):
        wCrawl = self.get_w("Crawl")
        lCrawl = self.mk_lCrawl(wCrawl, subTypeId)
        return self.Display(wCrawl, lCrawl)
    #endregion

    #region UI Flows
    def start_ui(self):
        while (True):
            active_acc = None
            prefs = self.dba.GetActivePrefs()
            # Lookup active account if its not set to default
            if prefs.default_acc_id != 0:
                active_acc = self.dba.GetActiveIgAccount()
            
            # Show Setup window if the account can't be loaded, or its set to default
            if prefs.default_acc_id == 0 or not active_acc:
                startRes = self.dSetup()
                if startRes.event == "Start":
                    startAcc = self.dba.obj_f.ig_account(-1, startRes.values[0], startRes.values[1], datetime.today().strftime(self.dba.date_format))
                    startAcc.id = self.dba.insert(startAcc)
                    prefs.default_acc_id = startAcc.id
                    active_acc = startAcc
                    self.dba.SaveActivePrefs(prefs)
            
            # Start Main UI
            mainRes = self.dMain()