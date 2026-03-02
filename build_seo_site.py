#!/usr/bin/env python3
"""
N3X1S Intelligence SEO Site Generator
=====================================
Transforms markdown articles into a fully SEO-optimized static site.
Target: 95+ Lighthouse score across all categories.
"""

import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import html

# Configuration
SITE_URL = "https://maxkle1nz.github.io/n3x1s-blog"
SITE_NAME = "N3X1S Intelligence"
SITE_DESCRIPTION = "Expert Python web scraping tutorials, automation guides, and data extraction techniques. Master web scraping with production-ready code examples."
BRAND_COLOR = "#00ff88"
BRAND_COLOR_DARK = "#0a0a0a"
AUTHOR_NAME = "N3X1S Intelligence"
AUTHOR_BIO = "Data extraction specialists with 8+ years of experience building production-grade scrapers, ETL pipelines, and automation systems. We've processed billions of data points for Fortune 500 companies."
FIVERR_URL = "https://www.fiverr.com/s/LdR6YN4"
GITHUB_URL = "https://github.com/maxkle1nz"
TWITTER_HANDLE = "@n3x1s_intel"

# Directories
ARTICLES_DIR = Path.home() / "clawd/money-machine/articles-ready"
OUTPUT_DIR = Path("/tmp/n3x1s-blog")

# Category definitions with keywords
CATEGORIES = {
    "web-scraping": {
        "name": "Web Scraping",
        "description": "Learn web scraping techniques with Python. From BeautifulSoup basics to Playwright for JavaScript-heavy sites.",
        "keywords": ["scrape", "scraping", "beautifulsoup", "playwright", "selenium", "yelp", "indeed", "linkedin", "glassdoor", "blocked"]
    },
    "data-engineering": {
        "name": "Data Engineering", 
        "description": "Build robust data pipelines, ETL systems, and storage solutions. CSV, JSON, databases, and data enrichment.",
        "keywords": ["etl", "pipeline", "database", "csv", "json", "mysql", "data enrichment", "store", "storage"]
    },
    "automation": {
        "name": "Python Automation",
        "description": "Automate repetitive tasks with Python. Scheduling, deployment, and production-ready scripts.",
        "keywords": ["automation", "schedule", "cron", "deploy", "vps", "linux", "scripts"]
    },
    "apis": {
        "name": "APIs & Integration",
        "description": "Work with APIs, reverse engineering, and choosing between scraping vs API approaches.",
        "keywords": ["api", "fastapi", "flask", "reverse engineer", "rest"]
    },
    "tutorials": {
        "name": "Step-by-Step Tutorials",
        "description": "Comprehensive guides for building real-world projects like price trackers and job scrapers.",
        "keywords": ["tracker", "price", "real estate", "pdf", "extract"]
    }
}

# Related articles mapping (will be auto-generated based on categories)
def calculate_reading_time(text: str) -> int:
    """Calculate reading time based on word count (200 wpm average)"""
    words = len(text.split())
    return max(1, round(words / 200))

def parse_markdown(content: str) -> Dict:
    """Parse markdown content and extract metadata"""
    lines = content.split('\n')
    title = ""
    body_start = 0
    
    # Find title (first H1)
    for i, line in enumerate(lines):
        if line.startswith('# '):
            title = line[2:].strip()
            body_start = i + 1
            break
    
    body = '\n'.join(lines[body_start:])
    
    # Extract all headings for TOC
    headings = []
    for line in lines:
        if line.startswith('## '):
            heading = line[3:].strip()
            slug = re.sub(r'[^\w\s-]', '', heading.lower()).replace(' ', '-')
            headings.append({'level': 2, 'text': heading, 'slug': slug})
        elif line.startswith('### '):
            heading = line[4:].strip()
            slug = re.sub(r'[^\w\s-]', '', heading.lower()).replace(' ', '-')
            headings.append({'level': 3, 'text': heading, 'slug': slug})
    
    # Extract code blocks for FAQ
    code_blocks = re.findall(r'```(\w+)?\n(.*?)```', body, re.DOTALL)
    
    # Create meta description from first paragraph
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and not p.startswith('#') and not p.startswith('```') and not p.startswith('-') and not p.startswith('>')]
    first_para = paragraphs[0] if paragraphs else ""
    # Clean markdown formatting
    first_para = re.sub(r'\*\*(.*?)\*\*', r'\1', first_para)
    first_para = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', first_para)
    meta_description = first_para[:157] + "..." if len(first_para) > 160 else first_para
    
    return {
        'title': title,
        'body': body,
        'headings': headings,
        'meta_description': meta_description,
        'word_count': len(body.split()),
        'reading_time': calculate_reading_time(body),
        'code_blocks': code_blocks
    }

def markdown_to_html(md: str) -> str:
    """Convert markdown to HTML with proper formatting"""
    html_content = md
    
    # Code blocks (must be first)
    def replace_code_block(match):
        lang = match.group(1) or 'text'
        code = html.escape(match.group(2).strip())
        return f'<pre><code class="language-{lang}">{code}</code></pre>'
    
    html_content = re.sub(r'```(\w+)?\n(.*?)```', replace_code_block, html_content, flags=re.DOTALL)
    
    # Inline code
    html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)
    
    # Headings with IDs for anchor links
    def heading_with_id(match):
        level = len(match.group(1))
        text = match.group(2).strip()
        slug = re.sub(r'[^\w\s-]', '', text.lower()).replace(' ', '-')
        return f'<h{level} id="{slug}">{text}</h{level}>'
    
    html_content = re.sub(r'^(#{2,6})\s+(.+)$', heading_with_id, html_content, flags=re.MULTILINE)
    
    # Bold
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    
    # Italic
    html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
    
    # Links with rel attributes for external
    def smart_link(match):
        text = match.group(1)
        url = match.group(2)
        if 'fiverr.com' in url or 'scrapingbee' in url or 'brightdata' in url or 'scraperapi' in url:
            return f'<a href="{url}" target="_blank" rel="nofollow sponsored noopener">{text}</a>'
        elif url.startswith('http') and 'maxkle1nz.github.io' not in url:
            return f'<a href="{url}" target="_blank" rel="noopener">{text}</a>'
        else:
            return f'<a href="{url}">{text}</a>'
    
    html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', smart_link, html_content)
    
    # Blockquotes (handle emoji prefixes)
    html_content = re.sub(r'^>\s*(.+)$', r'<blockquote>\1</blockquote>', html_content, flags=re.MULTILINE)
    
    # Horizontal rules
    html_content = re.sub(r'^---+$', '<hr>', html_content, flags=re.MULTILINE)
    
    # Lists
    lines = html_content.split('\n')
    result = []
    in_list = False
    list_type = None
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                result.append('<ul>')
                in_list = True
                list_type = 'ul'
            result.append(f'<li>{stripped[2:]}</li>')
        elif re.match(r'^\d+\.\s', stripped):
            if not in_list:
                result.append('<ol>')
                in_list = True
                list_type = 'ol'
            list_text = re.sub(r"^\d+\.\s", "", stripped)
            result.append(f'<li>{list_text}</li>')
        else:
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
                list_type = None
            result.append(line)
    
    if in_list:
        result.append(f'</{list_type}>')
    
    html_content = '\n'.join(result)
    
    # Paragraphs (wrap remaining text blocks)
    paragraphs = html_content.split('\n\n')
    processed = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<') or p.startswith('#'):
            processed.append(p)
        else:
            # Don't wrap if it's already wrapped or is a list/heading
            if not any(p.startswith(tag) for tag in ['<h', '<ul', '<ol', '<pre', '<blockquote', '<hr', '<p']):
                processed.append(f'<p>{p}</p>')
            else:
                processed.append(p)
    
    return '\n'.join(processed)

def categorize_article(title: str, content: str) -> str:
    """Determine the primary category for an article"""
    text = (title + ' ' + content).lower()
    scores = {}
    
    for cat_id, cat_info in CATEGORIES.items():
        score = sum(1 for kw in cat_info['keywords'] if kw in text)
        scores[cat_id] = score
    
    return max(scores, key=scores.get) if scores else 'tutorials'

def generate_faq_schema(title: str, headings: List[Dict]) -> List[Dict]:
    """Generate FAQ items from headings"""
    faqs = []
    for h in headings[:5]:  # Limit to 5 FAQs
        if h['level'] == 2:
            question = f"What is {h['text'].lower()}?" if not h['text'].endswith('?') else h['text']
            faqs.append({
                "question": question,
                "answer": f"This section covers {h['text'].lower()} in detail with code examples and best practices."
            })
    return faqs

def generate_article_html(article: Dict, all_articles: List[Dict]) -> str:
    """Generate full HTML for an article with all SEO elements"""
    
    # Find related articles (same category, different article)
    related = [a for a in all_articles if a['category'] == article['category'] and a['slug'] != article['slug']][:3]
    if len(related) < 3:
        # Fill with other articles
        others = [a for a in all_articles if a['slug'] != article['slug'] and a not in related]
        related.extend(others[:3-len(related)])
    
    # Generate TOC
    toc_html = '<nav class="toc" aria-label="Table of Contents"><h2>📑 Table of Contents</h2><ul>'
    for h in article['headings']:
        indent = '  ' * (h['level'] - 2)
        toc_html += f'{indent}<li><a href="#{h["slug"]}">{h["text"]}</a></li>'
    toc_html += '</ul></nav>'
    
    # Generate related articles section
    related_html = '<section class="related-articles"><h2>📚 Related Articles</h2><div class="related-grid">'
    for r in related:
        related_html += f'''
        <article class="related-card">
            <a href="{r['slug']}.html">
                <h3>{r['title']}</h3>
                <p>{r['meta_description'][:100]}...</p>
                <span class="read-time">{r['reading_time']} min read</span>
            </a>
        </article>'''
    related_html += '</div></section>'
    
    # Generate FAQ section
    faqs = generate_faq_schema(article['title'], article['headings'])
    faq_html = '<section class="faq-section" itemscope itemtype="https://schema.org/FAQPage"><h2>❓ Frequently Asked Questions</h2>'
    for faq in faqs:
        faq_html += f'''
        <div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
            <h3 itemprop="name">{faq['question']}</h3>
            <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">{faq['answer']}</p>
            </div>
        </div>'''
    faq_html += '</section>'
    
    # Breadcrumb schema
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": CATEGORIES[article['category']]['name'], "item": f"{SITE_URL}/category-{article['category']}.html"},
            {"@type": "ListItem", "position": 3, "name": article['title']}
        ]
    }
    
    # Article schema
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article['title'],
        "description": article['meta_description'],
        "author": {
            "@type": "Organization",
            "name": AUTHOR_NAME,
            "url": SITE_URL
        },
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE_URL}/favicon.svg"
            }
        },
        "datePublished": "2026-03-02",
        "dateModified": datetime.now().strftime("%Y-%m-%d"),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"{SITE_URL}/{article['slug']}.html"
        },
        "wordCount": article['word_count'],
        "articleSection": CATEGORIES[article['category']]['name']
    }
    
    # FAQ schema
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq['question'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq['answer']
                }
            } for faq in faqs
        ]
    }
    
    # Generate breadcrumb HTML
    breadcrumb_html = f'''
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <ol>
            <li><a href="index.html">Home</a></li>
            <li><a href="category-{article['category']}.html">{CATEGORIES[article['category']]['name']}</a></li>
            <li aria-current="page">{article['title'][:40]}...</li>
        </ol>
    </nav>'''
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="index, follow">
    <meta name="googlebot" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    
    <!-- Primary Meta Tags -->
    <title>{article['title']} | {SITE_NAME}</title>
    <meta name="title" content="{article['title']} | {SITE_NAME}">
    <meta name="description" content="{article['meta_description']}">
    <meta name="author" content="{AUTHOR_NAME}">
    <meta name="keywords" content="web scraping, python, {article['category']}, data extraction, automation, tutorial">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="{SITE_URL}/{article['slug']}.html">
    
    <!-- Hreflang -->
    <link rel="alternate" hreflang="en" href="{SITE_URL}/{article['slug']}.html">
    <link rel="alternate" hreflang="x-default" href="{SITE_URL}/{article['slug']}.html">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="{SITE_URL}/{article['slug']}.html">
    <meta property="og:title" content="{article['title']}">
    <meta property="og:description" content="{article['meta_description']}">
    <meta property="og:image" content="{SITE_URL}/og-image.png">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="article:published_time" content="2026-03-02T12:00:00Z">
    <meta property="article:modified_time" content="{datetime.now().isoformat()}Z">
    <meta property="article:author" content="{AUTHOR_NAME}">
    <meta property="article:section" content="{CATEGORIES[article['category']]['name']}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{SITE_URL}/{article['slug']}.html">
    <meta name="twitter:title" content="{article['title']}">
    <meta name="twitter:description" content="{article['meta_description']}">
    <meta name="twitter:image" content="{SITE_URL}/og-image.png">
    <meta name="twitter:site" content="{TWITTER_HANDLE}">
    <meta name="twitter:creator" content="{TWITTER_HANDLE}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="apple-touch-icon.png">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="{BRAND_COLOR}">
    
    <!-- Preconnect for performance -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="dns-prefetch" href="https://www.googletagmanager.com">
    
    <!-- Structured Data -->
    <script type="application/ld+json">{json.dumps(article_schema)}</script>
    <script type="application/ld+json">{json.dumps(breadcrumb_schema)}</script>
    <script type="application/ld+json">{json.dumps(faq_schema)}</script>
    
    <!-- Critical CSS (inline for performance) -->
    <style>
        :root {{
            --brand: {BRAND_COLOR};
            --bg: #0a0a0a;
            --bg-secondary: #111;
            --text: #e0e0e0;
            --text-muted: #888;
            --border: #222;
            --code-bg: #1a1a2e;
        }}
        
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        html {{ scroll-behavior: smooth; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
            font-size: 18px;
        }}
        
        /* Header */
        header {{
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        
        .logo {{
            color: var(--brand);
            font-weight: 700;
            font-size: 1.5rem;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        nav ul {{
            display: flex;
            list-style: none;
            gap: 1.5rem;
            flex-wrap: wrap;
        }}
        
        nav a {{
            color: var(--text);
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        nav a:hover {{ color: var(--brand); }}
        
        /* Breadcrumb */
        .breadcrumb {{
            max-width: 900px;
            margin: 1rem auto;
            padding: 0 1rem;
        }}
        
        .breadcrumb ol {{
            display: flex;
            list-style: none;
            gap: 0.5rem;
            font-size: 0.9rem;
            color: var(--text-muted);
            flex-wrap: wrap;
        }}
        
        .breadcrumb li::after {{ content: '/'; margin-left: 0.5rem; }}
        .breadcrumb li:last-child::after {{ content: ''; }}
        .breadcrumb a {{ color: var(--brand); text-decoration: none; }}
        
        /* Main content */
        main {{
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem 1rem 4rem;
        }}
        
        article {{ margin-bottom: 3rem; }}
        
        /* Typography */
        h1 {{
            font-size: clamp(1.8rem, 5vw, 2.5rem);
            color: var(--brand);
            margin-bottom: 1rem;
            line-height: 1.2;
        }}
        
        h2 {{
            font-size: 1.5rem;
            color: var(--brand);
            margin: 2.5rem 0 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}
        
        h3 {{
            font-size: 1.25rem;
            color: #fff;
            margin: 1.5rem 0 0.75rem;
        }}
        
        p {{ margin-bottom: 1.25rem; }}
        
        a {{ color: var(--brand); }}
        
        /* Meta info */
        .meta {{
            display: flex;
            gap: 1.5rem;
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }}
        
        .meta span {{ display: flex; align-items: center; gap: 0.3rem; }}
        
        /* TOC */
        .toc {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 2rem 0;
        }}
        
        .toc h2 {{
            font-size: 1.1rem;
            margin: 0 0 1rem;
            padding: 0;
            border: none;
        }}
        
        .toc ul {{
            margin: 0;
            padding-left: 1.5rem;
        }}
        
        .toc li {{
            margin: 0.5rem 0;
        }}
        
        .toc a {{
            color: var(--text);
            text-decoration: none;
        }}
        
        .toc a:hover {{
            color: var(--brand);
        }}
        
        /* Code */
        pre {{
            background: var(--code-bg);
            border-radius: 8px;
            padding: 1.25rem;
            overflow-x: auto;
            margin: 1.5rem 0;
            border: 1px solid var(--border);
        }}
        
        code {{
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 0.9rem;
        }}
        
        :not(pre) > code {{
            background: var(--code-bg);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
        }}
        
        /* Blockquotes */
        blockquote {{
            border-left: 4px solid var(--brand);
            background: var(--bg-secondary);
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            border-radius: 0 8px 8px 0;
        }}
        
        /* Lists */
        ul, ol {{
            margin: 1rem 0 1.5rem 2rem;
        }}
        
        li {{
            margin: 0.5rem 0;
        }}
        
        /* Related Articles */
        .related-articles {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid var(--border);
        }}
        
        .related-articles h2 {{
            border: none;
            margin-top: 0;
            padding-top: 0;
        }}
        
        .related-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }}
        
        .related-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.25rem;
            transition: border-color 0.2s, transform 0.2s;
        }}
        
        .related-card:hover {{
            border-color: var(--brand);
            transform: translateY(-2px);
        }}
        
        .related-card a {{
            text-decoration: none;
        }}
        
        .related-card h3 {{
            color: var(--brand);
            font-size: 1rem;
            margin: 0 0 0.5rem;
        }}
        
        .related-card p {{
            color: var(--text-muted);
            font-size: 0.9rem;
            margin: 0;
        }}
        
        .read-time {{
            display: block;
            color: var(--text-muted);
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }}
        
        /* FAQ Section */
        .faq-section {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid var(--border);
        }}
        
        .faq-section h2 {{
            border: none;
            margin-top: 0;
            padding-top: 0;
        }}
        
        .faq-item {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.25rem;
            margin: 1rem 0;
        }}
        
        .faq-item h3 {{
            color: var(--brand);
            margin: 0 0 0.75rem;
            font-size: 1rem;
        }}
        
        .faq-item p {{
            margin: 0;
            color: var(--text-muted);
        }}
        
        /* Author Box */
        .author-box {{
            background: linear-gradient(135deg, var(--bg-secondary), #1a1a2e);
            border: 1px solid var(--brand);
            border-radius: 12px;
            padding: 2rem;
            margin: 3rem 0;
            display: flex;
            gap: 1.5rem;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .author-avatar {{
            width: 80px;
            height: 80px;
            background: var(--brand);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            flex-shrink: 0;
        }}
        
        .author-info h4 {{
            color: var(--brand);
            margin-bottom: 0.5rem;
        }}
        
        .author-info p {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin: 0;
        }}
        
        /* CTA Box */
        .cta-box {{
            background: linear-gradient(135deg, #1a1a2e, var(--bg-secondary));
            border: 2px solid var(--brand);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            margin: 2rem 0;
        }}
        
        .cta-box h3 {{
            color: var(--brand);
            margin-bottom: 1rem;
        }}
        
        .cta-box p {{
            color: var(--text-muted);
            margin-bottom: 1.5rem;
        }}
        
        .cta-button {{
            display: inline-block;
            background: var(--brand);
            color: #000;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3);
            color: #000;
        }}
        
        /* Footer */
        footer {{
            background: var(--bg-secondary);
            border-top: 1px solid var(--border);
            padding: 3rem 2rem;
            margin-top: 4rem;
        }}
        
        .footer-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
        }}
        
        .footer-section h4 {{
            color: var(--brand);
            margin-bottom: 1rem;
        }}
        
        .footer-section ul {{
            list-style: none;
            margin: 0;
            padding: 0;
        }}
        
        .footer-section li {{
            margin: 0.5rem 0;
        }}
        
        .footer-section a {{
            color: var(--text-muted);
            text-decoration: none;
        }}
        
        .footer-section a:hover {{
            color: var(--brand);
        }}
        
        .footer-bottom {{
            max-width: 1200px;
            margin: 2rem auto 0;
            padding-top: 2rem;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            body {{ font-size: 16px; }}
            header {{ padding: 1rem; }}
            main {{ padding: 1rem; }}
            .author-box {{ flex-direction: column; text-align: center; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <a href="index.html" class="logo">
                <span>🔮</span> {SITE_NAME}
            </a>
            <nav aria-label="Main Navigation">
                <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="category-web-scraping.html">Web Scraping</a></li>
                    <li><a href="category-data-engineering.html">Data Engineering</a></li>
                    <li><a href="category-automation.html">Automation</a></li>
                    <li><a href="about.html">About</a></li>
                    <li><a href="{FIVERR_URL}" target="_blank" rel="noopener">Hire Us</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    {breadcrumb_html}
    
    <main>
        <article itemscope itemtype="https://schema.org/Article">
            <header>
                <h1 itemprop="headline">{article['title']}</h1>
                <div class="meta">
                    <span>📅 <time datetime="2026-03-02" itemprop="datePublished">March 2, 2026</time></span>
                    <span>⏱️ {article['reading_time']} min read</span>
                    <span>📝 {article['word_count']:,} words</span>
                    <span>📁 <a href="category-{article['category']}.html">{CATEGORIES[article['category']]['name']}</a></span>
                </div>
            </header>
            
            {toc_html}
            
            <div class="content" itemprop="articleBody">
                {article['html_content']}
            </div>
            
            <div class="author-box">
                <div class="author-avatar">🔮</div>
                <div class="author-info">
                    <h4>Written by {AUTHOR_NAME}</h4>
                    <p itemprop="author" itemscope itemtype="https://schema.org/Organization">
                        <span itemprop="name">{AUTHOR_BIO}</span>
                    </p>
                </div>
            </div>
            
            <div class="cta-box">
                <h3>🚀 Need a Custom Scraper?</h3>
                <p>Don't have time to build it yourself? We'll create a production-ready scraper tailored to your exact needs.</p>
                <a href="{FIVERR_URL}" class="cta-button" target="_blank" rel="nofollow sponsored noopener">Get Your Custom Scraper →</a>
            </div>
            
            {related_html}
            
            {faq_html}
        </article>
    </main>
    
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>🔮 {SITE_NAME}</h4>
                <p style="color: var(--text-muted);">Expert web scraping tutorials, automation guides, and data extraction techniques.</p>
            </div>
            <div class="footer-section">
                <h4>Categories</h4>
                <ul>
                    <li><a href="category-web-scraping.html">Web Scraping</a></li>
                    <li><a href="category-data-engineering.html">Data Engineering</a></li>
                    <li><a href="category-automation.html">Automation</a></li>
                    <li><a href="category-apis.html">APIs</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4>Resources</h4>
                <ul>
                    <li><a href="about.html">About Us</a></li>
                    <li><a href="{FIVERR_URL}" target="_blank" rel="noopener">Hire Us</a></li>
                    <li><a href="{GITHUB_URL}" target="_blank" rel="noopener">GitHub</a></li>
                    <li><a href="sitemap.xml">Sitemap</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4>Popular Tutorials</h4>
                <ul>
                    {''.join(f'<li><a href="{a["slug"]}.html">{a["title"][:35]}...</a></li>' for a in all_articles[:4])}
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>© 2026 {SITE_NAME}. All rights reserved. Built with 🐍 Python.</p>
        </div>
    </footer>
</body>
</html>'''

def generate_index_html(articles: List[Dict]) -> str:
    """Generate homepage with all articles"""
    
    # Group by category
    by_category = {}
    for article in articles:
        cat = article['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(article)
    
    # Article cards
    articles_html = ''
    for cat_id, cat_articles in by_category.items():
        cat_info = CATEGORIES[cat_id]
        articles_html += f'''
        <section class="category-section">
            <h2><a href="category-{cat_id}.html">{cat_info['name']}</a></h2>
            <p class="category-desc">{cat_info['description']}</p>
            <div class="article-grid">'''
        
        for article in cat_articles:
            articles_html += f'''
                <article class="article-card">
                    <a href="{article['slug']}.html">
                        <h3>{article['title']}</h3>
                        <p>{article['meta_description'][:120]}...</p>
                        <div class="card-meta">
                            <span>⏱️ {article['reading_time']} min</span>
                            <span>📝 {article['word_count']:,} words</span>
                        </div>
                    </a>
                </article>'''
        articles_html += '</div></section>'
    
    # Organization schema
    org_schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": SITE_NAME,
        "url": SITE_URL,
        "logo": f"{SITE_URL}/favicon.svg",
        "description": SITE_DESCRIPTION,
        "sameAs": [GITHUB_URL, FIVERR_URL]
    }
    
    # WebSite schema
    website_schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": SITE_URL,
        "description": SITE_DESCRIPTION,
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME
        }
    }
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="index, follow">
    
    <title>{SITE_NAME} — Python Web Scraping Tutorials & Data Extraction Guides</title>
    <meta name="description" content="{SITE_DESCRIPTION}">
    <meta name="keywords" content="web scraping, python, beautifulsoup, playwright, selenium, data extraction, automation, ETL, tutorials">
    <meta name="author" content="{AUTHOR_NAME}">
    
    <link rel="canonical" href="{SITE_URL}/">
    <link rel="alternate" hreflang="en" href="{SITE_URL}/">
    <link rel="alternate" hreflang="x-default" href="{SITE_URL}/">
    
    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_URL}/">
    <meta property="og:title" content="{SITE_NAME} — Python Web Scraping Tutorials">
    <meta property="og:description" content="{SITE_DESCRIPTION}">
    <meta property="og:image" content="{SITE_URL}/og-image.png">
    <meta property="og:site_name" content="{SITE_NAME}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{SITE_URL}/">
    <meta name="twitter:title" content="{SITE_NAME} — Python Web Scraping Tutorials">
    <meta name="twitter:description" content="{SITE_DESCRIPTION}">
    <meta name="twitter:image" content="{SITE_URL}/og-image.png">
    <meta name="twitter:site" content="{TWITTER_HANDLE}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="apple-touch-icon.png">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="{BRAND_COLOR}">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    
    <script type="application/ld+json">{json.dumps(org_schema)}</script>
    <script type="application/ld+json">{json.dumps(website_schema)}</script>
    
    <style>
        :root {{
            --brand: {BRAND_COLOR};
            --bg: #0a0a0a;
            --bg-secondary: #111;
            --text: #e0e0e0;
            --text-muted: #888;
            --border: #222;
        }}
        
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}
        
        header {{
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        
        .logo {{
            color: var(--brand);
            font-weight: 700;
            font-size: 1.5rem;
            text-decoration: none;
        }}
        
        nav ul {{
            display: flex;
            list-style: none;
            gap: 1.5rem;
            flex-wrap: wrap;
        }}
        
        nav a {{
            color: var(--text);
            text-decoration: none;
        }}
        
        nav a:hover {{ color: var(--brand); }}
        
        .hero {{
            background: linear-gradient(135deg, var(--bg-secondary), #1a1a2e);
            padding: 4rem 2rem;
            text-align: center;
            border-bottom: 1px solid var(--border);
        }}
        
        .hero h1 {{
            font-size: clamp(2rem, 5vw, 3rem);
            color: var(--brand);
            margin-bottom: 1rem;
        }}
        
        .hero p {{
            max-width: 700px;
            margin: 0 auto 2rem;
            color: var(--text-muted);
            font-size: 1.1rem;
        }}
        
        .hero-cta {{
            display: inline-block;
            background: var(--brand);
            color: #000;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin: 0.5rem;
        }}
        
        .hero-cta:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3);
        }}
        
        .hero-cta.secondary {{
            background: transparent;
            border: 2px solid var(--brand);
            color: var(--brand);
        }}
        
        main {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }}
        
        .category-section {{
            margin-bottom: 3rem;
        }}
        
        .category-section h2 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .category-section h2 a {{
            color: var(--brand);
            text-decoration: none;
        }}
        
        .category-desc {{
            color: var(--text-muted);
            margin-bottom: 1.5rem;
        }}
        
        .article-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }}
        
        .article-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: border-color 0.2s, transform 0.2s;
        }}
        
        .article-card:hover {{
            border-color: var(--brand);
            transform: translateY(-4px);
        }}
        
        .article-card a {{
            text-decoration: none;
        }}
        
        .article-card h3 {{
            color: var(--brand);
            font-size: 1.1rem;
            margin-bottom: 0.75rem;
            line-height: 1.3;
        }}
        
        .article-card p {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }}
        
        .card-meta {{
            display: flex;
            gap: 1rem;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}
        
        footer {{
            background: var(--bg-secondary);
            border-top: 1px solid var(--border);
            padding: 3rem 2rem;
        }}
        
        .footer-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
        }}
        
        .footer-section h4 {{
            color: var(--brand);
            margin-bottom: 1rem;
        }}
        
        .footer-section ul {{
            list-style: none;
        }}
        
        .footer-section li {{
            margin: 0.5rem 0;
        }}
        
        .footer-section a {{
            color: var(--text-muted);
            text-decoration: none;
        }}
        
        .footer-section a:hover {{
            color: var(--brand);
        }}
        
        .footer-bottom {{
            max-width: 1200px;
            margin: 2rem auto 0;
            padding-top: 2rem;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
        }}
        
        @media (max-width: 768px) {{
            header {{ padding: 1rem; }}
            .hero {{ padding: 2rem 1rem; }}
            main {{ padding: 2rem 1rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <a href="index.html" class="logo">🔮 {SITE_NAME}</a>
            <nav>
                <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="category-web-scraping.html">Web Scraping</a></li>
                    <li><a href="category-data-engineering.html">Data Engineering</a></li>
                    <li><a href="category-automation.html">Automation</a></li>
                    <li><a href="about.html">About</a></li>
                    <li><a href="{FIVERR_URL}" target="_blank" rel="noopener">Hire Us</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <section class="hero">
        <h1>🔮 Master Web Scraping with Python</h1>
        <p>{SITE_DESCRIPTION}</p>
        <a href="#articles" class="hero-cta">Browse Tutorials</a>
        <a href="{FIVERR_URL}" class="hero-cta secondary" target="_blank" rel="noopener">Hire a Scraper Expert</a>
    </section>
    
    <main id="articles">
        {articles_html}
    </main>
    
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>🔮 {SITE_NAME}</h4>
                <p style="color: var(--text-muted);">{SITE_DESCRIPTION}</p>
            </div>
            <div class="footer-section">
                <h4>Categories</h4>
                <ul>
                    {''.join(f'<li><a href="category-{cat}.html">{info["name"]}</a></li>' for cat, info in CATEGORIES.items())}
                </ul>
            </div>
            <div class="footer-section">
                <h4>Resources</h4>
                <ul>
                    <li><a href="about.html">About Us</a></li>
                    <li><a href="{FIVERR_URL}" target="_blank">Hire Us</a></li>
                    <li><a href="{GITHUB_URL}" target="_blank">GitHub</a></li>
                    <li><a href="sitemap.xml">Sitemap</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>© 2026 {SITE_NAME}. Built with 🐍 Python.</p>
        </div>
    </footer>
</body>
</html>'''

def generate_category_html(category_id: str, articles: List[Dict]) -> str:
    """Generate category page"""
    cat_info = CATEGORIES[category_id]
    cat_articles = [a for a in articles if a['category'] == category_id]
    
    articles_html = '<div class="article-grid">'
    for article in cat_articles:
        articles_html += f'''
            <article class="article-card">
                <a href="{article['slug']}.html">
                    <h3>{article['title']}</h3>
                    <p>{article['meta_description'][:120]}...</p>
                    <div class="card-meta">
                        <span>⏱️ {article['reading_time']} min</span>
                        <span>📝 {article['word_count']:,} words</span>
                    </div>
                </a>
            </article>'''
    articles_html += '</div>'
    
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": cat_info['name']}
        ]
    }
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="index, follow">
    
    <title>{cat_info['name']} Tutorials | {SITE_NAME}</title>
    <meta name="description" content="{cat_info['description']}">
    
    <link rel="canonical" href="{SITE_URL}/category-{category_id}.html">
    
    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_URL}/category-{category_id}.html">
    <meta property="og:title" content="{cat_info['name']} Tutorials | {SITE_NAME}">
    <meta property="og:description" content="{cat_info['description']}">
    <meta property="og:image" content="{SITE_URL}/og-image.png">
    
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{cat_info['name']} Tutorials | {SITE_NAME}">
    <meta name="twitter:description" content="{cat_info['description']}">
    
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="apple-touch-icon.png">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="{BRAND_COLOR}">
    
    <script type="application/ld+json">{json.dumps(breadcrumb_schema)}</script>
    
    <style>
        :root {{ --brand: {BRAND_COLOR}; --bg: #0a0a0a; --bg-secondary: #111; --text: #e0e0e0; --text-muted: #888; --border: #222; }}
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}
        header {{ background: var(--bg-secondary); border-bottom: 1px solid var(--border); padding: 1rem 2rem; position: sticky; top: 0; z-index: 100; }}
        .header-content {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }}
        .logo {{ color: var(--brand); font-weight: 700; font-size: 1.5rem; text-decoration: none; }}
        nav ul {{ display: flex; list-style: none; gap: 1.5rem; flex-wrap: wrap; }}
        nav a {{ color: var(--text); text-decoration: none; }}
        nav a:hover {{ color: var(--brand); }}
        .breadcrumb {{ max-width: 1200px; margin: 1rem auto; padding: 0 2rem; }}
        .breadcrumb ol {{ display: flex; list-style: none; gap: 0.5rem; font-size: 0.9rem; color: var(--text-muted); }}
        .breadcrumb li::after {{ content: '/'; margin-left: 0.5rem; }}
        .breadcrumb li:last-child::after {{ content: ''; }}
        .breadcrumb a {{ color: var(--brand); text-decoration: none; }}
        main {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        h1 {{ font-size: 2rem; color: var(--brand); margin-bottom: 0.5rem; }}
        .category-desc {{ color: var(--text-muted); margin-bottom: 2rem; font-size: 1.1rem; }}
        .article-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }}
        .article-card {{ background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; transition: border-color 0.2s, transform 0.2s; }}
        .article-card:hover {{ border-color: var(--brand); transform: translateY(-4px); }}
        .article-card a {{ text-decoration: none; }}
        .article-card h3 {{ color: var(--brand); font-size: 1.1rem; margin-bottom: 0.75rem; }}
        .article-card p {{ color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem; }}
        .card-meta {{ display: flex; gap: 1rem; font-size: 0.85rem; color: var(--text-muted); }}
        footer {{ background: var(--bg-secondary); border-top: 1px solid var(--border); padding: 2rem; margin-top: 3rem; text-align: center; color: var(--text-muted); }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <a href="index.html" class="logo">🔮 {SITE_NAME}</a>
            <nav>
                <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="category-web-scraping.html">Web Scraping</a></li>
                    <li><a href="category-data-engineering.html">Data Engineering</a></li>
                    <li><a href="category-automation.html">Automation</a></li>
                    <li><a href="about.html">About</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <ol>
            <li><a href="index.html">Home</a></li>
            <li aria-current="page">{cat_info['name']}</li>
        </ol>
    </nav>
    
    <main>
        <h1>{cat_info['name']}</h1>
        <p class="category-desc">{cat_info['description']}</p>
        {articles_html}
    </main>
    
    <footer>
        <p>© 2026 {SITE_NAME}. Built with 🐍 Python.</p>
    </footer>
</body>
</html>'''

def generate_about_html() -> str:
    """Generate about page"""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <title>About {SITE_NAME} | Web Scraping Experts</title>
    <meta name="description" content="Learn about {SITE_NAME} - data extraction specialists helping businesses automate data collection with Python.">
    
    <link rel="canonical" href="{SITE_URL}/about.html">
    
    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_URL}/about.html">
    <meta property="og:title" content="About {SITE_NAME}">
    <meta property="og:description" content="Data extraction specialists helping businesses automate data collection.">
    <meta property="og:image" content="{SITE_URL}/og-image.png">
    
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="apple-touch-icon.png">
    <meta name="theme-color" content="{BRAND_COLOR}">
    
    <style>
        :root {{ --brand: {BRAND_COLOR}; --bg: #0a0a0a; --bg-secondary: #111; --text: #e0e0e0; --text-muted: #888; --border: #222; }}
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; }}
        header {{ background: var(--bg-secondary); border-bottom: 1px solid var(--border); padding: 1rem 2rem; }}
        .header-content {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }}
        .logo {{ color: var(--brand); font-weight: 700; font-size: 1.5rem; text-decoration: none; }}
        nav ul {{ display: flex; list-style: none; gap: 1.5rem; }}
        nav a {{ color: var(--text); text-decoration: none; }}
        nav a:hover {{ color: var(--brand); }}
        main {{ max-width: 800px; margin: 0 auto; padding: 3rem 2rem; }}
        h1 {{ font-size: 2.5rem; color: var(--brand); margin-bottom: 2rem; }}
        h2 {{ font-size: 1.5rem; color: var(--brand); margin: 2rem 0 1rem; }}
        p {{ margin-bottom: 1.25rem; }}
        .cta-box {{ background: linear-gradient(135deg, #1a1a2e, var(--bg-secondary)); border: 2px solid var(--brand); border-radius: 12px; padding: 2rem; text-align: center; margin: 3rem 0; }}
        .cta-box h3 {{ color: var(--brand); margin-bottom: 1rem; }}
        .cta-button {{ display: inline-block; background: var(--brand); color: #000; padding: 0.75rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; }}
        .skills {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }}
        .skill {{ background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; text-align: center; }}
        .skill-icon {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        footer {{ background: var(--bg-secondary); border-top: 1px solid var(--border); padding: 2rem; text-align: center; color: var(--text-muted); }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <a href="index.html" class="logo">🔮 {SITE_NAME}</a>
            <nav>
                <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="category-web-scraping.html">Web Scraping</a></li>
                    <li><a href="about.html">About</a></li>
                    <li><a href="{FIVERR_URL}" target="_blank">Hire Us</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <main>
        <h1>🔮 About {SITE_NAME}</h1>
        
        <p>{AUTHOR_BIO}</p>
        
        <p>We specialize in building custom web scrapers, ETL pipelines, and automation systems that help businesses collect, clean, and analyze data at scale.</p>
        
        <h2>🛠️ Our Expertise</h2>
        
        <div class="skills">
            <div class="skill">
                <div class="skill-icon">🕷️</div>
                <h4>Web Scraping</h4>
                <p>BeautifulSoup, Scrapy, Playwright, Selenium</p>
            </div>
            <div class="skill">
                <div class="skill-icon">🐍</div>
                <h4>Python Development</h4>
                <p>FastAPI, Flask, pandas, SQLAlchemy</p>
            </div>
            <div class="skill">
                <div class="skill-icon">🔄</div>
                <h4>ETL Pipelines</h4>
                <p>Data transformation, cleaning, and loading</p>
            </div>
            <div class="skill">
                <div class="skill-icon">☁️</div>
                <h4>Cloud Deployment</h4>
                <p>AWS, GCP, Linux VPS, Docker</p>
            </div>
        </div>
        
        <h2>🎯 What We Offer</h2>
        
        <p><strong>Custom Web Scrapers:</strong> We build production-ready scrapers tailored to your exact requirements, handling JavaScript-heavy sites, anti-bot measures, and complex data structures.</p>
        
        <p><strong>Data Pipeline Development:</strong> From raw data to actionable insights — we design and implement complete ETL systems with proper error handling, monitoring, and scheduling.</p>
        
        <p><strong>Automation Solutions:</strong> Automate repetitive tasks, set up monitoring systems, and build tools that save hours of manual work every week.</p>
        
        <div class="cta-box">
            <h3>🚀 Ready to Automate Your Data Collection?</h3>
            <p>Let's discuss your project and build something amazing together.</p>
            <a href="{FIVERR_URL}" class="cta-button" target="_blank" rel="noopener">Hire Us on Fiverr →</a>
        </div>
    </main>
    
    <footer>
        <p>© 2026 {SITE_NAME}. Built with 🐍 Python.</p>
    </footer>
</body>
</html>'''

def generate_404_html() -> str:
    """Generate 404 error page"""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found | {SITE_NAME}</title>
    <meta name="robots" content="noindex">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <style>
        :root {{ --brand: {BRAND_COLOR}; --bg: #0a0a0a; --text: #e0e0e0; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; padding: 2rem; }}
        .container {{ max-width: 500px; }}
        h1 {{ font-size: 8rem; color: var(--brand); line-height: 1; }}
        h2 {{ font-size: 1.5rem; margin: 1rem 0; }}
        p {{ color: #888; margin-bottom: 2rem; }}
        a {{ display: inline-block; background: var(--brand); color: #000; padding: 0.75rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; }}
        a:hover {{ transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>The page you're looking for doesn't exist or has been moved.</p>
        <a href="index.html">← Back to Home</a>
    </div>
</body>
</html>'''

def generate_sitemap(articles: List[Dict]) -> str:
    """Generate sitemap.xml"""
    urls = [
        f'''  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>''',
        f'''  <url>
    <loc>{SITE_URL}/about.html</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>'''
    ]
    
    for cat_id in CATEGORIES:
        urls.append(f'''  <url>
    <loc>{SITE_URL}/category-{cat_id}.html</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>''')
    
    for article in articles:
        urls.append(f'''  <url>
    <loc>{SITE_URL}/{article['slug']}.html</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>''')
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>'''

def generate_robots_txt() -> str:
    """Generate robots.txt"""
    return f'''# robots.txt for {SITE_NAME}
# {SITE_URL}

User-agent: *
Allow: /

# Sitemap
Sitemap: {SITE_URL}/sitemap.xml

# Crawl-delay (optional, be nice to servers)
Crawl-delay: 1
'''

def generate_manifest() -> str:
    """Generate manifest.json for PWA-lite"""
    return json.dumps({
        "name": SITE_NAME,
        "short_name": "N3X1S",
        "description": SITE_DESCRIPTION,
        "start_url": "/",
        "display": "standalone",
        "background_color": BRAND_COLOR_DARK,
        "theme_color": BRAND_COLOR,
        "icons": [
            {"src": "favicon.svg", "sizes": "any", "type": "image/svg+xml"},
            {"src": "apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}
        ]
    }, indent=2)

def generate_favicon_svg() -> str:
    """Generate SVG favicon"""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#0a0a0a"/>
  <text x="50" y="70" font-size="60" text-anchor="middle" fill="{BRAND_COLOR}">🔮</text>
</svg>'''

def main():
    """Main build function"""
    print("🔮 N3X1S Intelligence SEO Site Generator")
    print("=" * 50)
    
    # Read all markdown files
    articles = []
    for md_file in sorted(ARTICLES_DIR.glob("*.md")):
        print(f"📄 Processing: {md_file.name}")
        content = md_file.read_text(encoding='utf-8')
        parsed = parse_markdown(content)
        
        # Generate slug from filename
        slug = md_file.stem
        
        article = {
            'filename': md_file.name,
            'slug': slug,
            'title': parsed['title'],
            'body': parsed['body'],
            'headings': parsed['headings'],
            'meta_description': parsed['meta_description'],
            'word_count': parsed['word_count'],
            'reading_time': parsed['reading_time'],
            'category': categorize_article(parsed['title'], parsed['body']),
            'html_content': markdown_to_html(parsed['body'])
        }
        articles.append(article)
    
    print(f"\n✅ Processed {len(articles)} articles")
    
    # Generate all HTML files
    print("\n🔧 Generating HTML files...")
    
    # Article pages
    for article in articles:
        html = generate_article_html(article, articles)
        output_path = OUTPUT_DIR / f"{article['slug']}.html"
        output_path.write_text(html, encoding='utf-8')
        print(f"  ✓ {article['slug']}.html")
    
    # Index page
    (OUTPUT_DIR / "index.html").write_text(generate_index_html(articles), encoding='utf-8')
    print("  ✓ index.html")
    
    # Category pages
    for cat_id in CATEGORIES:
        (OUTPUT_DIR / f"category-{cat_id}.html").write_text(generate_category_html(cat_id, articles), encoding='utf-8')
        print(f"  ✓ category-{cat_id}.html")
    
    # About page
    (OUTPUT_DIR / "about.html").write_text(generate_about_html(), encoding='utf-8')
    print("  ✓ about.html")
    
    # 404 page
    (OUTPUT_DIR / "404.html").write_text(generate_404_html(), encoding='utf-8')
    print("  ✓ 404.html")
    
    # Sitemap
    (OUTPUT_DIR / "sitemap.xml").write_text(generate_sitemap(articles), encoding='utf-8')
    print("  ✓ sitemap.xml")
    
    # Robots.txt
    (OUTPUT_DIR / "robots.txt").write_text(generate_robots_txt(), encoding='utf-8')
    print("  ✓ robots.txt")
    
    # Manifest
    (OUTPUT_DIR / "manifest.json").write_text(generate_manifest(), encoding='utf-8')
    print("  ✓ manifest.json")
    
    # Favicon
    (OUTPUT_DIR / "favicon.svg").write_text(generate_favicon_svg(), encoding='utf-8')
    print("  ✓ favicon.svg")
    
    print("\n" + "=" * 50)
    print("🎉 Build complete!")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"📊 Total articles: {len(articles)}")
    print(f"📂 Categories: {len(CATEGORIES)}")
    
    # Print category distribution
    print("\n📈 Category distribution:")
    for cat_id, cat_info in CATEGORIES.items():
        count = len([a for a in articles if a['category'] == cat_id])
        print(f"  • {cat_info['name']}: {count} articles")

if __name__ == "__main__":
    main()
