
#import lxml.etree
#import glob
import pathlib
from pprint import pprint
import jinja2
#from blogposts import Blog#, BlogPost
import blogmaker


if __name__ == '__main__':

    #draft_posts = pathlib.Path('post_markdown/*.md')
    
    bmaker = blogmaker.BlogMaker.from_template_files(
        blogroll_template_fname = pathlib.Path('templates/blogpage_template.html'),
        blogpost_template_fname = pathlib.Path('templates/blogpost_template.html'),
    )

    #environment = jinja2.Environment()
    #page_template_str = environment.from_string(page_template.read_text())
    #post_template_str = environment.from_string(post_template.read_text())

    posts = list()
    for fp in pathlib.Path('post_markdown/').glob('*.md'):
        print('post',  fp)
    #BlogMaker.from_templates(
    #    blogpage_template = ,
    #    blogpost_template = ,
    #    blogroll_template = 'templates/blogroll_template.html',
    #)
    
    
    draft_out_folder = 'draft/'
    #drafts = list()
    for fp in pathlib.Path('draft_markdown/').glob('*.md'):
        print('draft',  fp)
        post = blogmaker.BlogPost.from_markdown_file(fp)
        bmaker.write_blogpost_html(post, f'draft/{post.tag}.html')
        
        #print(post.title)
        #drafts.append(post)
        

    #print(post.body)

    # make main blog object
    if False:
        blog = Blog(
            markdown_folder = 'post_markdown',
            post_folder = 'post',
            blogpage_template = 'templates/blogpage_template.html',
            blogpost_template = 'templates/blogpost_template.html',
            blogroll_template = 'templates/blogroll_template.html',
        )

        blog.parse_posts()
        blog.write_posts()
        blog.write_blogpage()

    if False:
        blog = Blog(
            markdown_folder = 'draft_markdown',
            post_folder = 'draft',
            blogpage_template = 'templates/blogpage_template.html',
            blogpost_template = 'templates/blogpost_template.html',
            blogroll_template = 'templates/blogroll_template.html',
        )

        blog.parse_posts()
        blog.write_posts()




