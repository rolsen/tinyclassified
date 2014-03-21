import unittest

from services.db_service_test import *
from services.listing_service_test import *
from services.user_service_test import *

from controllers.admin_controller_test import *
from controllers.author_controller_test import *
from controllers.public_controller_test import *
from controllers.util_test import *


if __name__ == '__main__':
    import tiny_classified
    tiny_classified.attach_blueprints()
    unittest.main()
