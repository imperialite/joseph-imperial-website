"""Generate factual, academic website layouts. Run with Python 3.11+."""
from pathlib import Path
from html import escape
import math
import json

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
PAPERS = json.loads((ROOT / "publications.json").read_text(encoding="utf-8"))
SCHOLAR = "https://scholar.google.com/citations?user=irs_5ekAAAAJ&hl=en"
CV = "https://drive.google.com/drive/folders/1FvlEPuA5V5lDVFEz8fzwvr9fjEW6TRVS?usp=sharing"
LAYOUTS = [("classic", "Academic folio"), ("sidebar", "Research index"), ("publications", "Journal layout")]

PAPERS[4]["authors"] = "Joseph Marvin Imperial, Abdullah Barayan, Regina Stodden, Rodrigo Wilkens, Ricardo Munoz Sanchez, Lingyun Gao, Melissa Torgbi, Dawn Knight, Gail Forey, Reka R. Jablonkai, Ekaterina Kochmar, Robert Reynolds, Eugenio Ribeiro, Horacio Saggion, Elena Volodina, Sowmya Vajjala, Thomas Francois, Fernando Alva-Manchego, Harish Tayyar Madabushi"
PAPERS[6]["authors"] = "Francisco Eiras, Aleksandar Petrov, Bertie Vidgen, Christian Schroeder de Witt, Fabio Pizzati, Katherine Elkins, Supratik Mukhopadhyay, Adel Bibi, Botos Csaba, Fabro Steibel, Fazl Barez, Genevieve Smith, Gianluca Guadagni, Jon Chun, Jordi Cabot, Joseph Marvin Imperial, Juan A. Nolazco-Flores, Lori Landay, Matthew Jackson, Paul Röttger, Philip H.S. Torr, Trevor Darrell, Yong Suk Lee, Jakob Foerster"
(ROOT / "publications.json").write_text(json.dumps(PAPERS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def link(url, label, cls=""):
    return f'<a class="{cls}" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label}</a>'

def preview_bar(active):
    items = ''.join(f'<a href="{key}.html" {"aria-current=page" if key == active else ""}>{i}. {name}</a>' for i,(key,name) in enumerate(LAYOUTS,1))
    return f'<div class="preview-bar"><a href="index.html" class="compare-link">Compare layouts</a><nav aria-label="Website layout options">{items}</nav></div>'

def head(title):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="Joseph Imperial. Technical AI Governance Fellow at Pivotal Research and PhD Candidate at the University of Bath. Research, publications, and academic background."><title>{title}</title><link rel="icon" type="image/svg+xml" href="assets/favicon.svg"><link rel="stylesheet" href="assets/fonts.css"><link rel="stylesheet" href="styles.css"></head>'''

def profile_links():
    items = [link(SCHOLAR,"Google Scholar"),link("https://github.com/imperialite","Github"),link("https://aclanthology.org/people/joseph-marvin-imperial/","ACL Anthology"),link(CV,"CV")]
    return '<div class="profile-links">' + ''.join(items) + '</div>'

def identity():
    return f'''<header class="identity"><div class="identity-text"><p class="profile-label">Research &amp; Academic Profile</p><h1>Joseph Imperial</h1><p class="research-summary">I research the legal alignment of AI agents and the compliance of language models with policies, regulations, and expert-defined standards.</p><div class="appointments"><div><p class="appointment">Technical AI Governance Fellow</p><p class="institution">{link('https://www.pivotal-research.org/','Pivotal Research')}, United Kingdom</p></div><div><p class="appointment second-role">PhD Candidate, UKRI CDT in ART-AI</p><p class="institution">{link('https://www.bath.ac.uk/','University of Bath')}, United Kingdom</p></div></div><div class="profile-contact"><a class="email" href="mailto:jmri20@bath.ac.uk">jmri20@bath.ac.uk</a>{profile_links()}</div></div><figure class="portrait-frame"><img class="portrait" src="assets/joseph-imperial.jpg" alt="Joseph Imperial" width="1015" height="1131" fetchpriority="high"><span class="portrait-corner" aria-hidden="true"></span></figure></header>'''

def top_nav():
    cv_link=link(CV,'CV <span aria-hidden="true">↗</span>')
    return f'<nav class="top-nav wrap" aria-label="Main navigation"><a class="name-link" href="#top">Joseph Imperial</a><div><a href="#about">About Me</a><a href="#news">News</a><a href="#selected-publications">Publications</a>{cv_link}</div></nav>'

def section_nav():
    return f'<nav class="section-nav" aria-label="Sections"><a href="#about">About Me</a><a href="#news">News</a><a href="#selected-publications">Publications</a><a href="#background">Background</a>{link(CV,"CV")}</nav>'

def about():
    return f'''<section class="about" id="about"><h2>About Me</h2><p>I am a Technical AI Governance Fellow at Pivotal Research and a PhD Candidate in the UKRI Centre for Doctoral Training in Accountable, Responsible and Transparent AI at the University of Bath. My research focuses on the legal alignment of AI agents and the compliance of language models with policies, regulations, and expert-defined standards.</p><p>At Pivotal Research, I work with {link('https://www.noamkolt.com/','Noam Kolt')}. I also collaborate with {link('https://law-ai.org/team/benjamin-brady/','Ben Brady')} and {link('https://cullenokeefe.com/','Cullen O’Keefe')} at the Institute for Law &amp; AI on benchmarks for law-following AI. My doctoral research is supervised by {link('https://www.harishtayyarmadabushi.com/','Harish Tayyar Madabushi')} and {link('https://researchportal.bath.ac.uk/en/persons/gail-forey-2','Gail Forey')}.</p></section>'''

def publications():
    groups=[]
    for year in dict.fromkeys(p['year'] for p in PAPERS):
        rows=[]
        for paper in (p for p in PAPERS if p['year']==year):
            title=link(paper['url'], escape(paper['title']), 'paper-title') if paper['url'] else '<span class="paper-title">'+escape(paper['title'])+'</span>'
            authors=escape(paper['authors']).replace('Joseph Marvin Imperial','<strong>Joseph Marvin Imperial</strong>')
            if len(paper['authors'])>300:
                short='Joseph Marvin Imperial et al.' if paper['authors'].startswith('Joseph') else 'Francisco Eiras et al., including Joseph Marvin Imperial'
                authors=f'<details class="authors-details"><summary>{escape(short)} <span>Full author list</span></summary><p>{authors}</p></details>'
            else:
                authors=f'<p class="authors">{authors}</p>'
            venue=paper['venue'].replace(' · ',' — ')
            if paper['url']:
                action=link(paper['url'],'Project Page' if 'project' in paper['link_label'].lower() else 'Paper','paper-link')
            else:
                action='<span class="preprint-note">Preprint forthcoming</span>'
            rows.append(f'<article class="paper" data-topic="{paper["topic"]}" data-year="{year}"><h4>{title}</h4>{authors}<div class="paper-footer"><span class="venue">{venue}</span>{action}</div></article>')
        groups.append(f'<div class="year-group"><h3>{year}</h3><div>{"".join(rows)}</div></div>')
    return f'''<section class="publications" id="selected-publications"><div class="heading-row"><h2>Selected Publications</h2>{link(SCHOLAR,'Full list on Google Scholar','full-list')}</div><div class="publication-list">{''.join(groups)}</div></section>'''

def news():
    return f'''<section class="news" id="news"><h2>News</h2><ul><li><strong>NeurIPS 2026.</strong> ScrapeBench, GlobalPIQA, and Jarvis-Bench have been accepted. Preprints forthcoming.</li><li><strong>EMNLP 2026.</strong> {link('https://arxiv.org/abs/2606.05421','ComplexityMT')} and {link('https://arxiv.org/abs/2503.04736','Rethinking Standard Compliance in the LLM Era')} have been accepted.</li><li><strong>Nature.</strong> Our collaborative benchmark, {link('https://www.nature.com/articles/s41586-025-09962-4','Humanity’s Last Exam')}, is now published.</li><li><strong>Invited panel.</strong> {link('https://law-ai.org/event/2026-workshop-on-law-following-ai/','Workshop on Law-Following AI')}, hosted by the Institute for Law &amp; AI at Jesus College, Cambridge.</li></ul></section>'''

def background():
    return '''<section id="background" class="background"><h2>Education and Appointments</h2><dl class="timeline"><div><dt>2026–present</dt><dd><strong>Technical AI Governance Fellow</strong><span>Pivotal Research, London Initiative for Safe AI</span></dd></div><div><dt>2022–2026<br><small>(expected)</small></dt><dd><strong>PhD in Accountable, Responsible and Transparent AI</strong><span>University of Bath, United Kingdom</span></dd></div><div><dt>2018–present<br><small>(on study leave)</small></dt><dd><strong>Senior NLP Researcher</strong><span>National University, Philippines</span><p>Managed the Human Language Technology Lab and collaborated on NLP applications in education and food nutrition.</p></dd></div><div><dt>2018–2021</dt><dd><strong>M.S. in Computer Science</strong><span>De La Salle University, Philippines</span></dd></div><div><dt>2017–2018</dt><dd><strong>Research Fellow</strong><span>National University and Philippine-California Advanced Research Institutes</span><p>Text and speech analytics for disaster risk management, in collaboration with the University of California, Berkeley.</p></dd></div></dl></section><section class="awards"><h2>Awards &amp; Recognition</h2><ul><li>Outstanding Reviewer Award, ICML (2026, 2024) and ACL (2023)</li><li>Pivotal Research Fellowship (2025)</li><li>Doctoral Recognition Award, University of Bath (2024)</li><li>Researcher of the Year, National University Philippines (2023)</li><li>UKRI CDT Doctoral Fellowship (2022–2026)</li><li>Google AI and Tensorflow Grant (2021)</li></ul></section>'''

def media():
    return f'''<section class="media"><h2>Media Presence</h2><ul><li><span>AIHub</span>{link('https://aihub.org/2025/04/02/interview-with-joseph-marvin-imperial-aligning-generative-ai-with-technical-standards/','Aligning generative AI with technical standards')}</li><li><span>New Scientist</span>{link('https://www.newscientist.com/article/2473622-leading-ai-models-fail-new-test-of-artificial-general-intelligence/','Evaluating artificial general intelligence')}</li><li><span>Newsweek</span>{link('https://www.newsweek.com/openai-warns-us-government-agencies-of-rogue-activity-12492213','AI agents and safety')}</li></ul></section>'''

def footer():
    return f'''<footer><span>Joseph Imperial</span><a href="mailto:jmri20@bath.ac.uk">jmri20@bath.ac.uk</a><div>{link('https://www.linkedin.com/in/josephimperial/','LinkedIn')} · {link('https://x.com/josephimperial_','X')} · {link('https://www.researchgate.net/profile/Joseph_Marvin_Imperial','ResearchGate')}</div></footer>'''

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
        main=f'<div class="index-layout wrap"><aside class="profile-column">{identity()}{section_nav()}</aside><main id="main" class="content-column">{about()}{news()}{publications()}{background()}{media()}{footer()}</main></div>'
    elif key=='publications':
        main=f'<div class="journal-masthead">{top_nav()}<div class="wrap">{identity()}</div></div><main id="main" class="content-column wrap">{publications()}{about()}{news()}{background()}{media()}{footer()}</main>'
    else:
        main=f'<div class="folio-masthead">{top_nav()}<div class="wrap">{identity()}</div></div><main id="main" class="content-column wrap">{about()}{news()}{publications()}{background()}{media()}{footer()}</main>'
    (DIST/f'{key}.html').write_text(head(f'Joseph Imperial | {name}')+f'<body class="academic {key}" id="top"><a class="skip-link" href="#main">Skip to content</a>{preview_bar(key)}{main}</body></html>',encoding='utf-8')

descriptions={
    'classic':'A charcoal masthead, blue geometric linework, and an ivory reading surface. Biography and research lead into the publications.',
    'sidebar':'A charcoal profile column beside a spacious research index. Blue margin details organize the academic content.',
    'publications':'An ivory masthead with serif typography and an offset portrait. Publications appear first, with the latest paper highlighted.'
}
cards=''.join(f'''<article class="layout-option"><a class="screenshot-link" href="{key}.html"><img src="assets/{key}-preview.jpg" alt="{name} layout preview" width="1264" height="712"></a><h2><a href="{key}.html">{i}. {name}</a></h2><p>{descriptions[key]}</p><a class="open-layout" href="{key}.html">Open layout <span aria-hidden="true">→</span></a></article>''' for i,(key,name) in enumerate(LAYOUTS,1))
gallery=head('Joseph Imperial | Academic website options')+f'''<body class="comparison"><main class="comparison-page"><header class="comparison-heading"><div><p>Joseph Imperial</p><h1>Academic website options</h1><p>Charcoal, ivory, and blue. Three distinct layouts for your research and academic profile.</p></div><div class="palette" aria-label="Color palette: charcoal, ivory, blue"><i></i><i></i><i></i></div></header><div class="layout-options">{cards}</div><p class="comparison-note">Open each layout to see the full page. The navigation at the top lets you switch between options.</p></main></body></html>'''
(DIST/'index.html').write_text(gallery,encoding='utf-8')

# Retain previously shared URLs without retaining any rejected presentation.
for old,new in [('editorial','classic'),('precision','sidebar'),('studio','publications')]:
    (DIST/f'{old}.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0;url={new}.html"><title>Joseph Imperial</title></head><body><a href="{new}.html">Joseph Imperial — academic website preview</a></body></html>',encoding='utf-8')
print('Built three academic layouts and the comparison page.')
