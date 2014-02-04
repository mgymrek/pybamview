import unittest

from pybamview.bam_alignment import BamView
from pybamview.tests import test_data


class TestReadGroups(unittest.TestCase):
    def test_multiple_samples_in_one_read_group(self):
        test_bam_1 = test_data("test_1.bam")
        test_bam_2 = test_data("test_2.bam")
        view = BamView([test_bam_1, test_bam_2], "")
        self.assertEqual(len(view.LoadRGDictionary()), 2)
