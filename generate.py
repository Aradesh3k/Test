import os
from datetime import datetime
import html

POSTS_DIR = 'posts'
OUTPUT_DIR = 'docs'
BASE_TEMPLATE = 'templates/base.html'

def read_template():
    with open(BASE_TEMPLATE, 'r') as f:
        return f.read()


def parse_post(path):
    with open(path, 'r') as f:
        lines = [line.rstrip('\n') for line in f]
    if not lines:
        return None
    title = lines[0].lstrip('#').strip()
    body_lines = lines[1:]
    html_lines = []
    paragraph = []
    for line in body_lines:
        if line.startswith('# '):
            if paragraph:
                html_lines.append(f'<p>{html.escape(" ".join(paragraph))}</p>')
                paragraph = []
            html_lines.append(f'<h1>{html.escape(line[2:])}</h1>')
        elif line == '':
            if paragraph:
                html_lines.append(f'<p>{html.escape(" ".join(paragraph))}</p>')
                paragraph = []
        else:
            paragraph.append(line)
    if paragraph:
        html_lines.append(f'<p>{html.escape(" ".join(paragraph))}</p>')
    return title, '\n'.join(html_lines)

def slug_from_filename(filename):
    return os.path.splitext(filename)[0]


def build_posts(template):
    posts = []
    for name in sorted(os.listdir(POSTS_DIR), reverse=True):
        if not name.endswith('.md'):
            continue
        path = os.path.join(POSTS_DIR, name)
        parsed = parse_post(path)
        if not parsed:
            continue
        title, body_html = parsed
        slug = slug_from_filename(name)
        output_path = os.path.join(OUTPUT_DIR, f'{slug}.html')
        content = f'<h2>{title}</h2>\n{body_html}'
        with open(output_path, 'w') as f:
            f.write(template.format(title=title, content=content))
        date_str = slug.split('-')[0:3]
        try:
            date = datetime.strptime('-'.join(date_str), '%Y-%m-%d')
        except Exception:
            date = datetime.today()
        posts.append({'title': title, 'slug': slug, 'date': date})
    return posts

def build_index(template, posts):
    items = []
    for post in posts:
        date_fmt = post['date'].strftime('%Y-%m-%d')
        items.append(
            f'<li><a href="{post["slug"]}.html">{post["title"]}</a> '
            f'<small class="text-muted">{date_fmt}</small></li>'
        )
    content = '<ul class="list-unstyled">\n' + '\n'.join(items) + '\n</ul>'
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w') as f:
        f.write(template.format(title='Home', content=content))

def build_rss(posts):
    rss_items = []
    for post in posts:
        date_fmt = post['date'].strftime('%a, %d %b %Y %H:%M:%S +0000')
        rss_items.append(
            '<item>'
            + '<title>' + html.escape(post['title']) + '</title>'
            + '<link>{base_url}/' + post['slug'] + '.html</link>'
            + '<pubDate>' + date_fmt + '</pubDate>'
            + '</item>'
        )
    rss_content = (
        '<?xml version="1.0"?>\n'
        '<rss version="2.0">\n'
        '<channel>\n'
        '<title>My Blog</title>\n'
        '<link>{base_url}</link>\n'
        '<description>Simple blog example</description>\n'
        + ''.join(rss_items) +
        '\n</channel>\n'
        '</rss>'
    )
    with open(os.path.join(OUTPUT_DIR, 'rss.xml'), 'w') as f:
        f.write(rss_content)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    template = read_template()
    posts = build_posts(template)
    build_index(template, posts)
    build_rss(posts)


if __name__ == '__main__':
    main()
