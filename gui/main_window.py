"""
Main Window Implementation for OpenModelica Simulation Runner.

This module provides the main graphical user interface window
with input fields for executable selection and time parameters.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QSpinBox,
    QMessageBox, QGroupBox, QTextEdit, QProgressBar, QFrame,
    QSizePolicy, QSpacerItem, QApplication
)
from PyQt6.QtCore import Qt, QProcess, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QTextCursor

from .process_runner import ProcessRunner
from utils.validators import InputValidator


class MainWindow(QMainWindow):
    """
    Main application window for the OpenModelica Simulation Runner.
    
    This class provides a user-friendly interface for:
    - Selecting OpenModelica compiled executables
    - Setting simulation start and stop times
    - Running simulations with real-time output display
    - Comprehensive input validation and error handling
    
    Attributes:
        process_runner (Optional[ProcessRunner]): Manages simulation process
        validator (InputValidator): Validates user inputs
    """
    
    # Define constants
    WINDOW_TITLE = "OpenModelica Simulation Runner"
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    MIN_WIDTH = 650
    MIN_HEIGHT = 500
    
    # Time constraints
    MIN_START_TIME = 0
    MAX_START_TIME = 4
    MIN_STOP_TIME = 1
    MAX_STOP_TIME = 5
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the main window and setup the user interface.
        
        Args:
            parent (Optional[QWidget]): Parent widget, defaults to None
        """
        super().__init__(parent)
        
        # Initialize components
        self.process_runner: Optional[ProcessRunner] = None
        self.validator = InputValidator()
        self.simulation_running = False
        
        # Setup UI
        self._init_ui()
        self._apply_styles()
        self._setup_connections()
        
        # Log initialization
        self._append_output("OpenModelica Simulation Runner initialized.\n")
        self._append_output("Please select an executable and set time parameters.\n")
        
    def _init_ui(self):
        """Initialize all user interface components."""
        # Window properties
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setGeometry(100, 100, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 20)
        
        # Header section
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # Input section
        input_group = self._create_input_section()
        main_layout.addWidget(input_group)
        
        # Control buttons
        button_layout = self._create_control_buttons()
        main_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        main_layout.addWidget(self.progress_bar)
        
        # Output section
        output_group = self._create_output_section()
        main_layout.addWidget(output_group, stretch=1)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def _create_header(self) -> QVBoxLayout:
        """
        Create the header section with title and description.
        
        Returns:
            QVBoxLayout: Header layout
        """
        header_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("OpenModelica Simulation Control Panel")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel(
            "Run and control OpenModelica simulations with ease"
        )
        subtitle_font = QFont("Segoe UI", 10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #666;")
        header_layout.addWidget(subtitle_label)
        
        return header_layout
        
    def _create_input_section(self) -> QGroupBox:
        """
        Create the input parameters section.
        
        Returns:
            QGroupBox: Input section group box
        """
        input_group = QGroupBox("Simulation Parameters")
        input_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        
        # Layout for input section
        input_layout = QGridLayout(input_group)
        input_layout.setSpacing(15)
        input_layout.setContentsMargins(20, 20, 20, 20)
        
        # Executable path
        exec_label = QLabel("Executable:")
        exec_label.setFont(QFont("Segoe UI", 10))
        exec_label.setToolTip("Select the compiled OpenModelica executable")
        
        self.exec_path_input = QLineEdit()
        self.exec_path_input.setPlaceholderText(
            "Click Browse to select OpenModelica executable..."
        )
        self.exec_path_input.setReadOnly(True)
        self.exec_path_input.setMinimumHeight(35)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.setFixedSize(100, 35)
        self.browse_button.setToolTip("Browse for executable file")
        
        # Start time
        start_label = QLabel("Start Time:")
        start_label.setFont(QFont("Segoe UI", 10))
        start_label.setToolTip("Simulation start time in seconds")
        
        self.start_time_input = QSpinBox()
        self.start_time_input.setRange(self.MIN_START_TIME, self.MAX_START_TIME)
        self.start_time_input.setValue(0)
        self.start_time_input.setSuffix(" s")
        self.start_time_input.setMinimumHeight(35)
        self.start_time_input.setToolTip(
            f"Start time ({self.MIN_START_TIME} to {self.MAX_START_TIME} seconds)"
        )
        
        # Stop time
        stop_label = QLabel("Stop Time:")
        stop_label.setFont(QFont("Segoe UI", 10))
        stop_label.setToolTip("Simulation stop time in seconds")
        
        self.stop_time_input = QSpinBox()
        self.stop_time_input.setRange(self.MIN_STOP_TIME, self.MAX_STOP_TIME)
        self.stop_time_input.setValue(1)
        self.stop_time_input.setSuffix(" s")
        self.stop_time_input.setMinimumHeight(35)
        self.stop_time_input.setToolTip(
            f"Stop time ({self.MIN_STOP_TIME} to {self.MAX_STOP_TIME} seconds)"
        )
        
        # Time range info
        time_range_label = QLabel(
            f"Valid range: {self.MIN_START_TIME} ≤ start < stop ≤ {self.MAX_STOP_TIME}"
        )
        time_range_label.setFont(QFont("Segoe UI", 8))
        time_range_label.setStyleSheet("color: #666; font-style: italic;")
        
        # Add widgets to grid layout
        input_layout.addWidget(exec_label, 0, 0)
        input_layout.addWidget(self.exec_path_input, 0, 1, 1, 2)
        input_layout.addWidget(self.browse_button, 0, 3)
        
        input_layout.addWidget(start_label, 1, 0)
        input_layout.addWidget(self.start_time_input, 1, 1)
        input_layout.addWidget(stop_label, 1, 2)
        input_layout.addWidget(self.stop_time_input, 1, 3)
        
        input_layout.addWidget(time_range_label, 2, 1, 1, 3)
        
        # Set column stretch
        input_layout.setColumnStretch(1, 1)
        input_layout.setColumnStretch(2, 1)
        
        return input_group
        
    def _create_control_buttons(self) -> QHBoxLayout:
        """
        Create the control buttons section.
        
        Returns:
            QHBoxLayout: Control buttons layout
        """
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Run button
        self.run_button = QPushButton("▶  Run Simulation")
        self.run_button.setFixedHeight(45)
        self.run_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.run_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Fixed
        )
        
        # Clear button
        self.clear_button = QPushButton("Clear Output")
        self.clear_button.setFixedSize(120, 45)
        self.clear_button.setFont(QFont("Segoe UI", 10))
        
        # Add to layout
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.clear_button)
        
        return button_layout
        
    def _create_output_section(self) -> QGroupBox:
        """
        Create the output display section.
        
        Returns:
            QGroupBox: Output section group box
        """
        output_group = QGroupBox("Simulation Output")
        output_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        
        # Layout for output section
        output_layout = QVBoxLayout(output_group)
        output_layout.setContentsMargins(10, 15, 10, 10)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 9))
        self.output_text.setMinimumHeight(150)
        self.output_text.setPlaceholderText(
            "Simulation output will appear here..."
        )
        
        # Add to layout
        output_layout.addWidget(self.output_text)
        
        return output_group
        
    def _setup_connections(self):
        """Setup signal-slot connections."""
        # Button connections
        self.browse_button.clicked.connect(self._browse_executable)
        self.run_button.clicked.connect(self._run_simulation)
        self.clear_button.clicked.connect(self._clear_output)
        
        # Time input connections
        self.start_time_input.valueChanged.connect(self._validate_time_range)
        self.stop_time_input.valueChanged.connect(self._validate_time_range)
        
    def _apply_styles(self):
        """Apply custom styles to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #495057;
            }
            
            QPushButton {
                border: none;
                border-radius: 6px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            
            QPushButton#run_button {
                background-color: #28a745;
                color: white;
                padding: 10px 20px;
            }
            
            QPushButton#run_button:hover {
                background-color: #218838;
            }
            
            QPushButton#run_button:pressed {
                background-color: #1e7e34;
            }
            
            QPushButton#run_button:disabled {
                background-color: #6c757d;
                color: #dee2e6;
            }
            
            QPushButton#browse_button {
                background-color: #007bff;
                color: white;
                padding: 5px 15px;
            }
            
            QPushButton#browse_button:hover {
                background-color: #0056b3;
            }
            
            QPushButton#browse_button:pressed {
                background-color: #004085;
            }
            
            QPushButton#clear_button {
                background-color: #6c757d;
                color: white;
            }
            
            QPushButton#clear_button:hover {
                background-color: #5a6268;
            }
            
            QLineEdit, QSpinBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                font-size: 11px;
            }
            
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #007bff;
                background-color: #f8f9fa;
            }
            
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #f8f9fa;
                padding: 8px;
            }
            
            QProgressBar {
                border: none;
                background-color: #e9ecef;
                border-radius: 2px;
            }
            
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 2px;
            }
            
            QStatusBar {
                background-color: #f8f9fa;
                color: #495057;
            }
            
            QToolTip {
                background-color: #495057;
                color: white;
                border: 1px solid #343a40;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        
        # Set object names for specific styling
        self.run_button.setObjectName("run_button")
        self.browse_button.setObjectName("browse_button")
        self.clear_button.setObjectName("clear_button")
        
    def _browse_executable(self):
        """Open file dialog to select executable."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select OpenModelica Executable")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        # Set file filters
        if sys.platform == "win32":
            file_dialog.setNameFilter("Executable Files (*.exe);;All Files (*)")
        else:
            file_dialog.setNameFilter("Executable Files (*);;All Files (*)")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                executable_path = selected_files[0]
                self.exec_path_input.setText(executable_path)
                self._append_output(f"Selected executable: {executable_path}\n")
                self.statusBar().showMessage(
                    f"Selected: {os.path.basename(executable_path)}"
                )
                
    def _validate_time_range(self):
        """
        Validate time range and update UI accordingly.
        
        Ensures: 0 <= start < stop < 5
        """
        start_time = self.start_time_input.value()
        stop_time = self.stop_time_input.value()
        
        valid = self.validator.validate_time_range(start_time, stop_time)
        
        # Update run button state
        self.run_button.setEnabled(valid)
        
        # Update status bar
        if not valid:
            self.statusBar().showMessage(
                "Invalid time range: Must satisfy 0 ≤ start < stop < 5",
                3000
            )
        else:
            self.statusBar().showMessage(
                f"Time range: {start_time}s to {stop_time}s"
            )
            
        return valid
        
    def _run_simulation(self):
        """Execute the simulation with current parameters."""
        if self.simulation_running:
            return
            
        # Get input values
        executable_path = self.exec_path_input.text().strip()
        start_time = self.start_time_input.value()
        stop_time = self.stop_time_input.value()
        
        # Validate executable path
        if not executable_path:
            self._show_error(
                "No Executable Selected",
                "Please select an OpenModelica executable file."
            )
            return
            
        if not os.path.exists(executable_path):
            self._show_error(
                "Executable Not Found",
                f"The selected file does not exist:\n{executable_path}"
            )
            return
            
        # Validate time range
        if not self.validator.validate_time_range(start_time, stop_time):
            self._show_error(
                "Invalid Time Range",
                "Time range must satisfy: 0 ≤ start < stop < 5"
            )
            return
            
        # Prepare UI for simulation
        self._set_simulation_state(True)
        
        # Log simulation start
        self._append_output("=" * 60 + "\n")
        self._append_output("Starting simulation...\n")
        self._append_output(f"Executable: {os.path.basename(executable_path)}\n")
        self._append_output(f"Time range: {start_time}s to {stop_time}s\n")
        self._append_output("=" * 60 + "\n\n")
        
        # Create process runner
        self.process_runner = ProcessRunner(
            executable_path,
            start_time,
            stop_time
        )
        
        # Connect signals
        self.process_runner.output_received.connect(self._append_output)
        self.process_runner.process_finished.connect(self._on_simulation_finished)
        self.process_runner.process_error.connect(self._on_simulation_error)
        
        # Start simulation
        self.process_runner.start()
        
    def _set_simulation_state(self, running: bool):
        """
        Update UI elements based on simulation state.
        
        Args:
            running (bool): True if simulation is running
        """
        self.simulation_running = running
        
        # Disable inputs during simulation
        self.exec_path_input.setEnabled(not running)
        self.browse_button.setEnabled(not running)
        self.start_time_input.setEnabled(not running)
        self.stop_time_input.setEnabled(not running)
        self.clear_button.setEnabled(not running)
        
        # Update run button
        self.run_button.setEnabled(not running)
        self.run_button.setText("⏳ Running..." if running else "▶  Run Simulation")
        
        # Show/hide progress bar
        self.progress_bar.setVisible(running)
        
        # Update status bar
        if running:
            self.statusBar().showMessage("Simulation running...")
            
    def _on_simulation_finished(self, exit_code: int):
        """
        Handle simulation completion.
        
        Args:
            exit_code (int): Process exit code
        """
        self._set_simulation_state(False)
        
        if exit_code == 0:
            self._append_output("\n" + "=" * 60 + "\n")
            self._append_output("✓ Simulation completed successfully!\n")
            self._append_output("=" * 60 + "\n")
            self.statusBar().showMessage("Simulation completed successfully", 5000)
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                "Simulation completed successfully!\n\n"
                "Check the output below for results.",
                QMessageBox.StandardButton.Ok
            )
        else:
            self._append_output("\n" + "=" * 60 + "\n")
            self._append_output(f"✗ Simulation failed with exit code: {exit_code}\n")
            self._append_output("=" * 60 + "\n")
            self.statusBar().showMessage("Simulation failed", 5000)
            
            # Show error message
            QMessageBox.warning(
                self,
                "Simulation Failed",
                f"The simulation failed with exit code: {exit_code}\n\n"
                "Check the output for error details.",
                QMessageBox.StandardButton.Ok
            )
            
    def _on_simulation_error(self, error_message: str):
        """
        Handle simulation errors.
        
        Args:
            error_message (str): Error description
        """
        self._set_simulation_state(False)
        
        self._append_output(f"\n✗ Error: {error_message}\n")
        self.statusBar().showMessage("Simulation error", 5000)
        
        self._show_error(
            "Simulation Error",
            f"Failed to run simulation:\n{error_message}"
        )
        
    def _append_output(self, text: str):
        """
        Append text to output display.
        
        Args:
            text (str): Text to append
        """
        self.output_text.moveCursor(QTextCursor.MoveOperation.End)
        self.output_text.insertPlainText(text)
        self.output_text.moveCursor(QTextCursor.MoveOperation.End)
        
    def _clear_output(self):
        """Clear the output display."""
        self.output_text.clear()
        self._append_output("Output cleared.\n")
        
    def _show_error(self, title: str, message: str):
        """
        Show error message box.
        
        Args:
            title (str): Error title
            message (str): Error message
        """
        QMessageBox.critical(
            self,
            title,
            message,
            QMessageBox.StandardButton.Ok
        )
        
    def set_executable_path(self, path: str):
        """
        Set executable path (used for command line arguments).
        
        Args:
            path (str): Path to executable
        """
        self.exec_path_input.setText(path)
        
    def set_start_time(self, time: int):
        """
        Set start time (used for command line arguments).
        
        Args:
            time (int): Start time
        """
        self.start_time_input.setValue(time)
        
    def set_stop_time(self, time: int):
        """
        Set stop time (used for command line arguments).
        
        Args:
            time (int): Stop time
        """
        self.stop_time_input.setValue(time)
        
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        if self.simulation_running:
            # Ask for confirmation if simulation is running
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "A simulation is currently running.\n"
                "Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Terminate running process
                if self.process_runner:
                    self.process_runner.terminate()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
