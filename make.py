
import lxml.etree
import glob

from blogposts import BlogPosts


def posts_from_xml(path):

    # read and parse xml from posts files
    fnames = glob.glob(path)

    post_etrees = list()
    for fname in fnames:
        with open(fname, 'r') as f:
            text = f.read()
        post_etrees += lxml.etree.fromstring(text).xpath('post')

    return BlogPosts(post_etrees)

if __name__ == '__main__':
    
    # original template file to use
    template_fname = 'EDIT_ME_index_template.html'
    template_replace_tag = '<BLOG_PREVIEWS_HERE/>'

    # create individual post previews
    posts = posts_from_xml('posts/*.xml')

    # read template file and replace values with previews
    with open(template_fname, 'r') as f:
        index_html = f.read().replace(template_replace_tag, posts.get_html())
    
    # write index file
    with open('index.html', 'w') as f:
        f.write(index_html)

    print('wrote index.html')




