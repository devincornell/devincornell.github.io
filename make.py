
#import lxml.etree
#import glob
import pathlib

from pathlib import Path
from pprint import pprint
import jinja2
#from blogposts import Blog#, BlogPost
import blogmaker


if __name__ == '__main__':

    if False:
        bmaker = blogmaker.BlogMaker.read_from_markdown_files(
            markdown_files = list(Path('draft_markdown/').glob('*.md')),
            blogroll_template_fname = Path('templates/blogroll_template.html'),
            blogpost_template_fname = Path('templates/blogpost_template.html'),
        )
        bmaker.render_blogroll_page('blog_drafts.html')

        for post in bmaker.posts:
            post.render_blogpost_page(target_fpath=f'draft/{post.id}.html')

    if True:
        bmaker = blogmaker.BlogMaker.read_from_markdown_files(
            markdown_files = list(Path('post_markdown/').glob('*.md')),
            blogroll_template_fname = Path('templates/blogroll_template.html'),
            blogpost_template_fname = Path('templates/blogpost_template.html'),
        )
        bmaker.render_blogroll_page('blog.html')

        for post in bmaker.posts:
            post.render_blogpost_page(target_fpath=f'post/{post.id}.html')

    if True:
        bmaker = blogmaker.BlogMaker.read_from_markdown_files(
            markdown_files = list(Path('ai_post_markdown/').glob('*.md')),
            blogroll_template_fname = Path('templates/ai_blogroll_template.html'),
            blogpost_template_fname = Path('templates/ai_blogpost_template.html'),
        )
        bmaker.render_blogroll_page('ai-blog.html')

        for post in bmaker.posts:
            post.render_blogpost_page(target_fpath=f'ai_post/{post.id}.html')


