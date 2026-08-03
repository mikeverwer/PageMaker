from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import sv_ttk
from pathlib import Path
import os
import re
import json
from bs4 import BeautifulSoup, Tag, Comment
from PIL import Image, ImageDraw, ImageTk
import datetime
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PageMaker.MikeVerwer")
import html_reformat

SCRIPT_DIR = Path(__file__).resolve().parent
ICONS_DIR = SCRIPT_DIR / 'icons'


def main():
    root = Tk()
    apply_dark_theme(root)
    configure_styles()
    PageMaker(root)
    root.mainloop()

def load_icon(name: str):
    return PhotoImage(file=str(ICONS_DIR / f"{name}.png"))

def apply_dark_theme(root):
    BG         = "#1e1e1e"
    # BG         = "#21252B"
    SURFACE    = "#252526"   # entries, listboxes, text
    # SURFACE    = "#282C34"   # entries, listboxes, text
    SURFACE_HI = "#2d2d30"   # buttons, combobox
    # SURFACE_HI = "#282C34"   # buttons, combobox
    BORDER     = "#3e3e42"
    FG         = "#e0e0e0"
    ACCENT     = "#0047ab"   # your site blue — tie-in
    SELECT     = "#264f78"

    # Classic tk widgets (Listbox, Text, Canvas, Toplevel, Menu) via the
    # option database. Must run BEFORE any of those widgets get created.
    opts = {
        "*Background": BG,
        "*Foreground": FG,
        "*Listbox.background": SURFACE,
        "*Listbox.foreground": FG,
        "*Listbox.selectBackground": SELECT,
        "*Listbox.selectForeground": FG,
        "*Listbox.borderWidth": "0",
        "*Listbox.highlightThickness": "0",
        "*Text.background": SURFACE,
        "*Text.foreground": FG,
        "*Text.insertBackground": FG,
        "*Text.selectBackground": SELECT,
        "*Text.borderWidth": "0",
        "*Text.highlightThickness": "1",
        "*Text.highlightBackground": BORDER,
        "*Text.highlightColor": ACCENT,
        "*Canvas.background": BG,
        "*Canvas.highlightThickness": "0",
        "*Toplevel.background": BG,
        "*Menu.background": SURFACE,
        "*Menu.foreground": FG,
        # ttk.Combobox dropdown is internally a tk Listbox:
        "*TCombobox*Listbox.background": SURFACE,
        "*TCombobox*Listbox.foreground": FG,
        "*TCombobox*Listbox.selectBackground": SELECT,
    }
    for k, v in opts.items():
        root.option_add(k, v)
    root.configure(bg=BG)

    style = ttk.Style(root)
    style.theme_use("clam")

    # Catch-all
    style.configure(".",
        background=BG, foreground=FG, fieldbackground=SURFACE,
        bordercolor=BORDER, lightcolor=BG, darkcolor=BG,
        troughcolor=SURFACE)

    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("TSeparator", background=BORDER)

    style.configure("TButton",
        background=SURFACE_HI, foreground=FG,
        bordercolor=BORDER, focuscolor=BORDER, padding=4)
    style.map("TButton",
        background=[("active", BORDER), ("pressed", ACCENT)],
        bordercolor=[("focus", ACCENT)])

    style.configure("TEntry",
        fieldbackground=SURFACE, foreground=FG,
        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
        insertcolor=FG, padding=2)
    style.map("TEntry", bordercolor=[("focus", ACCENT)])

    style.configure("TCombobox",
        fieldbackground=SURFACE, background=SURFACE_HI, foreground=FG,
        bordercolor=BORDER, arrowcolor=FG,
        selectbackground=SELECT, selectforeground=FG)
    style.map("TCombobox",
        fieldbackground=[("readonly", SURFACE)],
        bordercolor=[("focus", ACCENT)])

    style.configure("TCheckbutton",
        background=BG, foreground=FG,
        focuscolor=BORDER,
        padding=(2, 2))
    style.map("TCheckbutton",
        background=[("active", BG)],)

    style.configure("Vertical.TScrollbar",
        background=SURFACE_HI, troughcolor=BG, bordercolor=BG,
        arrowcolor=FG, gripcount=0)
    style.map("Vertical.TScrollbar", background=[("active", ACCENT)])

    apply_custom_checkbox(root, style, SURFACE, BORDER, ACCENT, FG, size=16)


def _checkbox_images(surface, border, accent, fg, size=14, gap=5, radius=3):
    # Unchecked: empty rounded square with border
    w = size + gap
    off = Image.new("RGBA", (w, size), (0, 0, 0, 0))
    ImageDraw.Draw(off).rounded_rectangle(
        [(0, 0), (size - 1, size - 1)], radius=radius,
        fill=surface, outline=border, width=1)

    # Checked: accent fill + rounded rectangle
    on = Image.new("RGBA", (w, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(on)
    d.rounded_rectangle(
        [(0, 0), (size - 1, size - 1)], radius=radius,
        fill=accent, outline=accent, width=1)
    d.rounded_rectangle(
        [(5, 5), (size - 6, size - 6)],
        fill=fg, outline=None, radius=radius - 2
    )
    return ImageTk.PhotoImage(off), ImageTk.PhotoImage(on)


def apply_custom_checkbox(root, style, surface, border, accent, fg, size):
    # Keep references on root or they'll be garbage-collected
    root._chk_off, root._chk_on = _checkbox_images(surface, border, accent, fg, size)

    style.element_create(
        "Custom.Checkbutton.indicator", "image", root._chk_off,
        ("selected", root._chk_on),
        ("disabled", "selected", root._chk_on),
        padding=(2, 0, 6, 0), sticky="w")

    style.layout("TCheckbutton", [
        ("Checkbutton.padding", {"sticky": "nswe", "children": [
            ("Custom.Checkbutton.indicator", {"side": "left", "sticky": ""}),
            ("Checkbutton.focus", {"side": "left", "sticky": "", "children": [
                ("Checkbutton.label", {"sticky": "nswe"})
            ]})
        ]})
    ])


def configure_styles():
    style = ttk.Style()
    # Tight up/down buttons: no vertical padding so two can stack flush.
    # `relief` and `borderwidth` are set explicitly because some themes
    # add their own borders that would otherwise create visual gaps.
    style.configure(
        'OrderArrow.TButton',
        padding=(2, 1),                # (horizontal, vertical) in pixels
        borderwidth=1,
        relief='solid',
    )
    style.map(
        'OrderArrow.TButton',
        relief=[('pressed', 'sunken'), ('!pressed', 'flat')],
    )

def center_window(window: Toplevel | Tk):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    x_pos = (screen_width - window_width) // 2
    y_pos = int(((screen_height - window_height) // 2) * 0.75)
    window.geometry(f"+{x_pos}+{y_pos}")
    window.minsize(window_width, window_height)

#  /$$$$$$$                                                             /$$  /$$$$$$  /$$   /$$               /$$$$$$$                              
# | $$__  $$                                                           | $$ /$$__  $$|__/  | $$              | $$__  $$                             
# | $$  \ $$ /$$$$$$   /$$$$$$   /$$$$$$$  /$$$$$$  /$$$$$$$   /$$$$$$ | $$| $$  \__/ /$$ /$$$$$$    /$$$$$$ | $$  \ $$ /$$$$$$   /$$$$$$   /$$$$$$ 
# | $$$$$$$//$$__  $$ /$$__  $$ /$$_____/ /$$__  $$| $$__  $$ |____  $$| $$|  $$$$$$ | $$|_  $$_/   /$$__  $$| $$$$$$$/|____  $$ /$$__  $$ /$$__  $$
# | $$____/| $$$$$$$$| $$  \__/|  $$$$$$ | $$  \ $$| $$  \ $$  /$$$$$$$| $$ \____  $$| $$  | $$    | $$$$$$$$| $$____/  /$$$$$$$| $$  \ $$| $$$$$$$$
# | $$     | $$_____/| $$       \____  $$| $$  | $$| $$  | $$ /$$__  $$| $$ /$$  \ $$| $$  | $$ /$$| $$_____/| $$      /$$__  $$| $$  | $$| $$_____/
# | $$     |  $$$$$$$| $$       /$$$$$$$/|  $$$$$$/| $$  | $$|  $$$$$$$| $$|  $$$$$$/| $$  |  $$$$/|  $$$$$$$| $$     |  $$$$$$$|  $$$$$$$|  $$$$$$$
# |__/      \_______/|__/      |_______/  \______/ |__/  |__/ \_______/|__/ \______/ |__/   \___/   \_______/|__/      \_______/ \____  $$ \_______/
#                                                                                                                                /$$  \ $$          
#                                                                                                                               |  $$$$$$/          
#                                                                                                                                \______/           
class PersonalSitePage:
    def __init__(self, template_file_path: str = "default_page.html", md_filename: str = None, output_filename: str = "output",
                    description: str = '', new_title: str = "page", new_header: str = "Page", path_to_page: str = "/dir", 
                    links: list[dict] = None, index: int = 0, follow: int = 0, priority: float = 0.6,
                    write_to_path: bool = False, root: str = "outputs", page_type: str = 'Main', logger=None):
        self.step = 1
        self.page_url = 'https://mikeverwer.github.io'
        self.sitemap_entry = ""
        current_date = datetime.date.today()
        self.formatted_current_date = current_date.strftime('%Y-%m-%d')
        self.logging_text = logger
        self.path_to_page = self.clean_path(path_to_page=path_to_page)
        
        try:
            with open(template_file_path, "r", encoding="utf-8") as html_file:
                html_content = html_file.read()
            self.soup:BeautifulSoup = BeautifulSoup(html_content, "html.parser")

            # Find and modify:
            # | tag                      | Attribute        | Variable
            # |--------------------------|------------------|-----------------------------------------------------
            # | title                    | Tab Name         | new_title
            # | header -> a(second)      | Path to Page     | path_to_page
            # | h1                       | Page Title       | new_header
            # | nav class="right"        | Page Links       | tuple = (links: list[str], link_titles: list[str])
            # | class="markdown-content" | Markdown Content | output_file OR md_filename, prioritizes md_filename
            
            self.step = self.change_title(new_title=new_title)
            self.step = self.change_header(new_header=new_header, output_filename=output_filename)
            self.step = self.change_article(output_filename=output_filename, md_filename=md_filename, page_type=page_type)
            self.step = self.add_app(page_type=page_type, root=root, output_filename=output_filename)
            self.step = self.add_links(links=links)           
            self.step = self.clean_links(page_type=page_type)
            # meta content 
            # self.step = self.set_styles(page_type=page_type)      Deprecated - all pages now use the same css
            self.step = self.change_meta(index=index, follow=follow, description=description)
            self.step = self.last_mod_date()
            # Final step before sitemap - set filepath and write file to path
            self.step = self.make_html_file(write_to_path=write_to_path, root=root, output_filename=output_filename)
            self.step = self.make_sitemap_entry(output_filename=output_filename, priority=priority)
        except FileNotFoundError as fe:
            self.log(f"File not found.\n{fe}")
        except Exception as e:
            self.log(f"An error occurred after step {self.step}: {e}\n")
            raise



    #  ███    ███ ███████ ████████ ██   ██  ██████  ██████  ███████ 
    #  ████  ████ ██         ██    ██   ██ ██    ██ ██   ██ ██      
    #  ██ ████ ██ █████      ██    ███████ ██    ██ ██   ██ ███████ 
    #  ██  ██  ██ ██         ██    ██   ██ ██    ██ ██   ██      ██ 
    #  ██      ██ ███████    ██    ██   ██  ██████  ██████  ███████ 
    #                                                               
    
    def clean_path(self, path_to_page):
        if path_to_page[0] != '/' and path_to_page[0] != '\\':
            path_to_page = "/" + path_to_page
        if len(path_to_page) > 1 and (path_to_page[-1] != '/' and path_to_page[-1] != '\\'):
            path_to_page = path_to_page + "/"
        return path_to_page
    
    
    def change_title(self, new_title):
        if new_title:
            self.log("    Adding title...", end=" ")
            try:
                title_tag = self.soup.find("title")
                title_tag.string = f"{new_title}"
                self.log("complete.")
            except:
                self.log("no <title> tag found in the template.")
        else:
            self.log("    No title to add...", end=" ")
        return self.step + 1
    
    
    def _change_header_link(self, output_filename):
        self.log("    Adding header link...", end=" ")
        try:
            header_tag = self.soup.find("header")
            a_tags = header_tag.find_all("a")
            if len(a_tags) >= 2:
                a_tags[1]["href"] = f"#" if output_filename != 'index' else '/about.html'
            self.log("complete.")
        except:
            self.log("there is no second <a> tag within the <header> tag.")
        return self.step + 1
    

    def change_header(self, new_header, output_filename):
        if new_header:
            self.log("    Adding header...", end=" ")
            try:
                h1_tag = self.soup.find("header").find("h1")
                h1_tag.string = new_header
                self.log("complete.")
            except:
                self.log("no <h1> tag found in the template.")
            # self.step = self._change_header_link(output_filename)     # header links are now redundant
        else:
            self.log("    No header to add...", end=" ")
        return self.step + 1
    
    
    def change_article(self, output_filename, md_filename, page_type):
        self.log("    Adding content...", end=" ")
        path_to_article = f'/assets/docs{self.path_to_page}'
        article_details: tuple = ()
        article_date: str = None
        if md_filename:
            article_details = md_filename.split(', ')
            if len(article_details) > 1:
                md_filename = article_details[0]
                article_date = article_details[1]
        try:
            markdown_content = self.soup.find("div", class_="markdown-body")
            markdown_content["src"] = f"{path_to_article}{md_filename}.md" if md_filename else f"{path_to_article}{output_filename}.md"
            self.log("complete.", end=" ")
        except:
            self.log('no <div class="markdown-content"> tag found in the template.')
        if article_date:
            last_updated = ""
            if page_type == "Article":
                last_updated =  f"Written by Mike Verwer; {article_date}"
            elif page_type in ["Main", "App"]:
                last_updated = f"Last updated: {article_date}"
            try:
                article_date_tag = self.soup.find("p", id="article-date")
                article_date_tag.string = last_updated
                self.log("Included date.")
            except Exception as e:
                self.log("no date tag found, adding...", end=" ")
                article_tag = self.soup.find("article")
                article_date_tag = self.soup.new_tag("p", id="article-date")
                article_date_tag.string = last_updated
                article_tag.append(article_date_tag)
                self.log("date added.")
        else:
            self.log("No date to add.")
        return self.step + 1
    
    
    def add_app(self, page_type, root, output_filename):
        if page_type != "App":
            return self.step + 1
        # files are located in root/assets/apps/output_filename
        # inject content.html into main-section div (insert at top)
        # add <link rel="stylesheet" href="root/assets/apps/{output_filename}/app.css">
        # check /../apps/name/deps.txt for required libraries
        # add <script src=""
        self.log("    Adding the app...", end=" ")
        asset_path = f'{root}/assets/apps/{output_filename}'
        head_tag = self.soup.find("head")
        scripts = head_tag.find_all("script")

        if not os.path.isdir(asset_path):
            self.log(f"No app assets directory found at {asset_path}, skipping.")
            return self.step + 1
        
        try:
            main_section_tag = self.soup.find_all('div', class_="main-section")[0]
        except:
            self.log("No 'main-section' div found. Can not continue, skipping.")
            return self.step + 1
        
        # Remove 'zen-mode'
        removals = [
            ('div',    {'class_': 'panel-toggle-area'}),
        ]
        for tag_name, attrs in removals:
            for tag in self.soup.find_all(tag_name, **attrs):
                if tag is not None:
                    tag.decompose()
        
        # Inject app html
        try:
            with open(f'{asset_path}/content.html', "r", encoding="utf-8") as html_file:
                app_html = html_file.read()
            app_soup = BeautifulSoup(app_html, "html.parser")
            app_container_div = self.soup.new_tag("div", id="app-container")
            app_container_div.append(app_soup)
            main_section_tag.insert(0, app_container_div)
            self.log("App HTML injected...", end=' ')
        except FileNotFoundError:
            self.log("No app HTML found, skipping.")
            return self.step + 1
        
        # Add requirement imports
        self.log("Adding scripts...", end=' ')
        deps = []
        try:
            with open(f"{asset_path}/deps.txt", "r") as deps_file:
                for dep in deps_file:
                    link = dep.strip()
                    deps.insert(0, self.soup.new_tag("script", src=link))
        except FileNotFoundError:
            self.log(f"No dependencies found...", end=' ')

        deps.insert(0, self.soup.new_tag(
            "script", src=f"/assets/apps/{output_filename}/{output_filename}.js"))
        
        try:
            last_script = scripts[-1]
            for dep in deps:
                last_script.insert_after(dep)
        except IndexError:  # no scripts in the head tag
            deps.reverse()
            for dep in deps:
                head_tag.append(dep)

        # Add style sheet
        app_style_tag = self.soup.new_tag(
                "link", 
                rel="stylesheet", 
                href=f'/assets/apps/{output_filename}/{output_filename}.css')
        try:
            styles = head_tag.find_all("link", rel="stylesheet")
            last_style = styles[-1]
            last_style.insert_after(app_style_tag)
        except Exception:
            title_tag = head_tag.find("title")
            title_tag.insert_before(app_style_tag)

        self.log('Styles added... Complete.')
        return self.step + 1


    def add_links(self, links):
        if links is None:
            links = []

        self.log("    Adding links...", end=" ")
        nav_ids = ("rightNav", "side-links")
        navs_with_uls = [
            (nav, nav.find("ul"))
            for nav_id in nav_ids
            if (nav := self.soup.find("nav", id=nav_id)) is not None
        ]

        if not navs_with_uls:
            self.log("no suitable <nav> found.")
            return self.step + 1

        for nav_tag, ul_tag in navs_with_uls:
            if ul_tag is None:
                ul_tag = self.soup.new_tag("ul")
                nav_tag.append(ul_tag)
            else:   # remove any links from the template page
                for li_tag in ul_tag.find_all("li"):
                    li_tag.extract()

            for link in links:
                ul_tag.append(self._build_link_li(link))

        self.log("complete.")
        return self.step + 1
    

    def _build_link_li(self, link: dict):
        """Build <li><a href="..." [target="..."]>title</a></li>."""
        a_attrs = {"href": link['url']}
        if 'target' in link:
            a_attrs['target'] = link['target']
        a_tag = self.soup.new_tag("a", **a_attrs)
        a_tag.string = link['label']
        li_tag = self.soup.new_tag("li")
        li_tag.append(a_tag)
        return li_tag

    
    def clean_links(self, page_type):
        self.log("      Cleaning up links...", end=" ")
        try:
            empty_links = self.soup.find_all('li', lambda tag: tag.find('a', href=''))
            if empty_links:
                for li_tag in empty_links:
                    li_tag.extract()
                self.log("empty links removed.", end=".. ")
        except:
            self.log(f"no empty links.", end=".. ")
            
        if page_type == "Article":
            try:
                all_links = self.soup.find_all('li')
                for li_tag in all_links:
                    li_tag.extract()
                self.log("all page links removed.")
            except:
                self.log(f"no links in the template.")
        else:
            self.log('nothing else to clean.')
        return self.step + 1
    
    
    def set_styles(self, page_type):
        self.log("    Setting page CSS...", end=" ")
        style_tag = self.soup.find('link')
        href = ""
        if page_type == 'Main':
            href = "/styles/main_page_styles.css"
        elif page_type == "Article":
            href = "/styles/article_page_styles.css"
        style_tag["href"] = href
        self.log("complete.")
        return self.step + 1
    
    
    def add_robots_meta_content(self, index, follow):
        robots_meta_content = ""
        if index:
            robots_meta_content += 'index, '
        else:
            robots_meta_content += 'noindex, '
        if follow:
            robots_meta_content += 'follow'
        else:
            robots_meta_content += 'nofollow'
            
        if 'noindex' in robots_meta_content and 'nofollow' in robots_meta_content:
            self.log('this page will NOT be indexed by search engines.')
        elif 'nofollow' in robots_meta_content:
            self.log('page WILL be indexed by search engines.')
        elif 'noindex' in robots_meta_content:
            self.log('links on this page WILL be indexed by search engines.')
        else:
            self.log('page, and links, WILL be indexed by search engines.')
        return robots_meta_content
    
    
    def change_meta(self, index, follow, description):
        self.log('    Setting SEO...', end=" ")
        head_tag = self.soup.find('head')
        robots_meta_tag = None
        description_meta_tag = None

        try:
            robots_meta_tag = self.soup.find('meta', attrs={'name': 'robots'})
            robots_meta_tag['content'] = self.add_robots_meta_content(index, follow)
        except:
            self.log("    no `robots` meta tag in the template, adding... ", end=" ")
            robots_meta_tag = self.soup.new_tag('meta', name='robots')
            robots_meta_tag['content'] = self.add_robots_meta_content(index, follow)
            head_tag.append(robots_meta_tag)
            
        try:
            description_meta_tag = self.soup.find('meta', attrs={'name': 'description'})
            description_meta_tag['content'] = description
        except:
            self.log("    no 'description' meta tag in the template, adding... ", end=" ")
            description_meta_tag = self.soup.new_tag('meta', name='description')
            description_meta_tag["content"] = description
            head_tag.append(description_meta_tag)
        return self.step + 1
    
    
    def last_mod_date(self):
        try:
            date_tag = self.soup.find("span", class_="date-modified")
            date_tag.string = self.formatted_current_date
        except:
            pass
        return self.step + 1
    

    def make_html_file(self, write_to_path, root, output_filename):
        self.log("    Building HTML...", end=' ')
        if self.path_to_page[0] == '/' or self.path_to_page[0] == '\\':
            pass
        else:
            self.path_to_page = "/" + self.path_to_page
        if write_to_path:
            output_file_path = f"{root}{self.path_to_page}{output_filename}.html"
            output_directory = os.path.dirname(output_file_path)
            os.makedirs(output_directory, exist_ok=True)
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(str(html_reformat.reformat(self.soup.prettify())))
        else:
            output_file_path = f"outputs/{output_filename}.html"
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                output_file.write(str(html_reformat.reformat(self.soup.prettify())))
        self.log("Complete.")
        self.log(f"HTML file successfully created and written to {output_file.name}.\n")
        return self.step + 1
    
    
    def make_sitemap_entry(self, output_filename, priority):
        sitemap_entry  = f'  <url>\n'
        sitemap_entry += f'    <loc>{self.page_url}{self.path_to_page}{output_filename}.html</loc>\n'
        sitemap_entry += f'    <lastmod>{self.formatted_current_date}</lastmod>\n'
        sitemap_entry += f'    <changefreq>monthly</changefreq>\n'
        sitemap_entry += f'    <priority>{priority}</priority>\n'
        sitemap_entry += f'  </url>\n'
        self.sitemap_entry = sitemap_entry
        return self.step + 1
    
    
    def log(self, message, end=None, route_print=True):
        log_widget: Text = self.logging_text
        log_widget['state'] = 'normal'
        if route_print:
            print(message, end=end)
        if end is None:
            end = '\n'
        message += end
        log_widget.insert('end', message)
        log_widget.see('end')
        log_widget['state'] = 'disabled'
        

    

#   /$$$$$$$$                     /$$ /$$$$$$$$ /$$          
#  |__  $$__/                    | $$|__  $$__/|__/          
#     | $$     /$$$$$$   /$$$$$$ | $$   | $$    /$$  /$$$$$$ 
#     | $$    /$$__  $$ /$$__  $$| $$   | $$   | $$ /$$__  $$
#     | $$   | $$  \ $$| $$  \ $$| $$   | $$   | $$| $$  \ $$
#     | $$   | $$  | $$| $$  | $$| $$   | $$   | $$| $$  | $$
#     | $$   |  $$$$$$/|  $$$$$$/| $$   | $$   | $$| $$$$$$$/
#     |__/    \______/  \______/ |__/   |__/   |__/| $$____/ 
#                                                  | $$      
#                                                  | $$      
#                                                  |__/      
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
        
        self.tooltip = Toplevel(self.widget, background='#3e3e3e')
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        self.container = ttk.Frame(self.tooltip)
        self.container.grid(padx=5, sticky=(N,S,E,W))

        label = ttk.Label(
            self.tooltip, 
            text=self.text, 
            background='#3e3e3e', 
            foreground='#e3e3e3',
            justify=LEFT, 
            relief='solid',
            borderwidth=0)
        label.grid(padx=10, ipady=4, sticky=(E, W))

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


#  /$$       /$$           /$$       /$$$$$$$$       /$$ /$$   /$$                         /$$$$$$$  /$$           /$$                    
# | $$      |__/          | $$      | $$_____/      | $$|__/  | $$                        | $$__  $$|__/          | $$                    
# | $$       /$$ /$$$$$$$ | $$   /$$| $$        /$$$$$$$ /$$ /$$$$$$    /$$$$$$   /$$$$$$ | $$  \ $$ /$$  /$$$$$$ | $$  /$$$$$$   /$$$$$$ 
# | $$      | $$| $$__  $$| $$  /$$/| $$$$$    /$$__  $$| $$|_  $$_/   /$$__  $$ /$$__  $$| $$  | $$| $$ |____  $$| $$ /$$__  $$ /$$__  $$
# | $$      | $$| $$  \ $$| $$$$$$/ | $$__/   | $$  | $$| $$  | $$    | $$  \ $$| $$  \__/| $$  | $$| $$  /$$$$$$$| $$| $$  \ $$| $$  \ $$
# | $$      | $$| $$  | $$| $$_  $$ | $$      | $$  | $$| $$  | $$ /$$| $$  | $$| $$      | $$  | $$| $$ /$$__  $$| $$| $$  | $$| $$  | $$
# | $$$$$$$$| $$| $$  | $$| $$ \  $$| $$$$$$$$|  $$$$$$$| $$  |  $$$$/|  $$$$$$/| $$      | $$$$$$$/| $$|  $$$$$$$| $$|  $$$$$$/|  $$$$$$$
# |________/|__/|__/  |__/|__/  \__/|________/ \_______/|__/   \___/   \______/ |__/      |_______/ |__/ \_______/|__/ \______/  \____  $$
#                                                                                                                                /$$  \ $$
#                                                                                                                               |  $$$$$$/
#                                                                                                                                \______/ 
class LinkEditorDialog:
    def __init__(self, parent, initial_links):
        self.result = None
        self.working_links = [dict(link) for link in initial_links]

        self.window = Toplevel(parent)
        self.window.title("Edit Links")
        self.window.transient(parent)           # dialog floats above parent
        self.window.grab_set()                  # modal: blocks parent until close

        self._build_ui()
        self.window.update_idletasks()
        center_window(self.window)
        self._refresh_listbox()
        self.listbox.bind('<Button-1>', self._on_click)
        self.listbox.bind('<<ListboxSelect>>', self._on_select)
        self.window.bind('<Escape>', lambda e: self._clear_selection())


    
    def _build_ui(self):
        container = ttk.Frame(self.window)
        container.grid(row=0, column=0)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Up/Down buttons
        reorder_frame = ttk.Frame(container)
        reorder_frame.grid(row=0, column=0, padx=(10, 0), pady=10, sticky=N)

        self.sort_up_icon = load_icon('sort-up-icon')
        self.sort_down_icon = load_icon('sort-down-icon')
        self.order_up_btn = ttk.Button(
            reorder_frame, 
            image=self.sort_up_icon, 
            style='OrderArrow.TButton',
            takefocus=0,
            command=lambda: self._move(-1))
        self.order_down_btn = ttk.Button(
            reorder_frame, 
            image=self.sort_down_icon, 
            style='OrderArrow.TButton',
            takefocus=0,
            command=lambda: self._move(1))
        self.order_up_btn.grid(row=0, column=0, ipadx=2, ipady=4)
        self.order_down_btn.grid(row=1, column=0, ipadx=2, ipady=4)

        # Listbox showing current links
        self.listbox = Listbox(container, height=10, width=75)
        self.listbox.grid(row=0, column=1, columnspan=3, padx=(5, 20), pady=10)

        # Entry fields for adding/editing
        entry_frame = ttk.Frame(container)
        entry_frame.grid(row=1, column=1, padx=(10, 20), pady=10, columnspan=4, sticky=(N,S,E,W))
        entry_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(entry_frame, text="Label:").grid(row=0, column=0, padx=(5, 15), sticky=W)
        self.label_entry = ttk.Entry(entry_frame)
        self.label_entry.grid(row=0, column=1, sticky=(E,W))

        ttk.Label(entry_frame, text="URL:").grid(row=1, column=0, padx=(5, 15), pady=5, sticky=W)
        self.url_entry = ttk.Entry(entry_frame)
        self.url_entry.grid(row=1, column=1, pady=5, sticky=(E,W))

        self.target_bool = BooleanVar(value=False)
        self.target_check = ttk.Checkbutton(
            entry_frame, 
            text='Open in new tab', 
            takefocus=0, 
            variable=self.target_bool)
        self.target_check.grid(row=2, column=1, sticky=W)

        # Action buttons
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=4, column=2, columnspan=1, pady=10)
        ttk.Button(
            btn_frame, 
            text='Save', 
            takefocus=0,
            command=self._save).grid(row=0, column=0)
        ttk.Button(
            btn_frame, 
            text='Remove', 
            takefocus=0,
            command=self._remove).grid(row=0, column=1)
        ttk.Separator(
            btn_frame, 
            orient='horizontal').grid(row=1, column=0, columnspan=2, sticky=(E,W), pady=4)
        ttk.Button(
            btn_frame, 
            text='OK', 
            takefocus=0,
            command=self._on_ok).grid(row=2, column=0)
        ttk.Button(
            btn_frame, 
            text='Cancel', 
            takefocus=0,
            command=self._on_cancel).grid(row=2, column=1)

    def _refresh_listbox(self):
        self.listbox.delete(0, 'end')
        for link in self.working_links:
            text = f"{link['label']} → {link['url']}"
            if 'target' in link:
                text += f'   \u29C9'
            self.listbox.insert('end', text)

    def _move(self, direction: int):
        sel = self.listbox.curselection()
        if not sel:
            return
        else:
            sel = sel[0]
        if direction == -1 and sel == 0:    
            return      # cancel if trying to move the top entry up
        rows = self.working_links
        if direction == 1 and (len(rows) == 1 or sel == len(rows) - 1):
            return      # cancel if trying to move the bottom entry down
        idx = sel + direction
        rows[sel], rows[idx] = rows[idx], rows[sel] 
        self._refresh_listbox()
        self.listbox.selection_set(sel + direction)


    def _on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        link = self.working_links[sel[0]]
        self.label_entry.delete(0, 'end')
        self.label_entry.insert(0, link['label'])
        self.url_entry.delete(0, 'end')
        self.url_entry.insert(0, link['url'])
        self.target_bool.set(link.get('target') == '_blank')

    def _clear_selection(self):
        self.listbox.selection_clear(0, 'end')
        self.label_entry.delete(0, 'end')
        self.url_entry.delete(0, 'end')
        self.target_bool.set(False)

    def _on_click(self, event):
        index = self.listbox.nearest(event.y)
        bbox = self.listbox.bbox(index)

        # Click below the last item — bbox is None or the click is past its bottom edge
        if bbox is None or event.y > bbox[1] + bbox[3]:
            self._clear_selection()
            return 'break'  # stop Tk from selecting the nearest item

        # Click on the already-selected item — toggle off
        current = self.listbox.curselection()
        if current and current[0] == index:
            self.listbox.after_idle(self._clear_selection)

    def _save(self):
        current = self.listbox.curselection()       # index of current selection
        label = self.label_entry.get().strip()
        url = self.url_entry.get().strip()
        target = '_blank' if self.target_bool.get() else None
        if not label or not url:
            return
        link = {'label': label, 'url': url} if target is None else {
            'label': label, 'url': url, 'target': target}
        if not current:
            self.working_links.append(link)
        else:
            self.working_links[current[0]] = link
        self.label_entry.delete(0, 'end')
        self.url_entry.delete(0, 'end')
        self.target_bool.set(False)
        self._refresh_listbox()

    def _remove(self):
        sel = self.listbox.curselection()
        if sel:
            del self.working_links[sel[0]]
            self._refresh_listbox()

    def _on_ok(self):
        self.result = self.working_links
        self.window.destroy()
    
    def _on_cancel(self):
        self.window.destroy()

    def wait(self):
        self.window.wait_window()
        return self.result



#   /$$$$$$                                 /$$     /$$$$$$$                         
#  |_  $$_/                                | $$    | $$__  $$                        
#    | $$   /$$$$$$$   /$$$$$$  /$$   /$$ /$$$$$$  | $$  \ $$  /$$$$$$  /$$  /$$  /$$
#    | $$  | $$__  $$ /$$__  $$| $$  | $$|_  $$_/  | $$$$$$$/ /$$__  $$| $$ | $$ | $$
#    | $$  | $$  \ $$| $$  \ $$| $$  | $$  | $$    | $$__  $$| $$  \ $$| $$ | $$ | $$
#    | $$  | $$  | $$| $$  | $$| $$  | $$  | $$ /$$| $$  \ $$| $$  | $$| $$ | $$ | $$
#   /$$$$$$| $$  | $$| $$$$$$$/|  $$$$$$/  |  $$$$/| $$  | $$|  $$$$$$/|  $$$$$/$$$$/
#  |______/|__/  |__/| $$____/  \______/    \___/  |__/  |__/ \______/  \_____/\___/ 
#                    | $$                                                            
#                    | $$                                                            
#                    |__/                                                            
class InputRow:
    def __init__(self, parent, app):
        self.parent: ttk.Widget = parent
        self.app: PageMaker = app
        self.links: list[dict] = []
        self._build_row_ui()
    
    def _build_row_ui(self):
        # The row frame gets girdded by the PageMaker class after creation
        self.frame = ttk.Frame(self.parent)
        # self.frame.grid_rowconfigure(0, weight=1)
        # self.frame.grid_rowconfigure(1, weight=1)
        # self.frame.grid_columnconfigure(0, weight=1)

        xpad = 10
        column_counter = 0

        # Row number, delete and reorder buttons ------------------------------------------------------------
        self.row_order_frame = ttk.Frame(self.frame)
        self.row_label = ttk.Label(
            self.row_order_frame, text=str(self.row_number).rjust(2), 
            font=('Consolas', 22), anchor=W)
        self.delete_icon = load_icon('garbage')
        self.sort_up_icon = load_icon('sort-up-icon')
        self.sort_down_icon = load_icon('sort-down-icon')
        self.delete_row_btn = ttk.Button(
            self.row_order_frame, 
            image=self.delete_icon,
            style='OrderArrow.TButton',
            takefocus=0,
            command=self.delete)
        self.order_up_btn = ttk.Button(
            self.row_order_frame, 
            image=self.sort_up_icon, 
            style='OrderArrow.TButton',
            takefocus=0,
            command=lambda: self.move(-1))
        self.order_down_btn = ttk.Button(
            self.row_order_frame, 
            image=self.sort_down_icon, 
            style='OrderArrow.TButton',
            takefocus=0,
            command=lambda: self.move(1))
        # gridding
        self.row_order_frame.grid(row=0, column=column_counter, columnspan=1, rowspan=2, padx = xpad)
        self.row_label.grid(row=0, column=1, rowspan=2, sticky=(N,S,E,W))
        self.delete_row_btn.grid(row=2, column=0, columnspan=2, ipady=2, sticky=(E,W))
        self.order_up_btn.grid(row=0, column=0, sticky=(S))
        self.order_down_btn.grid(row=1, column=0, sticky=(N))
        column_counter += 1

        # Page type, and priority ---------------------------------------------------------------------------
        self.type_prio_frame = ttk.Frame(self.frame)
        self.page_type = StringVar(value='Main')
        self.page_type_label = ttk.Label(self.type_prio_frame, text="Page Type")
        self.page_type_combo = ttk.Combobox(self.type_prio_frame, textvariable=self.page_type, width=8)
        self.page_type_combo['values'] = ["Main", "Article", "App"]
        self.page_type_combo.state(["readonly"])

        self.priority_frame = ttk.Frame(self.frame)
        self.priority_label = ttk.Label(self.type_prio_frame, text='Priority')
        self.priority_entry = ttk.Entry(self.type_prio_frame, width=4)
        
        # gridding
        self.type_prio_frame.grid(row=0, column=column_counter, rowspan=2, padx = xpad)
        self.page_type_label.grid(row=0, column=0, columnspan=2, sticky=W)
        self.page_type_combo.grid(row=1, column=0, columnspan=2, sticky=W)
        self.priority_label.grid(row=2, column=0, sticky=S, pady=2)
        self.priority_entry.grid(row=2, column=1, padx=1, sticky=S, pady=2)
        column_counter += 1

        # Names & Path --------------------------------------------------------------------------------------
        self.entries_frame = ttk.Frame(self.frame)
        self.entries_frame.grid(row=0, column=column_counter, rowspan=2)
        sub_column_counter = 0

        # -- HTML Filename -----------------------------------------------------------------------------------
        self.html_filename_label = ttk.Label(self.entries_frame, text="HTML Filename\nno extension:", justify=CENTER)
        self.html_filename_entry = ttk.Entry(self.entries_frame, width=20)
        self.html_filename_label.grid(row=0, column=sub_column_counter, padx = xpad)
        self.html_filename_entry.grid(row=1, column=sub_column_counter, padx = xpad)
        sub_column_counter += 1

        # -- Markdown filename -------------------------------------------------------------------------------
        self.md_filename_label = ttk.Label(self.entries_frame, text="MD Filename\nno extension:", justify=CENTER)
        self.md_filename_entry = ttk.Entry(self.entries_frame, width=20)
        self.md_filename_label.grid(row=0, column=sub_column_counter, padx = xpad)
        self.md_filename_entry.grid(row=1, column=sub_column_counter, padx = xpad)
        sub_column_counter += 1

        # -- Page Title and Page Header ----------------------------------------------------------------------
        self.names_label = ttk.Label(self.entries_frame, text="Names\nformat: tab name, page title:", justify=CENTER)
        self.names_entry = ttk.Entry(self.entries_frame, width=25)
        self.names_label.grid(row=0, column=sub_column_counter, padx = xpad)
        self.names_entry.grid(row=1, column=sub_column_counter, padx = xpad)
        sub_column_counter += 1

        # -- Path to page ------------------------------------------------------------------------------------
        self.path_label = ttk.Label(self.entries_frame, text="Site Path - /path/to/file\nno extensions:", justify=CENTER)
        self.path_entry = ttk.Entry(self.entries_frame, width=25)
        self.path_label.grid(row=0, column=sub_column_counter, padx = xpad)
        self.path_entry.grid(row=1, column=sub_column_counter, padx = xpad)
        column_counter += 1

        # Links----------------------------------------------------------------------------------------------
        links_frame = ttk.Frame(self.frame)
        links_frame.grid(row=0, column=column_counter, rowspan=2, padx=4)
        ttk.Label(links_frame, text='').grid(row=0, column=0)
        self.edit_links_btn = ttk.Button(
            links_frame,
            text=self._links_btn_text(),
            command=self._open_link_editor,
            takefocus=0
        )
        self.edit_links_btn.grid(row=1, column=0, sticky=(S))
        ttk.Label(links_frame, text='').grid(row=2, column=0)
        column_counter += 1

        # SEO configuration ---------------------------------------------------------------------------------
        self.SEO_frame = ttk.Frame(self.frame)
        ttk.Label(self.SEO_frame, text='SEO').grid(row=0, column=0)
        self.SEO_index = IntVar(value=0)
        self.SEO_follow = IntVar(value=0)
        self.SEO_index_checkbox = ttk.Checkbutton(self.SEO_frame, text='index', takefocus=0, variable=self.SEO_index)
        self.SEO_index_checkbox.grid(row=1, column=0, sticky='w')
        self.SEO_follow_checkbox = ttk.Checkbutton(self.SEO_frame, text='follow', takefocus=0, variable=self.SEO_follow)
        self.SEO_follow_checkbox.grid(row=2, column=0)    
        self.description_text = Text(self.SEO_frame, height=4, wrap="word", font="_ 10")
        self.description_text.grid(row=0, column=1, rowspan=3, sticky=(N,S,E,W), padx=(4, 10)) 
        self.description_text.insert('1.0', "description")    
        self.SEO_frame.grid(row=0, column=column_counter, rowspan=2, sticky=(N,S,E,W), padx=4)
        self.frame.grid_columnconfigure(column_counter, weight=1)
        self.SEO_frame.grid_columnconfigure(1, weight=1)
        column_counter += 1

        # ---------------------------------------------------------------------------------------------------
        self.separator = ttk.Separator(self.frame, orient=HORIZONTAL)
        self.separator.grid(row=3, column=0, columnspan=column_counter, pady=(0, 5), sticky=(E,W))

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
                    "links": self.links
                }
        
    @property
    def row_number(self):
        """Row number is based on index of the input_rows list"""
        try:
            return self.app.input_rows.index(self) + 1
        except ValueError:  # During construction, before the row is added to the list
            return len(self.app.input_rows) + 1
    
    def refresh_row_display(self):
        self.row_label.config(text=str(self.row_number).rjust(2))
        self.frame.grid_configure(row=self.row_number)

    def delete(self):
        self.frame.destroy()
        deleted_row = self.row_number
        self.app.input_rows.remove(self)
        if not self.app.input_rows:
            self.app.add_row() 
        if deleted_row == 1:
            self.app.add_initial_row_tooltips()   
        for row in self.app.input_rows:
            row.refresh_row_display()
        
    def move(self, direction: int):
        if direction == -1 and self.row_number == 1:
            return
        rows = self.app.input_rows
        if direction == 1 and (len(rows) == 1 or self.row_number == len(rows)):
            return
        idx = self.row_number - 1
        idy = idx + direction
        rows[idx], rows[idy] = rows[idy], rows[idx] 
        rows[idx].refresh_row_display()
        rows[idy].refresh_row_display()

    def _links_btn_text(self):
        n = f"( {len(self.links)} )".center(14 + len(str(len(self.links))))
        return f"Edit Links\n{n}"
    
    def _open_link_editor(self):
        dialog = LinkEditorDialog(self.app.container, self.links)
        result = dialog.wait()
        if result is not None:
            self.links = result
            self.edit_links_btn.config(text=self._links_btn_text())
        



#   /$$$$$$$                                /$$      /$$           /$$                          
#  | $$__  $$                              | $$$    /$$$          | $$                          
#  | $$  \ $$  /$$$$$$   /$$$$$$   /$$$$$$ | $$$$  /$$$$  /$$$$$$ | $$   /$$  /$$$$$$   /$$$$$$ 
#  | $$$$$$$/ |____  $$ /$$__  $$ /$$__  $$| $$ $$/$$ $$ |____  $$| $$  /$$/ /$$__  $$ /$$__  $$
#  | $$____/   /$$$$$$$| $$  \ $$| $$$$$$$$| $$  $$$| $$  /$$$$$$$| $$$$$$/ | $$$$$$$$| $$  \__/
#  | $$       /$$__  $$| $$  | $$| $$_____/| $$\  $ | $$ /$$__  $$| $$_  $$ | $$_____/| $$      
#  | $$      |  $$$$$$$|  $$$$$$$|  $$$$$$$| $$ \/  | $$|  $$$$$$$| $$ \  $$|  $$$$$$$| $$      
#  |__/       \_______/ \____  $$ \_______/|__/     |__/ \_______/|__/  \__/ \_______/|__/      
#                       /$$  \ $$                                                               
#                      |  $$$$$$/                                                               
#                       \______/                                                                
class PageMaker:
    def __init__(self, root: Tk):
        # Root Configuration
        self.root: Tk = root
        self.root.title("PageMaker")
        self.root.iconbitmap(str(ICONS_DIR / 'page-maker-icon.ico'))
        # Keybinds
        # self.root.bind("<Configure>", self.reconfigure_window)
        self.root.bind('<Control-Button 1>', self.get_widget_info)
        self.root.bind('<Control-s>', self.save_config)
        self.root.bind("<Control-l>", self.load_config)
        self.root.bind("<F5>", self.autosave)
        self.root.bind("<F8>", self.autoload)
        self.root.bind("<MouseWheel>", self.on_mouse_wheel)
        # Globals
        self.autosave_interval = 900_000  # 15 minutes in milliseconds
        self.configs_directory = os.path.join(SCRIPT_DIR, "configs")
        self.autosave_filepath = os.path.join(self.configs_directory, "autosave.json")
        self.input_rows = []
        self.root.state('zoomed')
        # Window Creation
        self.build_window()
        self.root.update_idletasks()  # wait until the window is finished
        # Window Position
        center_window(self.root)
        # self.root.maxsize(screen_width, screen_height - 200)

        self.schedule_autosave()


    #  ██       █████  ██    ██  ██████  ██    ██ ████████ 
    #  ██      ██   ██  ██  ██  ██    ██ ██    ██    ██    
    #  ██      ███████   ████   ██    ██ ██    ██    ██    
    #  ██      ██   ██    ██    ██    ██ ██    ██    ██    
    #  ███████ ██   ██    ██     ██████   ██████     ██    
    #                                                                                                           
    def build_window(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.container = ttk.Frame(self.root, padding=(3, 3, 12, 12))
        self.container.grid(column=0, row=0, sticky=(N, S, E, W))
        self.container.rowconfigure(1, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.topbar_frame = ttk.Frame(self.container)
        self.topbar_frame.grid(row=0, column=0, pady=10)
        self.create_TopBar()
        self.root.update_idletasks()
        self.max_row_width = self.topbar_frame.winfo_width()
        
        self.scrollable_canvas = Canvas(self.container)
        self.scrollable_canvas.grid(row=1, column=0, sticky=(N, S, E, W))

        self.canvas_scrollbar = Scrollbar(
            self.container, 
            orient="vertical", 
            command=self.scrollable_canvas.yview)
        self.canvas_scrollbar.grid(row=1, column=2, sticky=(N, S), padx=5)

        self.scrollable_canvas['yscrollcommand'] = self.canvas_scrollbar.set
        self.scrollable_canvas.config(scrollregion=self.scrollable_canvas.bbox("all"))

        self.scrollable_frame = ttk.Frame(self.scrollable_canvas)
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.bind(
            "<Configure>", 
            lambda e: self.scrollable_canvas.configure(
                scrollregion=self.scrollable_canvas.bbox("all")))

        self.frame_window_id = self.scrollable_canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor=N)
        
        self.scrollable_canvas.bind(
            "<Configure>",
            self._on_canvas_configure)

        self.scrollable_canvas.configure(yscrollcommand=self.canvas_scrollbar.set)

        self.add_row()  # initial row
        self.add_initial_row_tooltips()

        self.root.update_idletasks()
        self.scrollable_canvas.config(width=self.scrollable_frame.winfo_width())
        self.scrollable_canvas.config(height=self.scrollable_frame.winfo_height() * 8)


    def create_TopBar(self):
        column_counter = 0

        # robots.txt entry
        self.robots_text = Text(self.topbar_frame, width=40, height=8, font="Helvetica 9")
        self.robots_text.grid(row=0, column=column_counter, rowspan=8, padx=10)
        self.robots_text.insert(0.1, 
            '# Add content for robots.txt\nUser-agent: *\nDisallow: /private/')
        column_counter += 1

        # root directory with write-to-path checkbox
        self.root_dir_entry = ttk.Entry(self.topbar_frame, width=50)
        self.root_dir_entry.grid(row=0, column=column_counter, padx=5, pady=5, columnspan=2, sticky=S)
        root_dir_button = ttk.Button(
            self.topbar_frame, text="Select Root Directory",
            takefocus=0,
            command=lambda: (self.root_dir_entry.delete(0, END),  # Clear existing text
                    self.root_dir_entry.insert(END, filedialog.askdirectory())))
        root_dir_button.grid(row=1, column=column_counter, padx=5)

        # Add row/Reset buttons
        row_buttons_frame = ttk.Frame(self.topbar_frame)
        row_buttons_frame.grid(row=5, column=column_counter, columnspan=3, sticky=S)

        add_row_button = ttk.Button(
            row_buttons_frame, 
            text="Add Row", 
            takefocus=0,
            command=self.add_row)
        add_row_button.grid(row=0, column=0, padx=10, pady=5, sticky=S)
        import_rows_button = ttk.Button(
            row_buttons_frame, 
            text='Import', 
            takefocus=0,
            command=self.import_rows)
        import_rows_button.grid(row=0, column=1, padx=10, pady=5, sticky=S)
        reset_button = ttk.Button(
            row_buttons_frame, 
            text="Reset", 
            takefocus=0,
            command=lambda: (
                self.reset_rows(), self.add_row(), self.add_initial_row_tooltips()
        ))
        reset_button.grid(row=0, column=2, padx=10, pady=5, sticky=S)
        column_counter += 1

        self.write_to_path = BooleanVar(value=True)
        checkbox = ttk.Checkbutton(
            self.topbar_frame, 
            text="Write File(s) to Path: ",
            takefocus=0, 
            variable=self.write_to_path)
        checkbox.grid(row=1, column=column_counter, padx=5, pady=5)
        ToolTip(checkbox, " If selected, the directory structure described \n by the 'Site Path' will be built, and the files    \n will be placed within.                                         ")
        column_counter += 1

        # template HTML file entry
        self.template_entry = ttk.Entry(self.topbar_frame, width=50)
        self.template_entry.grid(row=0, column=column_counter, padx=5, pady=5, sticky=S)
        template_button = ttk.Button(
            self.topbar_frame, 
            text='Select Template File',
            takefocus=0,
            command=lambda: (
                self.template_entry.delete(0, END),  # Clear existing text
                self.template_entry.insert(END, filedialog.askopenfilename(defaultextension='.html'))
        ))
        template_button.grid(row=1, column=column_counter, padx=5, pady=5)
        column_counter += 1

        # Save/Load/Make Files buttons
        save_button = ttk.Button(
            self.topbar_frame, 
            text="  Save Config  ",
            takefocus=0, 
            command=self.save_config)
        save_button.grid(row=0, column=column_counter, padx=5, pady=5)
        load_button = ttk.Button(
            self.topbar_frame, 
            text="  Load Config  ", 
            takefocus=0,
            command=self.load_config)
        load_button.grid(row=1, column=column_counter, padx=5, pady=5)
        small_sep = ttk.Separator(self.topbar_frame, orient=HORIZONTAL)
        small_sep.grid(row=3, column=column_counter, sticky='ew')
        make_html_button = ttk.Button(self.topbar_frame, text="Make HTML Files", command=self.make_files)
        make_html_button.grid(row=5, column=column_counter, padx=5, pady=5, sticky=S)
        column_counter += 1

        # Logging Text
        self.logging_text = Text(self.topbar_frame, width=80, height=8, font='Helvetica 9', wrap='none')
        self.logging_text.grid(row=0, column=column_counter, rowspan=8, padx=5)
        self.logging_text.insert('1.0', "Logging Window\n\n")
        self.logging_text["state"] = "disabled"
        column_counter += 1
        clear_log_button = ttk.Button(
            self.topbar_frame, 
            text='X', 
            takefocus=0,
            command=self.clear_log)
        clear_log_button.grid(row=0, column=column_counter)
        clear_log_button.config(width=2)
        self.topbar_frame.columnconfigure(column_counter, weight=1)
        
    def _on_canvas_configure(self, e):
        target = min(e.width, self.max_row_width)
        self.scrollable_canvas.itemconfig(self.frame_window_id, width=target)
        self.scrollable_canvas.coords(self.frame_window_id, e.width / 2, 0)

    def add_initial_row_tooltips(self):
        initial_row: InputRow = self.input_rows[0]
        ToolTip(initial_row.priority_label, "The priority of the page for web search results.\nShould be a number between 0.0 and 1.0")
        ToolTip(initial_row.SEO_frame, child='!label', text="Enter the description for the page\nin the text box.\n\nSelect 'index' if you want search\nengines to find the page.\n\nSelect 'follow' if you want the links\non the page to be indexed as well")
        ToolTip(initial_row.html_filename_label, "The name of html file to be built.\n\nexample: index\nNOT: index.html")
        ToolTip(initial_row.md_filename_label, "Only use if the markdown content file has\na different name than the html name.\n\nexample: content\nNOT: content.md")
        ToolTip(initial_row.names_label, "The text displayed on the browser,\ntab and the page Heading text.\n\nexample: about, Page Heading")
        ToolTip(initial_row.path_label, "The path to the page in the directory\nstructure of the site, from root.\nLeave blank or '/' if path is root path.\n\nexample: /assets/docs/")
        ToolTip(initial_row.edit_links_btn, "Open a dialog box to add, edit, or remove links\nthat should appear on the right side navbar.")


    #  ███    ███ ██ ███    ██  ██████  ██████      ███████ ██    ██ ███    ██  ██████ ███████ 
    #  ████  ████ ██ ████   ██ ██    ██ ██   ██     ██      ██    ██ ████   ██ ██      ██      
    #  ██ ████ ██ ██ ██ ██  ██ ██    ██ ██████      █████   ██    ██ ██ ██  ██ ██      ███████ 
    #  ██  ██  ██ ██ ██  ██ ██ ██    ██ ██   ██     ██      ██    ██ ██  ██ ██ ██           ██ 
    #  ██      ██ ██ ██   ████  ██████  ██   ██     ██       ██████  ██   ████  ██████ ███████ 
    #     

    def _refresh_row_displays(self):
        for row in self.input_rows:
            row.refresh_row_display()

    def add_row(self, parent=None):
        if parent is None:
            parent = self.scrollable_frame
        new_row = InputRow(parent, self)
        self.input_rows.append(new_row)
        new_row.frame.grid(row=new_row.row_number, column=0, padx=10, pady=1, sticky=(E,W))
        self.root.update_idletasks()
        self.scrollable_canvas.yview(MOVETO, 1)
        return new_row


    def on_mouse_wheel(self, event):
        widget: Widget = event.widget
        if self.scrollable_canvas.winfo_height() - self.scrollable_frame.winfo_height() > 0:
            return
        if widget.winfo_class() not in ["Text"]:
            self.scrollable_canvas.yview_scroll(-1 * int(event.delta/120), "units")   


    def get_widget_info(self, event):
        widget: Widget = event.widget
        x, y = widget.winfo_width(), widget.winfo_height()
        self.log(f"Clicked {widget.winfo_class()} - Hierarchy: {widget}")
        self.log(f"  size = ({x}, {y})")


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

    
    def reconfigure_window(self, event=None):
        self.root.update_idletasks()
        # window_width = self.root.winfo_width()
        pass


    # ███    ███  █████  ██   ██ ███████     ███████ ██ ██      ███████ ███████ 
    # ████  ████ ██   ██ ██  ██  ██          ██      ██ ██      ██      ██      
    # ██ ████ ██ ███████ █████   █████       █████   ██ ██      █████   ███████ 
    # ██  ██  ██ ██   ██ ██  ██  ██          ██      ██ ██      ██           ██ 
    # ██      ██ ██   ██ ██   ██ ███████     ██      ██ ███████ ███████ ███████ 
    #
    def make_files(self):
        root_path = self.root_dir_entry.get()
        if root_path == "":
            root_path = os.path.join(SCRIPT_DIR, 'outputs')

        template_file = self.template_entry.get()
        if template_file == "":
            template_file = 'default_page.html'
        
        self.sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        sitemap_content: list = []
        
        self.log("")
        for i, row in enumerate(self.input_rows):
            row: InputRow
            self.log("Gathering inputs...")
            page_type: str = row.page_type.get()
            SEO_priority: str = row.priority_entry.get()
            html_filename: str = row.html_filename_entry.get()
            md_filename: str = row.md_filename_entry.get()
            md_filename: str = None if md_filename == "" else md_filename
            description: str = row.description_text.get('1.0', 'end-1c').strip()
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
            links = row.links
            if links == []:
                links = None 
            SEO_index = row.SEO_index.get()
            SEO_follow = row.SEO_follow.get()
            self.log(f"  Attempting to build {html_filename}.html... ")
            page = PersonalSitePage(
                template_file_path=template_file, 
                output_filename=html_filename, 
                md_filename=md_filename, 
                description=description,
                new_title=title, 
                new_header=header, 
                path_to_page=page_path, 
                links=links, 
                index=SEO_index, 
                priority=SEO_priority, 
                follow=SEO_follow, 
                write_to_path=self.write_to_path.get(), 
                root=root_path, 
                page_type=page_type,
                logger=self.logging_text)
            if page:
                sitemap_content.append(page.sitemap_entry)
            else:
                self.log(f"Failed to get sitemap content for input row {i + 1}")
            
        self.log('No more pages to make.\nMaking sitemap.xml... ', end='')
        self.make_sitemap(sitemap_content=sitemap_content, root_path=root_path)
        
        self.log('Making robots.txt... ', end="")
        robots_filepath = f"{root_path}/robots.txt"
        robots_content: str = self.robots_text.get('1.0', 'end-1c').strip()
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
    # 
    def make_sitemap(self, sitemap_content, root_path):
        # grab the content from any existing sitemap and add pages that aren't already in it.
        sitemap_filepath = f"{root_path}\\sitemap.xml"
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
            with open(sitemap_filepath, 'w', encoding='utf-8') as output_sitemap:
                output_sitemap.write(str(self.sitemap))
            self.log(f"completed successfully. Sitemap written to {output_sitemap.name}")
        except:
            self.log("error: could not make sitemap.")
            pass


    # ███████  █████  ██    ██ ███████         ██     ██       ██████   █████  ██████  
    # ██      ██   ██ ██    ██ ██             ██      ██      ██    ██ ██   ██ ██   ██ 
    # ███████ ███████ ██    ██ █████         ██       ██      ██    ██ ███████ ██   ██ 
    #      ██ ██   ██  ██  ██  ██           ██        ██      ██    ██ ██   ██ ██   ██ 
    # ███████ ██   ██   ████   ███████     ██         ███████  ██████  ██   ██ ██████  
    #
    def save_config(self, save_file=None, autosave=False):
        if save_file is None:
            save_file = filedialog.asksaveasfilename(filetypes=[("JSON files", "*.json")], initialdir=self.configs_directory)
            save_file = f"{save_file}.json" if len(save_file.split('.')) < 2 else save_file  # make sure the file extension is present

        config_data = {
            "num_rows": len(self.input_rows),
            "pages": [],
            'project_data': {
                "root": self.root_dir_entry.get().strip(),
                "template": self.template_entry.get().strip(),
                "robots": self.robots_text.get('1.0', 'end-1c').strip()
            }
        }

        for row in self.input_rows:
            row: InputRow
            row_data: dict = {}
            for name, widget in row.widgets.items():
                if "-text" in name:
                    row_data[name] = widget.get('1.0', 'end-1c')
                elif "links" in name:
                    row_data[name] = row.links
                else:
                    row_data[name] = widget.get()
                row_data['links'] = row.links
            config_data["pages"].append(row_data)

        with open(str(save_file), "w") as f:
            json.dump(config_data, f, indent=2)

        if autosave:
            self.log("Autosaved.")
        else:
            self.log(f"Config saved successfully to {f.name}.")


    def load_config(self, filename=None, clear_rows=True):
        try:
            if filename:
                loaded_config = filename
            else:
                loaded_config = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], initialdir=self.configs_directory)
            with open(loaded_config, "r") as f:
                config_data = json.load(f)
            self.log(f"Loading '{loaded_config}'...")
            num_rows = config_data.get("num_rows", 0)
            pages = config_data.get("pages", [])
            project_data = config_data.get("project_data", {})

            if clear_rows:
                self.reset_rows()
            current_rows_amount = len(self.input_rows)
            # Create new rows from config data
            for i in range(num_rows):
                self.log(f"Building row {i + 1 + current_rows_amount}... ")
                new_row = self.add_row()

                for name, widget in new_row.widgets.items():
                    try:
                        data_entry = pages[i].get(name, "")
                        if "-text" in name:
                            widget: Text
                            data_entry = data_entry.strip()
                            widget.delete('1.0', "end")
                            widget.insert('end-1c', data_entry)
                        elif "-insert" in name:
                            widget: ttk.Entry
                            widget.insert(0, data_entry)
                        elif "-set" in name:
                            widget: Checkbutton | ttk.Checkbutton
                            widget.set(data_entry)  
                        elif "links" in name:
                            new_row.links = pages[i]['links']
                            new_row.edit_links_btn.config(text=new_row._links_btn_text())
                        else:
                            self.log(f"  {name} not found.")
                            raise Exception
                    except Exception as e:
                        self.log(f"  Error: {e}")


            self.add_initial_row_tooltips()

            # Site-wide settings:
            if clear_rows:
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


    def import_rows(self, event=None):
        self.load_config(clear_rows=False)
    

if __name__ == "__main__":
    main()
