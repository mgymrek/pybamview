from os.path import dirname, join

from pybamview.tests import __file__ as test_directory

def test_data(path):
    return join(dirname(test_directory), 'data', path)
