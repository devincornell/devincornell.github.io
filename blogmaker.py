
from __future__ import annotations

#import pathlib
from pathlib import Path
#import markdown
import dateutil.parser
import jinja2
import datetime
import typing
import dateutil.parser
import pymddoc
#pip install python-frontmatter
#import frontmatter

import dataclasses

@dataclasses.dataclass
class BlogMaker:
    ''' Main blog interface - creates BlogPosts for writing.
    '''
    #markdown_files: typing.List[str]
    #output_folder: str
    posts: typing.List[BlogPost]
    blogroll_template: jinja2.Template
    #blogpost_template: jinja2.Template
    
    @classmethod
    def read_from_markdown_files(cls, 
        markdown_files: typing.List[Path],
        blogroll_template_fname: str,
        blogpost_template_fname: str,
    ) -> BlogMaker:
        
        env = jinja2.Environment()
        blogpost_template = env.from_string(Path(blogpost_template_fname).read_text())
        blogroll_template = env.from_string(Path(blogroll_template_fname).read_text())

        # read posts
        posts: typing.List[BlogPost] = list()
        for p in markdown_files:
            if not p.exists():
                raise ValueError(f"Markdown file not found: {p}")
            else:
                post = BlogPost.read_markdown_file(
                    markdown_fpath=p, 
                    blogpost_template=blogpost_template,
                )
                posts.append(post)

        return cls(
            posts = posts,
            blogroll_template = blogroll_template,
        )
    
    def render_blogroll_page(self, fname: Path, post_link: typing.Callable[[BlogPost],str]) -> str:
        '''Renders the blogroll page according to the provided template.'''
        posts = list(sorted(self.posts, key=lambda p: p.date, reverse=True))
        html = self.blogroll_template.render(
            posts=posts,
            updated=datetime.datetime.now(),
            post_link=post_link,
        )
        with Path(fname).open('w') as f:
            f.write(html)

        return html



@dataclasses.dataclass
class BlogPost:
    ''' Contains information about an individual post.
    '''
    markdown_fpath: Path
    id: str
    title: str
    subtitle: str
    date: datetime.datetime
    date_str: str
    blogroll_img_url: str
    doc: pymddoc.MarkdownDoc
    blogpost_template: jinja2.Template
        
    @classmethod
    def read_markdown_file(cls, markdown_fpath: Path, blogpost_template: jinja2.Template) -> BlogPost:
        '''Read and parse a markdown file to create a post.'''
        
        markdown_fpath = Path(markdown_fpath)
        #html_folder = Path(html_folder)
        
        #with markdown_fpath.open('r') as f:
        #    md_text = f.read()
        
        #post_data = frontmatter.loads(md_text)
        doc = pymddoc.MarkdownDoc.from_file(markdown_fpath)
        meta = doc.extract_metadata()
        
        try:
            return cls(
                markdown_fpath = markdown_fpath,
                id = meta['id'],
                title = meta['title'],
                subtitle = meta['subtitle'],
                date = dateutil.parser.parse(meta['date']),
                date_str = meta['date'],
                blogroll_img_url = meta.get('blogroll_img_url', ''),
                doc = doc,
                blogpost_template = blogpost_template,
            )
        except KeyError as e:
            raise ValueError(f"Markdown file missing required metadatain YAML header: {e}")
        
    #def as_dict(self) -> typing.Dict[str, typing.Any]:
    #    '''Render the body and return all other attributes.'''
    #    data = dataclasses.asdict(self)
    #    del data['doc']
    #    return {
    #        'body_html': self.render_body_html(),
    #        **data,
    #    }
        
    #def info(self) -> typing.Dict[str,str]:
    #    '''Get dict minus the html body.'''
    #    info = dataclasses.asdict(self)
    #    del info['body']
    #    return info
    def render_blogpost_page(self, target_fpath: Path) -> str:
        '''Render a single blog post page and write it to target_fpath.'''
        post_html = self.blogpost_template.render(
            post=self,
            body_html = self.doc.render_html(),
        )
        with Path(target_fpath).open('w') as f:
            f.write(post_html)

        return post_html
    

