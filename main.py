import tkinter as tk
from tkinter import ttk
import os

import file_manager

fourteen_millimeter = ["NDG-CS", "NDC-CS", "MCN-CS", "MCS-CS", "MCW-CS", "SXR-CS", "SXW-CS", "MRD-CS"]

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("File Manager")
        self.geometry("200x200")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        self.path_entry = tk.Entry(master=self, textvariable="Test")
        self.path_entry.insert(0,string=file_manager.REMOTE_STL_PATH)
        
        self.folder_selction_combo = ttk.Combobox(master=self, state="readonly", values=os.listdir(file_manager.REMOTE_STL_PATH))
        self.folder_selction_combo.current(0)

        self.upload_files_button = tk.Button(master=self, text="Upload", command=self.upload_esp_and_prg)
        self.import_files_button = tk.Button(master=self, text="Import", command=self.import_files)

        self.path_entry.grid(row=0, column=0, sticky='news')
        self.folder_selction_combo.grid(row=1, column=0, sticky='news')
        self.upload_files_button.grid(row=2, column=0, sticky='news')
        self.import_files_button.grid(row=3, column=0, sticky='news')

    def upload_esp_and_prg(event):
        pass

    def import_files(event):
        pass

class FileChecker(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Check PRG Files")
        self.geometry("500x500")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.text_field = tk.Text(master=self)
        self.text_field.tag_configure("error", foreground="white", background="red")

        self.text_field.grid(row=0, column=0, sticky='news')

    def show(self, cases):
        index = 1
        for case in cases:
            output = ""
            output += str(case._id)

            output += ' ' + case.connection

            part_length = round(case.part_length, 2)
            cut_off = round(case.cut_off, 2)

            output += ' ' + str(part_length)
            output += ' ' + str(cut_off)

            if(not case.contains_text):
                output += " Text X"

            output += '\n'
            self.text_field.insert('end', output)

            # Highlight the file if the part length exceeds the cut-off.
            if((part_length - cut_off) > 0.01):
                self.text_field.tag_add('error', f'{index}.0', f'{index + 1}.0')
            elif((cut_off - part_length) > 0.01):
                self.text_field.tag_add('error', f'{index}.0', f'{index + 1}.0')

            if(any([i in case.connection for i in fourteen_millimeter]) and part_length > 14):
                self.text_field.tag_add('error', f'{index}.0', f'{index + 1}.0')
            elif(part_length > 17):
                self.text_field.tag_add('error', f'{index}.0', f'{index + 1}.0')
            index += 1



app = App()
app.mainloop()