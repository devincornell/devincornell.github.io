
#import lxml.etree
#import glob
import pathlib
from pprint import pprint
import jinja2
#from blogposts import Blog#, BlogPost
import blogmaker


if __name__ == '__main__':

    ################################# Data Science Blog #################################
    bmaker = blogmaker.BlogMaker.from_template_files(
        blogroll_template_fname = pathlib.Path('templates/blogroll_template.html'),
        blogpost_template_fname = pathlib.Path('templates/blogpost_template.html'),
    )

    # create posts
    if True:
        posts = list()
        html_folder = 'post/'
        for fp in pathlib.Path('post_markdown/').glob('*.md'):
            print('found post:',  fp)
            
            post = blogmaker.BlogPost.from_markdown_file(fp, html_folder)
            print(f'{post.info()}\n')

            html = bmaker.render_blogpost_page(post)
            
            with post.html_path.open('w') as f:
                f.write(html)
                
            posts.append(post)
            
        br_html = bmaker.render_blogroll_page(posts)
        with pathlib.Path(f'blog.html').open('w') as f:
            f.write(br_html)

    # create draft articles
    if False:
        draft_folder = 'draft/'
        for fp in pathlib.Path('draft_markdown/').glob('*.md'):
            print('found draft:',  fp)
            
            post = blogmaker.BlogPost.from_markdown_file(fp, draft_folder)
            html = bmaker.render_blogpost_page(post)
            
            with post.html_path.open('w') as f:
                f.write(html)


    
    ################################# AI Blog #################################
    bmaker = blogmaker.BlogMaker.from_template_files(
        blogroll_template_fname = pathlib.Path('templates/ai_blogroll_template.html'),
        blogpost_template_fname = pathlib.Path('templates/ai_blogpost_template.html'),
    )

    # create posts
    if True:
        posts = list()
        html_folder = 'ai_post/'
        for fp in pathlib.Path('ai_post_markdown/').glob('*.md'):
            print('found post:',  fp)
            
            post = blogmaker.BlogPost.from_markdown_file(fp, html_folder)
            print(f'{post.info()}\n')

            html = bmaker.render_blogpost_page(post)
            
            with post.html_path.open('w') as f:
                f.write(html)
                
            posts.append(post)
            
        br_html = bmaker.render_blogroll_page(posts)
        with pathlib.Path(f'ai-blog.html').open('w') as f:
            f.write(br_html)


        

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




