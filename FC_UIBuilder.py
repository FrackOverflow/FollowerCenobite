"""
FC_UIBuilder
UIBuilder handles dumb presentation logic. Only FC_UI.py should reference
this module. This module should never interact with controller classes.

This module is marked to be split into a seperate repo for reuse.
Please make your code here as reusable as possible.
"""
from datetime import datetime
import customtkinter as ctk
from PIL import Image
import os


# region Generic Components
class lazy():
    """
    Lazy type for CTk components that
    must be created before CTk is initialized.
    """
    def __init__(self, a_type, **kwargs):
        self.kwargs = kwargs
        self.type = a_type

    def get(self):
        return self.type(**self.kwargs)


class label_entry(ctk.CTkFrame):
    """ Labled text entry."""
    def __init__(self,
                 lbl_text,
                 placeholder_text="",
                 side=ctk.LEFT,
                 fill=ctk.X,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.label = ctk.CTkLabel(self, text=lbl_text)
        self.label.pack(side=side)
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder_text)
        self.entry.pack(side=side, fill=fill, expand=True)


class fs_entry(label_entry):
    """ File/Dir entry component."""
    def __init__(self,
                 lbl_text,
                 placeholder_text="",
                 dir_only=False,
                 btn_text="...",
                 side=ctk.LEFT,
                 initial_dir="",
                 *args,
                 **kwargs):
        super().__init__(lbl_text=lbl_text, placeholder_text=placeholder_text, side=side, *args, **kwargs)
        kwargs.pop("master")
        self.dir_only = dir_only
        self.button = ctk.CTkButton(master=self, text=btn_text, command=self._fs_select, **kwargs)
        self.button.pack(side=side)
        self.initial_dir = initial_dir

    def _fs_select(self):
        # Open file dialog and return selected file name
        if self.initial_dir and os.path.isdir(self.initial_dir):
            path = ctk.filedialog.askdirectory(self.initial_dir) if self.dir_only else ctk.filedialog.askopenfilename(self.initial_dir)
        else:
            path = ctk.filedialog.askdirectory() if self.dir_only else ctk.filedialog.askopenfilename()
        if path:
            self.entry.delete(0, -1)
            self.entry.insert(0, path)
        return path


class file_detect(ctk.CTkFrame):
    """ File detector button and output"""
    def __init__(self,
                 file_names=[],
                 path="",
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.btn_detect = ctk.CTkButton(self, text="Detect Files", command=self.detect_files)
        self.btn_detect.pack(side=ctk.BOTTOM, fill=ctk.X, expand=True)
        self.lbl_detect = ctk.CTkLabel(self, text="Files Detected:\t", justify=ctk.LEFT)
        self.lbl_detect.pack(side=ctk.TOP, fill=ctk.X, expand=True)
        self.file_names = file_names
        self.path = path

    def detect_files(self):
        files = os.listdir(self.path)
        count = 0
        for f in files:
            if os.path.isfile(os.path.join(self.path, f)) and f.endswith(".json") and f.startswith([self.file_names]):
                count += 1

        self.lbl_detect.configure(True, text=f"Files Detected:\t{count}")
        # TEST ME!
        # Report files that match but date cannot be parsed


class fc_dialogue(ctk.CTk):
    def __init__(self,
                 title,
                 body_font: lazy,
                 title_font: lazy,
                 image_dir=""):
        super().__init__()
        self.title = title
        self.image_dir = image_dir
        self.body_font = body_font.get()
        self.title_font = title_font.get()


class fc_warn(fc_dialogue):
    DEFAULT_ICON = {"Light": "db_err_light2.png",
                    "Dark": "db_err_dark.png"}

    def __init__(self,
                 warning,
                 body="",
                 light_icon="",
                 dark_icon="",
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.f_main = ctk.CTkFrame(self)
        self.f_main.pack(anchor=ctk.CENTER, padx=30, pady=30, fill=ctk.BOTH)
        # Warning Frame
        f_warn = ctk.CTkFrame(self.f_main)

        # Warning Icon
        if self.image_dir:
            if not light_icon:
                light_icon = self._get_def_icon()["Light"]
            if not dark_icon:
                dark_icon = self._get_def_icon()["Dark"]
            self.icon = ctk.CTkImage(size=(40, 40), light_image=Image.open(os.path.join(self.image_dir, light_icon)), dark_image=Image.open(os.path.join(self.image_dir, dark_icon)))
            ctk.CTkLabel(f_warn, text="", image=self.icon).pack(side=ctk.LEFT)

        # Warning Message
        self.lbl_warn = ctk.CTkLabel(f_warn, font=self.title_font, text=warning, justify=ctk.LEFT)
        self.lbl_warn.pack(side=ctk.LEFT, padx=10)
        f_warn.pack(anchor='w', pady=20, padx=40)

        # Warning Body
        if body:
            self.lbl_body = ctk.CTkLabel(self.f_main, font=self.body_font, text=body, justify=ctk.LEFT, wraplength=380)
            self.lbl_body.pack(anchor='w', fill=ctk.BOTH, padx=20, pady=10)

        self.btn_cls = ctk.CTkButton(self.f_main, font=self.body_font, text="Close", command=self.destroy)
        self.btn_cls.pack(side=ctk.BOTTOM, pady=20, anchor="center")

    @classmethod
    def _get_def_icon(cls):
        return cls.DEFAULT_ICON.copy()
# endregion


class f_base(ctk.CTkFrame):
    """ Base class for FC frames."""
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)


class f_main(f_base):
    """ Base class for frames that display in the main content area."""
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(corner_radius=0, fg_color="transparent", *args, **kwargs)


class fc_app(ctk.CTk):
    """
    FC App
    The main view class for FC
    """

    def __init__(self,
                 nav_font: lazy,
                 title_font: lazy,
                 image_path: str,
                 theme_path: str = ""):
        super().__init__()

        # Window Setup
        self.title("Follower Cenobite")
        self.geometry("1080x600")
        self.image_path = image_path
        #if theme_path:
        #    ctk.set_default_color_theme(theme_path)

        # 1x2 Grid Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Load images/fonts
        self._ld_images()

        # Navigation Frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="  Follower Cenobite", image=self.logo_image,
                                                   compound="left", font=title_font.get())
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.crawler_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Crawler",
                                            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                            image=self.crawler_image, anchor="w", command=self._clk_btn_crawler, font=nav_font.get())
        self.crawler_button.grid(row=1, column=0, sticky="ew")

        self.import_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Data Import",
                                           fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                           image=self.import_image, anchor="w", command=self._clk_btn_import, font=nav_font.get())
        self.import_button.grid(row=2, column=0, sticky="ew")

        self.settings_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Settings",
                                             fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                             image=self.settings_image, anchor="w", command=self._clk_btn_settings, font=nav_font.get())
        self.settings_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                      command=self._chg_ddl_theme)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Make Frames
        self.crawler_frame = f_crawler(self)
        self.import_frame = f_import(self)
        self.settings_frame = f_settings(self)
        self._get_f_by_name("crawler")

    def _ld_images(self):
        # Load Images (Consider Light & Dark Mode!)
        self.logo_image = ctk.CTkImage(Image.open(os.path.join(self.image_path, "fc_logo.png")), size=(39, 39))

        self.crawler_image = ctk.CTkImage(dark_image=Image.open(os.path.join(self.image_path, "crawler_dark.png")),
                                          light_image=Image.open(os.path.join(self.image_path, "crawler_light.png")), size=(30, 30))
        self.import_image = ctk.CTkImage(dark_image=Image.open(os.path.join(self.image_path, "import_dark.png")),
                                         light_image=Image.open(os.path.join(self.image_path, "import_light.png")), size=(30, 30))
        self.settings_image = ctk.CTkImage(dark_image=Image.open(os.path.join(self.image_path, "settings_dark.png")),
                                           light_image=Image.open(os.path.join(self.image_path, "settings_light.png")), size=(30, 30))

    def _get_f_by_name(self, name):
        # Get frame by name

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

    def _clk_btn_crawler(self):
        self._get_f_by_name("crawler")

    def _clk_btn_import(self):
        self._get_f_by_name("import")

    def _clk_btn_settings(self):
        self._get_f_by_name("settings")

    def _chg_ddl_theme(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)


class f_import(f_main):
    """ Data Import frame."""
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        # 1x2 grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=2)

        self._mk_import_detail()
        self._mk_import_general()
        self._register_events()

    def _mk_import_detail(self):
        """ Makes import detail frame with Manual/Auto tabs."""

        # Import detail frame
        self.f_detail = ctk.CTkFrame(self, corner_radius=0)
        self.f_detail.grid(row=0, column=0, sticky="nsew", columnspan=3)

        self.import_tabview = ctk.CTkTabview(self.f_detail)
        self.import_tabview.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)
        self.import_mantab = self.import_tabview.add("Manual")
        self.import_autotab = self.import_tabview.add("Auto")

        # Manual Tab
        self.import_mantab.grid_columnconfigure(0, weight=1)
        self.import_mantab.grid_rowconfigure([0, 1], weight=0)
        self.entr_flwg_man = fs_entry(lbl_text="Follower JSON\t", placeholder_text="Path/To/Followers.json", master=self.import_mantab)
        self.entr_flwg_man.grid(row=0, column=0, sticky="new", padx=15, pady=20)
        self.entr_flwr_man = fs_entry(lbl_text="Following JSON\t", placeholder_text="Path/To/Following.json", master=self.import_mantab)
        self.entr_flwr_man.grid(row=1, column=0, sticky="new", padx=15, pady=20)

        # Auto Tab
        self.import_autotab.grid_columnconfigure(0, weight=1)
        self.import_autotab.grid_rowconfigure([0, 1, 2], weight=0)
        self.import_autotab.grid_rowconfigure([3, 4], weight=1)

        self.entr_flwr_auto = label_entry(lbl_text="Follower Abbrv\t", placeholder_text="Follower File Abbrv", master=self.import_autotab)
        self.entr_flwr_auto.grid(row=0, column=0, sticky="new", padx=15, pady=20)

        self.entr_flwg_auto = label_entry(lbl_text="Following Abbrv\t", placeholder_text="Following File Abbrv", master=self.import_autotab)
        self.entr_flwg_auto.grid(row=1, column=0, sticky="new", padx=15, pady=20)

        # Date string must conform to https://docs.python.org/3/library/datetime.html#format-codes
        self.entr_date_format = label_entry(lbl_text="Date Format\t", placeholder_text="%d%M_%Y", master=self.import_autotab)
        self.entr_date_format.grid(row=2, column=0, sticky="new", padx=15, pady=20)
        self.preview = ctk.CTkLabel(self.import_autotab, text="File Name Format\n\nFollower\nFollowing", justify=ctk.LEFT)
        self.preview.grid(row=3, column=0, sticky="nws", padx=15, pady=20)
        self.detect_frame = ctk.CTkFrame(self.import_autotab, corner_radius=0)
        self.btn_detect = file_detect(self.entr_flwg_auto, self.entr_flwr_auto, self.entr_date_format, master=self.detect_frame)
        self.btn_detect.pack(side=ctk.RIGHT)
        self.detect_frame.grid(row=4, column=0, sticky="sw", padx=15, pady=20)
        
    def _register_events(self):
        for event in ["<FocusOut>", "<Leave>", "<Enter>", "<Return>"]:
            self.entr_flwg_auto.entry.bind(event, self.update_preview)
            self.entr_flwr_auto.entry.bind(event, self.update_preview)
            self.entr_date_format.entry.bind(event, self.update_preview)
            self.entr_file_path.entry.bind(event, self.update_file_path)

        # Wire up file detect
    def _mk_import_general(self):
        # Setup General options frame
        self.f_general = ctk.CTkFrame(self, corner_radius=0)
        self.f_general.grid(row=0, column=4, sticky="nsew")
        self.f_general.grid_columnconfigure(0, weight=1)
        self.f_general.grid_rowconfigure(3, weight=1)

        self.btn_run = ctk.CTkButton(self.f_general, text="Run")
        self.btn_run.grid(row=3, column=0, sticky="s", padx=15, pady=15)

        self.user_ddl = ctk.CTkOptionMenu(self.f_general, values=["User1", "User2", "User3"], command=self.update_preview)
        self.user_ddl.grid(row=0, column=0, sticky="n", padx=15, pady=15)

        self.entr_file_path = fs_entry("Data Folder\t", r"Path\To\Data\Folder\\", True, master=self.f_general, side=ctk.TOP)
        self.entr_file_path.grid(row=1, column=0, sticky="n", padx=15, pady=15)

    def update_file_path(self, _):
        data_dir = self.entr_file_path.entry.get()
        self.entr_flwg_man.initial_dir = data_dir
        self.entr_flwg_man.initial_dir = data_dir
        self.btn_detect.path = data_dir

    def update_preview(self, _):
        date_str = datetime.today().strftime(self.entr_date_format.entry.get())
        suffix = f"{date_str}.json"
        middle = f"_{self.user_ddl.get()}_"
        flwr = self.entr_flwr_auto.entry.get()
        flwg = self.entr_flwg_auto.entry.get()
        preview_text = f"File Name Format\n\nFollower\t{flwr}{middle}{suffix}\nFollowing\t{flwg}{middle}{suffix}"
        self.preview.configure(True, text=preview_text)
        self.btn_detect.file_names = [f"{flwr}{middle}", f"{flwg}{middle}"]


# Seperate into classes, remove DBA ------
class f_crawler(f_main):
        def __init__(self,
                     *args,
                     **kwargs):
            super().__init__(*args, **kwargs)
            # Make the CTk frame for the crawler tab
            frame = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
            frame.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(frame, text="CRAWLER").pack()
            self.crawler_tabview = ctk.CTkTabview(frame)
            f_flwr = self.crawler_tabview.add("Follwers")
            f_flwg = self.crawler_tabview.add("Following")
            f_dfb = self.crawler_tabview.add("DFB")
            f_idfb = self.crawler_tabview.add("IDFB")

            # Get follower data
            """selectedAcc = self.dba.get_active_ig_account()
            follows = self.dba.get_newest_follows_by_acc(selectedAcc)
            if len(follows) > 0:
                headings = []
                dfb = [f for f in follows if f.dfb()][0:100]
                idfb = [f for f in follows if f.idfb()][0:100]
                flwr = [f for f in follows if f.follower][0:100]
                flwg = [f for f in follows if f.following][0:100]
            else:
                headings = ["Username", "Account Id", "Date", "Follower", "Following"]
                dfb = idfb = flwr = flwg = []"""
            # keys = dc.follow.
            #for (dataview, frame) in [(flwr, f_flwr), (flwg, f_flwg), (dfb, f_dfb), (idfb, f_idfb)]:
                #if dataview:
                    #self._mk_table(headings, dataview, [])
                #else:
                    #self._mk_table(headings, [], [])

        def _mk_table(self, headings, data, ordered_keys):
            # Make a table for displaying data
            # for i in range(len(headings))
            return None


class f_settings(f_main):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        # Make the frame for the settings tab
        frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        ctk.CTkLabel(frame, text="SETTINGS").pack()
