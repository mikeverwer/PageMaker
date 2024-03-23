from bs4 import BeautifulSoup

def personal_site(template_file_path: str = "default_page.html", md_filename: str = None, output_file: str = "output", new_title: str = "page", new_header: str = "Page", path_to_page: str = "/page", links: list[str] = None, link_titles: list[str] = None, write_to_path: bool = False):
    try:
        with open(template_file_path, "r", encoding="utf-8") as html_file:
            html_content = html_file.read()
        soup = BeautifulSoup(html_content, "html.parser")

        # Find and modify:
        # | tag                  | Attribute        |
        # |----------------------|------------------|
        # | title                | Tab Name         |
        # | header -> a(second)  | Path to Page     |
        # | h1                   | Page Title       | 
        # | nav class="right"    | Page Links       |
        # | zero-md              | Markdown Content |

        title_tag = soup.find("title")
        title_tag.string = f"{new_title}  ||  Mike Verwer"
        zero_md_tag = soup.find("zero-md")
        zero_md_tag["src"] = f"{output_file}.md" if md_filename is None else f"{md_filename}.md"

        header_tag = soup.find("header")
        if header_tag:
            a_tags = header_tag.find_all("a")
            if len(a_tags) >= 2:
                a_tags[1]["href"] = f"{path_to_page}.html"
            else:
                print("There is no second <a> tag within the <header> tag.")
        else:
            print("No <header> tag found in the HTML document.")

        nav_tag = soup.find("nav", class_="right")
        if links is not None:
            ul_tag = nav_tag.find("ul")
            if ul_tag:
                # Create and append <li> elements with <a> tags to the <ul> tag
                for i, href in enumerate(links):
                    li_tag = soup.new_tag("li")
                    if " target=" in href:
                        link_portions = href.split()
                        href_portion = link_portions[0]
                        target_portion = link_portions[1].split('=')[1]
                        a_tag = soup.new_tag("a", href=href_portion, target=target_portion)
                    else:
                        a_tag = soup.new_tag("a", href=href)
                    a_tag.string = link_titles[i]
                    li_tag.append(a_tag)
                    ul_tag.append(li_tag)
            else:
                print("No <ul> tag with class='right' found in the HTML document.")
        else:
            print("No links to add.")
        
        if not path_to_page[0] == '/' or not path_to_page[0] == '\\':
            path_to_page = "/" + path_to_page
        if write_to_path:
            output_file = f"outputs{path_to_page}.html"
        else:
            output_file = f"outputs/{output_file}.html"
        # Write the modified HTML content to the output file
        with open(output_file, "w", encoding="utf-8") as output_file:
            output_file.write(str(soup.prettify()))

        print(f"HTML file successfully created and written to {output_file.name}.")
    except FileNotFoundError:
        print("Template HTML file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
html_file_path = "default_page.html"  # Path to your HTML file
output_file_path = "output"  # Path to the output HTML file
personal_site(html_file_path, output_file_path, "home", "Home", "/index.html")
