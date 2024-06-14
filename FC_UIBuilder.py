"""
FC_UIBuilder
UIBuilder handles dumb presentation logic. Only FC_UI.py should reference 
this module. This module should never interact with controller classes.
"""
import customtkinter as ctk


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


class f_import(f_main):
    """ Data Import frame."""
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        # 1x2 grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self._mk_import_detail()
        self._mk_import_general()

    def _mk_import_detail(self):
        """ Makes import detail frame with Manual/Auto tabs."""

        # Import detail frame
        self.f_detail = ctk.CTkFrame(self, corner_radius=0)
        self.f_detail.grid(row=0, column=0, sticky="nw", columnspan=3)

        self.import_tabview = ctk.CTkTabview(self.f_detail)
        self.import_tabview.pack(side=ctk.LEFT)
        self.import_mantab = self.import_tabview.add("Manual")
        self.import_autotab = self.import_tabview.add("Auto")

        # Manual Tab
        self.import_mantab.grid_columnconfigure(0, weight=1)
        self.import_mantab.grid_rowconfigure(1, weight=1)
        self.entr_flwg_man = fs_entry(lbl_text="Follower JSON: ", placeholder_text="Path/To/Followers.json", master=self.import_mantab)
        self.entr_flwg_man.grid(row=0, column=0, sticky="nw")
        self.entr_flwr_man = fs_entry(lbl_text="Following JSON: ", placeholder_text="Path/To/Following.json", master=self.import_mantab)
        self.entr_flwr_man.grid(row=1, column=0, sticky="nw")

        # Auto Tab
        self.import_autotab.grid_columnconfigure(0, weight=1)
        self.import_autotab.grid_rowconfigure(3, weight=1)
        self.entr_flwr_auto = label_entry(lbl_text="Follower Abbrv: ", placeholder_text="Follower File Abbrv", master=self.import_autotab)
        self.entr_flwr_auto.grid(row=0, column=0, sticky="nw")
        self.entr_flwg_auto = label_entry(lbl_text="Following Abbrv: ", placeholder_text="Following File Abbrv", master=self.import_autotab)
        self.entr_flwg_auto.grid(row=1, column=0, sticky="nw")
        self.entr_date_format = label_entry(lbl_text="Date Format: ", placeholder_text="%d%M_%Y", master=self.import_autotab)
        self.entr_date_format.grid(row=2, column=0, sticky="nw")
        self.btn_detect = file_detect(self.entr_flwg_auto, self.entr_flwr_auto, self.entr_date_format, master=self.import_autotab)
        self.btn_detect.grid(row=3, column=0, sticky="nw")

    def _mk_import_general(self):
        # Setup General options frame
        self.f_general = ctk.CTkFrame(self, corner_radius=0)
        self.f_general.grid(row=0, column=3, sticky="e")
        self.f_general.grid_columnconfigure(0, weight=1)
        self.f_general.grid_rowconfigure(3, weight=1)
        self.btn_run = ctk.CTkButton(self.f_general, text="Run")
        self.btn_run.grid(row=3, column=0, sticky="s")

        ### AUTO TAB NEEDS FOLDER TO LOOK IN, COULD ALSO USE FOR AMN TAB BUT NOT REALLY REQUIRED...
        ### Add folder select to general pane and use it as a starting folder for man tab and a detect folder for auto tab
        """

        #ctk.CTkLabel(f_general, text="GENERALIMPORT").pack()
        #ctk.CTkEntry(f_general).pack()
        #ctk.CTkLabel(f_detail, text="DETAILIMPORT").pack()
        #ctk.CTkEntry(f_detail).pack()
        """


class label_entry(f_base):
    """ Labled text entry."""
    def __init__(self,
                 lbl_text,
                 placeholder_text="",
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.label = ctk.CTkLabel(self, text=lbl_text)
        self.label.pack(side=ctk.LEFT)
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder_text)
        self.entry.pack(side=ctk.LEFT)


class fs_entry(label_entry):
    """ File/Dir entry component."""
    def __init__(self,
                 lbl_text,
                 placeholder_text="",
                 dir_only=False,
                 btn_text="...",
                 *args,
                 **kwargs):
        super().__init__(lbl_text=lbl_text, placeholder_text=placeholder_text, *args, **kwargs)
        kwargs.pop("master")
        self.dir_only = dir_only
        self.button = ctk.CTkButton(master=self, text=btn_text, command=self._fs_select, **kwargs)
        self.button.pack(side=ctk.LEFT)

    def _fs_select(self):
        # Open file dialog and return selected file name
        path = ctk.filedialog.askdirectory() if self.dir_only else ctk.filedialog.askopenfilename()
        if path:
            self.entry.delete(0, -1)
            self.entry.insert(0, path)
        return path


class file_detect(f_base):
    """ File detector button and output"""
    def __init__(self,
                 flwr_entry: fs_entry,
                 flwg_entry: fs_entry,
                 fdate_entry: fs_entry,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.btn_detect = ctk.CTkButton(self, text="Detect Files", command=self.detect_files)
        self.btn_detect.pack(side=ctk.LEFT)
        self.lbl_detect = ctk.CTkLabel(self, text="Files Detected: ")
        self.lbl_detect.pack(side=ctk.LEFT)
        self.flwr_entry = flwr_entry.entry.get
        self.flwg_entry = flwg_entry.entry.get
        self.fdate_entry = fdate_entry.entry.get

    def detect_files(self):
        flwg_abbr = self.flwg_entry()
        flwr_abbr = self.flwr_entry()
        f_date = self.fdate_entry()

        print(f"ACC_{flwg_abbr}_{flwr_abbr}_{f_date}.json")
