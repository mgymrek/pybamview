"""
Module for storing bam alignment info
"""
import pandas as pd
import pysam
import pyfasta

NUMCHAR = 100
GAPCHAR = "."
DELCHAR = "*"
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
        self.grid = None
        self.LoadGrid()

    def LoadGrid(self):
        """
        Load grid of alingments with buffer around start pos
        """
        # Get reference
        chromlen = len(self.ref[self.chrom])
        if chromlen <= self.pos:
            self.grid = None
            return
        elif chromlen <= self.pos+NUMCHAR:
            reference = self.ref[self.chrom][self.pos:]
        else: reference = self.ref[self.chrom][self.pos:self.pos+NUMCHAR]
        reference = [reference[i] for i in range(len(reference))]
        griddict = {"position": range(self.pos, self.pos+NUMCHAR), "reference": reference}
        # Get reads
        region=str("%s:%s-%s"%(self.chrom, int(self.pos), int(self.pos+NUMCHAR)))
        aligned_reads = self.bamreader.fetch(region=region)
        readindex = 0
        read_properties = []
        for read in aligned_reads:
            # get reference position
            position = read.pos
            # get nucleotides
            nucs = read.query
            # get CIGAR
            cigar = read.cigar
            # get strand
            strand = not read.is_reverse
            # get sample - TODO
            read_properties.append({"pos": position})
            # get representation
            rep = []
            currentpos = 0
            for c in cigar:
                if c[0] == 0: # match
                    for i in range(c[1]):
                        rep.append(nucs[currentpos])
                        currentpos += 1
                elif c[0] == 1: # put insertion in next base position
                    rep.append(nucs[currentpos:currentpos+c[1]])
                    currentpos = currentpos+c[1]
                elif c[0] == 2: # deletion
                    for i in range(c[1]):
                        rep.append(DELCHAR)
            # Fix boundaries
            if position < self.pos:
                rep = rep[self.pos-position:]
            else:
                for i in range(position-self.pos): rep = [GAPCHAR] + rep
            if len(rep) > len(reference):
                rep = rep[0:len(reference)]
            rep.extend(GAPCHAR*(len(reference)-len(rep)))
            # Check if reverse
            if not strand:
                rep = map(str.lower, rep)
            # Put in dictionary
            griddict["aln%s"%readindex] = rep
            readindex += 1
        self.grid = pd.DataFrame(griddict)
        # Fix insertions
        alncols = [item for item in self.grid.columns if item != "position"]
        for i in range(self.grid.shape[0]):
            maxchars = max(self.grid.ix[i,alncols].apply(len))
            if maxchars > 1:
                for col in alncols:
                    val = self.grid.ix[i, col]
                    if len(val) < maxchars: self.grid.ix[i,col] = GAPCHAR*(maxchars-len(val)+1) + val
        # Sort columns appropriately
        readprops = pd.DataFrame({"read": ["aln%s"%i for i in range(readindex)], "pos": [read_properties[i]["pos"] for i in range(readindex)]})
        if self.settings.get("SORT","bypos") == "bypos":
            readprops = readprops.sort("pos")
            self.grid = self.grid[["position","reference"] + list(readprops["read"].values)]
            self.CollapseGridByPosition()

    def MergeRows(self, row1, row2):
        x = []
        for i in range(len(row1)):
            if row1[i][0] == GAPCHAR and row2[i][0] == GAPCHAR:
                x.append(row1[i])
            elif row1[i] == GAPCHAR:
                x.append(row2[i])
            else: x.append(row1[i])
        return x
                
    def CollapseGridByPosition(self):
        """
        If more than one read can fit on the same line, put it there
        """
        cols_to_delete = []
        col_to_ends = {"dummy":{"end":1000000, "rank":-1}}
        alncols = [item for item in self.grid.columns if item != "position" and item != "reference"]
        for col in alncols:
            track = self.grid.ix[:,col].values
            x = [i for i in range(len(track)) if track[i][0] != GAPCHAR]
            start = min(x)
            end = max(x)
            if start > min([item["end"] for item in col_to_ends.values()]):
                mincol = [(col_to_ends[k]["rank"], k) for k in col_to_ends.keys() if col_to_ends[k]["end"] < start]
                mincol.sort()
                mincol = mincol[0][1]
                self.grid[mincol] = self.MergeRows(list(self.grid[mincol].values), list(self.grid[col].values))
                cols_to_delete.append(col)
                t = self.grid.ix[:,mincol].values
                y = [i for i in range(len(t)) if t[i] != GAPCHAR]
                col_to_ends[mincol]["end"] = max(y)
            col_to_ends[col] = {"end": end, "rank": alncols.index(col)}
        self.grid = self.grid.drop(cols_to_delete, 1)
            
    def GetReferenceTrack(self, _pos):
        """
        Return string for the reference track
        """
        if self.grid is None: return "N"*NUMCHAR
        refseries = self.grid.reference.values
        reference = ""
        for i in range(len(refseries)):
            reference = reference + refseries[i]
        return reference.upper()

    def GetAlignmentTrack(self, _pos):
        """
        Return list of strings for the alignment track
        """
        alncols = [item for item in self.grid.columns if item != "reference" and item != "position"]
        alignments = []
        for col in alncols:
            alignments.append("".join(self.grid[col].values))
        return alignments

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
