import pathlib
import markdown
import dateutil.parser
import jinja2


class Blog:
    ''' Main blog interface - creates BlogPosts for writing.
    '''
    
    def __init__(self, 
                    markdown_folder: str, 
                    post_folder: str,
                    blogpage_template: str,
                    blogpost_template: str,
                    blogroll_template: str
                ):
        self.md_path = pathlib.Path(markdown_folder)
        self.post_path = pathlib.Path(post_folder)

        # read template files (accessed from BlogPost children)
        environment = jinja2.Environment()        
        self.blogpage_template = environment.from_string(pathlib.Path(blogpage_template).read_text())
        self.blogpost_template = environment.from_string(pathlib.Path(blogpost_template).read_text())
        self.blogroll_template = environment.from_string(pathlib.Path(blogroll_template).read_text())
        
        # extract markdown files
        self.posts = [BlogPost(p, self) for p in self.md_path.glob('*.md')]

    def __iter__(self):
        return iter(self.posts)

    def parse_posts(self):
        for post in self.posts:
            post.parse_post()

    def write_posts(self):
        for post in self.posts:
            post.write_post()

    def write_blogpage(self, blogfile: str = 'blog.html'):
        br_html = ''
        for blog in sorted(self.posts, key=lambda x: x.metadata['parsed_date'], reverse=True):
            title, date = blog.metadata['title'], blog.metadata['date']
            print(f'creating blog page ({date}): {title}')
            br_html += blog.get_blogroll_html()
        blog_html = self.blogpage_template.render(blogroll=br_html)
        
        print(f'creating blog main page with {len(self.posts)} posts.')
        with open(blogfile, 'w') as f:
            f.write(blog_html)




class BlogPost:
    ''' Handles parsing of single blog post.
    '''
    # read in template data and read markdown file
    def __init__(self, post_path: pathlib.Path, blog: Blog):
        self.post_path = post_path
        self.blog = blog
        self.parsed_date = None

        self.md_text = self.post_path.read_text()

    ###################### Toplevel API Functions ######################

    def parse_post(self):
        ''' Parse the blog post and store components.
        '''
        # separate into header and body information
        self.metadata = self.parse_metadata(self.md_text)
        self.body = self.parse_body(self.md_text)

        # convert markdown to html
        self.post_html = markdown.markdown(self.body)

    def write_post(self):
        ''' Write post to a file (call .parse_post() first).
        '''
        if not hasattr(self, 'post_html'):
            raise ValueError('Must call .parse_post() before using .write_post().')

        # get blogpost html
        blogpost_html = self.format_blogpost(
            title=self.metadata['title'],
            subtitle=self.metadata['subtitle'],
            date=self.metadata['date'],
            body=self.post_html
        )
        self.get_fname().write_text(blogpost_html)

    def get_blogroll_html(self):
        return self.format_blogroll(
            path = self.get_fname(),
            title = self.metadata['title'],
            subtitle = self.metadata['subtitle'],
            date = self.metadata['date']
        )


    ###################### Parsing Functions ######################

    @classmethod
    def parse_body(cls, markdown: str):
        ''' Removes yaml header from top of markdown text.
        '''
        return '---'.join(markdown.split('---')[2:])

    @classmethod
    def parse_metadata(cls, markdown: str):
        ''' Parses metadata at the top of the markdown text.
        '''
        try:
            header = markdown.split('---')[1]
        except IndexError as e:
            print(markdown)
            print(f'fuck!!!')
            raise e
        
        meta = dict()
        for attr in header.split('\n'):
            if len(attr.strip()):
                s = attr.split(':')
                attr, val = s[0].strip(), s[1].strip()
                
                # error check surrounding double quotes
                if not (val[0] == '"' and val[-1] == '"'):
                    raise ValueError('Blog post markdown yaml values must '
                                        'be surrounded by double quotes.')
                
                # remove surrounding double quotes, save value
                meta[attr] = val[1:-1]

                if attr == 'date':
                    meta['parsed_date'] = dateutil.parser.parse(meta['date'])
        
        return meta

    ###################### String Formatting Functions ######################

    def get_fname(self):
        return self.blog.post_path.joinpath(f"{self.metadata['id']}.html")

    def format_blogpost(self, title:str, subtitle:str, date:str, body:str):
        ''' Return blogpost template with values substituted.
        '''
        return self.blog.blogpost_template.render(
            title=title,
            subtitle=subtitle,
            date=date,
            body=body,
        )
    
    def format_blogroll(self, path: str, title: str, subtitle:str, date:str):
        ''' Return blogroll template with values substituted.
        '''
        return self.blog.blogroll_template.render(
            path=path,
            title=title,
            subtitle=subtitle,
            date=date,
        )



