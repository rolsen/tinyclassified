"""Tests for user_service.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import copy

import mox

try:
    from tinyclassified import tiny_classified
except:
    import tiny_classified

import db_service
import email_service
import user_service

TEST_EMAIL = 'test@example.com'
TEST_HASH = 'testhashofapassword'
TEST_USER = {
    'email': TEST_EMAIL,
    'password_hash': TEST_HASH,
    'is_admin': False
}

class UserServiceTests(mox.MoxTestBase):

    def test_create_email_exists(self):
        self.mox.StubOutWithMock(user_service, 'read')
        user_service.read(TEST_EMAIL).AndReturn(TEST_USER)

        self.mox.StubOutWithMock(tiny_classified, 'get_db_adapter')

        self.mox.ReplayAll()

        with self.assertRaises(ValueError):
            user_service.create(TEST_USER)

    def test_create_success(self):
        self.mox.StubOutWithMock(user_service, 'read')
        user_service.read(TEST_EMAIL).AndReturn(None)

        test_db_adapter = mox.Mox().CreateMock(db_service.DBAdapter)
        test_db_adapter.upsert_user(TEST_USER)
        tiny_classified.set_db_adapter(test_db_adapter)

        self.mox.ReplayAll()

        user_service.create(TEST_USER)

    def test_update_not_exists(self):
        self.mox.StubOutWithMock(user_service, 'read')
        user_service.read(TEST_EMAIL).AndReturn(None)

        self.mox.ReplayAll()

        with self.assertRaises(ValueError):
            user_service.update(TEST_EMAIL, TEST_USER)

    def test_update_success(self):
        test_id = 'original_id'
        test_user_original = copy.deepcopy(TEST_USER)
        test_user_original['_id'] = test_id
        test_user_new = copy.deepcopy(TEST_USER)

        self.mox.StubOutWithMock(user_service, 'read')
        user_service.read(TEST_EMAIL).AndReturn(test_user_original)

        test_db_adapter = mox.Mox().CreateMock(db_service.DBAdapter)
        test_db_adapter.upsert_user(test_user_new)
        tiny_classified.db_adapter = test_db_adapter

        self.mox.ReplayAll()

        user_service.update(TEST_EMAIL, test_user_new)
        self.assertEqual(test_id, test_user_new['_id'])

    def test_delete_email_str(self):
        test_db_adapter = mox.Mox().CreateMock(db_service.DBAdapter)
        test_db_adapter.delete_user(TEST_EMAIL)
        tiny_classified.db_adapter = test_db_adapter

        self.mox.ReplayAll()

        user_service.delete(TEST_EMAIL)

    def test_delete_user_dict(self):
        test_db_adapter = mox.Mox().CreateMock(db_service.DBAdapter)
        test_db_adapter.delete_user(TEST_USER)
        tiny_classified.db_adapter = test_db_adapter

        self.mox.ReplayAll()

        user_service.delete(TEST_EMAIL)

    def test_update_password_send_email(self):
        test_user = copy.deepcopy(TEST_USER)
        new_pass = 'dasecretword'

        self.mox.StubOutWithMock(user_service, 'update')
        user_service.update(test_user['email'], mox.IsA(dict))

        self.mox.StubOutWithMock(email_service, 'send')
        email_service.send(
            [test_user['email']],
            user_service.PASSWORD_EMAIL_SUBJECT,
            mox.IsA(basestring)
        )

        self.mox.ReplayAll()

        user_service.update_password(test_user, new_pass, True, False);

    def test_update_password_send_email_with_password(self):
        test_user = copy.deepcopy(TEST_USER)
        new_pass = 'dasecretword'

        self.mox.StubOutWithMock(user_service, 'update')
        user_service.update(test_user['email'], mox.IsA(dict))

        self.mox.StubOutWithMock(email_service, 'send')
        email_service.send(
            [test_user['email']],
            user_service.PASSWORD_EMAIL_SUBJECT,
            mox.Regex(r'.*%s.*' % new_pass)
        )

        self.mox.ReplayAll()

        user_service.update_password(test_user, new_pass, True, True);
