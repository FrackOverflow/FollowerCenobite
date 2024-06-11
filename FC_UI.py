import customtkinter
import os
from PIL import Image
from datetime import datetime
from FC_DBAccess import dbAccessor


class fc_app(customtkinter.CTk):
    """
    FC View class.
    Contains all UI logic for FC
    """

    def __init__(self, dba: dbAccessor):
        super().__init__()

        # Window Setup
        self.dba = dba
        self.title("Follower Cenobite")
        self.geometry("700x450")

        # 1x2 Grid Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Images (Light & Dark Mode!)
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "FormatMe/test_images/")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "large_test_image.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.crawler_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                    dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

        # Navigation Frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Follower Cenobite", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.crawler_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Crawler",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.crawler_image, anchor="w", command=self._crawler_button_event)
        self.crawler_button.grid(row=1, column=0, sticky="ew")

        self.import_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Data Import",
                                                     fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                     image=self.chat_image, anchor="w", command=self._import_button_event)
        self.import_button.grid(row=2, column=0, sticky="ew")

        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Settings",
                                                       fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       image=self.add_user_image, anchor="w", command=self._settings_button_event)
        self.settings_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Make Frames
        self.crawler_frame = self._mk_crawler_frame()
        self.import_frame = self._mk_import_frame()
        self.settings_frame = self._mk_settings_frame()
        self._slct_frame_by_name("crawler")

    def _mk_crawler_frame(self):
        # Make the CTk frame for the crawler tab
        frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(frame, text="CRAWLER").pack()
        self.crawler_tabview = customtkinter.CTkTabview(frame)
        f_flwr = self.crawler_tabview.add("Follwers")
        f_flwg = self.crawler_tabview.add("Following")
        f_dfb = self.crawler_tabview.add("DFB")
        f_idfb = self.crawler_tabview.add("IDFB")

        # Get follower data
        selectedAcc = self.dba.get_active_ig_account()
        follows = self.dba.get_newest_follows_by_acc(selectedAcc)
        if len(follows) > 0:
            headings = []
            dfb = [f for f in follows if f.dfb()][0:100]
            idfb = [f for f in follows if f.idfb()][0:100]
            flwr = [f for f in follows if f.follower][0:100]
            flwg = [f for f in follows if f.following][0:100]
        else:
            headings = ["Username", "Account Id", "Date", "Follower", "Following"]
            dfb = idfb = flwr = flwg = []
        # keys = dc.follow.
        #for (dataview, frame) in [(flwr, f_flwr), (flwg, f_flwg), (dfb, f_dfb), (idfb, f_idfb)]:
            #if dataview:
                #self._mk_table(headings, dataview, [])
            #else:
                #self._mk_table(headings, [], [])

        return frame

    def _mk_table(self, headings, data, ordered_keys):
        # Make a table for displaying data
        # for i in range(len(headings))
        return None

    def _mk_import_frame(self):
        # Make the frame for the import tab
        frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        customtkinter.CTkLabel(frame, text="IMPORT").pack()
        return frame

    def _mk_settings_frame(self):
        # Make the frame for the settings tab
        frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        customtkinter.CTkLabel(frame, text="SETTINGS").pack()
        return frame

    def _slct_frame_by_name(self, name):
        # set button color for selected button
        self.crawler_button.configure(fg_color=("gray75", "gray25") if name == "crawler" else "transparent")
        self.import_button.configure(fg_color=("gray75", "gray25") if name == "import" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")

        # show selected frame
        if name == "crawler":
            self.crawler_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.crawler_frame.grid_forget()
        if name == "import":
            self.import_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.import_frame.grid_forget()
        if name == "settings":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.settings_frame.grid_forget()

    def _crawler_button_event(self):
        self.select_frame_by_name("crawler")

    def _import_button_event(self):
        self.select_frame_by_name("import")

    def _settings_button_event(self):
        self.select_frame_by_name("settings")

    def _change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


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
        usrname = customtkinter.CTkInputDialog(text="Enter your Instagram Username:", title="FC User Setup")
        usrname = usrname.get_input()
        if not usrname:
            return False
        usr_abbrv = customtkinter.CTkInputDialog(text="Enter an abbreviation for your username:", title="FC User Setup")
        usr_abbrv = usr_abbrv.get_input()
        if not usr_abbrv:
            return False

        # Save new ig account to database
        startAcc = dba.obj_f.ig_account(-1, usrname, usr_abbrv, datetime.today().strftime(dba.date_format))
        startAcc.id = dba.save_ig_account(startAcc)
        if startAcc.id <= 0:
            warning(f"There was an issue saving {usrname} to the database", "Database Error")
        else:
            active_acc = startAcc
            prefs.default_acc_id = startAcc.id
            dba.save_active_prefs(prefs)

    # Check if an active account exists and the ID is not default (0) or null (-1)
    if active_acc and active_acc.id > 0:
        return True
    else:
        return False


def warning(body, title):
    """
    Creates a simple warning dialog

    Args:
        body (str): Dialog Body
        title (str): Dialog title
    """
    window = customtkinter.CTk()
    window.title = title
    window.geometry("240x120")
    customtkinter.CTkLabel(window, text=body, justify=customtkinter.LEFT).pack()
    customtkinter.CTkButton(window, text="Close", command=window.destroy).pack()
    window.mainloop()
