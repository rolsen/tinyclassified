"""Utility functions / classes for controller testing.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""

class TestCollection():
    find_hash = None
    find_result = None
    deleted = []

    def find_one(self, find_hash):
        self.find_hash = find_hash
        return self.find_result

    def remove(self, remove):
        self.deleted.append(remove)


class TestDBAdapter():
    collection = None

    def get_listings_collection(self):
        return self.collection


def check_dict(expected_dict, test_dict):
    """Check that two dictionaries are the same for each key in the first dict.

    Check that each key value pair in expected_dict is also in test dictionary
    but do not check that the relationship is bidirectional (test_dict may
    contain keys / values not in expected_dict).

    @return: True if everything in expected_dict is in test_dict. False
        otherwise.
    @rtype: bool
    """
    for (key, value) in expected_dict.items():
        if test_dict[key] != value:
            return False
    return True
