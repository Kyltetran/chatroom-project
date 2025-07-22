# client/setup_path.py

import sys
import os

# Add the project root (one level up from /client) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
