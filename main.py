# import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import json
import make_html as make


class ToolTip:
    def __init__(self, widget, text, child=None):
        self.widget: Widget = widget
        self.text = text
        self.child: str = child
        self.tooltip = None
        
        if child:
            self.widget = self.widget.children[child]

        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox('insert')
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip, text=self.text, background='#f0f0fa', justify=LEFT, relief='solid', borderwidth=0)
        label.grid(ipadx=4, ipady=4, sticky=(E, W))

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class InputRow:
    def __init__(self, parent):
        self.parent = parent
        self.frame = Frame(self.parent)
        self.frame.grid_rowconfigure(1, weight=1)
        column_counter = 0

        # HTML Filename 
        self.html_filename_label = ttk.Label(self.frame, text="HTML Filename\nno extension:", justify=CENTER)
        self.html_filename_entry = ttk.Entry(self.frame, width=20)
        self.html_filename_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.html_filename_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        # Markdown filename
        self.md_filename_label = ttk.Label(self.frame, text="MD Filename\nno extension:", justify=CENTER)
        self.md_filename_entry = ttk.Entry(self.frame, width=20)
        self.md_filename_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.md_filename_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        # SEO configuration
        self.SEO_frame = ttk.Frame(self.frame)
        self.SEO_frame.grid(row=0, column=column_counter)
        self.SEO_label = ttk.Label(self.SEO_frame, text='SEO').grid(row=0, column=0)
        self.SEO_index = IntVar(value=0)
        self.SEO_follow = IntVar(value=0)
        self.SEO_index_checkbox = Checkbutton(self.SEO_frame, text='index', variable=self.SEO_index).grid(row=2, column=0, padx=0, pady=0, sticky='w')
        self.SEO_follow_checkbox = Checkbutton(self.SEO_frame, text='follow', variable=self.SEO_follow).grid(row=3, column=0, padx=0, pady=0)    
        self.description_text = Text(self.SEO_frame, width=30, height=4, wrap="word", font="Helvetica 9")
        self.description_text.grid(row=0, column=1, rowspan=4)        
        self.SEO_frame.grid(column=column_counter, rowspan=2, sticky='n s', padx=4)
        column_counter += 1

        # Page Title and Page Header
        self.names_label = ttk.Label(self.frame, text="Names\nformat: tab name, page title:", justify=CENTER)
        self.names_entry = ttk.Entry(self.frame, width=25)
        self.names_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.names_entry.grid(row=1, column=column_counter, padx=10, pady=0,)
        column_counter += 1

        # Path to page
        self.path_label = ttk.Label(self.frame, text="Site Path - /path/to/file\nno extensions:", justify=CENTER)
        self.path_entry = ttk.Entry(self.frame, width=25)
        self.path_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.path_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        # Right navbar link text
        self.link_labels_label = ttk.Label(self.frame, text="Link labels\nseparate with \' , \':", justify=CENTER)
        self.link_labels_entry = ttk.Entry(self.frame, width=40)
        self.link_labels_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.link_labels_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        # Right navbar links
        self.links_label = ttk.Label(self.frame, text="Links - separate with \' , \'\ninclude extensions:", justify=CENTER)
        self.links_entry = ttk.Entry(self.frame, width=60)
        self.links_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.links_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        self.frame.pack(pady=1)  # re-pack the frame to accommodate for the new row
        # self.open_description_dialog()

    def open_description_dialog(self):
        # DescriptionDialog(self)
        pass


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
        
        self.scrollable_canvas = Canvas(master)
        self.canvas_scrollbar = Scrollbar(self.scrollable_canvas, orient="vertical", command=self.scrollable_canvas.yview)

        self.scrollable_frame = Frame(self.scrollable_canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.scrollable_canvas.configure(scrollregion=self.scrollable_canvas.bbox("all")))

        self.scrollable_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_canvas.configure(yscrollcommand=self.canvas_scrollbar.set)
        self.scrollable_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        self.add_row()  # initial row
        self.add_initial_row_tooltips()


    def on_mouse_wheel(self, event):  # TODO: may not work as a class method with arguments
        self.scrollable_canvas.yview_scroll(-1 * int(event.delta/120), "units")        


    def add_row(self):
        new_row = InputRow(self.master)
        self.input_rows.append(new_row)


    def reset_rows(self):
        for row in self.input_rows:
            row.frame.destroy()
        self.input_rows = []


    def create_row_buttons(self):
        add_row_button = ttk.Button(self.row_buttons_frame, text="  Add Row  ", command=self.add_row)
        add_row_button.grid(row=0, column=0, padx=10, pady=5)

        reset_button = ttk.Button(self.row_buttons_frame, text="Reset Rows", command=lambda: (self.reset_rows(), self.add_row()))
        reset_button.grid(row=0, column=1, padx=10, pady=5)


    def create_TopBar_buttons(self):
        # Create your generic buttons here
        save_button = ttk.Button(self.topbar_button_frame, text="  Save Config  ", command=self.save_config)
        save_button.grid(row=0, column=0, padx=5, pady=5)

        load_button = ttk.Button(self.topbar_button_frame, text="  Load Config  ", command=self.load_config)
        load_button.grid(row=0, column=1, padx=25, pady=5)

        self.root_dir_entry = ttk.Entry(self.topbar_button_frame, width=50)
        self.root_dir_entry.grid(row=0, column=2, padx=5, pady=5)
        root_dir_button = ttk.Button(self.topbar_button_frame, text="Select Root Directory", command=lambda: (self.root_dir_entry.delete(0, END),  # Clear existing text
                                                                                                      self.root_dir_entry.insert(END, filedialog.askdirectory())))
        root_dir_button.grid(row=1, column=2, padx=5, pady=5)

        self.template_entry = ttk.Entry(self.topbar_button_frame, width=50)
        self.template_entry.grid(row=0, column=3, padx=5, pady=5)
        template_button = ttk.Button(self.topbar_button_frame, text='Select Template File', command=lambda: (self.template_entry.delete(0, END),  # Clear existing text
                                                                                                     self.template_entry.insert(END, filedialog.askopenfilename(defaultextension='.html'))))
        template_button.grid(row=1, column=3, padx=5, pady=5)

        make_html_button = ttk.Button(self.topbar_button_frame, text="Make HTML Files", command=self.make_files)
        make_html_button.grid(row=0, column=4, padx=5, pady=5)

        self.write_to_path = BooleanVar(value=True)
        checkbox = Checkbutton(self.topbar_button_frame, text="Write File(s) to Path: ", variable=self.write_to_path)
        checkbox.grid(row=0, column=5, padx=5, pady=5)
        ToolTip(checkbox, " If selected, the directory structure described \n by the 'Site Path' will be built, and the files    \n will be placed within.                                         ")


    def make_files(self):
        root_path = self.root_dir_entry.get()
        if root_path == "":
            root_path = '/outputs'
        template_file = self.template_entry.get()
        if template_file == "":
            template_file = 'default_page.html'
        for i, row in enumerate(self.input_rows):
            print("Gathering inputs...")
            row: InputRow
            html_filename: str = row.html_filename_entry.get()
            md_filename: str = row.md_filename_entry.get()
            md_filename: str = None if md_filename == "" else md_filename
            description = row.description_text.get('1.0', 'end')
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
            make.personal_site(template_file_path=template_file, output_filename=html_filename, md_filename=md_filename, description=description,
                               new_title=title, new_header=header, path_to_page=page_path, links=links, link_titles=link_labels, index=SEO_index, 
                               follow=SEO_follow, write_to_path=self.write_to_path.get(), root=root_path)
            
        print('No more pages to make.\n\n')

    
    def add_initial_row_tooltips(self):
        initial_row: InputRow = self.input_rows[0]
        ToolTip(initial_row.SEO_frame, child='!label', text="Enter the description for the page in the text box.\n\nSelect 'index' if you want search\nengines to find the page.\n\nSelect 'follow' if you want the links\non the page to be indexed as well")
        ToolTip(initial_row.html_filename_label, "The name of html file to be built.\n\nexample: index\nNOT: index.html")
        ToolTip(initial_row.md_filename_label, "Only use if the markdown content file has\na different name than the html name.\n\nexample: content\nNOT: content.md")
        ToolTip(initial_row.names_label, "The text displayed on the browser,\ntab and the page Heading text.\n\nexample: about, Page Heading")
        ToolTip(initial_row.path_label, "The path to the page in the directory\nstructure of the site, from root.\nLeave blank or '/' if path is root path.\n\nexample: /assets/docs/")
        ToolTip(initial_row.link_labels_label, "Text for the page links on the right navbar.\nexample: Link 1, Link 2")
        ToolTip(initial_row.links_label, "Links for the page links on the right navbar. \nCan include a target.\nexample: https://example.com target=_blank, /docs/other_page.html")


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
            row: InputRow
            row_data = {
                'SEO index': row.SEO_index.get(),
                'SEO follow': row.SEO_follow.get(),
                'SEO description': row.description_text.get('1.0', 'end'),
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
                    new_row.description_text.insert('end', input_data[i].get("SEO description"))
                except:
                    print("SEO info not found.")
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
