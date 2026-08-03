"""Adds tbot/code/lib to sys.path so every kb_tools script can `import okf`."""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_LIB = os.path.normpath(os.path.join(_HERE, "..", "lib"))
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
