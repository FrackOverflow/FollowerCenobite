from FC_DBAccess import dbAccessor
from FC_UI import fc_app, setup, warning


class FollowerCenobite():
    """
    FC App Launcher, handles setup & context switching
    """
    def main(self):
        self.dba = dbAccessor()
        if setup(self.dba):
            app = fc_app(self.dba)
            app.mainloop()
        else:
            warning("Setup Failed, please try again.", "FC Setup Failed")


if __name__ == "__main__":
    fc = FollowerCenobite()
    fc.main()
