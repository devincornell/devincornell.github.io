
#import lxml.etree
#import glob
from pprint import pprint

from blogposts import Blog#, BlogPost


if __name__ == '__main__':

    # make main blog object
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
    #    print(post.post_path)
    #    post.parse_post()
    #    post.write_post
    #    pprint(post.metadata)
        #print(type(post.md_text))
        #pprint(post.md_text)






