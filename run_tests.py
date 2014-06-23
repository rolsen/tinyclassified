import unittest

from services.db_service_test import *
from services.email_service_test import *
from services.listing_service_test import *
from services.user_service_test import *

from controllers.admin_controller_test import *
from controllers.author_controller_test import *
from controllers.author_contact_controller_test import *
from controllers.login_controller_test import *
from controllers.public_controller_test import *
from controllers.util_test import *

def setup_tests():
    import tiny_classified
    tiny_classified.initialize_standalone()

if __name__ == '__main__':
    setup_tests()
    unittest.main()
