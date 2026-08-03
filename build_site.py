"""
build_site.py

Headless equivalent of PageMaker.make_files(), driven entirely by a JSON
config produced by PageMaker's own "Save Config" button — no Tkinter
required. Meant to be run manually/locally (e.g. via a PowerShell wrapper),
not on a CI trigger — every page's date is stamped with today, matching
PageMaker's own GUI behavior, on the assumption that you're the one
deciding when a full rebuild should happen.

Usage:
    python build_site.py --config site_config.json

--root and --template are optional overrides for project_data.root/template
in the JSON — only useful if you want to build somewhere other than what's
already saved in the config (e.g. a scratch/test directory).
"""
import argparse
import json
import re
from pathlib import Path

from pagemaker_core import PersonalSitePage


def build(config_path: str, root_override: str = None, template_override: str = None) -> str:
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    project = config.get("project_data", {})
    root_path = root_override or project.get("root") or "outputs"
    template_file = template_override or project.get("template") or "default_page.html"
    robots_content = project.get("robots", "")

    sitemap_content = []

    for i, page in enumerate(config.get("pages", [])):
        html_filename = (page.get("html filename -insert") or "").strip()
        if not html_filename:
            print(f"  Row {i + 1}: missing HTML filename, skipping.")
            continue
        html_filename = html_filename.split(".")[0]

        md_filename = (page.get("md filename -insert") or "").strip() or None
        description = (page.get("SEO description -text") or "").strip()

        names = (page.get("names -insert") or "").split(", ")
        title = names[0] if names and names[0] else None
        header = names[1] if len(names) > 1 else None

        page_path = (page.get("path -insert") or "").strip() or "/"

        priority_raw = (page.get("priority -insert") or "").strip()
        priority = float(priority_raw) if priority_raw else None

        links = page.get("links") or None
        index = page.get("SEO index -set", 0)
        follow = page.get("SEO follow -set", 0)
        page_type = page.get("type -set", "Main")

        print(f"Building {html_filename}.html...")
        page_obj = PersonalSitePage(
            template_file_path=template_file,
            output_filename=html_filename,
            md_filename=md_filename,
            description=description,
            new_title=title,
            new_header=header,
            path_to_page=page_path,
            links=links,
            index=index,
            priority=priority,
            follow=follow,
            write_to_path=True,
            root=root_path,
            page_type=page_type,
            logger=None,  # headless: PersonalSitePage.log() just prints
        )
        sitemap_content.append(page_obj.sitemap_entry)

    make_sitemap(sitemap_content, root_path)
    write_robots(robots_content, root_path)
    print("\nProcess complete, your website is built!")
    return root_path


def make_sitemap(sitemap_content, root_path: str) -> None:
    """Headless port of PageMaker.make_sitemap() — same merge logic, no self.log."""
    sitemap_filepath = Path(root_path) / "sitemap.xml"
    loc_tag = re.compile(r"<loc>(.*?)</loc>")
    lastmod_tag = re.compile(r"<lastmod>(.*?)</lastmod>")
    priority_tag = re.compile(r"<priority>(.*?)</priority>")

    if sitemap_filepath.exists():
        print("Found existing sitemap, updating...", end=" ")
        content = sitemap_filepath.read_text(encoding="utf-8").split("</urlset>")[0]
        loc_tags = loc_tag.findall(content)

        for sitemap_page in sitemap_content:
            page_loc = loc_tag.findall(sitemap_page)[0]
            if page_loc in loc_tags:
                page_lastmod = lastmod_tag.findall(sitemap_page)[0]
                page_priority = priority_tag.findall(sitemap_page)[0]
                start_search = content.find(f"<loc>{page_loc}</loc>")
                if start_search != -1:
                    lastmod_start = content.find("<lastmod>", start_search)
                    lastmod_end = content.find("</lastmod>", lastmod_start) + len("</lastmod>")
                    priority_start = content.find("<priority>", start_search)
                    priority_end = content.find("</priority>", priority_start) + len("</priority>")
                    content = (content[:lastmod_start] + f"<lastmod>{page_lastmod}</lastmod>" + content[lastmod_end:])
                    content = (content[:priority_start] + f"<priority>{page_priority}</priority>" + content[priority_end:])
            else:
                content += sitemap_page
        content += "\n</urlset>"
    else:
        print("No current sitemap, building...", end=" ")
        content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        content += "".join(sitemap_content)
        content += "</urlset>"

    Path(root_path).mkdir(parents=True, exist_ok=True)
    sitemap_filepath.write_text(content, encoding="utf-8")
    print(f"sitemap.xml written to {sitemap_filepath}")


def write_robots(robots_content: str, root_path: str) -> None:
    robots_filepath = Path(root_path) / "robots.txt"
    Path(root_path).mkdir(parents=True, exist_ok=True)
    robots_filepath.write_text(robots_content, encoding="utf-8")
    print(f"robots.txt written to {robots_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the PageMaker JSON config (from Save Config)")
    parser.add_argument("--root", default=None, help="Override project_data.root (optional — defaults to what's saved in the config)")
    parser.add_argument("--template", default=None, help="Override project_data.template (optional — defaults to what's saved in the config)")
    args = parser.parse_args()
    build(args.config, root_override=args.root, template_override=args.template)
