from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
import os
import re
import json
from bs4 import BeautifulSoup, Tag, Comment
import datetime
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PageMaker.MikeVerwer")
import html_reformat

SCRIPT_DIR = Path(__file__).resolve().parent
ICONS_DIR = SCRIPT_DIR / 'icons'


def main():
    root = Tk()
    configure_styles()
    PageMaker(root)
    root.mainloop()

def load_icon(name: str):
    return PhotoImage(file=str(ICONS_DIR / f"{name}.png"))

def configure_styles():
    style = ttk.Style()

    # Tight up/down buttons: no vertical padding so two can stack flush.
    # `relief` and `borderwidth` are set explicitly because some themes
    # add their own borders that would otherwise create visual gaps.
    style.configure(
        'OrderArrow.TButton',
        padding=(1, 0),                # (horizontal, vertical) in pixels
        borderwidth=0,
        relief='flat',
    )
    style.map(
        'OrderArrow.TButton',
        relief=[('pressed', 'sunken'), ('!pressed', 'flat')],
    )

    # Delete button with a red border. ttk doesn't expose "border color"
    # as a simple option on most built-in themes — we have to use the
    # 'bordercolor' element option, which works on the 'clam' theme and
    # any theme that inherits it. If your app isn't already using clam,
    # the styles below won't take effect; see notes after the code.
    style.configure(
        'Delete.TButton',
        padding=(0, 0),
        relief='solid'
    )
    style.map(
        'Delete.TButton',
        # bordercolor=[
        #     ('pressed', '#922b21'),    # darker red when pressed
        #     ('active', '#e74c3c'),     # lighter red on hover
        # ],
    )

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
                    links: list[str] = None, link_titles: list[str] = None, index: int = 0, follow: int = 0, priority: float = 0.6,
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
            self.step = self.add_links(links=links, link_titles=link_titles)           
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
            elif page_type == "Main":
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
            "script", src=f"/assets/apps/{output_filename}.js"))
        
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
                src='/assets/apps/{output_filename}.css')
        try:
            styles = head_tag.find_all("link", rel="stylesheet")
            last_style = styles[-1]
            last_style.insert_after(app_style_tag)
        except Exception:
            title_tag = head_tag.find("title")
            title_tag.insert_before(app_style_tag)

        self.log('Styles added... Complete.')
        return self.step + 1


    def add_links(self, links, link_titles):
        if not links:
            self.log("    No links to add on the page.")
            return self.step + 1

        if len(links) != len(link_titles):
            self.log(f"    Mismatched links/titles ({len(links)} vs {len(link_titles)}); skipping.")
            return self.step + 1

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

            for href, title in zip(links, link_titles):
                ul_tag.append(self._build_link_li(href, title))

        self.log("complete.")
        return self.step + 1
    

    def _build_link_li(self, href, title):
        """Build <li><a href="..." [target="..."]>title</a></li>."""
        a_attrs = {"href": href}
        parts = href.split(maxsplit=1)
        if len(parts) == 2 and parts[1].startswith("target="):
            a_attrs["href"] = parts[0]
            a_attrs["target"] = parts[1].split("=", 1)[1]
        a_tag = self.soup.new_tag("a", **a_attrs)
        a_tag.string = title
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
        # self.row_number: int = number
        self.app: PageMaker = app

        self.frame = ttk.Frame(self.parent)
        # self.frame.grid(row=self.row_number, column=0, pady=1, sticky=(E, W))
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        column_counter = 0

        # Row number, delete and reorder buttons ------------------------------------------------------------
        self.row_order_frame = ttk.Frame(self.frame)
        self.row_label = ttk.Label(self.row_order_frame, text=str(self.row_number), font=('TkDefaultFont', 22), anchor=W)
        self.delete_icon = load_icon('garbage')
        self.sort_up_icon = load_icon('sort-up_16px')
        self.sort_down_icon = load_icon('sort-down_16px')
        self.delete_row_btn = ttk.Button(
            self.row_order_frame, 
            image=self.delete_icon,
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
        self.row_order_frame.grid(row=0, column=column_counter, columnspan=1, rowspan=2, padx=2)
        self.row_label.grid(row=0, column=0, rowspan=2, sticky=(N,S,E,W))
        self.delete_row_btn.grid(row=2, column=0, columnspan=2, sticky=(E,W))
        self.order_up_btn.grid(row=0, column=1, sticky=(S))
        self.order_down_btn.grid(row=1, column=1, sticky=(N))
        column_counter += 1

        # Page type, and priority ---------------------------------------------------------------------------
        self.type_frame = ttk.Frame(self.frame)
        self.page_type = StringVar(value='Main')
        self.page_type_label = ttk.Label(self.type_frame, text="Page Type")
        self.page_type_combo = ttk.Combobox(self.type_frame, textvariable=self.page_type, width=6)
        self.page_type_combo['values'] = ["Main", "Article", "App"]
        self.page_type_combo.state(["readonly"])

        self.priority_frame = ttk.Frame(self.frame)
        self.priority_label = ttk.Label(self.priority_frame, text='Priority')
        self.priority_entry = ttk.Entry(self.priority_frame, width=3)
        # layout
        column_counter += 1

        self.type_frame.grid(row=0, column=1, rowspan=2, sticky=(N,E))
        self.page_type_label.grid(row=0, column=0)
        self.page_type_combo.grid(row=1, column=0)
        self.priority_frame.grid(row=1, column=1, rowspan=2, sticky=E)
        self.priority_label.grid(row=0, column=0)
        self.priority_entry.grid(row=0, column=1, padx=1, sticky=W)
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
        # gridding
        self.link_labels_label.grid(row=0, column=column_counter, padx=5, pady=0, )
        self.links_label.grid(row=1, column=column_counter, padx=5, pady=0)
        column_counter += 1

        self.link_labels_entry.grid(row=0, column=column_counter, padx=1, pady=0, sticky=(E, W))
        self.links_entry.grid(row=1, column=column_counter, padx=1, pady=0, sticky=(E, W))
        column_counter += 1

        self.frame.grid_columnconfigure(column_counter, weight=1)

        # ---------------------------------------------------------------------------------------------------
        self.separator = ttk.Separator(self.frame, orient=HORIZONTAL)
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
        
    @property
    def row_number(self):
        """Row number is based on index of the input_rows list"""
        try:
            return self.app.input_rows.index(self) + 1
        except ValueError:  # During construction, before the row is added to the list
            return len(self.app.input_rows) + 1
    
    def refresh_row_display(self):
        self.row_label.config(text=str(self.row_number))
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
        self.root.title("WebPage Generator")
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
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        x_pos = (screen_width - window_width) // 2
        self.root.geometry(f"+{x_pos}+25")
        self.root.minsize(window_width, window_height)
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
        
        self.scrollable_canvas = Canvas(self.container)
        self.scrollable_canvas.grid(row=1, column=0, sticky=(N, S, E, W))

        self.canvas_scrollbar = Scrollbar(
            self.container, 
            orient="vertical", 
            command=self.scrollable_canvas.yview)
        self.canvas_scrollbar.grid(row=1, column=2, sticky=(N, S), padx=5)

        self.scrollable_canvas['yscrollcommand'] = self.canvas_scrollbar.set
        self.scrollable_canvas.config(scrollregion=self.scrollable_canvas.bbox("all"))
        self.scrollable_canvas.columnconfigure(0, weight=1)
        self.scrollable_canvas.rowconfigure(0, weight=1)

        self.scrollable_frame = ttk.Frame(self.scrollable_canvas)
        self.scrollable_frame.grid(row=0, column=0, sticky=(N, E, S, W))
        self.scrollable_frame.bind(
            "<Configure>", 
            lambda e: self.scrollable_canvas.configure(
                scrollregion=self.scrollable_canvas.bbox("all")))

        self.scrollable_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
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
        root_dir_button = ttk.Button(self.topbar_frame, text="Select Root Directory", command=
            lambda: (self.root_dir_entry.delete(0, END),  # Clear existing text
                    self.root_dir_entry.insert(END, filedialog.askdirectory())))
        root_dir_button.grid(row=1, column=column_counter, padx=5)

        # Add row/Reset buttons
        row_buttons_frame = ttk.Frame(self.topbar_frame)
        row_buttons_frame.grid(row=5, column=column_counter, columnspan=3, sticky=S)

        add_row_button = ttk.Button(row_buttons_frame, text="Add Row", command=self.add_row)
        add_row_button.grid(row=0, column=0, padx=10, pady=5, sticky=S)
        import_rows_button = ttk.Button(row_buttons_frame, text='Import', command=self.import_rows)
        import_rows_button.grid(row=0, column=1, padx=10, pady=5, sticky=S)
        reset_button = ttk.Button(row_buttons_frame, text="Reset", command=lambda: (
            self.reset_rows(), self.add_row(), self.add_initial_row_tooltips()
        ))
        reset_button.grid(row=0, column=2, padx=10, pady=5, sticky=S)
        column_counter += 1

        self.write_to_path = BooleanVar(value=True)
        checkbox = Checkbutton(self.topbar_frame, text="Write File(s) to Path: ", variable=self.write_to_path)
        checkbox.grid(row=1, column=column_counter, padx=5, pady=5)
        ToolTip(checkbox, " If selected, the directory structure described \n by the 'Site Path' will be built, and the files    \n will be placed within.                                         ")
        column_counter += 1

        # template HTML file entry
        self.template_entry = ttk.Entry(self.topbar_frame, width=50)
        self.template_entry.grid(row=0, column=column_counter, padx=5, pady=5, sticky=S)
        template_button = ttk.Button(
            self.topbar_frame, text='Select Template File', command=lambda: (
                self.template_entry.delete(0, END),  # Clear existing text
                self.template_entry.insert(END, filedialog.askopenfilename(defaultextension='.html'))
        ))
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

        # Logging Text
        self.logging_text = Text(self.topbar_frame, width=80, height=8, font='Helvetica 9', background="#dcdcdc", wrap='none')
        self.logging_text.grid(row=0, column=column_counter, rowspan=8, padx=5)
        self.logging_text.insert('1.0', "Logging Window\n\n")
        self.logging_text["state"] = "disabled"
        column_counter += 1
        clear_log_button = ttk.Button(self.topbar_frame, text='X', command=self.clear_log)
        clear_log_button.grid(row=0, column=column_counter)
        clear_log_button.config(width=2)
        self.topbar_frame.columnconfigure(column_counter, weight=1)
        

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
        new_row.frame.grid(row=new_row.row_number, column=0, pady=1, sticky=(E,W))
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
            links = row.links_entry.get().split(", ")
            if links == [""]:
                links = None 
            link_labels = row.link_labels_entry.get().split(", ")
            if link_labels == [""]:
                link_labels = None
            SEO_index = row.SEO_index.get()
            SEO_follow = row.SEO_follow.get()
            self.log(f"  Attempting to build {html_filename}.html... ")
            page = PersonalSitePage(template_file_path=template_file, output_filename=html_filename, md_filename=md_filename, description=description,
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
            "rows": len(self.input_rows),
            "input_data": [],
            'project_data': {
                "root": self.root_dir_entry.get(),
                "template": self.template_entry.get(),
                "robots": self.robots_text.get('1.0', 'end-1c').strip()
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


    def load_config(self, filename=None, clear_rows=True):
        try:
            if filename:
                loaded_config = filename
            else:
                loaded_config = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], initialdir=self.configs_directory)
            with open(loaded_config, "r") as f:
                config_data = json.load(f)
            self.log(f"Loading '{loaded_config}'...")
            num_rows = config_data.get("rows", 0)
            input_data = config_data.get("input_data", [])
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
                        data_entry = input_data[i].get(name, "")
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
                    except:
                        name.split('-')
                        self.log(f"  {name} not found.")
                        pass

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
