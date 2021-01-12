

import markdown
import glob
import lxml.etree

def attr(element, name):
    if name in {'header', 'body'}:
        return markdown.markdown(element.xpath(f'{name}/text()')[0])
    else:
        return element.xpath(f'{name}/text()')[0]

replacement_map = {
    'title': '###TITLE GOES HERE###',
    'date': '###DATE GOES HERE###',
    'header': '###HEADER GOES HERE###',
    'body': '###BODY GOES HERE###',
}

template = '''
###TITLE GOES HERE###
###DATE GOES HERE###
###HEADER GOES HERE###
###BODY GOES HERE###
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
        html = template
        for key, replace_str in replacement_map.items():
            html = html.replace(replace_str, attr(post, key))
        name = attr(post, 'name')
        with open(f'posts/{name}.html', 'w') as f:
            f.write(html)

    # create main blog post html file

    print(html)




