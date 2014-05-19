"""
The MIT License (MIT)

Copyright (c) 2014 Melissa Gymrek <mgymrek@mit.edu>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from itertools import chain
import sys

import pandas as pd
import pysam
import pyfasta

from .constants import ENDCHAR, GAPCHAR, DELCHAR
from .constants import BAM_CMATCH, BAM_CINS, BAM_CDEL, BAM_CREF_SKIP,\
    BAM_CSOFT_CLIP, BAM_CHARD_CLIP, BAM_CPAD, BAM_CEQUAL, BAM_CDIFF

def GetSamplesFromBamFiles(bamfiles):
    """ Return dictionary of sample -> list of bam files """
    samplesToBam = {}
    for bam in bamfiles:
        try:
            br = pysam.Samfile(bam, "rb")
        except:
            sys.stderr.write("ERROR: Could not open %s. Is this a valid bam file?\n"%bam)
            continue
        for r in br.header.get("RG", []):
            ident = r["ID"]
            sample = r.get("SM", ident)
            if bam not in samplesToBam.get(sample, []):
                samplesToBam[sample] = samplesToBam.get(sample, []) + [bam]
    return samplesToBam

def ParseCigar(cigar, nucs):
    """
    Return list of strings, each item corresponding to a single reference position
    """
    rep = []
    currentpos = 0
    wasinsert = False
    for c in cigar:
        if c[0] in [BAM_CMATCH, BAM_CEQUAL, BAM_CDIFF]: # match (M, X, =)
            for i in range(c[1]):
                if wasinsert:
                    rep[-1] = rep[-1] + nucs[currentpos]
                else: rep.append(nucs[currentpos])
                wasinsert = False
                currentpos += 1
        elif c[0] == BAM_CINS: # put insertion in next base position (I)
            if wasinsert:
                rep[-1] = rep[-1] + nucs[currentpos:currentpos+c[1]]
            else:
                rep.append(nucs[currentpos:currentpos+c[1]])
            currentpos = currentpos+c[1]
            wasinsert = True
        elif c[0] in [BAM_CDEL, BAM_CREF_SKIP]: # deletion (D) or skipped region from the reference (N)
            for i in range(c[1]):
                if wasinsert:
                    rep[-1] = rep[-1] + DELCHAR
                else: rep.append(DELCHAR)
                wasinsert = False
        elif c[0] in [BAM_CSOFT_CLIP, BAM_CHARD_CLIP]: # hard clipping or soft clipping
            pass # do nothing
        elif c[0] == 6: # padding (silent deletion from padded reference) (P)
            if wasinsert:
                rep[-1] = rep[-1] + DELCHAR*c[1]
            else: rep.append(DELCHAR*c[1])
            wasinsert = True
        else:
            sys.stderr.write("ERROR: Invalid CIGAR operation (%s) in read %s \n"%(c[0], read.qname))
    return rep

class AlignmentGrid(object):
    """
    Class for storing a grid of alignments
    """
    def __init__(self, _bamreaders, _read_groups, _ref, _chrom, _pos, _samples=[], _settings={}):
        self.bamreaders = _bamreaders
        self.read_groups = _read_groups
        self.ref = _ref
        self.chrom = _chrom
        self.startpos = _pos
        self.settings = _settings
        self.pos = self.startpos-int(self.settings["NUMCHAR"]*0.5)
        if self.pos < 0: self.pos = 0
        self.samples = set(
            chain.from_iterable(rg.itervalues() for rg in _read_groups))
        for item in _samples:
            if item not in self.samples: sys.stderr.write("WARNING: %s not in BAM\n"%item)
        if len(_samples) > 0:
            self.samples = [item for item in _samples if item in self.samples]
        self.grid_by_sample = dict([(sample, {}) for sample in self.samples])
        self.LoadGrid()

    def LoadGrid(self):
        """
        Load grid of alignments with buffer around start pos
        """
        # Get reference
        if self.ref is None or self.chrom not in self.ref.keys():
            reference = ["N"]*self.settings["NUMCHAR"]
        else:
            chromlen = len(self.ref[self.chrom])
            if chromlen <= self.pos:
                return
            elif chromlen <= self.pos+self.settings["NUMCHAR"]:
                reference = self.ref[self.chrom][self.pos:]
            else: reference = self.ref[self.chrom][self.pos:self.pos+self.settings["NUMCHAR"]]
            reference = [reference[i] for i in range(len(reference))]
        griddict = {"position": range(self.pos, self.pos+len(reference)), "reference": reference}
        # Get reads
        region=str("%s:%s-%s"%(self.chrom, max(1, int(self.pos)), int(self.pos+self.settings["NUMCHAR"])))
        aligned_reads = []
        for bi, br in enumerate(self.bamreaders):
            try:
                aligned_reads.extend((bi, read) for read in
                                     br.fetch(region=region))
            except: pass
        readindex = 0
        read_properties = []
        for bamindex, read in aligned_reads:
            # get reference position
            position = read.pos
            # get nucleotides
            nucs = read.query
            # get CIGAR
            cigar = read.cigar
            # get strand
            strand = not read.is_reverse
            # get sample
            rg = self.read_groups[bamindex].get(
                dict(read.tags).get("RG",""),"")
            read_properties.append({"pos": position,"sample":rg})
            # get representation
            if cigar is None:
                sys.stderr.write("WARNING: read %s has no CIGAR string. It will not be displayed.\n"%read.qname)
                continue
            rep = ParseCigar(cigar, nucs)
            # Fix boundaries
            if position < self.pos:
                rep = rep[self.pos-position:]
            else:
                for i in range(position-self.pos): rep = [ENDCHAR] + rep
            if len(rep) > len(reference):
                rep = rep[0:len(reference)]
            rep.extend(ENDCHAR*(len(reference)-len(rep)))
            # Check if reverse
            if not strand:
                rep = map(str.lower, rep)
            # Put in dictionary
            griddict["aln%s"%readindex] = rep
            readindex += 1
        grid = pd.DataFrame(griddict)
        # Fix insertions
        alncols = [item for item in grid.columns if item != "position"]
        for i in range(grid.shape[0]):
            maxchars = max(grid.ix[i,alncols].apply(len))
            if maxchars > 1:
                for col in alncols:
                    val = grid.ix[i, col]
                    if len(val) < maxchars: grid.ix[i,col] = GAPCHAR*(maxchars-len(val)) + val
        readprops = pd.DataFrame({"read": ["aln%s"%i for i in range(readindex)], "pos": [read_properties[i]["pos"] for i in range(readindex)],\
                                     "sample": [read_properties[i]["sample"] for i in range(readindex)]})
        # Split by sample
        for sample in self.samples:
            if readprops.shape[0] > 0:
                self.grid_by_sample[sample] = grid[["position","reference"] + list(readprops[readprops["sample"]==sample]["read"].values)]
            else: self.grid_by_sample[sample] = grid[["position","reference"]]
        # Sort columns appropriately
        if self.settings.get("SORT","bypos") == "bypos":
            readprops = readprops.sort("pos")
            if readprops.shape[0] > 0:
                for sample in self.samples:
                    self.grid_by_sample[sample] = \
                        self.CollapseGridByPosition(self.grid_by_sample[sample][["position","reference"] + list(readprops[readprops["sample"]==sample]["read"].values)])
                    pass
            else: pass

    def MergeRows(self, row1, row2):
        x = []
        for i in range(len(row1)):
            if row1[i][0] == ENDCHAR and row2[i][0] == ENDCHAR:
                x.append(row1[i])
            elif row1[i][0] == ENDCHAR or row1[i][-1] == ENDCHAR:
                x.append(row2[i])
            else: x.append(row1[i])
        return x
                
    def CollapseGridByPosition(self, grid):
        """
        If more than one read can fit on the same line, put it there
        """
        cols_to_delete = []
        col_to_ends = {"dummy":{"end":1000000, "rank":-1}}
        alncols = [item for item in grid.columns if item != "position" and item != "reference"]
        for col in alncols:
            track = grid.ix[:,col].values
            x = [i for i in range(len(track)) if track[i][0] != ENDCHAR and track[i][0] != GAPCHAR]
            if len(x) == 0:
                start = 0
                end = 0
            else:
                start = min(x)
                end = max(x)
            if start > min([item["end"] for item in col_to_ends.values()]):
                mincol = [(col_to_ends[k]["rank"], k) for k in col_to_ends.keys() if col_to_ends[k]["end"] < start]
                mincol.sort()
                mincol = mincol[0][1]
                grid[mincol] = self.MergeRows(list(grid[mincol].values), list(grid[col].values))
                cols_to_delete.append(col)
                t = grid.ix[:,mincol].values
                y = [i for i in range(len(t)) if t[i][0] != ENDCHAR and t[i][0] != GAPCHAR]
                col_to_ends[mincol]["end"] = max(y)
            col_to_ends[col] = {"end": end, "rank": alncols.index(col)}
        return grid.drop(cols_to_delete, 1)
            
    def GetReferenceTrack(self, _pos):
        """
        Return string for the reference track
        """
        if len(self.grid_by_sample.keys()) == 0: return "N"*self.settings["NUMCHAR"]
        refseries = self.grid_by_sample.values()[0].reference.values
        reference = ""
        for i in range(len(refseries)):
            reference = reference + refseries[i]
        return reference.upper()

    def GetPositions(self, _pos):
        positions = []
        if len(self.grid_by_sample.keys()) == 0: return range(self.pos, self.pos+self.settings["NUMCHAR"])
        refseries = self.grid_by_sample.values()[0].reference.values
        for i in range(len(refseries)):
            positions.extend([self.pos+i]*len(refseries[i]))
        return positions

    def GetAlignmentTrack(self, _pos):
        """
        Return list of strings for the alignment track
        """
        alignments_by_sample = {}
        for sample in self.grid_by_sample:
            grid = self.grid_by_sample[sample]
            alncols = [item for item in grid.columns if item != "reference" and item != "position"]
            alignments = []
            for col in alncols:
                alignments.append("".join(grid[col].values))
            alignments_by_sample[sample] = alignments
        return alignments_by_sample

    def __str__(self):
        return "[AlignmentGrid: %s:%s]"%(self.chrom, self.pos)

class BamView(object):
    """
    Class for storing view of Bam Alignments
    """
    def __init__(self, _bamfiles, _reffile):
        self.bamfiles = _bamfiles
        self.bamreaders = []
        for bam in self.bamfiles:
            try:
                br = pysam.Samfile(bam, "rb")
                self.bamreaders.append(br)
            except:
                sys.stderr.write("ERROR: could not open %s. Is this a valid bam file?\n"%bam)
        if _reffile != "":
            try:
                self.reference = pyfasta.Fasta(_reffile)
            except:
                self.reference = None
        else: self.reference = None
        self.alignment_grid = None
        self.read_groups = self.LoadRGDictionary()

    def samples(self):
        return set(
            chain.from_iterable(rg.itervalues() for rg in self.read_groups))

    def LoadRGDictionary(self):
        return [
            {r["ID"]: r.get("SM", r["ID"]) for r in br.header.get("RG", [])}
            for br in self.bamreaders]

    def GetPositions(self, start_pos):
        """
        Get vector of positions for columns
        """
        return self.alignment_grid.GetPositions(start_pos)

    def LoadAlignmentGrid(self, _chrom, _pos, _samples=[], _settings={}):
        """
        Load an alignment grid for a view at a specific chr:pos
        """
        reload = True
        if self.alignment_grid is not None:
            if (self.alignment_grid.chrom == _chrom) and (self.alignment_grid.startpos >= (_pos-5)) and (self.alignment_grid.startpos <= (_pos+5)):
                reload = False
        if reload:
            self.alignment_grid = AlignmentGrid(self.bamreaders, self.read_groups, self.reference, \
                                                    _chrom, _pos, _samples=_samples, _settings=_settings)

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
