"""Tests for author_controller.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import mox

import tiny_classified

import util


def function_undecorated():
    return flask.render_template('util_test.html')

@util.require_login()
def function_require_login():
    return function_undecorated()

@util.require_login(admin=True)
def function_require_admin():
    return function_undecorated()

class UtilTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        tiny_classified.app.debug = True
        self.app = tiny_classified.app.test_client()

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
