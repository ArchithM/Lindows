"""
Linux Terminal for Windows
A terminal emulator that provides Linux command capabilities on Windows.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from terminal_core import LinuxTerminal

def main():
    terminal = LinuxTerminal()
    terminal.run()

if __name__ == '__main__':
    main()