"""
FC_UI

View interface for FC.
"""
import customtkinter as ctk
from datetime import datetime
from FC_DBAccess import dbAccessor
import FC_UIBuilder as ui_b


def setup(dba: dbAccessor):
    """
    Get the active user account by getting one if it already exists,
    or by prompting the user to create a new account
    Args:
        dba (dbAccessor): the active database connection

    Returns:
        bool: value indicating if an active account could be created/loaded

    """

    active_acc = None
    prefs = dba.get_active_prefs()

    # Lookup active account if its not set to default
    if prefs.default_acc_id != 0:
        active_acc = dba.get_active_ig_account()

    # Show Setup window if the account is missing or default
    if prefs.default_acc_id == 0 or not active_acc:

        # Get ig account info with popup dialogs
        usrname = ctk.CTkInputDialog(text="Enter your Instagram Username:", title="FC User Setup")
        usrname = usrname.get_input()
        if not usrname:
            return False
        usr_abbrv = ctk.CTkInputDialog(text="Enter an abbreviation for your username:", title="FC User Setup")
        usr_abbrv = usr_abbrv.get_input()
        if not usr_abbrv:
            return False

        # Save new ig account to database
        startAcc = dba.obj_f.ig_account(-1, usrname, usr_abbrv, datetime.today().strftime(dba.date_format))
        startAcc.id = dba.save_ig_account(startAcc)
        if startAcc.id <= 0:
            ui_b.fc_warn(f"There was an issue saving {usrname} to the database", "Database Error")
        else:
            active_acc = startAcc
            prefs.default_acc_id = startAcc.id
            dba.save_active_prefs(prefs)

    # Check if an active account exists and the ID is not default (0) or null (-1)
    if active_acc and active_acc.id > 0:
        return True
    else:
        return False


# Need to restructure to UI Controller class,
# Seperate out generic controls into their own section, these are marked to be moved
# to a new repo of custom CTk UI components.
# UI Factory will hold global values like fonts, DBA, etc
class ui_factory():
    def __init__(self, dba: dbAccessor):
        self.dba = dba
        FONTFAM = "OCR A Extended"
        self.nav_font = ui_b.lazy(ctk.CTkFont, family=FONTFAM, size=16)
        self.title_font = ui_b.lazy(ctk.CTkFont, family=FONTFAM, size=18, weight="bold")
        self.body_font = ui_b.lazy(ctk.CTkFont, family=FONTFAM, size=16)

    def fc_warn(self,
                title,
                warning,
                body="",
                light_icon="",
                dark_icon="",
                *args,
                **kwargs):
        return ui_b.fc_warn(warning, body, light_icon, dark_icon, title, body_font=self.body_font, title_font=self.title_font,
                            image_dir=self.dba.image_path, *args, **kwargs)

    def fc_app(self,
               *args,
               **kwargs):
        return ui_b.fc_app(self.nav_font, self.title_font, self.dba.image_path, *args, **kwargs)

if __name__ == "__main__":
    fact = ui_factory(dbAccessor())
    w = fact.fc_warn("AAA",  "BBB")
    w.mainloop()
    # a = fc_warn("testwarn", body="TESTbodaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", title="TESTTITLE", image_dir=r"C:\Users\KarmaThief\Desktop\OddFood\Web_Assets\FollowerCenobite\ProgramData\Images")
    # a.mainloop()
