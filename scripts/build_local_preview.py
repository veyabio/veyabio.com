from pathlib import Path
from datetime import datetime
import html
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"

SERVICES = [
    ("01", "Website Content & Copywriting", "Clear, accurate copy that keeps the science intact and the reader engaged.", "Full website copy, page-by-page editing, messaging architecture, and content audits for scientific organisations.", ["Website copy", "Editing", "Content audits", "Messaging"]),
    ("02", "LinkedIn & Social Campaigns", "Consistent, credible content that turns expertise into visibility.", "Content calendars, spotlight series, editorial planning, and campaign strategy for complex scientific stories.", ["Editorial calendars", "Spotlight series", "Campaign strategy"]),
    ("03", "Marketing Collateral", "Polished materials built for partners, visitors, and decision-makers.", "Welcome brochures, international delegation packages, one-pagers, flyers, and print-ready communication.", ["Brochures", "Delegation packages", "One-pagers"]),
    ("04", "Advertising & Promotion", "Focused campaign assets that make launches, events, and opportunities easier to notice.", "Messaging and promotional materials for events, launches, recruitment drives, and targeted campaigns.", ["Flyers", "Event campaigns", "Launch assets"]),
    ("05", "Science & Data Translation", "Technical depth, translated into a story a non-specialist can follow.", "Research, evidence, and technical detail shaped into accessible, accurate communication for wider audiences.", ["Research translation", "Audience framing", "Data stories"]),
]
NAV = [("Home", "/"), ("Services", "/services/"), ("Work", "/work/"), ("Blog", "/blog/"), ("Contact", "/contact/")]
EMAIL = "hello@veyabio.com"


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    _, head, body = text.split("---", 2)
    data = {}
    for line in head.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data, body.lstrip()


def inline_markdown(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)


def markdown_to_html(text):
    lines, parts, paragraph = text.splitlines(), [], []
    list_type = None

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            parts.append("<p>" + inline_markdown(" ".join(x.strip() for x in paragraph)) + "</p>")
            paragraph = []

    def close_list():
        nonlocal list_type
        if list_type:
            parts.append(f"</{list_type}>")
            list_type = None

    for line in lines:
        value = line.strip()
        if not value:
            flush_paragraph(); close_list(); continue
        if value.startswith("## "):
            flush_paragraph(); close_list(); parts.append("<h2>" + inline_markdown(value[3:]) + "</h2>")
        elif value.startswith("### "):
            flush_paragraph(); close_list(); parts.append("<h3>" + inline_markdown(value[4:]) + "</h3>")
        elif value.startswith("> "):
            flush_paragraph(); close_list(); parts.append("<blockquote><p>" + inline_markdown(value[2:]) + "</p></blockquote>")
        elif re.match(r"^\d+\. ", value):
            flush_paragraph()
            if list_type != "ol": close_list(); parts.append("<ol>"); list_type = "ol"
            parts.append("<li>" + inline_markdown(re.sub(r"^\d+\. ", "", value)) + "</li>")
        elif value.startswith("- "):
            flush_paragraph()
            if list_type != "ul": close_list(); parts.append("<ul>"); list_type = "ul"
            parts.append("<li>" + inline_markdown(value[2:]) + "</li>")
        else:
            paragraph.append(value)
    flush_paragraph(); close_list()
    return "\n".join(parts)


def expand_includes(text):
    pattern = re.compile(r"{%\s*include\s+([^\s%]+)\s*%}")
    for _ in range(6):
        updated = pattern.sub(lambda match: (ROOT / "_includes" / match.group(1).strip("'\"")).read_text(encoding="utf-8"), text)
        if updated == text:
            break
        text = updated
    return text


def common(text, page):
    current_url = page.get("url", "/")

    def navigation(_match):
        return "\n".join(
            f'<a href="{url}"' + (' aria-current="page"' if current_url == url else "") + f'>{label}</a>'
            for label, url in NAV
        )

    text = re.sub(r"{%\s*for item in site\.data\.navigation\s*%}.*?{%\s*endfor\s*%}", navigation, text, flags=re.S)
    text = re.sub(r"{{\s*'([^']+)'\s*\|\s*relative_url\s*}}", lambda match: match.group(1), text)
    text = text.replace("{{ site.email }}", EMAIL).replace("{{ site.lang | default: 'en' }}", "en")
    text = text.replace("{{ page.layout | default: 'default' }}", page.get("layout", "default"))
    title = page.get("title", "VeyaBio")
    description = page.get("description", "VeyaBio helps scientific organisations communicate complex work clearly.")
    seo = f'<title>{html.escape(title)} | VeyaBio</title>\n<meta name="description" content="{html.escape(description, quote=True)}">'
    text = text.replace("{% seo %}", seo).replace("{% feed_meta %}", '<link rel="alternate" type="application/atom+xml" href="/feed.xml">')
    text = text.replace("{{ page.title }}", page.get("title", "")).replace("{{ page.description }}", page.get("description", "")).replace("{{ page.category }}", page.get("category", ""))
    text = text.replace('{{ page.read_time | default: "5 min read" }}', page.get("read_time", "5 min read"))
    text = text.replace('{{ page.date | date: "%d %B %Y" }}', page.get("date", datetime.now()).strftime("%d %B %Y"))
    return text


POSTS = []
for post_path in sorted((ROOT / "_posts").glob("*.md"), reverse=True):
    meta, body = front_matter(post_path)
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", post_path.stem)
    meta.update(url=f"/blog/{slug}/", body=markdown_to_html(body), date=datetime.strptime(post_path.name[:10], "%Y-%m-%d"))
    POSTS.append(meta)


def wrap(page, content, layout="default"):
    _, layout_body = front_matter(ROOT / "_layouts" / f"{layout}.html")
    if layout == "post":
        post_page = common(expand_includes(layout_body.replace("{{ content }}", content)), page)
        _, default_body = front_matter(ROOT / "_layouts" / "default.html")
        return common(expand_includes(default_body.replace("{{ content }}", post_page)), page)
    return common(expand_includes(layout_body.replace("{{ content }}", content)), page)


def render_source(path):
    page, body = front_matter(path)
    page.setdefault("layout", "default")
    if path == ROOT / "index.html":
        page["url"] = "/"
    elif path.name == "404.html":
        page["url"] = "/404.html"
    else:
        page["url"] = "/" + str(path.parent.relative_to(ROOT)).replace("\\", "/").strip("/") + "/"

    if path == ROOT / "index.html":
        lines = "".join(
            f'<a class="service-line" href="/services/#service-{index}"><h3>{title}</h3><p>{short}</p><span aria-hidden="true">→</span></a>'
            for index, (_number, title, short, _body, _deliverables) in enumerate(SERVICES, 1)
        )
        body = re.sub(r"{%\s*for service in site\.data\.services\s*%}.*?{%\s*endfor\s*%}", lines, body, flags=re.S)
    elif path.as_posix().endswith("services/index.html"):
        details = "".join(
            f'<article class="service-detail reveal" id="service-{index}"><span class="number">{number}</span><h2>{title}</h2><div class="service-detail-copy"><p>{service_body}</p><div class="deliverables">' + "".join(f"<span>{item}</span>" for item in deliverables) + "</div></div></article>"
            for index, (number, title, _short, service_body, deliverables) in enumerate(SERVICES, 1)
        )
        body = re.sub(r"{%\s*for service in site\.data\.services\s*%}.*?{%\s*endfor\s*%}", details, body, flags=re.S)

    if path.as_posix().endswith("blog/index.html"):
        featured = POSTS[0]
        featured_html = f'<a class="featured-post reveal" href="{featured["url"]}"><div class="featured-visual" aria-hidden="true"></div><div class="featured-copy"><p class="eyebrow eyebrow-light">Featured · {featured["category"]}</p><h2>{featured["title"]}</h2><p>{featured["description"]}</p><span class="text-link">Read the article <span>→</span></span></div></a>'
        body = re.sub(r"{%\s*assign featured.*?{%\s*endif\s*%}", featured_html, body, flags=re.S)
        cards = "".join(f'<a class="post-card reveal" href="{post["url"]}"><div class="post-card-meta"><span>{post["category"]}</span><span>{post["read_time"]}</span></div><h2>{post["title"]}</h2><p>{post["description"]}</p></a>' for post in POSTS[1:])
        body = re.sub(r"{%\s*for post in site\.posts offset:1\s*%}.*?{%\s*endfor\s*%}", cards, body, flags=re.S)

    rendered_body = common(expand_includes(body), page)
    return page, wrap(page, rendered_body, page.get("layout", "default"))


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    sources = [ROOT / "index.html", ROOT / "404.html"] + list(ROOT.glob("*/index.html"))
    for source in sources:
        if any(name in source.relative_to(ROOT).parts for name in ("_site", "tmp", "vendor")):
            continue
        page, text = render_source(source)
        target = OUT / page["url"].lstrip("/")
        if page["url"].endswith("/"):
            target = target / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    for post in POSTS:
        target = OUT / post["url"].lstrip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(wrap(post, post["body"], "post"), encoding="utf-8")
    shutil.copytree(ROOT / "assets", OUT / "assets")
    shutil.copy2(ROOT / "CNAME", OUT / "CNAME")
    feed_items = "".join(f'<entry><title>{html.escape(post["title"])}</title><link href="https://veyabio.com{post["url"]}" /></entry>' for post in POSTS)
    (OUT / "feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>VeyaBio</title>{feed_items}</feed>', encoding="utf-8")
    page_urls = ["/", "/services/", "/work/", "/blog/", "/contact/"] + [post["url"] for post in POSTS]
    sitemap_urls = "".join(f'<url><loc>https://veyabio.com{url}</loc></url>' for url in page_urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sitemap_urls}</urlset>', encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: https://veyabio.com/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(list(OUT.rglob('*.html')))} pages in {OUT}")


if __name__ == "__main__":
    main()