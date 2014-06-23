"""Tests for author_controller.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import mox

try:
    from tinyclassified import tiny_classified
except:
    import tiny_classified

import util

TEST_TAG0 = {'foo': ['stuff'], '_id': 0}
TEST_TAG1 = {'bar': ['stuff'], '_id': 1}

def function_undecorated():
    return flask.render_template(
        'util_test.html',
        base_url=config['BASE_URL'],
        parent_template=config.get('PARENT_TEMPLATE', 'base.html')
    )

@util.require_login()
def function_require_login():
    return function_undecorated()

@util.require_login(admin=True)
def function_require_admin():
    return function_undecorated()

class UtilTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        app = tiny_classified.get_app()
        app.debug = True
        self.app = app.test_client()

    def test_require_login_not_logged_in(self):
        self.mox.StubOutWithMock(util, 'check_active_requirement')
        util.check_active_requirement().AndReturn(False)

        self.mox.StubOutWithMock(util, 'redirect_inactive_user')
        util.redirect_inactive_user().AndReturn('redirect_302')

        self.mox.ReplayAll()

        result = function_require_login()
        self.assertEqual('redirect_302', result)

    def test_require_login_not_admin(self):
        self.mox.StubOutWithMock(util, 'check_active_requirement')
        util.check_active_requirement().AndReturn(True)

        self.mox.StubOutWithMock(util, 'check_admin_requirement')
        util.check_admin_requirement(True).AndReturn(False)

        self.mox.StubOutWithMock(util, 'redirect_inactive_user')
        util.redirect_inactive_user().AndReturn('redirect_302')

        self.mox.ReplayAll()

        result = function_require_admin()
        self.assertEqual('redirect_302', result)

    def test_remove_element_by_id_exists(self):
        tags = [TEST_TAG0, TEST_TAG1]

        result = util.remove_element_by_id(tags, 0)
        self.assertTrue(result)
        self.assertEqual(1, len(tags))
        self.assertEqual(TEST_TAG1, tags[0])

    def test_remove_element_by_id_not_exist(self):
        tags = [TEST_TAG0, TEST_TAG1]

        result = util.remove_element_by_id(tags, 3)
        self.assertFalse(result)
        self.assertEqual(2, len(tags))
        self.assertEqual(TEST_TAG0, tags[0])
        self.assertEqual(TEST_TAG1, tags[1])
