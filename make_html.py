from bs4 import BeautifulSoup
import os
import datetime


def add_SEO_meta_content(index, follow):
    robots_meta_content = ""
    if index:
        robots_meta_content += 'index, '
    else:
        robots_meta_content += 'noindex, '
    if follow:
        robots_meta_content += 'follow'
    else:
        robots_meta_content += 'nofollow'

    return robots_meta_content


class PersonalSitePage:
    def __init__(self, template_file_path: str = "default_page.html", md_filename: str = None, output_filename: str = "output",
                    description: str = '', new_title: str = "page", new_header: str = "Page", path_to_page: str = "/page", 
                    links: list[str] = None, link_titles: list[str] = None, index: int = 0, follow: int = 0, priority: float = 0.6,
                    write_to_path: bool = False, root: str = "outputs", page_type: str = 'Main', logger=None):
        self.step = 1
        self.logging_text = logger
        index = False if index == 0 else True
        follow = False if follow == 0 else True
        
        try:
            with open(template_file_path, "r", encoding="utf-8") as html_file:
                html_content = html_file.read()
            self.soup = BeautifulSoup(html_content, "html.parser")

            # Find and modify:
            # | tag                  | Attribute        | Variable
            # |----------------------|------------------|-----------------------------------------------------
            # | title                | Tab Name         | new_title
            # | header -> a(second)  | Path to Page     | path_to_page
            # | h1                   | Page Title       | new_header
            # | nav class="right"    | Page Links       | tuple = (links: list[str], link_titles: list[str])
            # | zero-md              | Markdown Content | output_file OR md_filename, prioritizes md_filename
            
            self.step = self.change_title(new_title=new_title)
            self.step = self.change_header(new_header=new_header, path_to_page=path_to_page, output_filename=output_filename)
            self.step = self.change_article(output_filename=output_filename, md_filename=md_filename)
            self.step, path_to_page = self.modify_path(path_to_page)
            self.step = self.add_links(links=links, link_titles=link_titles)           
            self.step = self.clean_links(page_type=page_type)
            # meta content 
            self.step = self.change_meta(index=index, follow=follow, description=description)
            # Final step before sitemap - set filepath and write file to path
            self.step, path_to_page = self.make_html_file(write_to_path=write_to_path, path_to_page=path_to_page, root=root, output_filename=output_filename)
            self.step, self.sitemap_entry = self.make_sitemap_entry(path_to_page=path_to_page, output_filename=output_filename, priority=priority)
        except FileNotFoundError as fe:
            self.log(f"File not found.\n{fe}")
        except Exception as e:
            self.log(f"An error occurred after step {self.step}: {e}\n")

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
    
    def change_header(self, new_header, path_to_page, output_filename):
        if new_header:
            self.log("    Adding header...", end=" ")
            try:
                h1_tag = self.soup.find("h1")
                h1_tag.string = new_header
                self.log("complete.")
            except:
                self.log("no <h1> tag found in the template.")
            self.step = self.step + 1
            self.log("    Adding header link...", end=" ")
            try:
                header_tag = self.soup.find("header")
                a_tags = header_tag.find_all("a")
                if len(a_tags) >= 2:
                    a_tags[1]["href"] = f"{path_to_page}{output_filename}.html" if output_filename != 'index' else '/assets/docs/about.html'
                self.log("complete.")
            except:
                self.log("there is no second <a> tag within the <header> tag.")
        else:
            self.log("    No header to add...", end=" ")
        return self.step + 1
    
    def change_article(self, output_filename, md_filename):
        if output_filename or md_filename:
            self.log("    Adding content...", end=" ")
            try:
                zero_md_tag = self.soup.find("zero-md")
                zero_md_tag["src"] = f"{output_filename}.md" if md_filename is None else f"{md_filename}.md"
                self.log("complete.")
            except:
                self.log("no <zero-md> tag found in the template.")
        else:
            self.log("    No article to add...", end=" ")
        return self.step + 1
    
    def modify_path(self, path_to_page):
        if path_to_page[0] != '/' and path_to_page[0] != '\\':
            path_to_page = "/" + path_to_page
        if len(path_to_page) > 1 and (path_to_page[-1] != '/' and path_to_page[-1] != '\\'):
            path_to_page = path_to_page + "/"
        return self.step + 1, path_to_page
    
    def add_links(self, links, link_titles):
        step = 0
        if links:
            step += 1
            self.log("    Adding links...", end=" ")
            try:
                step += 1
                nav_tag = self.soup.find("nav", class_="right")
                if nav_tag and links is not None:
                    step += 1
                    ul_tag = nav_tag.find("ul")
                    if ul_tag:
                        # Create and append <li> elements with <a> tags to the <ul> tag
                        step += 1
                        for i, href in enumerate(links):
                            li_tag = self.soup.new_tag("li")
                            if " target=" in href:
                                link_portions = href.split()
                                href_portion = link_portions[0]
                                target_portion = link_portions[1].split('=')[1]
                                a_tag = self.soup.new_tag("a", href=href_portion, target=f"{target_portion}")
                            else:
                                a_tag = self.soup.new_tag("a", href=href)
                            a_tag.string = link_titles[i]
                            li_tag.append(a_tag)
                            ul_tag.append(li_tag)
                        step += 1
                        self.log("complete.")
                    else:
                        self.log("no <ul> tag with class='right' found in the template.")
            except Exception as e:
                self.log(f"no <nav> tag found in the template. Failed at step {step}.\n      {e}")
        else:
            self.log("    No links to add on the page.")
        return self.step + 1
    
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
                self.log(f"no links in the template:")
        else:
            self.log('nothing to clean.')
        return self.step + 1
    
    def change_meta(self, index, follow, description):
        self.log('    Setting SEO...', end=" ")
        robots_meta = None
        description_meta = None
        try:
            robots_meta = self.soup.find('meta', attrs={'name': 'robots'})
            robots_meta['content'] = add_SEO_meta_content(index, follow)
        except:
            self.log("    no `robots` meta tag in the template, adding... ", end=" ")
            robots_meta = self.soup.new_tag('meta', name='robots')
            robots_meta['name'] = 'robots'
            robots_meta['content'] = add_SEO_meta_content(index, follow)
        try:
            description_meta = self.soup.find('meta', attrs={'name': 'description'})
            description_meta['content'] = description
        except:
            self.log("    no 'description' meta tag in the template, adding... ", end=" ")
            description_meta = self.soup.new_tag('meta', name='description')
            description_meta['name'] = 'description'
            description_meta["content"] = description

        robots_meta_content: str = robots_meta['content']
        if 'noindex' in robots_meta_content and 'nofollow' in robots_meta_content:
            self.log('this page will NOT be indexed by search engines.')
        elif 'nofollow' in robots_meta_content:
            self.log('page WILL be indexed by search engines.')
        elif 'noindex' in robots_meta_content:
            self.log('links on this page WILL be indexed by search engines.')
        else:
            self.log('page, and links, WILL be indexed by search engines.')
        return self.step + 1
    
    def make_html_file(self, write_to_path, path_to_page, root, output_filename):
        if path_to_page[0] == '/' or path_to_page[0] == '\\':
            pass
        else:
            path_to_page = "/" + path_to_page
        if write_to_path:
            output_file_path = f"{root}{path_to_page}{output_filename}.html"
            output_directory = os.path.dirname(output_file_path)
            os.makedirs(output_directory, exist_ok=True)
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(str(self.soup.prettify()))
        else:
            output_file_path = f"outputs/{output_filename}.html"
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                output_file.write(str(self.soup.prettify()))
        self.log(f"HTML file successfully created and written to {output_file.name}.\n")
        return self.step + 1, path_to_page
    
    def make_sitemap_entry(self, path_to_page, output_filename, priority):
        page_url = 'https://mikeverwer.github.io'
        current_date = datetime.date.today()
        formatted_date = current_date.strftime('%Y-%m-%d')
        sitemap_entry = f'  <url>\n'
        sitemap_entry += f'    <loc>{page_url}{path_to_page}{output_filename}.html</loc>\n'
        sitemap_entry += f'    <lastmod>{formatted_date}</lastmod>\n'
        sitemap_entry += f'    <changefreq>monthly</changefreq>\n'
        sitemap_entry += f'    <priority>{priority}</priority>\n'
        sitemap_entry += f'  </url>\n'

        return self.step + 1, sitemap_entry
    
    def log(self, message, end=None, route_print=True):
        log_widget = self.logging_text
        log_widget['state'] = 'normal'
        if route_print:
            print(message, end=end)
        if end is None:
            end = '\n'
        message += end
        log_widget.insert('end', message)
        log_widget.see('end')
        log_widget['state'] = 'disabled'
    
def main():
    # Example usage:
    html_file_path = "default_page.html"  # Path to your HTML file
    output_file_path = "index"  # Path to the output HTML file
    PersonalSitePage(html_file_path, output_file_path, "home", "Home")


if __name__ == '__main__':
    main()
