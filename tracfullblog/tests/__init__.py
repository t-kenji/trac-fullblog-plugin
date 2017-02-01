
from unittest import TestCase, TestSuite, makeSuite

from trac.perm import DefaultPermissionStore
from trac.test import EnvironmentStub

from tracfullblog.db import FullBlogSetup


class FullBlogTestCaseTemplate(TestCase):

    def setUp(self):
        self.env = EnvironmentStub(enable=['trac.*', 'tracfullblog.*'])
        # tables
        if hasattr(self.env, 'db_transaction'):
            with self.env.db_transaction as db:
                FullBlogSetup(self.env).upgrade_environment(db)
        else:
            FullBlogSetup(self.env).upgrade_environment(self.env.get_db_cnx())
        # permissions
        self.env.config.set('trac', 'permission_store',
                            'DefaultPermissionStore')
        self.env.config.set('trac', 'permission_policies',
                            'DefaultPermissionPolicy')

    def tearDown(self):
        self.env.destroy_db()
        del self.env


def test_suite():
    suite = TestSuite()
    import tracfullblog.tests.core
    suite.addTest(makeSuite(tracfullblog.tests.core.FullBlogCoreTestCase))
    import tracfullblog.tests.model
    suite.addTest(makeSuite(tracfullblog.tests.model.GroupPostsByMonthTestCase))
    suite.addTest(makeSuite(tracfullblog.tests.model.GetBlogPostsTestCase))
    import tracfullblog.tests.web_ui
    suite.addTest(makeSuite(tracfullblog.tests.web_ui.FullBlogListtingsTestCase))
    suite.addTest(makeSuite(tracfullblog.tests.web_ui.FullBlogRssTestCase))
    suite.addTest(makeSuite(tracfullblog.tests.web_ui.FullBlogPostTestCase))
    return suite
