"""Shared header markup for the source site and generated character pages."""
import re

def apply_navigation(content, depth=0, current=None):
    prefix = "../" * depth
    def link(filename, label, page):
        active = ' aria-current="page"' if current == page else ''
        return f'<a href="{prefix}{filename}"{active}>{label}</a>'
    header = f'''<header class="site-header screen-only">
      <a class="logo" href="{prefix}index.html" aria-label="TBD's Dragon Den – home">
        <div class="logo-mark"><img src="{prefix}Eldritch%20shadows/IconDragonDenSketchEmbedded.svg" alt="" class="logo-icon" /></div>
        <div class="logo-text">TBD's Dragon Den</div>
      </a>
      <nav class="site-nav" aria-label="Main navigation">
        {link('index.html#projects', 'Projects', 'projects')}
        {link('about.html', 'About', 'about')}
        {link('contact.html', 'Contact', 'contact')}
        <span class="site-pill">Indie worlds &amp; games</span>
      </nav>
    </header>'''
    if re.search(r'<header\b', content):
        content = re.sub(r'<header\b[^>]*>.*?</header>', lambda _: header, content, count=1, flags=re.S)
    else:
        content = content.replace('<body>', '<body>' + header, 1)
    content = re.sub(r'<link\b[^>]*href="[^"]*site-header\.css"[^>]*>\s*', '', content)
    return content.replace('</head>', f'  <link rel="stylesheet" href="{prefix}site-header.css" />\n</head>', 1)
