
from trac.core import TracError
from trac.perm import PermissionCache, PermissionSystem, PermissionError
from trac.resource import Resource
from trac.test import Mock
from trac.util.html import Markup
from trac.web.api import HTTPNotFound, RequestDone
from trac.web.href import Href

from tracfullblog.model import BlogPost, get_blog_posts
from tracfullblog.web_ui import FullBlogModule

from tracfullblog.tests import FullBlogTestCaseTemplate


class FullBlogListtingsTestCase(FullBlogTestCaseTemplate):

    def test_no_permission(self):
        req = Mock(method='GET', base_path='', cgi_location='',
                   path_info='/blog', href=Href('/trac'), args={}, chrome={},
                   perm=PermissionCache(self.env, 'user'), authname='user')
        module = FullBlogModule(self.env)
        assert module.match_request(req)
        self.assertRaises(PermissionError, module.process_request, req)

    def test_no_posts(self):
        PermissionSystem(self.env).grant_permission('user', 'BLOG_VIEW')
        req = Mock(method='GET', base_path='', cgi_location='',
                   path_info='/blog', href=Href('/trac'), args={}, chrome={},
                   perm=PermissionCache(self.env, 'user'), authname='user')

        module = FullBlogModule(self.env)
        assert module.match_request(req)
        template, data, _ = module.process_request(req)

        self.assertEquals('fullblog_view.html', template)
        self.assertEqual([], data['blog_post_list'])

    def test_single_post(self):
        PermissionSystem(self.env).grant_permission('user', 'BLOG_VIEW')
        bp = BlogPost(self.env, 'first_post')
        bp.update_fields(fields={'title': 'First Post', 'author': 'user',
            'body': 'First body'})
        self.assertEquals([], bp.save('user'))
        req = Mock(method='GET', base_path='', cgi_location='',
                   path_info='/blog', href=Href('/trac'), args={}, chrome={},
                   perm=PermissionCache(self.env, 'user'), authname='user')

        module = FullBlogModule(self.env)
        assert module.match_request(req)
        template, data, _ = module.process_request(req)

        self.assertEqual(1, data['blog_total'])
        self.assertEqual(1, len(data['blog_post_list']))
        self.assertEqual('First Post', data['blog_post_list'][0].title)

class FullBlogRssTestCase(FullBlogTestCaseTemplate):

    def test_rss_no_posts(self):
        PermissionSystem(self.env).grant_permission('user', 'BLOG_VIEW')
        req = Mock(method='GET', base_path='', cgi_location='',
                   path_info='/blog', href=Href('/trac'),
                   abs_href=Href('http://domain/trac'),
                   args={'format': 'rss'}, chrome={},
                   perm=PermissionCache(self.env, 'user'), authname='user')

        module = FullBlogModule(self.env)
        assert module.match_request(req)
        template, data, _ = module.process_request(req)

        self.assertEquals('fullblog.rss', template)


class FullBlogPostTestCase(FullBlogTestCaseTemplate):

    def test_new_blog_post(self):
        PermissionSystem(self.env).grant_permission('user', 'BLOG_ADMIN')
        redirects = []
        def redirect(r):
            redirects.append(r)
            raise(RequestDone)
        req = Mock(method='POST', base_path='', cgi_location='',
                   path_info='/blog/create', href=Href('/trac'),
                   args={'name': 'new_post', 'title': 'New post',
                         'author': 'admin', 'body': 'The body',
                         'action': 'new', 'blog-save': ''},
                   chrome={'warnings': []},
                   perm=PermissionCache(self.env, 'user'), authname='admin',
                   redirect=redirect)

        module = FullBlogModule(self.env)
        assert module.match_request(req)
        self.assertRaises(RequestDone, module.process_request, req)
        self.assertEquals(['/trac/blog/new_post'], redirects)
        self.assertEquals([], req.chrome['warnings'])

        posts = get_blog_posts(self.env)
        self.assertEquals(1, len(posts))
        self.assertEquals('New post', posts[0][4])
