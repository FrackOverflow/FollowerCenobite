from FC_DBAccess import dbAccessor
from FC_UI import MainApp, setup, warning


class FollowerCenobite():
    def main(self):
        self.dba = dbAccessor()
        if setup(self.dba):
            MainApp(self.dba)
        else:
            warning("Setup Failed, please try again.", "FC Setup Failed")

        
if __name__ == "__main__":
    fc = FollowerCenobite()
    fc.main()