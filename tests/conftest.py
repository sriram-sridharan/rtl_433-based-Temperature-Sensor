import os
import sys
import io

# Change cwd to this directory before test modules are imported, so that `temp_simplified.py`'s module-level load_config('config.ini') finds tests/config.ini.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Replace stdin with an empty buffer so the module-level stdin loop exits immediately on import.
sys.stdin = io.StringIO()
