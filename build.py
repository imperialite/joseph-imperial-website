"""Generate factual, academic website layouts. Run with Python 3.11+."""
from pathlib import Path
from html import escape
import math
import json
import sys
import re

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
PAPERS = json.loads((ROOT / "publications.json").read_text(encoding="utf-8"))
LAYOUTS = [("classic", "Academic folio"), ("sidebar", "Research index"), ("publications", "Journal layout")]

CONTENT = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
SITE = CONTENT["site"]
SCHOLAR, CV = SITE["scholar_url"], SITE["cv_url"]
PUBLIC = "--public" in sys.argv
ANALYTICS_ID = SITE.get("analytics_id", "")
if not isinstance(ANALYTICS_ID, str) or (ANALYTICS_ID and not re.fullmatch(r"G-[A-Z0-9]+", ANALYTICS_ID)):
    raise ValueError("Google Analytics Measurement ID must be blank or start with G- followed by uppercase letters and digits.")



def link(url, label, cls=""):
    return f'<a class="{cls}" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label}</a>'

def preview_bar(active):
    items = ''.join(f'<a href="{key}.html" {"aria-current=page" if key == active else ""}>{i}. {name}</a>' for i,(key,name) in enumerate(LAYOUTS,1))
    return f'<div class="preview-bar"><a href="design-options.html" class="compare-link">Compare layouts</a><nav aria-label="Website layout options">{items}</nav></div>'

def head(title, indexable=False):
    robots = '' if PUBLIC and indexable else '<meta name="robots" content="noindex,nofollow">'
    analytics = f'<script defer src="assets/analytics.js" data-measurement-id="{ANALYTICS_ID}"></script>' if PUBLIC and indexable and ANALYTICS_ID else ''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{robots}<meta name="description" content="{escape(SITE['description'], quote=True)}"><title>{title}</title><link rel="icon" type="image/svg+xml" href="assets/favicon.svg?v=2"><link rel="stylesheet" href="assets/fonts.css"><link rel="stylesheet" href="styles.css">{analytics}</head>'''

def profile_links():
    items = [link(SCHOLAR,"Google Scholar"),link(SITE["github_url"],"Github"),link(SITE["anthology_url"],"ACL Anthology"),link(CV,"CV")]
    return '<div class="profile-links">' + ''.join(items) + '</div>'

def identity():
    return f'''<header class="identity"><div class="identity-text"><h1>{escape(SITE["name"])}</h1><p class="research-summary">I research the legal alignment of AI agents and the compliance of language models with policies, regulations, and expert-defined standards.</p><div class="appointments">{''.join(f'<div><p class="appointment">{role}</p></div>' for role in CONTENT['profile'])}</div><div class="profile-contact"><a class="email" href="mailto:{escape(SITE['email'],quote=True)}">{escape(SITE['email'])}</a>{profile_links()}</div></div><figure class="portrait-frame"><img class="portrait" src="assets/joseph-imperial.jpg" alt="Joseph Imperial" width="1015" height="1131" fetchpriority="high"><span class="portrait-corner" aria-hidden="true"></span></figure></header>'''

def top_nav():
    cv_link=link(CV,'CV <span aria-hidden="true">↗</span>')
    return f'<nav class="top-nav wrap" aria-label="Main navigation"><a class="name-link" href="#top">Joseph Imperial</a><div><a href="#about">About Me</a><a href="#news">News</a><a href="#selected-publications">Publications</a>{cv_link}</div></nav>'

def section_nav():
    return f'<nav class="section-nav" aria-label="Sections"><a href="#about">About Me</a><a href="#news">News</a><a href="#selected-publications">Publications</a><a href="#experience">Experience</a><a href="#education">Education</a>{link(CV,"CV")}</nav>'

def about():
    paragraphs = ''.join(f'<p>{text}</p>' for text in CONTENT['about'])
    return f'<section class="about" id="about"><h2>About Me</h2>{paragraphs}</section>'


def publications():
    groups=[]
    for year in dict.fromkeys(p['year'] for p in PAPERS):
        rows=[]
        for paper in (p for p in PAPERS if p['year']==year):
            title=link(paper['url'], escape(paper['title']), 'paper-title') if paper['url'] else '<span class="paper-title">'+escape(paper['title'])+'</span>'
            authors=escape(paper['authors']).replace('Joseph Marvin Imperial','<strong>Joseph Marvin Imperial</strong>')
            authors=f'<p class="authors">{authors}</p>'
            venue=escape(paper['venue'])
            if paper['url']:
                action=link(paper['url'],'Project Page' if 'project' in paper['link_label'].lower() else 'Paper','paper-link')
            else:
                action=f'<span class="preprint-note">{escape(paper["link_label"] or "Preprint forthcoming")}</span>'
            paper_class = "paper paper-featured" if paper.get("featured") else "paper"
            rows.append(f'<article class="{paper_class}" data-topic="{escape(paper["topic"],quote=True)}" data-year="{escape(year,quote=True)}"><h4>{title}</h4>{authors}<div class="paper-footer"><span class="venue">{venue}</span>{action}</div></article>')
        groups.append(f'<div class="year-group"><h3>{escape(year)}</h3><div>{"".join(rows)}</div></div>')
    return f'''<section class="publications" id="selected-publications"><div class="heading-row"><h2>Selected Publications</h2><p class="publication-note">{CONTENT['publication_note']}</p></div><div class="publication-list">{''.join(groups)}</div></section>'''

def news():
    items = ''.join(f'<li>{text}</li>' for text in CONTENT['news'])
    return f'<section class="news" id="news"><h2>News</h2><ul>{items}</ul></section>'


def timeline_section(key, heading, classes):
    rows = []
    for item in CONTENT[key]:
        note = f'<br><small>({escape(item["note"])})</small>' if item['note'] else ''
        paragraphs = ''.join(f'<p>{text}</p>' for text in item['paragraphs'])
        rows.append(f'<div><dt>{escape(item["date"])}{note}</dt><dd><strong>{escape(item["title"])}</strong><span>{escape(item["institution"])}</span>{paragraphs}</dd></div>')
    return f'<section id="{key}" class="{classes}"><h2>{heading}</h2><dl class="timeline">{"".join(rows)}</dl></section>'


def experience():
    return timeline_section('experience', 'Experience', 'background experience')


def education():
    return timeline_section('education', 'Education', 'background education')


def awards():
    return timeline_section('awards', 'Awards &amp; Recognition', 'awards')


def media():
    rows = ''.join(f'<li><span>{escape(item["outlet"])}</span><p>{item["html"]}</p></li>' for item in CONTENT['media'])
    return f'<section class="media" id="media"><h2>Media Presence</h2><ul>{rows}</ul></section>'


def socials():
    items = ''.join(f'<li>{link(item["url"],escape(item["label"]))}</li>' for item in CONTENT['socials'])
    return f'<section class="socials" id="socials"><h2>Socials</h2><ul>{items}</ul></section>'


def footer():
    return f"""<footer><span>{escape(SITE['name'])}</span><a href="mailto:{escape(SITE['email'],quote=True)}">{escape(SITE['email'])}</a><p class="design-credit">This website's design and color palette are inspired by the {link('https://law-ai.org/', 'Institute for Law &amp; AI')} website.</p></footer>"""


paths=[]
for ring in range(38):
    points=[]
    for step in range(181):
        angle=step*math.tau/180
        radius=65+ring*4.15
        x=250+radius*math.cos(angle)+17*math.sin(angle*3+ring*.075)
        y=250+radius*.87*math.sin(angle)+18*math.cos(angle*2+ring*.075)
        points.append(f'{x:.2f},{y:.2f}')
    paths.append('<path d="M'+' L'.join(points)+'Z"/>')
(DIST/'assets'/'line-motif.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500"><g fill="none" stroke="#1567e8" stroke-width=".65">'+''.join(paths)+'</g></svg>',encoding='utf-8')

for key,name in LAYOUTS:
    if key=='sidebar':
        main=f'<div class="index-layout wrap"><aside class="profile-column">{identity()}{section_nav()}</aside><main id="main" class="content-column">{about()}{news()}{publications()}{experience()}{education()}{awards()}{media()}{socials()}{footer()}</main></div>'
    elif key=='publications':
        main=f'<div class="journal-masthead">{top_nav()}<div class="wrap">{identity()}</div></div><main id="main" class="content-column wrap">{publications()}{about()}{news()}{experience()}{education()}{awards()}{media()}{socials()}{footer()}</main>'
    else:
        main=f'<div class="folio-masthead">{top_nav()}<div class="wrap">{identity()}</div></div><main id="main" class="content-column wrap">{about()}{news()}{publications()}{experience()}{education()}{awards()}{media()}{socials()}{footer()}</main>'
    if key == "sidebar":
        (DIST/"index.html").write_text(head(escape(SITE["name"]), indexable=True)+f'<body class="academic sidebar chosen-site" id="top"><a class="skip-link" href="#main">Skip to content</a>{main}</body></html>',encoding="utf-8")
    (DIST/f'{key}.html').write_text(head(f'Joseph Imperial | {name}')+f'<body class="academic {key}" id="top"><a class="skip-link" href="#main">Skip to content</a>{preview_bar(key)}{main}</body></html>',encoding='utf-8')

descriptions={
    'classic':'A charcoal masthead, blue geometric linework, and an ivory reading surface. Biography and research lead into the publications.',
    'sidebar':'A charcoal profile column beside a spacious research index. Blue margin details organize the academic content.',
    'publications':'An ivory masthead with serif typography and an offset portrait. Publications appear first, with the latest paper highlighted.'
}
cards=''.join(f'''<article class="layout-option"><a class="screenshot-link" href="{key}.html"><img src="assets/{key}-preview.jpg" alt="{name} layout preview" width="1264" height="712"></a><h2><a href="{key}.html">{i}. {name}</a></h2><p>{descriptions[key]}</p><a class="open-layout" href="{key}.html">Open layout <span aria-hidden="true">→</span></a></article>''' for i,(key,name) in enumerate(LAYOUTS,1))
gallery=head('Joseph Imperial | Academic website options')+f'''<body class="comparison"><main class="comparison-page"><header class="comparison-heading"><div><p>Joseph Imperial</p><h1>Academic website options</h1><p>Charcoal, ivory, and blue. Three distinct layouts for your research and academic profile.</p></div><div class="palette" aria-label="Color palette: charcoal, ivory, blue"><i></i><i></i><i></i></div></header><div class="layout-options">{cards}</div><p class="comparison-note">Open each layout to see the full page. The navigation at the top lets you switch between options.</p></main></body></html>'''
(DIST/'design-options.html').write_text(gallery,encoding='utf-8')

# Retain previously shared URLs without retaining any rejected presentation.
for old,new in [('editorial','classic'),('precision','sidebar'),('studio','publications')]:
    (DIST/f'{old}.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0;url={new}.html"><title>Joseph Imperial</title></head><body><a href="{new}.html">Joseph Imperial — academic website preview</a></body></html>',encoding='utf-8')
print('Built the Research index homepage and retained design previews.')
