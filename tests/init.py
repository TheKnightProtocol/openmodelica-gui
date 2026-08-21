"""
Test Package for OpenModelica Simulation Runner.

This package contains all unit tests for the application.
"""

import sys
from pathlib import Path

# Add project root to Python path for test imports
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
