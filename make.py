
#import lxml.etree
#import glob
from pprint import pprint

from blogposts import Blog#, BlogPost


if __name__ == '__main__':

    # make main blog object
    blog = Blog(
        markdown_folder = 'post_markdown',
        blogpost_template_fname = 'templates/blogpost_template.html',
        blogroll_template_fname = 'templates/blogroll_template.html',
        post_folder = 'post'
    )

    blog.parse_posts()
    blog.write_posts('post')
    #for post in blog:
    #    print(post.post_path)
    #    post.parse_post()
    #    post.write_post
    #    pprint(post.metadata)
        #print(type(post.md_text))
        #pprint(post.md_text)






