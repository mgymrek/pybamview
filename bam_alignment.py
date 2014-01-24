"""
Module for storing bam alignment info
"""

import pysam
import pyfasta

class AlignmentGrid(object):
    """
    Class for storing a grid of alignments
    """
    def __init__(self, _bamreader, _ref, _chrom, _pos, _settings={}):
        self.bamreader = _bamreader
        self.ref = _ref
        self.chrom = _chrom
        self.pos = _pos
        self.settings = _settings
        self.LoadGrid()

    def LoadGrid(self):
        """
        Load grid of alingments with buffer around start pos
        """
        pass # TODO

    def GetReferenceTrack(self, _pos):
        """
        Return string for the reference track
        """
        return "***********ACACTAGCTAGCTACTAGTCGATCGATCGACTATCGATCGATCGATCGTACG******" # TODO

    def GetAlignmentTrack(self, _pos):
        """
        Return list of strings for the alignment track
        """
        return ["***********ACACTAGCTAGCTACTAGTCGATCGATCGACTATCGATCGATCGATCGTACG******",\
                    "*********ACACACTAGCTAGCTACTAGTCGATCGATCGACTATCGATCGATCGATCGTACG******"] # TODO

    def __str__(self):
        return "[AlignmentGrid: %s:%s]"%(self.chrom, self.pos)

class BamView(object):
    """
    Class for storing view of Bam Alignments
    """
    def __init__(self, _bamfile, _reffile):
        self.bamfile = _bamfile
        self.bamreader = pysam.Samfile(_bamfile, "rb")
        self.reference = pyfasta.Fasta(_reffile)
        self.alignment_grid = None

    def LoadAlignmentGrid(self, _chrom, _pos, _settings={}):
        """
        Load an alignment grid for a view at a specific chr:pos
        """
        self.alignment_grid = AlignmentGrid(self.bamreader, self.reference, _chrom, _pos, _settings=_settings)

    def GetReferenceTrack(self, start_pos):
        """
        Return string for the reference track
        """
        return self.alignment_grid.GetReferenceTrack(start_pos)

    def GetAlignmentTrack(self, start_pos):
        """
        Return list of strings for the alignment tracks
        """
        return self.alignment_grid.GetAlignmentTrack(start_pos)

    def __str__(self):
        return "[BamView: %s]"%self.bamfile
