
from __future__ import annotations

import pathlib
import markdown
import dateutil.parser
import jinja2
import datetime
import typing
import dateutil.parser

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

    def render_blogpost_page(self, post: BlogPost) -> str:
        '''Render a single blog post page.'''
        return self.blogpost_template.render(post=post.as_dict())
    
    def render_blogroll_page(self, posts: typing.List[BlogPost]) -> str:
        '''Renders the blogroll page according to the provided template.'''
        posts = list(sorted(posts, key=lambda p: p.date, reverse=True))
        return self.blogroll_template.render(
            posts=[p.as_dict() for p in posts],
            updated=datetime.datetime.now(),
        )


@dataclasses.dataclass
class BlogPost:
    ''' Contains information about an individual post.
    '''
    fpath: pathlib.Path
    html_path: pathlib.Path
    title: str
    subtitle: str
    entered_date: str
    date: datetime.datetime
    tag: str
    blogroll_img_url: str
    body: str
        
    @classmethod
    def from_markdown_file(cls, fname: str, html_folder: str) -> BlogPost:
        '''Read and parse a markdown file to create a post.'''
        
        fpath = pathlib.Path(fname)
        html_folder = pathlib.Path(html_folder)
        
        with fpath.open('r') as f:
            md_text = f.read()
        
        post_data = frontmatter.loads(md_text)
        
        return cls(
            fpath = fpath,
            html_path = html_folder.joinpath(post_data['id']+'.html'),
            title = post_data['title'],
            subtitle = post_data['subtitle'],
            entered_date = post_data['date'],
            date = dateutil.parser.parse(post_data['date']),
            tag = post_data['id'],
            blogroll_img_url = post_data.get('blogroll_img_url', ''),
            body = post_data.content,
        )
        
    def as_dict(self) -> typing.Dict[str, typing.Any]:
        '''Render the body and return all other attributes.'''
        return {
            'body_html': self.render_body_html(),
            **dataclasses.asdict(self),
        }
        
    def info(self) -> typing.Dict[str,str]:
        '''Get dict minus the html body.'''
        info = dataclasses.asdict(self)
        del info['body']
        return info
    
    def render_body_html(self) -> str:
        '''Converts article body to html using markdown package.'''
        return markdown.markdown(self.body)


    

