"""Tests for Internet-facing controllers managing user logins / password resets.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
"""
import copy
import mox
import werkzeug

try:
    from tinyclassified import tiny_classified
    from tinyclassified import services
except:
    import tiny_classified
    import services

import login_controller
import util


WEIRD_CASE_EMAIL = 'TesT@exaMple.coM'
TEST_USER = dict(
    email='test@example.com',
    password_hash=werkzeug.generate_password_hash('password', method='sha512'),
    is_admin=False
)

class LoginControllerTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        app = tiny_classified.get_app()
        app.debug = True
        self.app = app.test_client()
        self.user = copy.deepcopy(TEST_USER)

    def test_render_login(self):
        result = self.app.get('/login')
        self.assertTrue('Login' in result.data)
        self.assertEqual(200, result.status_code)

    def test_login_found(self):
        self.mox.StubOutWithMock(services.user_service, 'read')
        services.user_service.read(self.user['email']).AndReturn(self.user)
        self.mox.ReplayAll()

        result = self.app.post(
            '/login',
            data={util.SESS_EMAIL: WEIRD_CASE_EMAIL, 'password': 'password'}
        )

        self.assertEqual(result.status_code, 302)
        with self.app.session_transaction() as sess:
            self.assertEqual(sess[util.SESS_EMAIL], self.user['email'])
            self.assertEqual(sess['is_admin'], self.user['is_admin'])

    def test_login_not_found(self):
        self.mox.StubOutWithMock(services.user_service, 'read')
        services.user_service.read(self.user['email']).AndReturn(None)
        self.mox.ReplayAll()

        result = self.app.post(
            '/login',
            data={util.SESS_EMAIL: WEIRD_CASE_EMAIL, 'password': 'password'}
        )

        self.assertEqual(result.status_code, 302)
        with self.app.session_transaction() as sess:
            self.assertFalse(util.SESS_EMAIL in sess)
            self.assertTrue(util.SESS_VALIDATION_ERROR in sess)
            self.assertTrue(util.SESS_VALIDATION_SHOW_RESET in sess)

    def test_login_password_fail(self):
        self.mox.StubOutWithMock(services.user_service, 'read')
        services.user_service.read(self.user['email']).AndReturn(self.user)
        self.mox.ReplayAll()

        result = self.app.post(
            '/login',
            data={util.SESS_EMAIL: self.user['email'], 'password': 'wrong'}
        )

        self.assertEqual(result.status_code, 302)
        with self.app.session_transaction() as sess:
            self.assertFalse(util.SESS_EMAIL in sess)
            self.assertTrue(util.SESS_VALIDATION_ERROR in sess)
            self.assertTrue(util.SESS_VALIDATION_SHOW_RESET in sess)

    def test_logout(self):
        with self.app.session_transaction() as sess:
            sess[util.SESS_EMAIL] = self.user['email']
            sess[util.SESS_IS_ADMIN] = False

        result = self.app.get('/logout')

        self.assertEqual(result.status_code, 302)
        with self.app.session_transaction() as sess:
            self.assertEqual(sess.get(util.SESS_EMAIL, None), None)
            self.assertEqual(sess.get(util.SESS_IS_ADMIN, None), None)

    def test_render_forgot_password(self):
        result = self.app.get('/forgot_password')
        self.assertTrue('Reset' in result.data)
        self.assertEqual(200, result.status_code)

    def test_forgot_password(self):
        self.mox.StubOutWithMock(services.user_service, 'read')
        services.user_service.read(self.user['email']).AndReturn(self.user)

        self.mox.StubOutWithMock(services.user_service, 'update_password')
        services.user_service.update_password(
            self.user,
            mox.IsA(str),
            True,
            True
        )

        self.mox.ReplayAll()

        self.app.post(
            '/forgot_password',
            data={util.SESS_EMAIL: WEIRD_CASE_EMAIL}
        )

        result = self.app.get('/logout')
        self.assertEqual(result.status_code, 302)

    def test_forgot_password_user_not_found(self):
        self.mox.StubOutWithMock(services.user_service, 'read')
        services.user_service.read(self.user['email']).AndReturn(None)

        self.mox.StubOutWithMock(services.user_service, 'update_password')

        self.mox.ReplayAll()

        self.app.post(
            '/forgot_password',
            data={util.SESS_EMAIL: self.user['email']}
        )

        result = self.app.get('/logout')
        self.assertEqual(result.status_code, 302)
