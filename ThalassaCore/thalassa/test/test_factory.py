import unittest

import thalassa.factory

class TestFactory(unittest.TestCase):

    def setUp(self):
        thalassa.factory._reference_bank = None

    def test_replacing(self):
        """ Test setting thalassa.factory references bank with enabled
            replace flag.

        Step 1: Set references and check if Create() works as intended.
        Step 2: Set references again with replace option enabled.
            - Check whether calling for old settings raises KeyError
            - Check if Create() works with new settings
        """
        class type_for_test:
            pass
        class replacing_type:
            pass

        thalassa.factory.SetReferences(
            new_references = {
                type_for_test: type_for_test
                }
            )
        instance = thalassa.factory.Create(type_for_test)
        self.assertIsInstance(instance, type_for_test)

        thalassa.factory.SetReferences(
            new_references = {
                replacing_type: replacing_type
                },
            replace = True,
            )
        with self.assertRaises(KeyError):
            thalassa.factory.Create(type_for_test)
        instance = thalassa.factory.Create(replacing_type)
        self.assertIsInstance(instance, replacing_type)