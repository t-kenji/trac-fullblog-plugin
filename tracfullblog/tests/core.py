from trac.core import TracError
from trac.perm import PermissionCache, PermissionSystem, PermissionError
from trac.resource import Resource
from trac.test import Mock
from trac.util.html import Markup
from trac.web.api import HTTPNotFound
from trac.web.href import Href

from tracfullblog.core import FullBlogCore
from tracfullblog.model import BlogPost, get_blog_posts

from tracfullblog.tests import FullBlogTestCaseTemplate


class FullBlogCoreTestCase(FullBlogTestCaseTemplate):

    def test_create_post_missing_default_fields(self):
        PermissionSystem(self.env).grant_permission('user', 'BLOG_VIEW')
        core = FullBlogCore(self.env)
        req = Mock(method='GET', base_path='', cgi_location='',
                   path_info='/blog', href=Href('/trac'), args={}, chrome={},
                   perm=PermissionCache(self.env, 'user'), authname='user')
        bp = BlogPost(self.env, 'about')
        warnings = core.create_post(req, bp, req.authname)
        self.assertEquals(warnings, [('title', 'Title is empty.'),
            ('body', 'Body is empty.'), ('author', 'Author is empty.')])

    def test_create_post(self):
        PermissionSystem(self.env).grant_permission('user', 'BLOG_VIEW')
        core = FullBlogCore(self.env)
        req = Mock(method='GET', base_path='', cgi_location='',
                   path_info='/blog', href=Href('/trac'), args={}, chrome={},
                   perm=PermissionCache(self.env, 'user'), authname='user')
        bp = BlogPost(self.env, 'about')
        bp.update_fields(fields={'title': 'test_create_post', 'author': 'user',
            'body': 'First body'})
        warnings = core.create_post(req, bp, req.authname)
        self.assertEquals(warnings, [])
        posts = get_blog_posts(self.env)
        self.assertEquals(1, len(posts))
        self.assertEquals('test_create_post', posts[0][4])
