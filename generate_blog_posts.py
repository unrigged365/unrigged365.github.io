#!/usr/bin/env python3
"""
Blog Post Generator Script

This script automatically generates HTML blog posts from markdown articles.
It only creates new blog posts for articles that don't already have them.

Usage: python generate_blog_posts.py
"""

import os
import re
from pathlib import Path

def extract_title_from_markdown(content):
    """Extract the first # title from markdown content"""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "Untitled Article"

def extract_subtitle_from_markdown(content):
    """Extract the italic subtitle (usually the second line)"""
    lines = content.split('\n')
    for line in lines[1:5]:  # Check first few lines after title
        line = line.strip()
        if line.startswith('*') and line.endswith('*') and len(line) > 2:
            return line[1:-1]  # Remove the asterisks
    return ""

def markdown_to_html(markdown_content):
    """Convert markdown to HTML with custom formatting"""

    # Remove the title (first line starting with #)
    lines = markdown_content.split('\n')
    content_lines = []
    skip_first_title = True

    for line in lines:
        if skip_first_title and line.startswith('# '):
            skip_first_title = False
            continue
        content_lines.append(line)

    # Join back
    content = '\n'.join(content_lines).strip()

    # Convert headers (## -> <h2>)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2> <br>', content, flags=re.MULTILINE)

    # Convert bold text (**text** -> <strong>text</strong>)
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)

    # Convert italic text (*text* -> <em>text</em>)
    content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', content)

    # Convert paragraphs - split by double newlines
    paragraphs = content.split('\n\n')
    html_content = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Check if it's a header
        if para.startswith('<h2>'):
            html_content.append(para)
            continue

        # Check if it's a list
        if para.startswith(('- ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            # Convert to HTML list
            list_items = []
            list_lines = para.split('\n')
            for line in list_lines:
                line = line.strip()
                if line.startswith(('- ', '* ')):
                    list_items.append(f'<li>{line[2:]}</li>')
                elif re.match(r'^\d+\.\s', line):
                    list_items.append(f'<li>{line[3:]}</li>')

            if any(line.startswith(('- ', '* ')) for line in list_lines):
                html_content.append('<ul>\n' + '\n'.join(list_items) + '\n</ul>')
            else:
                html_content.append('<ol>\n' + '\n'.join(list_items) + '\n</ol>')
            continue

        # Check if it's a horizontal rule
        if para.strip() == '---':
            html_content.append('<hr />')
            continue

        # Regular paragraph
        # Handle line breaks within paragraphs
        para_lines = para.split('\n')
        if len(para_lines) > 1:
            # Multiple lines in paragraph - join with <br />
            para_content = '<br />\n'.join(line.strip() for line in para_lines if line.strip())
            html_content.append(f'<p>{para_content}</p>')
        else:
            html_content.append(f'<p>{para}</p>')

    return '\n\n'.join(html_content)

def get_existing_blog_posts():
    """Get list of existing blog post filenames (without .html extension)"""
    blog_dir = Path('blog_articles')
    if not blog_dir.exists():
        return set()

    existing = set()
    for html_file in blog_dir.glob('*.html'):
        if html_file.name != 'single.html':  # Skip template
            existing.add(html_file.stem)  # filename without extension

    return existing

def get_articles_to_process():
    """Get list of markdown articles that need blog posts"""
    articles_dir = Path('articles')
    if not articles_dir.exists():
        print("❌ Articles directory not found!")
        return []

    existing_blogs = get_existing_blog_posts()
    articles_to_process = []

    for md_file in articles_dir.glob('*.md'):
        # Skip Windows zone identifier files
        if ':Zone.Identifier' in md_file.name:
            continue

        article_name = md_file.stem
        if article_name not in existing_blogs:
            articles_to_process.append(md_file)

    return articles_to_process

def load_template():
    """Load the single.html template"""
    template_path = Path('blog_articles/single.html')
    if not template_path.exists():
        print("❌ Template file blog_articles/single.html not found!")
        return None

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_blog_post(article_path, template):
    """Generate a blog post HTML file from markdown article"""

    # Read the markdown file
    with open(article_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Extract title and subtitle
    title = extract_title_from_markdown(markdown_content)
    subtitle = extract_subtitle_from_markdown(markdown_content)

    # Convert markdown to HTML
    article_html = markdown_to_html(markdown_content)

    # Create the HTML content by modifying template
    html_content = template

    # Replace title
    html_content = html_content.replace(
        '<title>Blog Single - Keep It Simple</title>',
        f'<title>{title} - Keep It Simple</title>'
    )

    # Replace article title in the content
    html_content = html_content.replace(
        'Hey, We Love Open Sans!',
        title
    )

    # Replace the href in the title link
    article_filename = article_path.stem + '.html'
    html_content = html_content.replace(
        'href="single.html"',
        f'href="{article_filename}"'
    )

    # Remove the image section
    image_pattern = r'<div class="entry__content-media">.*?</div>'
    html_content = re.sub(image_pattern, '', html_content, flags=re.DOTALL)

    # Prepare content with subtitle if it exists
    if subtitle:
        content_with_subtitle = f'<p><em>{subtitle}</em></p>\n\n{article_html}'
    else:
        content_with_subtitle = article_html

    # Replace the article content
    content_pattern = r'(<div class="entry__content">)(.*?)(</div> <!-- entry__content -->)'
    replacement = f'\\1\n\n                        {content_with_subtitle}\n                    \\3'
    html_content = re.sub(content_pattern, replacement, html_content, flags=re.DOTALL)

    # Update meta information
    html_content = html_content.replace('July 12, 2019', 'September 22, 2025')
    html_content = html_content.replace('John Doe', 'Author')
    html_content = html_content.replace('Ghost', 'Philosophy')

    # Create output filename
    output_path = Path('blog_articles') / f'{article_path.stem}.html'

    # Write the HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path

def main():
    """Main function to generate blog posts"""
    print("🔍 Scanning for new articles to convert...")

    # Get articles that need blog posts
    articles_to_process = get_articles_to_process()

    if not articles_to_process:
        print("✅ No new articles found. All articles already have blog posts!")
        return

    print(f"📝 Found {len(articles_to_process)} new article(s) to process:")
    for article in articles_to_process:
        print(f"   • {article.name}")

    # Load template
    template = load_template()
    if not template:
        return

    # Generate blog posts
    print("\n🚀 Generating blog posts...")
    generated_files = []

    for article_path in articles_to_process:
        try:
            output_path = generate_blog_post(article_path, template)
            generated_files.append(output_path)
            print(f"✅ Generated: {output_path.name}")
        except Exception as e:
            print(f"❌ Error processing {article_path.name}: {str(e)}")

    print(f"\n🎉 Successfully generated {len(generated_files)} blog post(s)!")

    if generated_files:
        print("\n📁 New blog posts created in blog_articles/:")
        for file_path in generated_files:
            print(f"   • {file_path.name}")

if __name__ == "__main__":
    main()