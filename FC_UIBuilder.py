import customtkinter as ctk


class f_base(ctk.CTkFrame):
    """ Base class for FC frames."""
    def __init__(self, *args, **kwargs):
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
        self.grid_columnconfigure(1, weight=1)

        # Import detail frame
        self.f_detail = ctk.CTkFrame(self, corner_radius=0)
        self.f_detail.grid(row=0, column=0, sticky="nw")

        self._mk_import_tabv(self.f_detail)

    def _mk_import_tabv(self, master):
        self.import_tabview = ctk.CTkTabview(master)
        self.import_tabview.pack()
        self.import_mantab = self.import_tabview.add("Manual")
        self.import_autotab = self.import_tabview.add("Auto")

        # Setup grid layouts for each tab
        self.import_mantab.grid_columnconfigure(0, weight=1)
        self.import_mantab.grid_rowconfigure(1, weight=1)
        self.entr_flwg_man = fs_entry(lbl_text="Follower JSON: ", placeholder_text="Path/To/Followers.json", master=self.import_mantab)
        self.entr_flwg_man.grid(row=0, column=0, sticky="nw")
        self.entr_flwr_man = fs_entry(lbl_text="Following JSON: ", placeholder_text="Path/To/Following.json", master=self.import_mantab)
        self.entr_flwr_man.grid(row=1, column=0, sticky="nw")

        self.import_autotab.grid_columnconfigure(0, weight=1)
        self.import_autotab.grid_rowconfigure(2, weight=1)

        self.entr_flwr_auto = label_entry(lbl_text="Follower Abbrv: ", placeholder_text="Follower File Abbrv", master=self.import_autotab)
        self.entr_flwr_auto.grid(row=0, column=0, sticky="nw")

        self.entr_flwg_auto = label_entry(lbl_text="Following Abbrv: ", placeholder_text="Following File Abbrv", master=self.import_autotab)
        self.entr_flwg_auto.grid(row=1, column=0, sticky="nw")

        """
        # Auto Tab
        # Flwr/Flwg prefix
        # Detect Button


        # Import general options
        f_general = ctk.CTkFrame(self, corner_radius=0)
        f_general.grid(row=0, column=1, sticky="ne")
        # Column for global frame values
        # Date format
        # Data Folder

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
