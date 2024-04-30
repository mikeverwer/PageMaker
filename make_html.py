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
                    write_to_path: bool = False, root: str = "outputs", page_type: str = 'Main'):
        self.step = 1
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
            if new_title:
                print("    Adding title...", end=" ")
                try:
                    title_tag = self.soup.find("title")
                    title_tag.string = f"{new_title}"
                    print("complete.")
                except:
                    print("no <title> tag found in the template.")
            self.step += 1  # step 2

            self.step = self.change_header(new_header)
            if new_header:
                print("    Adding header...", end=" ")
                try:
                    h1_tag = self.soup.find("h1")
                    h1_tag.string = new_header
                    print("complete.")
                except:
                    print("no <h1> tag found in the template.")
            self.step += 1  # step 3

            self.step = self.change_article(output_filename=output_filename, md_filename=md_filename)
            if output_filename or md_filename:
                print("    Adding content...", end=" ")
                try:
                    zero_md_tag = self.soup.find("zero-md")
                    zero_md_tag["src"] = f"{output_filename}.md" if md_filename is None else f"{md_filename}.md"
                    print("complete.")
                except:
                    print("no <zero-md> tag found in the template.")
            self.step += 1  # step 4

            self.step, path_to_page = self.modify_path(path_to_page)
            if path_to_page[0] != '/' and path_to_page[0] != '\\':
                path_to_page = "/" + path_to_page
            if len(path_to_page) > 1 and (path_to_page[-1] != '/' and path_to_page[-1] != '\\'):
                path_to_page = path_to_page + "/"
            self.step += 1  # step 5

            
            if new_header:
                print("    Adding header link...", end=" ")
                try:
                    header_tag = self.soup.find("header" )
                    a_tags = header_tag.find_all("a")
                    if len(a_tags) >= 2:
                        a_tags[1]["href"] = f"{path_to_page}{output_filename}.html" if output_filename != 'index' else '/assets/docs/about.html'
                    print("complete.")
                except:
                    print("there is no second <a> tag within the <header> tag.")
            self.step += 1  # step 6

            self.step = self.add_links(links=links, link_titles=link_titles)
            if links:
                print("    Adding links...", end=" ")
                try:
                    nav_tag = self.soup.find("nav", class_="right")
                    if nav_tag and links is not None:
                        ul_tag = nav_tag.find("ul")
                        if ul_tag:
                            # Create and append <li> elements with <a> tags to the <ul> tag
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
                            print("complete.")
                        else:
                            print("no <ul> tag with class='right' found in the template.")
                except:
                    print("no <nav> tag found in the template.")
            else:
                print("    No links to add on the page.")
            self.step += 1  # step 7
            
            self.step = self.clean_links(page_type=page_type)
            # clean up any empty links
            print("      Cleaning up links...", end=" ")
            try:
                empty_links = self.soup.find_all('li', lambda tag: tag.find('a', href=''))
                if empty_links:
                    for li_tag in empty_links:
                        li_tag.extract()
                if page_type == "Article":
                    all_links = self.soup.find_all('li')
                    for li_tag in all_links:
                        li_tag.extract()
                print("complete.")
            except:
                print("nothing to clean.")
            self.step += 1  # step 8

            # meta content 
            self.step = self.change_meta(index=index, follow=follow, description=description)       
            print('    Setting SEO...', end=" ")
            robots_meta = None
            description_meta = None
            try:
                robots_meta = self.soup.find('meta', attrs={'name': 'robots'})
                robots_meta['content'] = add_SEO_meta_content(index, follow)
            except:
                print("    no `robots` meta tag in the template, adding... ", end=" ")
                robots_meta = self.soup.new_tag('meta')
                robots_meta['name'] = 'robots'
                robots_meta['content'] = add_SEO_meta_content(index, follow)
            try:
                description_meta = self.soup.find('meta', attrs={'name': 'description'})
                description_meta['content'] = description
            except:
                print("    no 'description' meta tag in the template, adding... ", end=" ")
                description_meta = self.soup.new_tag('meta')
                description_meta['name'] = 'description'
                description_meta["content"] = description

            robots_meta_content: str = robots_meta['content']
            if 'noindex' in robots_meta_content and 'nofollow' in robots_meta_content:
                print('this page will NOT be indexed by search engines.')
            elif 'nofollow' in robots_meta_content:
                print('page WILL be indexed by search engines.')
            elif 'noindex' in robots_meta_content:
                print('links on this page WILL be indexed by search engines.')
            else:
                print('page, and links, WILL be indexed by search engines.')
            self.step += 1  # step 9

            # Final step - set filepath and write file to path
            self.step, path_to_page = self.make_html_file(path_to_page=path_to_page, root=root, output_filename=output_filename)
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
            print(f"HTML file successfully created and written to {output_file.name}.\n")
            self.step += 1  # step 10

            self.step, sitemap_entry = self.make_sitemap(page_url=page_url, path_to_page=path_to_page, priority=priority)
            # Build sitemap_entry
            page_url = 'https://mikeverwer.github.io'
            current_date = datetime.date.today()
            formatted_date = current_date.strftime('%Y-%m-%d')
            sitemap_entry = f'  <url>\n'
            sitemap_entry += f'    <loc>{page_url}{path_to_page}.html</loc>\n'
            sitemap_entry += f'    <lastmod>{formatted_date}</lastmod>\n'
            sitemap_entry += f'    <changefreq>monthly</changefreq>\n'
            sitemap_entry += f'    <priority>{priority}</priority>\n'
            sitemap_entry += f'  </url>\n'

            return sitemap_entry
        except FileNotFoundError as fe:
            print(f"File not found.\n{fe}")
        except Exception as e:
            print(f"An error occurred after step {self.step}: {e}\n")

         # Find and modify:
            # | tag                  | Attribute        | Variable
            # |----------------------|------------------|-----------------------------------------------------
            # | title                | Tab Name         | new_title
            # | header -> a(second)  | Path to Page     | path_to_page
            # | h1                   | Page Title       | new_header
            # | nav class="right"    | Page Links       | tuple = (links: list[str], link_titles: list[str])
            # | zero-md              | Markdown Content | output_file OR md_filename, prioritizes md_filename
    def change_title(self, new_title=None):
        return self.step + 1
    
    def change_header(self, new_header=None):
        return self.step + 1
    
    def change_article(self, output_filename, md_filename=None):
        return self.step + 1
    
    def modify_path(self, path_to_page):
        return self.step + 1, path_to_page
    
    def add_links(self, links, link_titles):
        return self.step + 1
    
    def clean_links(self, page_type):
        return self.step + 1
    
    def change_meta(self, index, follow, description):
        return self.step + 1
    
    def make_html_file(self, path_to_page, root, output_filename):
        return self.step + 1, path_to_page
    
    def make_sitemap(self, page_url, path_to_page, priority):
        return self.step + 1, sitemap_entry

    
def main():
    # Example usage:
    html_file_path = "default_page.html"  # Path to your HTML file
    output_file_path = "index"  # Path to the output HTML file
    personal_site(html_file_path, output_file_path, "home", "Home")


if __name__ == '__main__':
    main()
