# import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import json
import make_html as make

class DescriptionDialog:
    def __init__(self, parent_row):
        self.parent: InputRow = parent_row
        self.dialog = Toplevel()
        self.text_entry = Text(self.dialog, height=5, width=30)
        self.text_entry.pack() 
        self.text_content = self.text_entry.get("1.0", "end-1c")       
        accept_button = Button(self.dialog, text="Accept", command=self.accept)
        accept_button.pack()        
        cancel_button = Button(self.dialog, text="Cancel", command=self.cancel)
        cancel_button.pack()

    def check_content(self):
        if len(self.text_content) > 1:
            self.parent.description_label_text.set('Desc.  ✓')
        else:
            self.parent.description_label_text.set('Desc.  ✗')

    def accept(self):
        self.text_content = self.text_entry.get("1.0", "end-1c")
        self.parent.description_content.set(self.text_content)
        self.check_content()
        print(self.parent.description_content.get())
        self.dialog.destroy()

    def cancel(self):
        self.parent.description_content.set('')
        self.dialog.destroy()


class InputRow:
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.frame.grid_rowconfigure(1, weight=1)
        column_counter = 0

        # small frame to hold the SEO configuration
        self.SEO_frame = Frame(self.frame)
        self.SEO_label = Label(self.SEO_frame, text='SEO').grid(row=0, column=column_counter)
        self.SEO_index = BooleanVar(value=False)
        self.SEO_follow = BooleanVar(value=False)
        self.SEO_index_checkbox = Checkbutton(self.SEO_frame, text='index', variable=self.SEO_index).grid(row=2, column=0, padx=0, pady=0)
        self.SEO_follow_checkbox = Checkbutton(self.SEO_frame, text='follow', variable=self.SEO_follow).grid(row=3, column=0, padx=0, pady=0)        
        self.description_content = StringVar(value="")
        self.description_label_text = StringVar(value=f'Desc.  ✗' if self.description_content.get() == "" else f'Desc.  ✓')
        self.description_label = Label(self.SEO_frame, textvariable=self.description_label_text).grid(row=2, column=1)
        self.description_button = ttk.Button(self.SEO_frame, textvariable=self.description_label_text, command=self.open_description_dialog)
        self.description_button.grid(row=3, column=1)
        
        self.SEO_frame.grid(column=column_counter, rowspan=2, sticky='n s')
        column_counter += 1

        self.html_filename_label = Label(self.frame, text="HTML Filename\nno extension:")
        self.html_filename_entry = Entry(self.frame, width=20)
        self.html_filename_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.html_filename_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        self.md_filename_label = Label(self.frame, text="MD Filename\nno extension:")
        self.md_filename_entry = Entry(self.frame, width=20)
        self.md_filename_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.md_filename_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        self.names_label = Label(self.frame, text="Names\nformat: tab name, page title:")
        self.names_entry = Entry(self.frame, width=25)
        self.names_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.names_entry.grid(row=1, column=column_counter, padx=10, pady=0,)
        column_counter += 1

        self.path_label = Label(self.frame, text="Site Path - /path/to/file\nno extensions:")
        self.path_entry = Entry(self.frame, width=25)
        self.path_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.path_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        self.link_labels_label = Label(self.frame, text="Link Labels\nseparate with \' , \':")
        self.link_labels_entry = Entry(self.frame, width=40)
        self.link_labels_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.link_labels_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        self.links_label = Label(self.frame, text="Links - separate with \' , \'\ninclude extensions:")
        self.links_entry = Entry(self.frame, width=60)
        self.links_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.links_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        self.frame.pack()  # re-pack the frame to accommodate for the new row
        # self.open_description_dialog()

    def open_description_dialog(self):
        DescriptionDialog(self)


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox('insert')
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = Label(self.tooltip, text=self.text, background='#ffffe0', relief='solid', borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class PageMaker:
    def __init__(self, master):
        self.master = master
        self.input_rows = []

        self.topbar_button_frame = Frame(self.master)
        self.topbar_button_frame.pack(pady=10)
        self.create_TopBar_buttons()

        self.row_buttons_frame = Frame(self.master)
        self.row_buttons_frame.pack(pady=10)
        self.create_row_buttons()
        
        self.add_row()  # initial row
        self.add_initial_row_tooltips()


    def create_TopBar_buttons(self):
        # Create your generic buttons here
        save_button = Button(self.topbar_button_frame, text="  Save Config  ", command=self.save_config)
        save_button.grid(row=0, column=0, padx=5, pady=5)

        load_button = Button(self.topbar_button_frame, text="  Load Config  ", command=self.load_config)
        load_button.grid(row=0, column=1, padx=25, pady=5)

        self.root_dir_entry = Entry(self.topbar_button_frame, width=50)
        self.root_dir_entry.grid(row=0, column=2, padx=5, pady=5)
        root_dir_button = Button(self.topbar_button_frame, text="Select Root Directory", command=lambda: (self.root_dir_entry.delete(0, END),  # Clear existing text
                                                                                                      self.root_dir_entry.insert(END, filedialog.askdirectory())))
        root_dir_button.grid(row=1, column=2, padx=5, pady=5)

        self.template_entry = Entry(self.topbar_button_frame, width=50)
        self.template_entry.grid(row=0, column=3, padx=5, pady=5)
        template_button = Button(self.topbar_button_frame, text='Select Template File', command=lambda: (self.template_entry.delete(0, END),  # Clear existing text
                                                                                                     self.template_entry.insert(END, filedialog.askopenfilename(defaultextension='.html'))))
        template_button.grid(row=1, column=3, padx=5, pady=5)

        make_html_button = Button(self.topbar_button_frame, text="Make HTML Files", command=self.make_files)
        make_html_button.grid(row=0, column=4, padx=5, pady=5)

        self.write_to_path = BooleanVar(value=True)
        checkbox = Checkbutton(self.topbar_button_frame, text="Write File(s) to Path: ", variable=self.write_to_path)
        checkbox.grid(row=0, column=5, padx=5, pady=5)
        ToolTip(checkbox, " If selected, the directory structure described \n by the 'Site Path' will be built, and the files    \n will be placed within.                                         ")


    def create_row_buttons(self):
        add_row_button = Button(self.row_buttons_frame, text="  Add Row  ", command=self.add_row)
        add_row_button.grid(row=0, column=0, padx=10, pady=5)

        reset_button = Button(self.row_buttons_frame, text="Reset Rows", command=lambda: (self.reset_rows(), 
                                                                                             self.add_row()))
        reset_button.grid(row=0, column=1, padx=10, pady=5)


    def make_files(self):
        root_path = self.root_dir_entry.get()
        if root_path == "":
            root_path = '/outputs'
        template_file = self.template_entry.get()
        if template_file == "":
            template_file = 'default_page.html'
        for i, row in enumerate(self.input_rows):
            print("Gathering inputs...")
            html_filename: str = row.html_filename_entry.get()
            md_filename: str = row.md_filename_entry.get()
            md_filename: str = None if md_filename == "" else md_filename
            names: list = row.names_entry.get().split(", ")
            if html_filename == '':
                print(f"  Input Error.  Missing: HTML Filename in input row {i + 1}. Skipping attempt.")
                continue
            else:
                if len(html_filename.split('.')) > 1:
                    html_filename = html_filename.split('.')[0]
            if names == ['']:
                print(f"  No Names input in the '{html_filename}' row, attempting to make the page anyway.")
                title = None
            else:
                title = names[0]
            if len(names) < 2:
                header = None
            else: 
                header = names[1]
            page_path = row.path_entry.get()
            if page_path == "":
                page_path = '/'
                print(f"  The path-to-page in the '{html_filename}' row was blank, attempting to make the page anyway.")                
            links = row.links_entry.get().split(", ")
            if links == [""]:
                links = None 
            link_labels = row.link_labels_entry.get().split(", ")
            if link_labels == [""]:
                link_labels = None
            SEO_index = row.SEO_index.get()
            SEO_follow = row.SEO_follow.get()
            print(f"  Attempting to build {html_filename}.html... ")
            make.personal_site(template_file_path=template_file, output_filename=html_filename, md_filename=md_filename, new_title=title, 
                                   new_header=header, path_to_page=page_path, links=links, link_titles=link_labels, index=SEO_index, 
                                   follow=SEO_follow, write_to_path=self.write_to_path.get(), root=root_path)
            
        print('No more pages to make.\n\n')

    
    def add_initial_row_tooltips(self):
        initial_row = self.input_rows[0]
        ToolTip(initial_row.SEO_frame, "Select 'index' if you want search\nengines to find the page.\n\nSelect 'follow' if you want the links\non the page to be indexed as well")
        ToolTip(initial_row.html_filename_label, "The name of html file to be built.\n\nexample: index\nNOT: index.html")
        ToolTip(initial_row.md_filename_label, "Only use if the markdown content file has\na different name than the html name.\n\nexample: content\nNOT: content.md")
        ToolTip(initial_row.names_label, "The text displayed on the browser,\ntab and the page Heading text.\n\nexample: about, Page Heading")
        ToolTip(initial_row.path_label, "The path to the page in the directory\nstructure of the site, from root.\nLeave blank or '/' if path is root path.\n\nexample: /assets/docs/")
        ToolTip(initial_row.link_labels_label, "Text for the page links on the right navbar.\nexample: Link 1, Link 2")
        ToolTip(initial_row.links_label, "Links for the page links on the right navbar. \nCan include a target.\nexample: https://example.com target=_blank, /docs/other_page.html")


    def add_row(self):
        new_row = InputRow(self.master)
        self.input_rows.append(new_row)


    def reset_rows(self):
        for row in self.input_rows:
            row.frame.destroy()
        self.input_rows = []


    def save_config(self):
        save_file = filedialog.asksaveasfilename(filetypes=[("JSON files", "*.json")], initialdir=os.path.join(os.getcwd(), "configs"))
        save_file = f"{save_file}.json" if len(save_file.split('.')) < 2 else save_file
        config_data = {
            "rows": len(self.input_rows),
            "input_data": [],
            'project_data': {
                "root": self.root_dir_entry.get(),
                "template": self.template_entry.get()
            }
        }

        for row in self.input_rows:
            row_data = {
                'SEO index': row.SEO_index.get(),
                'SEO follow': row.SEO_follow.get(),
                "html filename": row.html_filename_entry.get(),
                "md filename": row.md_filename_entry.get(),
                "names": row.names_entry.get(),
                "path": row.path_entry.get(),
                "link labels": row.link_labels_entry.get(),
                "links": row.links_entry.get(),
            }
            config_data["input_data"].append(row_data)

        with open(str(save_file), "w") as f:
            json.dump(config_data, f)

        print("Config saved successfully.")
        pass


    def load_config(self):
        try:
            loaded_config = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], initialdir=os.path.join(os.getcwd(), "configs"))
            with open(loaded_config, "r") as f:
                config_data = json.load(f)

            num_rows = config_data.get("rows", 0)
            input_data = config_data.get("input_data", [])
            project_data = config_data.get("project_data", {})

            self.reset_rows()

            # Create new rows from config data
            for i in range(num_rows):
                new_row = InputRow(self.master)
                try:
                    new_row.SEO_index.set(input_data[i].get("SEO index", ""))
                    new_row.SEO_follow.set(input_data[i].get("SEO follow", ""))
                except:
                    pass
                new_row.html_filename_entry.insert(0, input_data[i].get("html filename", ""))
                new_row.md_filename_entry.insert(0, input_data[i].get("md filename", ""))
                new_row.names_entry.insert(0, input_data[i].get("names", ""))
                new_row.path_entry.insert(0, input_data[i].get("path", ""))
                new_row.link_labels_entry.insert(0, input_data[i].get("link labels", ""))
                new_row.links_entry.insert(0, input_data[i].get("links", ""))
                self.input_rows.append(new_row)
            self.add_initial_row_tooltips()
            
            self.root_dir_entry.delete(0, END)
            self.template_entry.delete(0, END)
            self.root_dir_entry.insert(0, project_data['root'])
            self.template_entry.insert(0, project_data['template'])

            print("Config loaded successfully.")
        except FileNotFoundError:
            print("Config file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON.")


def main():
    root = Tk()
    root.title("WebPage Generator")
    app = PageMaker(root)
    root.mainloop()
    

if __name__ == "__main__":
    main()
