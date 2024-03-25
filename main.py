import tkinter as tk
from tkinter import filedialog, messagebox
import json
import make_html as make

class InputRow:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.html_filename_label = tk.Label(self.frame, text="HTML Filename\nno extension:")
        self.html_filename_entry = tk.Entry(self.frame, width=20)
        self.html_filename_label.grid(row=0, column=0, padx=10, pady=0)
        self.html_filename_entry.grid(row=1, column=0, padx=10, pady=5)

        self.md_filename_label = tk.Label(self.frame, text="MD Filename\nno extension:")
        self.md_filename_entry = tk.Entry(self.frame, width=20)
        self.md_filename_label.grid(row=0, column=1, padx=10, pady=0)
        self.md_filename_entry.grid(row=1, column=1, padx=10, pady=5)

        self.names_label = tk.Label(self.frame, text="Names\nformat: tab name, page title:")
        self.names_entry = tk.Entry(self.frame, width=30)
        self.names_label.grid(row=0, column=2, padx=10, pady=0)
        self.names_entry.grid(row=1, column=2, padx=10, pady=5,)

        self.path_label = tk.Label(self.frame, text="Site Path - /path/to/file\nno extensions:")
        self.path_entry = tk.Entry(self.frame, width=40)
        self.path_label.grid(row=0, column=3, padx=10, pady=0)
        self.path_entry.grid(row=1, column=3, padx=10, pady=5)

        self.link_labels_label = tk.Label(self.frame, text="Link Labels\nseparate with \' , \':")
        self.link_labels_entry = tk.Entry(self.frame, width=50)
        self.link_labels_label.grid(row=0, column=4, padx=10, pady=0)
        self.link_labels_entry.grid(row=1, column=4, padx=10, pady=5)

        self.links_label = tk.Label(self.frame, text="Links - separate with \' , \'\ninclude extensions:")
        self.links_entry = tk.Entry(self.frame, width=50)
        self.links_label.grid(row=0, column=5, padx=10, pady=0)
        self.links_entry.grid(row=1, column=5, padx=10, pady=5)

        self.frame.pack()

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
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text, background='#ffffe0', relief='solid', borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class App:
    def __init__(self, master):
        self.master = master
        self.input_rows = []

        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(pady=10)

        self.create_TopBar_buttons()

        self.add_row_button = tk.Button(self.master, text="Add Row", command=self.add_row)
        self.add_row_button.pack(pady=10)
        
        self.add_row()  # initial row
        self.add_initial_row_tooltips()

    def create_TopBar_buttons(self):
        # Create your generic buttons here
        save_button = tk.Button(self.button_frame, text="  Save Config  ", command=self.save_config)
        save_button.grid(row=0, column=0, padx=5, pady=5)

        load_button = tk.Button(self.button_frame, text="  Load Config  ", command=self.load_config)
        load_button.grid(row=0, column=1, padx=25, pady=5)

        self.root_dir_entry = tk.Entry(self.button_frame)
        self.root_dir_entry.grid(row=0, column=2, padx=5, pady=5)
        root_dir_button = tk.Button(self.button_frame, text="Select Root Directory", command=lambda: self.root_dir_entry.insert(tk.END, filedialog.askdirectory()))
        root_dir_button.grid(row=1, column=2, padx=5, pady=5)

        self.template_entry = tk.Entry(self.button_frame)
        self.template_entry.grid(row=0, column=3, padx=5, pady=5)
        template_button = tk.Button(self.button_frame, text='Select Template File', command=lambda: self.template_entry.insert(tk.END, filedialog.askopenfilename(defaultextension='.html')))
        template_button.grid(row=1, column=3, padx=5, pady=5)

        make_html_button = tk.Button(self.button_frame, text="Make HTML Files", command=self.make_files)
        make_html_button.grid(row=0, column=4, padx=5, pady=5)

        self.write_to_path = tk.BooleanVar(value=True)
        checkbox = tk.Checkbutton(self.button_frame, text="Write File(s) to Path: ", variable=self.write_to_path)
        checkbox.grid(row=0, column=5, padx=5, pady=5)
        ToolTip(checkbox, " If selected, the directory structure described \n by the 'Site Path' will be built, and the files    \n will be placed within.                                         ")
    
    def make_files(self):
        root_path = self.root_dir_entry.get()
        if root_path == "":
            root_path = '/outputs'
        template_file = self.template_entry.get()
        if template_file == "":
            template_file = 'default_page.html'
        for row in self.input_rows:
            html_filename = row.html_filename_entry.get()
            md_filename = row.md_filename_entry.get()
            md_filename = None if md_filename == "" else md_filename
            names = row.names_entry.get().split(", ")
            page_path = row.path_entry.get()
            links = row.links_entry.get().split(", ")
            if links == "":
                links = None   
            link_labels = row.link_labels_entry.get().split(", ")
            if link_labels == "":
                link_labels = None
            if html_filename and len(names) >= 2 and page_path:
                print(self.write_to_path.get())
                make.personal_site(template_file_path=template_file, output_file=html_filename, md_filename=md_filename, new_title=names[0], 
                                   new_header=names[1], path_to_page=page_path, links=links, link_titles=link_labels, write_to_path=self.write_to_path.get(), root=root_path)
            else:
                print("Input Error")
    
    def add_initial_row_tooltips(self):
        initial_row = self.input_rows[0]
        ToolTip(initial_row.html_filename_label, "The name of html file to be built.\nexample: index\nNOT: index.html")
        ToolTip(initial_row.md_filename_label, "Only use if the markdown content file has \na different name than the html name.\nexample: content\nNOT: content.md")
        ToolTip(initial_row.names_label, "The text displayed on the browser\n tab and the page Heading text.\nexample: about, Page Heading")
        ToolTip(initial_row.path_label, "The path to the page on the site.\nexample: /assets/docs/example.html")
        ToolTip(initial_row.link_labels_label, "Text for the page links on the right navbar.\nexample: Link 1, Link 2")
        ToolTip(initial_row.links_label, "Links for the page links on the right navbar. \nCan include a target.\nexample: https://example.com target=_blank, /docs/other_page.html")

    def add_row(self):
        new_row = InputRow(self.master)
        self.input_rows.append(new_row)

    def save_config(self):
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
                "html filename": row.html_filename_entry.get(),
                "md filename": row.md_filename_entry.get(),
                "names": row.names_entry.get(),
                "path": row.path_entry.get(),
                "link labels": row.link_labels_entry.get(),
                "links": row.links_entry.get(),
            }
            config_data["input_data"].append(row_data)

        with open("config.json", "w") as f:
            json.dump(config_data, f)

        print("Config saved successfully.")
        pass

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config_data = json.load(f)

            num_rows = config_data.get("rows", 0)
            input_data = config_data.get("input_data", [])
            project_data = config_data.get("project_data", {})

            # Clear existing rows
            for row in self.input_rows:
                row.frame.destroy()
            self.input_rows = []

            # Create new rows from config data
            for i in range(num_rows):
                new_row = InputRow(self.master)
                new_row.html_filename_entry.insert(0, input_data[i].get("html filename", ""))
                new_row.md_filename_entry.insert(0, input_data[i].get("md filename", ""))
                new_row.names_entry.insert(0, input_data[i].get("names", ""))
                new_row.path_entry.insert(0, input_data[i].get("path", ""))
                new_row.link_labels_entry.insert(0, input_data[i].get("link labels", ""))
                new_row.links_entry.insert(0, input_data[i].get("links", ""))
                self.input_rows.append(new_row)
            self.add_initial_row_tooltips()
            
            self.root_dir_entry.insert(0, project_data['root'])
            self.template_entry.insert(0, project_data['template'])

            print("Config loaded successfully.")
        except FileNotFoundError:
            print("Config file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON.")

def main():
    root = tk.Tk()
    root.title("WebPage Generator")
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
