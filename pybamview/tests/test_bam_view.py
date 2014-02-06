import unittest

from pybamview.constants import ENDCHAR, GAPCHAR, DELCHAR
from pybamview.constants import BAM_CMATCH, BAM_CINS, BAM_CDEL, BAM_CREF_SKIP,\
    BAM_CSOFT_CLIP, BAM_CHARD_CLIP, BAM_CPAD, BAM_CEQUAL, BAM_CDIFF
from pybamview.bam_alignment import BamView, ParseCigar
from pybamview.tests import test_data


class TestReadGroups(unittest.TestCase):
    def test_multiple_samples_in_one_read_group(self):
        test_bam_1 = test_data("test_1.bam")
        test_bam_2 = test_data("test_2.bam")
        view = BamView([test_bam_1, test_bam_2], "")
        self.assertEqual(len(view.LoadRGDictionary()), 2)

class TestCigarParsing(unittest.TestCase):
    def testM(self):
        cigar = [(BAM_CMATCH, 5)]
        nucs = "AAAAA"
        self.assertEqual(["A","A","A","A","A"], ParseCigar(cigar, nucs))

    def testI(self):
        cigar = [(BAM_CMATCH, 2), (BAM_CINS, 2), (BAM_CMATCH, 2)]
        nucs = "AAAAAA"
        self.assertEqual(["A","A","AAA","A"], ParseCigar(cigar, nucs))

    def testD(self):
        cigar = [(BAM_CMATCH, 2), (BAM_CDEL, 2), (BAM_CMATCH, 2)]
        nucs = "AAAA"
        self.assertEqual(["A","A",DELCHAR,DELCHAR,"A","A"], ParseCigar(cigar, nucs))

    def testS(self):
        cigar = [(BAM_CSOFT_CLIP, 10), (BAM_CMATCH, 2)]
        nucs = "AA"
        self.assertEqual(["A","A"], ParseCigar(cigar, nucs))
    
    def testH(self):
        cigar = [(BAM_CHARD_CLIP, 10), (BAM_CMATCH, 2)]
        nucs = "AA"
        self.assertEqual(["A","A"], ParseCigar(cigar, nucs))

    def testX(self):
        cigar = [(BAM_CDIFF, 5)]
        nucs = "AAAAA"
        self.assertEqual(["A","A","A","A","A"], ParseCigar(cigar, nucs))

    def testEquals(self):
        cigar = [(BAM_CEQUAL, 5)]
        nucs = "AAAAA"
        self.assertEqual(["A","A","A","A","A"], ParseCigar(cigar, nucs))

    def testP(self):
        cigar = [(BAM_CMATCH, 4), (BAM_CPAD, 1), (BAM_CINS, 1), (BAM_CMATCH, 9)]
        nucs = "ATCAAGACCGATAC"
        self.assertEqual(["A","T","C","A",DELCHAR+"AG","A","C","C","G","A","T","A","C"], ParseCigar(cigar, nucs))

        cigar = [(BAM_CMATCH, 4), (BAM_CINS, 1), (BAM_CPAD, 1), (BAM_CMATCH, 9)]
        nucs = "ATCAAGACCGATAC"
        self.assertEqual(["A","T","C","A","A"+DELCHAR+"G","A","C","C","G","A","T","A","C"], ParseCigar(cigar, nucs))

        cigar = [(BAM_CMATCH, 4), (BAM_CINS, 2), (BAM_CPAD, 2), (BAM_CINS, 2), (BAM_CMATCH, 3)]
        nucs = "ATCAGGAGAGT"
        self.assertEqual(["A","T","C","A","GG"+DELCHAR*2+"AGA","G","T"], ParseCigar(cigar, nucs))

        cigar = [(BAM_CMATCH, 4), (BAM_CPAD, 2), (BAM_CINS, 2), (BAM_CPAD, 2), (BAM_CMATCH, 3)]
        nucs = "ATCAGGAGC"
        self.assertEqual(["A","T","C","A",DELCHAR*2 + "GG" + DELCHAR*2 + "A","G","C"], ParseCigar(cigar, nucs))

        cigar = [(BAM_CMATCH, 5), (BAM_CPAD, 2), (BAM_CMATCH, 5)]
        nucs = "GATCAGACCG"
        self.assertEqual(["G","A","T","C","A",DELCHAR*2 + "G","A","C","C","G"], ParseCigar(cigar, nucs))

        cigar = [(BAM_CMATCH, 2), (BAM_CPAD, 2), (BAM_CDEL, 2)]
        nucs = "GA"
        self.assertEqual(["G","A",DELCHAR*3,DELCHAR], ParseCigar(cigar, nucs))

    def testN(self):
        cigar = [(BAM_CMATCH, 2), (BAM_CREF_SKIP, 2), (BAM_CMATCH, 2)]
        nucs = "AAAA"
        self.assertEqual(["A","A",DELCHAR,DELCHAR,"A","A"], ParseCigar(cigar, nucs))

    def testComplicatedCigars(self):
        cigar = [(BAM_CMATCH, 5), (BAM_CINS, 2), (BAM_CDEL, 2), (BAM_CMATCH, 2), (BAM_CDEL, 2), (BAM_CINS, 2), (BAM_CMATCH, 3)]
        nucs = "ACGTGAAGGAAGTC"
        self.assertEqual(["A","C","G","T","G","AA"+DELCHAR,DELCHAR,"G","G",DELCHAR,DELCHAR,"AAG","T","C"], ParseCigar(cigar,nucs))

if __name__ == '__main__':
    unittest.main()
