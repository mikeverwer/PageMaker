from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import re
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

        label = ttk.Label(self.tooltip, text=self.text, background='#f0f0fa', justify=LEFT, relief='solid',
                           borderwidth=0)
        label.grid(ipadx=4, ipady=4, sticky=(E, W))

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class InputRow:
    def __init__(self, parent, number: int):
        self.parent = parent
        self.row_number = number
        self.frame = Frame(self.parent, padx=10)
        self.frame.grid_rowconfigure(1, weight=1)
        column_counter = 0

        # Row number, page type, and priority ---------------------------------------------------------------
        self.row_label = ttk.Label(self.frame, text=str(self.row_number), font='_ 22')

        self.type_frame = ttk.Frame(self.frame)
        self.page_type = StringVar(value='Main')
        self.page_type_label = ttk.Label(self.type_frame, text="Page Type:")
        self.page_type_combo = ttk.Combobox(self.type_frame, textvariable=self.page_type, width=6)
        self.page_type_combo['values'] = ["Main", "Article"]
        self.page_type_combo.state(["readonly"])

        self.priority_label = ttk.Label(self.frame, text='Priority:')
        self.priority_entry = ttk.Entry(self.frame, width=4)
        # layout
        self.row_label.grid(row=0, column=column_counter, rowspan=2, columnspan=1, sticky=(N, W))
        self.page_type_label.grid(row=0, column=0)
        self.page_type_combo.grid(row=1, column=0)
        self.type_frame.grid(row=0, column=1, rowspan=2, sticky=N)
        # column_counter += 1
        self.priority_label.grid(row=1, column=column_counter)
        column_counter += 1
        self.priority_entry.grid(row=1, column=column_counter, padx=1, sticky=W)
        column_counter += 1

        # HTML Filename -------------------------------------------------------------------------------------
        self.html_filename_label = ttk.Label(self.frame, text="HTML Filename\nno extension:", justify=CENTER)
        self.html_filename_entry = ttk.Entry(self.frame, width=20)
        self.html_filename_label.grid(row=0, column=column_counter, padx=10, pady=0, sticky=S)
        self.html_filename_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        # Markdown filename ---------------------------------------------------------------------------------
        self.md_filename_label = ttk.Label(self.frame, text="MD Filename\nno extension:", justify=CENTER)
        self.md_filename_entry = ttk.Entry(self.frame, width=20)
        self.md_filename_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.md_filename_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        # SEO configuration ---------------------------------------------------------------------------------
        self.SEO_frame = ttk.Frame(self.frame)
        self.SEO_frame.grid(row=0, column=column_counter)
        self.SEO_label = ttk.Label(self.SEO_frame, text='SEO').grid(row=0, column=0)
        self.SEO_index = IntVar(value=0)
        self.SEO_follow = IntVar(value=0)
        self.SEO_index_checkbox = Checkbutton(self.SEO_frame, text='index', variable=self.SEO_index).grid(row=2, column=0, padx=0, pady=0, sticky='w')
        self.SEO_follow_checkbox = Checkbutton(self.SEO_frame, text='follow', variable=self.SEO_follow).grid(row=3, column=0, padx=0, pady=0)    
        self.description_text = Text(self.SEO_frame, width=30, height=4, wrap="word", font="Helvetica 9")
        self.description_text.grid(row=0, column=1, rowspan=4) 
        self.description_text.insert('1.0', "description")       
        self.SEO_frame.grid(column=column_counter, rowspan=2, sticky='n s', padx=4)
        column_counter += 1

        # Page Title and Page Header ------------------------------------------------------------------------
        self.names_label = ttk.Label(self.frame, text="Names\nformat: tab name, page title:", justify=CENTER)
        self.names_entry = ttk.Entry(self.frame, width=25)
        self.names_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.names_entry.grid(row=1, column=column_counter, padx=10, pady=0,)
        column_counter += 1

        # Path to page --------------------------------------------------------------------------------------
        self.path_label = ttk.Label(self.frame, text="Site Path - /path/to/file\nno extensions:", justify=CENTER)
        self.path_entry = ttk.Entry(self.frame, width=25)
        self.path_label.grid(row=0, column=column_counter, padx=10, pady=0)
        self.path_entry.grid(row=1, column=column_counter, padx=10, pady=0)
        column_counter += 1

        # Links----------------------------------------------------------------------------------------------
        # Right navbar link text
        self.link_labels_label = ttk.Label(self.frame, text="Link\nlabels:", justify=LEFT)
        self.link_labels_entry = ttk.Entry(self.frame, width=100)

        # Right navbar links
        self.links_label = ttk.Label(self.frame, text="Links:", justify=LEFT)
        self.links_entry = ttk.Entry(self.frame, width=100)

        self.link_labels_label.grid(row=0, column=column_counter, padx=5, pady=0, )
        self.links_label.grid(row=1, column=column_counter, padx=5, pady=0)
        column_counter += 1
        self.link_labels_entry.grid(row=0, column=column_counter, padx=1, pady=0,)
        self.links_entry.grid(row=1, column=column_counter, padx=1, pady=0)
        column_counter += 1

        # ---------------------------------------------------------------------------------------------------
        self.separator = ttk.Separator(self.frame, orient=HORIZONTAL)
        # self.separator.pack(fill='x', padx=2, pady=1)
        self.separator.grid(row=3, column=0, columnspan=column_counter, sticky="ew", ipadx=4)

        # Dictionary of widgets that need to be saved/loaded
        # Specify get/set methods with key options: -set, -insert, -text
        self.widgets = {
                    "type -set": self.page_type,
                    "priority -insert": self.priority_entry,
                    "SEO index -set": self.SEO_index,
                    "SEO follow -set": self.SEO_follow,
                    "SEO description -text": self.description_text,
                    "html filename -insert": self.html_filename_entry,
                    "md filename -insert": self.md_filename_entry,
                    "names -insert": self.names_entry,
                    "path -insert": self.path_entry,
                    "link labels -insert": self.link_labels_entry,
                    "links -insert": self.links_entry,
                }

        self.frame.pack(pady=1)  # re-pack the frame to accommodate for the new row


class PageMaker:
    def __init__(self, root: Tk):
        # Root Configuration
        self.root: Tk = root
        self.root.title("WebPage Generator")
        self.root.iconbitmap('page-maker-icon.ico')
        # Keybinds
        self.root.bind('<Button 1>', self.remove_focus)
        self.root.bind('<Control-s>', self.save_config)
        self.root.bind("<Control-l>", self.load_config)
        self.root.bind("<F5>", self.autosave)
        self.root.bind("<F8>", self.autoload)
        # Globals
        self.autosave_interval = 300_000  # 5 minutes in milliseconds
        self.cwd = os.getcwd()
        self.configs_directory = os.path.join(self.cwd, "configs")
        self.autosave_filepath = os.path.join(self.configs_directory, "autosave.json")
        self.input_rows = []
        # Window Creation
        self.build_window()
        self.root.update_idletasks()  # wait until the window is finished
        # Window Position
        screen_width = self.root.winfo_screenwidth()
        window_width = self.root.winfo_width()
        x_pos = (screen_width - window_width) // 2  # not working, centers the left edge
        self.root.geometry(f"+{x_pos}+25")

        self.schedule_autosave()


    def build_window(self):
        self.topbar_frame = Frame(self.root)
        self.topbar_frame.pack(pady=10)
        self.create_TopBar()
        
        self.scrollable_canvas = Canvas(self.root)
        self.canvas_scrollbar = Scrollbar(self.scrollable_canvas, orient="vertical", command=self.scrollable_canvas.yview)

        self.scrollable_frame = Frame(self.scrollable_canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.scrollable_canvas.configure(scrollregion=self.scrollable_canvas.bbox("all")))

        self.scrollable_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_canvas.configure(yscrollcommand=self.canvas_scrollbar.set)
        self.scrollable_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        self.add_row()  # initial row
        self.add_initial_row_tooltips()


    def create_TopBar(self):
        column_counter = 0

        # robots.txt entry
        self.robots_text = Text(self.topbar_frame, width=40, height=8, font="Helvetica 9")
        self.robots_text.grid(row=0, column=column_counter, rowspan=8, padx=10)
        self.robots_text.insert(0.1, '# Add content for robots.txt\nUser-agent: *\nDisallow: /private/')
        column_counter += 1

        # root directory with write-to-path checkbox
        self.root_dir_entry = ttk.Entry(self.topbar_frame, width=50)
        self.root_dir_entry.grid(row=0, column=column_counter, padx=5, pady=5, columnspan=2, sticky=S)
        root_dir_button = ttk.Button(self.topbar_frame, text="Select Root Directory", command=
                                     lambda: (self.root_dir_entry.delete(0, END),  # Clear existing text
                                              self.root_dir_entry.insert(END, filedialog.askdirectory())))
        root_dir_button.grid(row=1, column=column_counter, padx=5)
        column_counter += 1

        self.write_to_path = BooleanVar(value=True)
        checkbox = Checkbutton(self.topbar_frame, text="Write File(s) to Path: ", variable=self.write_to_path)
        checkbox.grid(row=1, column=column_counter, padx=5, pady=5)
        ToolTip(checkbox, " If selected, the directory structure described \n by the 'Site Path' will be built, and the files    \n will be placed within.                                         ")
        column_counter += 1

        # template HTML file entry
        self.template_entry = ttk.Entry(self.topbar_frame, width=50)
        self.template_entry.grid(row=0, column=column_counter, padx=5, pady=5, sticky=S)
        template_button = ttk.Button(self.topbar_frame, text='Select Template File', command=lambda: (self.template_entry.delete(0, END),  # Clear existing text
                                                                                                     self.template_entry.insert(END, filedialog.askopenfilename(defaultextension='.html'))))
        template_button.grid(row=1, column=column_counter, padx=5, pady=5)
        column_counter += 1

        # Save/Load/Make Files buttons
        save_button = ttk.Button(self.topbar_frame, text="  Save Config  ", command=self.save_config)
        save_button.grid(row=0, column=column_counter, padx=5, pady=5)
        load_button = ttk.Button(self.topbar_frame, text="  Load Config  ", command=self.load_config)
        load_button.grid(row=1, column=column_counter, padx=5, pady=5)
        small_sep = ttk.Separator(self.topbar_frame, orient=HORIZONTAL)
        small_sep.grid(row=3, column=column_counter, sticky='ew')
        make_html_button = ttk.Button(self.topbar_frame, text="Make HTML Files", command=self.make_files)
        make_html_button.grid(row=5, column=column_counter, padx=5, pady=5, sticky=S)
        column_counter += 1

        # Add row/Reset row buttons
        row_buttons_frame = ttk.Frame(self.topbar_frame)
        row_buttons_frame.grid(row=5, column=0, columnspan=column_counter, sticky=S)

        add_row_button = ttk.Button(row_buttons_frame, text="  Add Row  ", command=self.add_row)
        add_row_button.grid(row=0, column=0, padx=10, pady=5, sticky=S)
        reset_button = ttk.Button(row_buttons_frame, text="Reset", command=lambda: (self.reset_rows(), self.add_row(), self.add_initial_row_tooltips()))
        reset_button.grid(row=0, column=1, padx=10, pady=5, sticky=S)

        # Logging Text
        self.logging_text = Text(self.topbar_frame, width=80, height=8, font='Helvetica 9', background="#dcdcdc", wrap='none')
        self.logging_text.grid(row=0, column=column_counter, rowspan=8, padx=5)
        self.logging_text.insert('1.0', "Logging Window\n\n")
        self.logging_text["state"] = "disabled"
        column_counter += 1
        clear_log_button = ttk.Button(self.topbar_frame, text='X', command=self.clear_log)
        clear_log_button.grid(row=0, column=column_counter)
        clear_log_button.config(width=2)
        

    def add_initial_row_tooltips(self):
        initial_row: InputRow = self.input_rows[0]
        ToolTip(initial_row.priority_label, "The priority of the page for web search results.\nShould be a number between 0.0 and 1.0")
        ToolTip(initial_row.SEO_frame, child='!label', text="Enter the description for the page\nin the text box.\n\nSelect 'index' if you want search\nengines to find the page.\n\nSelect 'follow' if you want the links\non the page to be indexed as well")
        ToolTip(initial_row.html_filename_label, "The name of html file to be built.\n\nexample: index\nNOT: index.html")
        ToolTip(initial_row.md_filename_label, "Only use if the markdown content file has\na different name than the html name.\n\nexample: content\nNOT: content.md")
        ToolTip(initial_row.names_label, "The text displayed on the browser,\ntab and the page Heading text.\n\nexample: about, Page Heading")
        ToolTip(initial_row.path_label, "The path to the page in the directory\nstructure of the site, from root.\nLeave blank or '/' if path is root path.\n\nexample: /assets/docs/")
        ToolTip(initial_row.link_labels_label, "Text for the page links on the right navbar.\n\nSeparate with `,`\nexample: Link 1, Link 2")
        ToolTip(initial_row.links_label, "Links for the page links on the right navbar. \nCan include a target.\n\nSeparate with `,`\nexample: https://example.com target=_blank, /docs/other_page.html")


    #  ________ ___  ___  ________   ________ _________  ___  ________  ________   ________      
    # |\  _____\\  \|\  \|\   ___  \|\   ____\\___   ___\\  \|\   __  \|\   ___  \|\   ____\     
    # \ \  \__/\ \  \\\  \ \  \\ \  \ \  \___\|___ \  \_\ \  \ \  \|\  \ \  \\ \  \ \  \___|_    
    #  \ \   __\\ \  \\\  \ \  \\ \  \ \  \       \ \  \ \ \  \ \  \\\  \ \  \\ \  \ \_____  \   
    #   \ \  \_| \ \  \\\  \ \  \\ \  \ \  \____   \ \  \ \ \  \ \  \\\  \ \  \\ \  \|____|\  \  
    #    \ \__\   \ \_______\ \__\\ \__\ \_______\  \ \__\ \ \__\ \_______\ \__\\ \__\____\_\  \ 
    #     \|__|    \|_______|\|__| \|__|\|_______|   \|__|  \|__|\|_______|\|__| \|__|\_________\
    #                                                                                \|_________|

    def add_row(self):
        new_row = InputRow(self.root, len(self.input_rows) + 1)
        self.input_rows.append(new_row)


    def on_mouse_wheel(self, event):  # TODO: may not work as a class method with arguments
        self.scrollable_canvas.yview_scroll(-1 * int(event.delta/120), "units")   


    def remove_focus(self, event=None):
        focused_widget = self.root.focus_get()
        if focused_widget:
            focused_widget.focus_set()

    
    def autoload(self, event=None):
        self.load_config(self.autosave_filepath)


    def autosave(self, event=None):
        self.save_config(self.autosave_filepath, autosave=True)
        self.schedule_autosave()


    def schedule_autosave(self):
        self.root.after(self.autosave_interval, self.autosave)


    def reset_rows(self):
        for row in self.input_rows:
            row.frame.destroy()
        self.input_rows = []
        self.robots_text.delete('1.0', "end")
        self.robots_text.insert('1.0', '# Add content for robots.txt\nUser-agent: *\nDisallow: /private/')
        self.root_dir_entry.delete(0, END)
        self.template_entry.delete(0, END)
        self.clear_log()


    def get_template(self, event=None):

        self.template_entry.delete(0, END),  # Clear existing text
        self.template_entry.insert(END, filedialog.askopenfilename(defaultextension='.html'))


    def clear_log(self):
        self.logging_text['state'] = 'normal'
        self.logging_text.delete('1.0', END)
        self.logging_text.insert('1.0', "Logging Window\n\n")
        self.logging_text.see('end')
        self.logging_text['state'] = 'disabled'


    def log(self, message, end=None, route_print=True):
        log_widget = self.logging_text
        log_widget['state'] = 'normal'
        if route_print:
            print(message, end=end)
        if end is None:
            end = '\n'
        message += end
        log_widget.insert(END, message)
        log_widget.see('end')
        log_widget['state'] = 'disabled'


    # ███    ███  █████  ██   ██ ███████     ███████ ██ ██      ███████ ███████ 
    # ████  ████ ██   ██ ██  ██  ██          ██      ██ ██      ██      ██      
    # ██ ████ ██ ███████ █████   █████       █████   ██ ██      █████   ███████ 
    # ██  ██  ██ ██   ██ ██  ██  ██          ██      ██ ██      ██           ██ 
    # ██      ██ ██   ██ ██   ██ ███████     ██      ██ ███████ ███████ ███████ 

    def make_files(self):
        root_path = self.root_dir_entry.get()
        if root_path == "":
            root_path = '/outputs'

        template_file = self.template_entry.get()
        if template_file == "":
            template_file = 'default_page.html'
        
        self.sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        sitemap_content: list = []
        
        self.log("")
        for i, row in enumerate(self.input_rows):
            self.log("Gathering inputs...")
            row: InputRow
            page_type = row.page_type.get()
            SEO_priority: str = row.priority_entry.get()
            html_filename: str = row.html_filename_entry.get()
            md_filename: str = row.md_filename_entry.get()
            md_filename: str = None if md_filename == "" else md_filename
            description = row.description_text.get('1.0', 'end-1c')
            names: list = row.names_entry.get().split(", ")
            if html_filename == '':
                self.log(f"  Input Error.  Missing: HTML Filename in input row {i + 1}. Skipping attempt.")
                continue
            else:
                if len(html_filename.split('.')) > 1:
                    html_filename = html_filename.split('.')[0]
            if SEO_priority == "":
                SEO_priority = None
            else: 
                SEO_priority = float(SEO_priority)
            if names == ['']:
                self.log(f"  No Names input in the '{html_filename}' row, attempting to make the page anyway.")
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
                self.log(f"  The path-to-page in the '{html_filename}' row was blank, attempting to make the page anyway.")                
            links = row.links_entry.get().split(", ")
            if links == [""]:
                links = None 
            link_labels = row.link_labels_entry.get().split(", ")
            if link_labels == [""]:
                link_labels = None
            SEO_index = row.SEO_index.get()
            SEO_follow = row.SEO_follow.get()
            self.log(f"  Attempting to build {html_filename}.html... ")
            page = make.PersonalSitePage(template_file_path=template_file, output_filename=html_filename, md_filename=md_filename, description=description,
                               new_title=title, new_header=header, path_to_page=page_path, links=links, link_titles=link_labels, index=SEO_index, 
                               priority=SEO_priority, follow=SEO_follow, write_to_path=self.write_to_path.get(), root=root_path, page_type=page_type,
                               logger=self.logging_text)
            if page:
                sitemap_content.append(page.sitemap_entry)
            else:
                self.log(f"Failed to get sitemap content for input row {i + 1}")
            
        self.log('No more pages to make.\nMaking sitemap.xml... ', end='')
        self.make_sitemap(sitemap_content=sitemap_content, root_path=root_path)
        
        self.log('Making robots.txt... ', end="")
        robots_filepath = f"{root_path}/robots.txt"
        robots_content: str = self.robots_text.get('1.0', 'end-1c')
        try:
            os.makedirs(root_path, exist_ok=True)
            with open(robots_filepath, 'w', encoding='utf-8') as filename:
                filename.write(str(robots_content))
            self.log('complete.')
        except Exception as e:
            self.log(f'could not create robots.txt.\n{e}')
            raise
            
        self.log("\nProcess complete, your website is built!")


    # ███████ ██ ████████ ███████ ███    ███  █████  ██████  
    # ██      ██    ██    ██      ████  ████ ██   ██ ██   ██ 
    # ███████ ██    ██    █████   ██ ████ ██ ███████ ██████  
    #      ██ ██    ██    ██      ██  ██  ██ ██   ██ ██      
    # ███████ ██    ██    ███████ ██      ██ ██   ██ ██       
     
    def make_sitemap(self, sitemap_content, root_path):
        # grab the content from any existing sitemap and add pages that aren't already in it.
        sitemap_filepath = f"{root_path}/sitemap.xml"
        step = 0
        loop = 0
        try:
            step += 1
            with open(sitemap_filepath, 'r', encoding='utf-8') as existing_sitemap:
                step += 1
                self.log('found existing sitemap, updating...', end=' ')
                content = existing_sitemap.read()
                content = content.split('</urlset>')[0]

                step += 1
                loc_tag = re.compile(r'<loc>(.*?)</loc>')
                lastmod_tag = re.compile(r'<lastmod>(.*?)</lastmod>')
                priority_tag = re.compile(r'<priority>(.*?)</priority>')

                loc_tags = loc_tag.findall(content)

                step += 1
                loop = 0
                for sitemap_page in sitemap_content:
                    loop += 1
                    page_loc = loc_tag.findall(sitemap_page)[0]
                    if page_loc in loc_tags:  # an existing page was updated, update the contents
                        url_number = loc_tags.index(page_loc)
                        page_lastmod = lastmod_tag.findall(sitemap_page)[0]
                        page_priority = priority_tag.findall(sitemap_page)[0]

                        # Update the content
                        start_search = content.find(f"<loc>{page_loc}</loc>")
                        if start_search != -1:
                            lastmod_start = content.find(f"<lastmod>", start_search)
                            lastmod_end = content.find(f"</lastmod>", lastmod_start) + len("</lastmod>")
                            priority_start = content.find(f"<priority>", start_search)
                            priority_end = content.find(f"</priority>", priority_start) + len("</priority>")

                            content = content[:lastmod_start] + f"<lastmod>{page_lastmod}</lastmod>" + content[lastmod_end:]
                            content = content[:priority_start] + f"<priority>{page_priority}</priority>" + content[priority_end:]
                    else:
                        content += sitemap_page
                content += '\n</urlset>'
                self.sitemap = content

        except Exception as e:
            self.log(f'  No current sitemap, building...', end=' ')
            print(f"Failed at {step = }, {loop = }\n{e}")
            for sitemap_page in sitemap_content:
                self.sitemap += sitemap_page
            self.sitemap += '</urlset>'

        # write to file
        try:
            os.makedirs(root_path, exist_ok=True)
            with open(sitemap_filepath, 'w', encoding='utf-8') as output_filename:
                output_filename.write(str(self.sitemap))
            self.log("completed successfully.")
        except:
            self.log("error: could not make sitemap.")
            pass


    # ███████  █████  ██    ██ ███████         ██     ██       ██████   █████  ██████  
    # ██      ██   ██ ██    ██ ██             ██      ██      ██    ██ ██   ██ ██   ██ 
    # ███████ ███████ ██    ██ █████         ██       ██      ██    ██ ███████ ██   ██ 
    #      ██ ██   ██  ██  ██  ██           ██        ██      ██    ██ ██   ██ ██   ██ 
    # ███████ ██   ██   ████   ███████     ██         ███████  ██████  ██   ██ ██████  

    def save_config(self, save_file=None, autosave=False):
        if save_file is None:
            save_file = filedialog.asksaveasfilename(filetypes=[("JSON files", "*.json")], initialdir=os.path.join(os.getcwd(), "configs"))
            save_file = f"{save_file}.json" if len(save_file.split('.')) < 2 else save_file  # make sure the file extension is present

        config_data = {
            "rows": len(self.input_rows),
            "input_data": [],
            'project_data': {
                "root": self.root_dir_entry.get(),
                "template": self.template_entry.get(),
                "robots": self.robots_text.get('1.0', 'end-1c')
            }
        }

        for row in self.input_rows:
            row: InputRow
            row_data: dict = {}
            for name, widget in row.widgets.items():
                if "-text" in name:
                    row_data[name] = widget.get('1.0', 'end-1c')
                else:
                    row_data[name] = widget.get()
            config_data["input_data"].append(row_data)

        with open(str(save_file), "w") as f:
            json.dump(config_data, f)

        if autosave:
            self.log("Autosaved.")
        else:
            self.log(f"Config saved successfully to {f.name}.")


    def load_config(self, filename=None):
        try:
            if filename:
                loaded_config = filename
            else:
                loaded_config = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], initialdir=os.path.join(os.getcwd(), "configs"))
            with open(loaded_config, "r") as f:
                config_data = json.load(f)
            self.log(f"Loading '{loaded_config}'...")
            num_rows = config_data.get("rows", 0)
            input_data = config_data.get("input_data", [])
            project_data = config_data.get("project_data", {})

            self.reset_rows()
            # Create new rows from config data
            for i in range(num_rows):
                self.log(f"Building row {i + 1}... ")
                new_row = InputRow(self.root, i + 1)

                for name, widget in new_row.widgets.items():
                    try:
                        data_entry = input_data[i].get(name, "")
                        if "-text" in name:
                            widget.delete('1.0', "end")
                            widget.insert('end-1c', data_entry)
                        elif "-insert" in name:
                            widget.insert(0, data_entry)
                        elif "-set" in name:
                            widget.set(data_entry)                    
                    except:
                        name.split('-')
                        self.log(f"  {name[0]} not found.")
                        pass

                self.input_rows.append(new_row)

            self.add_initial_row_tooltips()

            # Site-wide settings:
            self.root_dir_entry.delete(0, END)
            self.template_entry.delete(0, END)
            self.robots_text.delete('1.0', END)
            self.root_dir_entry.insert(0, project_data['root'])
            self.template_entry.insert(0, project_data['template'])
            self.robots_text.insert('1.0', project_data['robots'])

            self.log("Config loaded successfully.")
            # self.autosave()
        except FileNotFoundError:
            self.log("Config file not found.")
        except json.JSONDecodeError:
            self.log("Error decoding JSON.")


def main():
    root = Tk()
    PageMaker(root)
    root.mainloop()
    

if __name__ == "__main__":
    main()
