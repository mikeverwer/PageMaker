"""
pagemaker_core.py

The GUI-free half of PageMaker: PersonalSitePage takes a template file and a
set of page parameters and writes out a finished HTML page. This module has
no Tkinter, PIL, sv_ttk, or ctypes dependency, so it can run headlessly from
a plain CLI/PowerShell invocation (or anywhere else Python + BeautifulSoup
are available).

Extracted from main.pyw's PersonalSitePage class, with one intentional
change: log() now tolerates logger=None (see below). Everything else is
unchanged — this is meant to stay a straightforward copy of the class in
main.pyw, so keep the two in sync if you edit PersonalSitePage in either
place.
"""
import os
import datetime
from bs4 import BeautifulSoup
import html_reformat


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
            # self.step = self.change_header(new_header=new_header, output_filename=output_filename)  # Deprecated
            self.step = self.change_article(output_filename=output_filename, md_filename=md_filename, page_type=page_type)
            self.step = self.remove_app(page_type=page_type)
            self.step = self.add_app(page_type=page_type, root=root, output_filename=output_filename)
            self.step = self.add_links(links=links)           
            self.step = self.clean_links(page_type=page_type)
            # meta content 
            # self.step = self.set_styles(page_type=page_type)            # Deprecated - all pages now use the same css
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


    # ----- Methods ----------------------------------------------------------------------------------------------------
    
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
            self.log("No date to add, removing...", end=" ")
            try:
                self.soup.find("p", id="article-date").decompose()
                self.log("date tag removed.")
            except Exception as e:
                self.log("No date tag to edit, continuing.")

        return self.step + 1


    def remove_app(self):
        self.log("    Checking for an app to remove...", end=" ")

        app_container = self.soup.find("div", id="app-container")
        if app_container:
            app_container.decompose()

        app_scripts = self.soup.find_all("script", class_="app-script")
        for script in app_scripts:
            script.decompose()

        app_styles = self.soup.find_all("link", rel="stylesheet", class_="app-styles")
        for style in app_styles:
            style.decompose()

        self.log("All app elements removed.")

        return self.step + 1
    
    
    def add_app(self, page_type, root, output_filename):
        if page_type != "App":
            return self.step + 1
        self.log("    Adding the app...", end=" ")
        # files are located in root/assets/apps/output_filename
        # inject content.html into main-section div (insert at top)
        # add <link rel="stylesheet" href="root/assets/apps/{output_filename}/{output_filename}.css">
        # check /../apps/name/deps.txt for required libraries
        # add <script src="">
        asset_directory_name = output_filename if output_filename !=  'index' else 'heart_surface'
        local_asset_directory = f'{root}/assets/apps/{asset_directory_name}'                    # used to append /content.html or /deps.txt
        relative_asset_path = f'/assets/apps/{asset_directory_name}/{asset_directory_name}'     # only needs an appended file extension

        head_tag = self.soup.find("head")
        scripts = head_tag.find_all("script")

        if not os.path.isdir(local_asset_directory):
            self.log(f"No app assets directory found at {local_asset_directory}, skipping.")
            return self.step + 1
        
        try:
            main_section_tag = self.soup.find_all('div', class_="main-section")[0]
        except:
            self.log("No 'main-section' div found. Can not continue, skipping.")
            return self.step + 1
        
        # Inject app html
        try:
            with open(f'{local_asset_directory}/content.html', "r", encoding="utf-8") as html_file:
                app_html = html_file.read()
            app_soup = BeautifulSoup(app_html, "html.parser")
            app_container_div = self.soup.new_tag("div", id="app-container")
            app_container_div.append(app_soup)
            if output_filename != 'index':
                main_section_tag.insert(0, app_container_div)   # typical apps want their html above the article
            else:   
                main_section_tag.append(app_container_div)      # The homepage needs its app after the article
            self.log("App HTML injected...", end=' ')
        except FileNotFoundError:
            self.log("No app HTML found, skipping.")
            return self.step + 1
        
        # Add requirement imports
        self.log("Adding scripts...", end=' ')
        deps = []
        try:
            with open(f"{local_asset_directory}/deps.txt", "r") as deps_file:
                for dep in deps_file:
                    link = dep.strip()
                    deps.insert(0, self.soup.new_tag(
                        "script", 
                        src=link, attrs={'class': "app-script"}))
        except FileNotFoundError:
            self.log(f"No dependencies found...", end=' ')

        # add app javascript
        deps.insert(0, self.soup.new_tag(
                "script", 
                src=f"{relative_asset_path}.js",
                attrs={'class': "app-script"}
            ))
        
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
                href=f'{relative_asset_path}.css',
                attrs={'class': "app-styles"}
            )
        try:
            styles = head_tag.find_all("link", rel="stylesheet")
            last_style = styles[-1]
            last_style.insert_after(app_style_tag)
        except IndexError:
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
                    li_tag.decompose()

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
                    li_tag.decompose()
                self.log("empty links removed.", end=".. ")
        except:
            self.log(f"no empty links.", end=".. ")
            
        if page_type == "Article":
            try:
                all_links = self.soup.find_all('li')
                for li_tag in all_links:
                    li_tag.decompose()
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
        if end is None:
            end = '\n'
        if route_print:
            print(message, end=end)
        log_widget = self.logging_text
        if log_widget is not None:
            log_widget['state'] = 'normal'
            log_widget.insert('end', message + end)
            log_widget.see('end')
            log_widget['state'] = 'disabled'
        

