#!/usr/bin/env python3
## file that loads and runs the CPU
"""Main."""

import sys
from cpu import *

cpu = CPU()

cpu.load()
cpu.run()