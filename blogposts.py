
import markdown
import dateutil.parser

class BlogPosts:
    def __init__(self, post_etrees):

        # create blogpost objects and sort by date
        self.posts = [BlogPost(p) for p in post_etrees]
        self.posts = list(sorted(self.posts, key=lambda p: p.date(), reverse=True))
    
    def get_html(self):
        return '\n'.join([p.get_html() for p in self.posts])


class BlogPost:
    post_keys = ['post_id', 'title', 'author', 'date', 'header', 'body']

    html_template = \
    '''
    <div class="resume-item d-flex flex-column flex-md-row justify-content-between mb-5">
        <div class="resume-content">
            <h3 class="mb-0"><a data-toggle="collapse" href="#{post_id}" role="button" aria-expanded="false" aria-controls="{post_id}">{title}</a></h3>
            <div class="subheading mb-3">{date}</div>
            {header}
            <p><a data-toggle="collapse" href="#{post_id}" role="button" aria-expanded="false" aria-controls="{post_id}">Expand full post...</a></p>
            <div class="collapse" id="{post_id}">
                {body}
            </div>
        </div>
        <div class="resume-date text-md-right">
            <span class="text-primary"></span>
        </div>
    </div>
    '''

    def __init__(self, post_etree):
        self.data = dict()
        for key in self.post_keys:
            self.data[key] = self.attr(post_etree, key)

    @staticmethod
    def attr(post, name):
        ''' Extract text from single attribute of a post xml element.
        '''
        if name in {'header', 'body'}:
            return markdown.markdown(post.xpath(f'{name}/text()')[0])
        else:
            return post.xpath(f'{name}/text()')[0]

    def get_html(self):
        ''' Get post as html string generated from template.
        '''
        return self.html_template.format(**self.data)

    def date(self):
        ''' Get parsed date (for sorting posts).
        '''
        return dateutil.parser.parse(self.data['date'])


