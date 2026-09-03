#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common.generic_listing import run

if __name__ == "__main__":
    run("airweb", int(sys.argv[1]) if len(sys.argv) > 1 else 4)

