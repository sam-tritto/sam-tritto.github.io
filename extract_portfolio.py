import os
import re
import shutil
import urllib.parse
from html.parser import HTMLParser

class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
    
    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True
            
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
            
    def handle_data(self, data):
        if self.in_title:
            self.title += data

class ContentParser(HTMLParser):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.body_parts = []
        self.skip_depth = 0
        self.in_script = False
        self.in_style = False
        self.allowed_tags = {'h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'img', 'a'}

    def is_nav_or_header(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag in ['header', 'nav']:
            return True
        if attr_dict.get('id') in ['atIdViewHeader', 'navigation-drawer']:
            return True
        if attr_dict.get('role') in ['navigation', 'banner']:
            return True
        classes = attr_dict.get('class', '')
        if 'navigation' in classes or 'sidebar' in classes or 'header' in classes:
            if 'drawer' in classes or 'nav' in classes:
                return True
        return False

    def handle_starttag(self, tag, attrs):
        if tag == 'script': 
            self.in_script = True
        elif tag == 'style': 
            self.in_style = True

        if self.skip_depth > 0:
            self.skip_depth += 1
            return
        if self.is_nav_or_header(tag, attrs):
            self.skip_depth = 1
            return
            
        if self.in_script or self.in_style:
            return

        if tag in self.allowed_tags:
            if tag == 'img':
                attr_dict = dict(attrs)
                src = urllib.parse.unquote(attr_dict.get('src', ''))
                alt = attr_dict.get('alt', '')
                self.body_parts.append(f'<img src="{src}" alt="{alt}" class="post-image">')
            elif tag == 'a':
                attr_dict = dict(attrs)
                href = urllib.parse.unquote(attr_dict.get('href', ''))
                if href.endswith('.html') and not href.startswith('http'):
                    href = href.replace(' ', '-').replace('_', '-').lower()
                self.body_parts.append(f'<a href="{href}">')
            else:
                self.body_parts.append(f'<{tag}>')

    def handle_endtag(self, tag):
        if tag == 'script': 
            self.in_script = False
        elif tag == 'style': 
            self.in_style = False

        if self.skip_depth > 0:
            self.skip_depth -= 1
            return

        if self.in_script or self.in_style:
            return

        if tag in self.allowed_tags and tag != 'img':
            self.body_parts.append(f'</{tag}>')

    def handle_data(self, data):
        if self.skip_depth > 0 or self.in_script or self.in_style:
            return
        txt = data.strip()
        if not txt:
            return
        if "Skip to main content" in txt or "Skip to navigation" in txt:
            return
        if txt == "Sam's Data Portfolio" or txt == f"Sam's Data Portfolio - {self.title}":
            return
        
        # Output clean text
        self.body_parts.append(data)

def slugify(name):
    # Convert spaces/special chars to single dash, lowercase
    name = name.replace('.html', '')
    slug = re.sub(r'[^a-zA-Z0-9\s_-]', '', name)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug.lower() + '.html'

def main():
    pub_dir = "/Users/sam/Desktop/Desktop Cloud/Data_Science/Portfolio/PUBLISHED"
    dest_dir = "/Users/sam/Desktop/Desktop Cloud/Data_Science/Projects/sam-tritto.github.io/projects"
    
    os.makedirs(dest_dir, exist_ok=True)
    
    html_files = [f for f in os.listdir(pub_dir) if f.endswith('.html')]
    
    # Track metadata for generated pages to construct index.html later
    project_metadata = []

    for fname in html_files:
        # Skip top level utility pages
        if fname in ['Home.html', 'More Projects.html', '404.html']:
            continue
            
        src_path = os.path.join(pub_dir, fname)
        
        # 1. Parse Title
        with open(src_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        t_parser = TitleParser()
        t_parser.feed(html_content)
        title = t_parser.title.replace("Sam's Data Portfolio - ", "").strip()
        if not title:
            title = fname.replace('.html', '')
            
        # 2. Parse Content
        c_parser = ContentParser(title)
        c_parser.feed(html_content)
        
        body_content = "".join(c_parser.body_parts)
        # Post-processing cleaning
        body_content = re.sub(r'<p>\s*</p>', '', body_content)
        
        # 3. Save clean page
        slug = slugify(fname)
        dest_path = os.path.join(dest_dir, slug)
        
        template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Sam's Data Portfolio</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <article class="post-container">
        <a href="../index.html" class="post-back">&larr; Back to Portfolio</a>
        <header class="post-header-area">
            <h1>{title}</h1>
        </header>
        <section class="post-content">
            {body_content}
        </section>
    </article>
</body>
</html>
"""
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(template)
            
        print(f"Generated: {slug} (Title: {title})")
        
        # Extract a snippet for index.html card preview
        snippet = ""
        # Find first paragraph
        p_match = re.search(r'<p>(.*?)</p>', body_content, re.DOTALL)
        if p_match:
            # Strip tag wrappers
            snippet = re.sub(r'<[^>]+>', '', p_match.group(1)).strip()
            if len(snippet) > 180:
                snippet = snippet[:177] + "..."
        
        # 4. Copy asset folders if they exist
        asset_folder_name = fname.replace('.html', '')
        src_asset_path = os.path.join(pub_dir, asset_folder_name)
        if os.path.isdir(src_asset_path):
            dest_asset_path = os.path.join(dest_dir, asset_folder_name)
            # Remove existing to overwrite cleanly if rerun
            if os.path.exists(dest_asset_path):
                shutil.rmtree(dest_asset_path)
            shutil.copytree(src_asset_path, dest_asset_path)
            print(f"  Copied assets folder: {asset_folder_name}")
            
        # Collect metadata
        project_metadata.append({
            'title': title,
            'slug': slug,
            'snippet': snippet,
            'filename': fname
        })
        
    # Write metadata to a json file for index.html generation
    import json
    meta_path = os.path.join(os.path.dirname(dest_dir), 'projects_meta.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(project_metadata, f, indent=2)
    print(f"Saved metadata for {len(project_metadata)} projects to projects_meta.json")

if __name__ == '__main__':
    main()
