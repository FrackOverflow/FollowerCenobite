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

        # TEST
        ctk.CTkLabel(self.f_detail, text="DISPLAYTEST").pack()
        self._mk_import_tabv(self.f_detail)

    def _mk_import_tabv(self, master):
        self.import_tabview = ctk.CTkTabview(master)
        self.import_tabview.pack()
        self.import_mantab = self.import_tabview.add("Manual")
        self.import_autotab = self.import_tabview.add("Auto")

        # Setup grid layouts for each tab
        self.import_mantab.grid_columnconfigure(0, weight=1)
        self.import_mantab.grid_rowconfigure(1, weight=1)
        self.import_autotab.grid_columnconfigure(1, weight=1)
        self.import_autotab.grid_rowconfigure(2, weight=1)
        testfsbtn = fs_entry(lbl_txt="Follower JSON: ", plchldr="Path/To/File.json", master=self.import_mantab)
        testfsbtn.grid(row=1, column=0, sticky="nw")

        """
        # Manual Tab
        # 2 File selects

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


class fs_entry(f_base):
    """ File/Dir entry component."""
    def __init__(self,
                 lbl_txt,
                 plchldr="",
                 dir_only=False,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.selection = ""
        # Add elements to frame
        # ICON?
        self.label = ctk.CTkLabel(self, text=lbl_txt).pack(side=ctk.TOP)
        self.entry = ctk.CTkEntry(self, placeholder_text=plchldr).pack(side=ctk.TOP)
        self.button = self._fs_button(dir_only=dir_only).pack(side=ctk.TOP)

    def _file_select(self):
        # Open file dialog and return selected file name
        path = ctk.filedialog.askopenfilename()
        self.entry.configure(require_redraw=True, placeholder_text=path)
        return path

    def _dir_select(self):
        # Open file dialog and return selected folder name
        path = ctk.filedialog.askdirectory()
        self.entry.configure(require_redraw=True, placeholder_text=path)
        return path

    def _fs_button(self, dir_only=False, **kwargs):
        cmd = self._dir_select if dir_only else self._file_select
        return ctk.CTkButton(master=self, command=cmd, *kwargs)
