
#import lxml.etree
#import glob
import pathlib
from pprint import pprint
import jinja2
#from blogposts import Blog#, BlogPost
import blogmaker


if __name__ == '__main__':

    bmaker = blogmaker.BlogMaker.from_template_files(
        blogroll_template_fname = pathlib.Path('templates/blogroll_template.html'),
        blogpost_template_fname = pathlib.Path('templates/blogpost_template.html'),
    )


    posts = list()
    post_folder = 'post/'
    for fp in pathlib.Path('post_markdown/').glob('*.md'):
        print('found post:',  fp)
        
        post = blogmaker.BlogPost.from_markdown_file(fp)
        html = bmaker.render_blogpost_page(post)
        
        with pathlib.Path(f'{post_folder}/{post.tag}.html').open('w') as f:
            f.write(html)
            
        posts.append(post)
        
    bmaker.render_blogroll_page(posts)
    
    
    
    draft_folder = 'draft/'
    for fp in pathlib.Path('draft_markdown/').glob('*.md'):
        print('found draft:',  fp)
        
        post = blogmaker.BlogPost.from_markdown_file(fp)
        html = bmaker.render_blogpost_page(post)
        
        with pathlib.Path(f'{draft_folder}/{post.tag}.html').open('w') as f:
            f.write(html)

        

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




