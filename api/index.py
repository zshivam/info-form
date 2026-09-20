import sys
import os

# Add backend folder to sys.path so all backend modules (database, models, etc.) can be loaded
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app
