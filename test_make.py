
#import lxml.etree
#import glob
#import pathlib
from pathlib import Path
from pprint import pprint
import jinja2
#from blogposts import Blog#, BlogPost
import blogmaker


if __name__ == '__main__':

    ################################# Data Science Blog #################################

    # create draft articles
    if True:
        bmaker = blogmaker.BlogMaker.read_from_markdown_files(
            markdown_files = list(Path('draft_markdown/').glob('*.md')),
            blogroll_template_fname = Path('templates/blogroll_template.html'),
            blogpost_template_fname = Path('templates/blogpost_template.html'),
        )
        bmaker.render_blogroll_page('test_blog.html')

        for post in bmaker.posts:
            post.render_blogpost_page(target_fpath=f'draft/{post.id}.html')
        