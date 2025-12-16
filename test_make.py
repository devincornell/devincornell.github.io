
#import lxml.etree
#import glob
#import pathlib
from pathlib import Path
from pprint import pprint
import jinja2
#from blogposts import Blog#, BlogPost
import blogmaker
import pymddoc


if __name__ == '__main__':

    ################################# Data Science Blog #################################

    if False:
        doc = pymddoc.MarkdownDoc.from_file('post_markdown/better_dataframes_encapsulation.md')
        print(doc.render_html())

    # create draft articles
    if True:
        bmaker = blogmaker.BlogMaker.read_from_markdown_files(
            markdown_files = list(Path('post_markdown/').glob('*.md')),
            blogroll_template_fname = Path('templates/blogroll_template.html'),
            blogpost_template_fname = Path('templates/blogpost_template.html'),
        )
        bmaker.render_blogroll_page('test_blog.html')

        for post in bmaker.posts:
            post.render_blogpost_page(target_fpath=f'test_post/{post.id}.html')
        