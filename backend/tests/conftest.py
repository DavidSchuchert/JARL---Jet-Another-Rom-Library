"""Pytest configuration and shared fixtures."""
import sys
from pathlib import Path

# Ensure the app module is importable
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))
