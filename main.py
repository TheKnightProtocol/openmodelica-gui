#!/usr/bin/env python3
"""
OpenModelica Simulation Runner - Main Entry Point

This application provides a graphical user interface for running
OpenModelica simulations with configurable parameters.

Author: FOSSEE Screening Task
Version: 1.0.0
"""

import sys
import argparse
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import MainWindow
from utils.validators import InputValidator


def parse_arguments():
    """
    Parse command line arguments for the application.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="OpenModelica Simulation Runner - GUI Application"
    )
    parser.add_argument(
        "executable",
        nargs="?",
        help="Path to the OpenModelica compiled executable"
    )
    parser.add_argument(
        "start_time",
        nargs="?",
        type=int,
        help="Simulation start time (0 <= start < 5)"
    )
    parser.add_argument(
        "stop_time",
        nargs="?",
        type=int,
        help="Simulation stop time (start < stop < 5)"
    )
    
    return parser.parse_args()


def main():
    """
    Main application entry point.
    
    Initializes the Qt application, creates the main window,
    and starts the event loop.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("OpenModelica Simulation Runner")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FOSSEE")
    app.setOrganizationDomain("fossee.in")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    
    # Pre-populate fields if command line arguments provided
    if args.executable:
        window.set_executable_path(args.executable)
    if args.start_time is not None:
        window.set_start_time(args.start_time)
    if args.stop_time is not None:
        window.set_stop_time(args.stop_time)
    
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
