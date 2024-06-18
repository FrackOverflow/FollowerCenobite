"""
FollowerCenobite

FollowerCenobite is gives a detailed view of Instagram data over time.
FC is not a bot, it consumes JSON data about follows/likes and allows
you to drill down and see your relationship with users across multiple
accounts.
"""
from FC_DBAccess import dbAccessor
from FC_UI import ui_factory, setup


class FollowerCenobite():
    """
    FC App
    Entry point for FollowerCenobite
    """
    def main(self):
        self.dba = dbAccessor()
        ui_f = ui_factory(self.dba)
        if setup(self.dba):
            app = ui_f.fc_app(self.dba)
            app.mainloop()
        else:
            ui_f.fc_warn("Setup Failed, please try again.", "FC Setup Failed")


if __name__ == "__main__":
    fc = FollowerCenobite()
    fc.main()
