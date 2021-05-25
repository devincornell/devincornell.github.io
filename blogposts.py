import pathlib
import markdown
import dateutil.parser

class BlogPost:
    ''' Handles parsing of single blog post.
    '''
    # read in template data and read markdown file
    def __init__(self, 
                    post_path: pathlib.Path, # path to markdown file
                    blogpost_template_path: pathlib.Path,
                    blogroll_template_path: pathlib.Path
                ):
        self.post_path = post_path
        self.bp_template = blogpost_template_path.read_text()
        self.br_template = blogroll_template_path.read_text()

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

    def write_post(self, outfolder_path: pathlib.Path):
        ''' Write post to a file (call .parse_post() first).
        '''
        if not hasattr(self, 'post_html'):
            raise ValueError('Must call .parse_post() before using .write_post().')
        
        # write down fname
        fpath = outfolder_path.joinpath(self.get_fname())

        # get blogpost html
        blogpost_html = self.format_blogpost(
            title=self.metadata['title'],
            subtitle=self.metadata['subtitle'],
            date=self.metadata['date'],
            body=self.post_html
        )
        fpath.write_text(blogpost_html)

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
        header = markdown.split('---')[1]
        
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

        return meta

    ###################### String Formatting Functions ######################

    def get_fname(self):
        return f"{self.metadata['id']}.html"

    def format_blogpost(self, title:str, subtitle:str, date:str, body:str):
        ''' Return blogpost template with values substituted.
        '''
        return self.bp_template.format(
            title=title,
            subtitle=subtitle,
            date=date,
            body=body,
        )
    
    def format_blogroll(self, path: str, title: str, subtitle:str, date:str):
        ''' Return blogroll template with values substituted.
        '''
        return self.bp_template.format(
            path=path,
            title=title,
            subtitle=subtitle,
            date=date,
        )


class Blog:
    ''' Main blog interface - creates BlogPosts for writing.
    '''
    
    def __init__(self, 
                    markdown_folder: str, 
                    blogpost_template_fname: str,
                    blogroll_template_fname: str,
                    post_folder: str
                ):
        self.md_path = pathlib.Path(markdown_folder)
        self.post_path = pathlib.Path(post_folder)
        
        blogpost_template_path = pathlib.Path(blogpost_template_fname)
        blogroll_template_path = pathlib.Path(blogroll_template_fname)

        
        # extract markdown files
        self.posts = [BlogPost(p, blogpost_template_path, blogroll_template_path) 
                        for p in self.md_path.glob('*.md')]

    def __iter__(self):
        return iter(self.posts)

    def parse_posts(self):
        for post in self.posts:
            post.parse_post()

    def write_posts(self, outfolder_fname: str):
        outfolder_path = pathlib.Path(outfolder_fname)
        for post in self.posts:
            post.write_post(outfolder_path)



