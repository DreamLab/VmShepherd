from unittest import TestCase
from vmshepherd import VmShepherd


class TestVmShepherd(TestCase):

    def test_vmshepherd(self):
        self.assertIsNotNone(VmShepherd)
        self.assertTrue(True)
