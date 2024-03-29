from bs4 import BeautifulSoup
import os

def personal_site(template_file_path: str = "default_page.html", md_filename: str = None, output_filename: str = "output", 
                  new_title: str = "page", new_header: str = "Page", path_to_page: str = "/page", links: list[str] = None, 
                  link_titles: list[str] = None, write_to_path: bool = False, root: str = "outputs"):
    try:
        with open(template_file_path, "r", encoding="utf-8") as html_file:
            html_content = html_file.read()
        soup = BeautifulSoup(html_content, "html.parser")

        # Find and modify:
        # | tag                  | Attribute        | Variable
        # |----------------------|------------------|-----------------------------------------------------
        # | title                | Tab Name         | new_title
        # | header -> a(second)  | Path to Page     | path_to_page
        # | h1                   | Page Title       | new_header
        # | nav class="right"    | Page Links       | tuple = (links: list[str], link_titles: list[str])
        # | zero-md              | Markdown Content | output_file OR md_filename, prioritizes md_filename

        title_tag = soup.find("title")
        if title_tag:
            title_tag.string = f"{new_title}  ||  Mike Verwer"
        else:
            print("No <title> tag found in the template.")
        h1_tag = soup.find("h1")
        if h1_tag:
            h1_tag.string = new_header
        else:
            print("No <h1> tag found in the template.")
        zero_md_tag = soup.find("zero-md")
        if zero_md_tag:
            zero_md_tag["src"] = f"{output_filename}.md" if md_filename is None else f"{md_filename}.md"
        else:
            print("No <zero-md> tag found in the template.")

        if path_to_page[0] != '/' and path_to_page[0] != '\\':
            path_to_page = "/" + path_to_page
        if len(path_to_page) > 1 and (path_to_page[-1] != '/' and path_to_page[-1] != '\\'):
            path_to_page = path_to_page + "/"

        header_tag = soup.find("header")
        if header_tag:
            a_tags = header_tag.find_all("a")
            if len(a_tags) >= 2:
                a_tags[1]["href"] = f"{path_to_page}{output_filename}.html" if output_filename != 'index' else '/assets/docs/about.html'
            else:
                print("There is no second <a> tag within the <header> tag.")
        else:
            print("No <header> tag found in the template.")

        nav_tag = soup.find("nav", class_="right")
        if nav_tag and links is not None:
            ul_tag = nav_tag.find("ul")
            if ul_tag:
                # Create and append <li> elements with <a> tags to the <ul> tag
                for i, href in enumerate(links):
                    li_tag = soup.new_tag("li")
                    if " target=" in href:
                        link_portions = href.split()
                        href_portion = link_portions[0]
                        target_portion = link_portions[1].split('=')[1]
                        a_tag = soup.new_tag("a", href=href_portion, target=f"{target_portion}")
                    else:
                        a_tag = soup.new_tag("a", href=href)
                    a_tag.string = link_titles[i]
                    li_tag.append(a_tag)
                    ul_tag.append(li_tag)
            else:
                print("No <ul> tag with class='right' found in the template.")
        else:
            print("No links to add or no <nav> tag found in the template.")
        
        if path_to_page[0] == '/' or path_to_page[0] == '\\':
            pass
        else:
            path_to_page = "/" + path_to_page
        if write_to_path:
            output_file_path = f"{root}{path_to_page}{output_filename}.html"
            output_directory = os.path.dirname(output_file_path)
            os.makedirs(output_directory, exist_ok=True)
            with open(output_file_path, 'w', encoding='utf-8') as output_filename:
                output_filename.write(str(soup.prettify()))
        else:
            output_file_path = f"outputs/{output_filename}.html"
            with open(output_file_path, "w", encoding="utf-8") as output_filename:
                output_filename.write(str(soup.prettify()))

        print(f"HTML file successfully created and written to {output_filename.name}.")
    except FileNotFoundError as fe:
        print(f"File not found.\n{fe}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    # Example usage:
    html_file_path = "default_page.html"  # Path to your HTML file
    output_file_path = "output"  # Path to the output HTML file
    personal_site(html_file_path, output_file_path, "home", "Home", "/index.html")


if __name__ == '__main__':
    main()
