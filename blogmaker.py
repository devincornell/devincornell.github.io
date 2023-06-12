
from __future__ import annotations

import pathlib
import markdown
import dateutil.parser
import jinja2
import datetime
import typing

#pip install python-frontmatter
import frontmatter

import dataclasses

@dataclasses.dataclass
class BlogMaker:
    ''' Main blog interface - creates BlogPosts for writing.
    '''
    #markdown_files: typing.List[str]
    #output_folder: str
    blogroll_template: jinja2.Template
    blogpost_template: jinja2.Template
    environment: jinja2.Environment
    
    @classmethod
    def from_template_files(cls, 
            blogroll_template_fname: str,
            blogpost_template_fname: str,
        ) -> BlogMaker:
        environment = jinja2.Environment()
        return cls(
            environment = environment,
            blogroll_template = environment.from_string(pathlib.Path(blogroll_template_fname).read_text()),
            blogpost_template = environment.from_string(pathlib.Path(blogpost_template_fname).read_text()),
        )

    def write_blogpost_html(self, post: BlogPost, fname: str) -> str:
        '''Render a single blog post page.'''
        html = self.blogpost_template.render(post=post.as_dict())
        
        with pathlib.Path(fname).open('w') as f:
            f.write(html)
        
    
    
    
    def format_blogpost(self, title:str, subtitle:str, date:str, body:str):
        ''' Return blogpost template with values substituted.
        '''
        return self.blog.blogpost_template.render(
            title=title,
            subtitle=subtitle,
            date=date,
            body=body,
        )

    
    def render_blogroll_page(self, posts: typing.List[BlogPost]) -> str:
        '''Renders the blogroll page according to the provided template.'''
        pass
    
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

#def read_and_parse_posts(markdown_fnames: typing.List[str]) -> typing.Generator[BlogPost, None, None]:
#    '''Yields parsed posts to the caller.'''
#    for md_fname in markdown_fnames:
#        post = BlogPost.from_file(md_fname)
#        yield post

@dataclasses.dataclass
class BlogPost:
    ''' Handles parsing of single blog post.
    '''
    fpath: pathlib.Path
    title: str
    subtitle: str
    date: datetime.datetime
    tag: str
    body: str
    
    @classmethod
    def from_markdown_file(cls, fname: str) -> BlogPost:
        fpath = pathlib.Path(fname)
        
        with fpath.open('r') as f:
            md_text = f.read()
        
        post_data = frontmatter.loads(md_text)
        
        return cls(
            fpath = fpath,
            title = post_data['title'],
            subtitle = post_data['subtitle'],
            date = post_data['date'],
            tag = post_data['id'],
            body = post_data.content,
            #body_html = markdown.markdown(post_data.content),
        )
    
    def render_html(self) -> str:
        '''Converts article body to html using markdown package.'''
        return markdown.markdown(self.body)

    def as_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            'body_html': self.render_html(),
            **dataclasses.asdict(self),
        }

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



