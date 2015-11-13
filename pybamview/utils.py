# -*- coding: utf-8 -*-
import os
import random
import sys
from subprocess import Popen, PIPE, STDOUT

def message(msg, msgtype='progress'):
    """Send a message to console.

    Args:
        msgtype (str): one of 'progress', 'warning', 'error', or 'debug'
    """
    message = "[%(level)s]: %(text)s" % dict(level=msgtype.upper(), text=msg)
    sys.stderr.write(message.strip() + "\n")

    if msgtype == 'error':
        sys.exit(1)


def random_ports(port, n):
    """Generate a list of n random ports near the given port.

    The first 5 ports will be sequential, and the remaining n-5 will be
    randomly selected in the range [port-2*n, port+2*n].
    (copied from IPython notebookapp.py)
    """
    for i in range(min(5, n)):
        yield port + i

    for i in range(n-5):
        yield max(1, port + random.randint(-2*n, 2*n))


def ParseTargets(targetfile):
    """ Return list of targets, each is dict with region and name """
    x = []

    with open(targetfile, "r") as f:
        for line in f:
            items = line.strip().split("\t")
            if len(items) != 4:
                message("invalid target file. should have 4 columns", "error")
            chrom, start, end, name = items
            region = "%s:%s"%(chrom, start)
            x.append({"name": name, "region": region, "coords": (chrom, int(start), int(end))})
        line = f.readline()

    with open(targetfile, "r") as f:
        line = f.readline()

    return x

def WriteParamFile(paramfile, jspath, filetype, reference_track, samples, alignments_by_sample, fromindex, toindex):
    """
    Generate paramfile for creating snapshots from the command line
    """
    f = open(paramfile, "w")
    f.write('var exports = module.exports = {};\n')
    f.write('exports.reference_track = "%s";\n' % reference_track)
    f.write('exports.samples = %s;\n' % str(samples))
    f.write('exports.alignBySample = {\n')
    for sample in alignments_by_sample:
        f.write('"%s": "%s",\n' % (sample, alignments_by_sample[sample]))
    f.write('};\n')
    f.write('exports.fromindex = %s;\n' % fromindex)
    f.write('exports.toindex = %s;\n' % toindex)
    f.write('exports.jspath = "%s";\n' % jspath)
    if filetype in ["html","svg"]:
        f.write('exports.filetype = "%s";\n' % filetype)
    elif filetype == "pdf":
        f.write('exports.filetype = "svg";\n')
    else:
        f.write('exports.filetype = "none";\n')
    f.close()

def RunCommand(cmd):
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, \
                  stderr=STDOUT, close_fds=True)
    ex = p.wait()
    if ex != 0:
        stdout, stderr = "", ""
        if p.stdout is not None: stdout = p.stdout.read()
        if p.stderr is not None: stderr = p.stderr.read()
        message("ERROR: command '%s' failed.\n\nSTDOUT:%s\nSTDERR:%s"%(cmd, stdout, stderr))
    return ex

def CheckProgram(program):
    """ Check whether a program is installed """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    for path in os.environ["PATH"].split(os.pathsep):
        path = path.strip('"')
        exe_file = os.path.join(path, program)
        if is_exe(exe_file): return True
    return False

def CheckNodeJSPackage(package):
    """ Check whether a node.js package is installed """
    cmd = "node -e \"var d3=require('%s');\"" % package
    x = RunCommand(cmd)
    return x == 0
