

import markdown
import glob
import lxml.etree

post_replacement_map = {
    'name': '<<<NAME_GOES_HERE>>>',
    'title': '<<<TITLE_GOES_HERE>>>',
    'author': '<<<AUTHOR_GOES_HERE>>>',
    'date': '<<<DATE_GOES_HERE>>>',
    'header': '<<<HEADER_GOES_HERE>>>',
    'body': '<<<BODY_GOES_HERE>>>',
}

post_preview_template = \
'''
<div class="resume-item d-flex flex-column flex-md-row justify-content-between mb-5">
    <div class="resume-content">
        <h3 class="mb-0"><a href="/posts/<<<NAME_GOES_HERE>>>.html"><<<TITLE_GOES_HERE>>></a></h3>
        <div class="subheading mb-3">By <<<AUTHOR_GOES_HERE>>> on <<<DATE_GOES_HERE>>></div>
        <<<HEADER_GOES_HERE>>>
        <p><a class="btn btn-primary" data-toggle="collapse" href="#blogCollapse{i}" role="button" aria-expanded="false" aria-controls="blogCollapse{i}">Full post</a></p>
        <div class="collapse" id="blogCollapse{i}">
            <<<BODY_GOES_HERE>>>
        </div>
    </div>
    <div class="resume-date text-md-right">
        <span class="text-primary"></span>
    </div>
</div>
'''

def template_replace(template_html, post):
    ''' Replace attributes of a post in a template string.
    '''
    for key, replace_str in post_replacement_map.items():
        template_html = template_html.replace(replace_str, attr(post, key))
    return template_html

def attr(post, name):
    ''' Extract text from single attribute of a post xml element.
    '''
    if name in {'header', 'body'}:
        return markdown.markdown(post.xpath(f'{name}/text()')[0])
    else:
        return post.xpath(f'{name}/text()')[0]

post_template = '''
<<<TITLE_GOES_HERE>>>
<<<DATE_GOES_HERE>>>
<<<HEADER_GOES_HERE>>>
<<<BODY_GOES_HERE>>>
'''


if __name__ == '__main__':
    fnames = glob.glob('posts/*.xml')

    # read and parse xml from posts files
    posts = list()
    for fname in fnames:
        with open(fname, 'r') as f:
            text = f.read()
        posts += lxml.etree.fromstring(text).xpath('post')

    # create files for individual posts
    for post in posts:
        name = attr(post, 'name')
        fname = f'posts/{name}.html'
        with open(fname, 'w') as f:
            f.write(template_replace(post_template, post))
        print(f'wrote post file: {fname}')
    
    # create individual post previews
    post_previews = list()
    for post in posts:
        post_previews.append(template_replace(post_preview_template, post))

    # read template file and replace values with previews
    with open('EDIT_ME_index_template.html', 'r') as f:
        index_html = f.read().replace('<<<BLOG_PREVIEWS_HERE>>>', '\n'.join(post_previews))

    
    # write index file
    with open('index.html', 'w') as f:
        f.write(index_html)

    print('wrote index.html')



