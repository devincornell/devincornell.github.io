
import lxml.etree
import glob

from blogposts import Blog, BlogPost


if __name__ == '__main__':

    # make main blog object
    blog = Blog(
        markdown_folder = 'post_markdown',
        blogpost_template_fname = 'templates/blogpost_template.html',
        blogroll_template_fname = 'templates/blogroll_template.html',
        post_folder = 'post'
    )





