import os
import sys

# Add parent of ai_service to sys.path so that ai_service module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
