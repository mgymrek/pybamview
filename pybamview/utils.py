# -*- coding: utf-8 -*-
import random
import sys


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
            x.append({"name": name, "region": region})
        line = f.readline()

    with open(targetfile, "r") as f:
        line = f.readline()

    return x
