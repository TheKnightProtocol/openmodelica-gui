"""
GUI Package for OpenModelica Simulation Runner.

This package contains all graphical user interface components
for the OpenModelica simulation runner application.
"""

__version__ = "1.0.0"
__author__ = "FOSSEE Screening Task"

from .main_window import MainWindow
from .process_runner import ProcessRunner

__all__ = ["MainWindow", "ProcessRunner"]
