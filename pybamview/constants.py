# Global constants used by other files

import sys

PREFIX = "/usr/local/"
CSS_PREFIX = PREFIX + "/pybamview/css"
JS_PREFIX = PREFIX + "/pybamview/javascript"
NUMDISPLAY = 120 # how many characters to display at once
NUMCHAR = 500 # how many bp to load at once
ENDCHAR = "-"
GAPCHAR = "."
DELCHAR = "*"

NUC_TO_COLOR = {
    "A": "red",
    'a': "red",
    "C": "blue",
    "c": "blue",
    "G": "green",
    "g": "green",
    "T": "orange",
    "t": "orange",
    "-": "white"
}



