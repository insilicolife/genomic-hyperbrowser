import sys

from proto.hyperbrowser.preprocesstracks import *

control = getController(None, sys.argv[1])
control.execute()

