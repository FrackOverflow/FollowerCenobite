from collections import namedtuple
import PySimpleGUI as sg
from sys import exit as sysexit
import FC_DataClasses as dc

class TitledContent():
    def __init__(self, title, content):
        self.title = title
        self.content = content

class ui_builder():
    WindowResponse = namedtuple("WindowResponse", ["event", "values"])
    IgUser = namedtuple("IgUser",["username","full_name"])
    #region Simple UI Responses
    # Shutdown and indicate the User exited the program
    def UserShutdown(self, title, res):
        sysexit(f"The User exited the program from the {title} window, final event was  {res.event}")

    # Indicate the user exited the window
    def UserExit(self, title, res):
        print(f"The User exited the {title} window, final event was {res.event}")

    def UserCapture(self, title, res):
        print(f"{res.event} captured from the {title} window")
    #endregion

    #region Components
    def MakeTextInput(self, label, defaultValue = "", tip = ""):
        text = sg.Text(label)
        tinput = sg.InputText(defaultValue)
        if tip:
            text.tooltip = tip
        return [text, tinput]

    def MakeTabGroup(self, tcList):
        tabs = []
        for tc in tcList:
            tabs.append([sg.Tab(tc.title, tc.content)])
        return [sg.TabGroup(tabs)]

    def MakeTable(self, dataRecords: list[dc.dbObj], headings = []):
        #Flatten records to 2D list
        if dataRecords and not headings:
            headings = list(dataRecords[0].GetDisplayData().keys())
        tblData = [[r.values()] for r in dataRecords]
        return [[sg.Table(tblData, headings=headings)]]

    def MakeWindowMenu(self, win):
        menu = self.dba.GetMenuById(win.menu_id)
        return [sg.Menu(menu.menu_def)]

    def MakeProgBar(self, units, name):
        return [sg.ProgressBar(units, key=name)]
    #endregion
    