"""
Process Runner for OpenModelica Simulation.

This module manages the execution of OpenModelica compiled executables
with proper argument passing and signal handling.
"""

from PyQt6.QtCore import QProcess, QObject, pyqtSignal, pyqtSlot
from typing import Optional, List
import os
import sys


class ProcessRunner(QObject):
    """
    Manages the execution of external simulation processes.
    
    This class handles:
    - Process creation and management
    - Standard output/error reading
    - Signal emission for output and completion
    - Proper argument formatting for OpenModelica executables
    
    Attributes:
        executable_path (str): Path to the simulation executable
        start_time (int): Simulation start time
        stop_time (int): Simulation stop time
        process (Optional[QProcess]): The managed QProcess instance
    """
    
    # Signals
    output_received = pyqtSignal(str)
    process_finished = pyqtSignal(int)
    process_error = pyqtSignal(str)
    
    def __init__(self, executable_path: str, start_time: int, stop_time: int):
        """
        Initialize the ProcessRunner.
        
        Args:
            executable_path (str): Path to the executable
            start_time (int): Start time for simulation
            stop_time (int): Stop time for simulation
        """
        super().__init__()
        self.executable_path = executable_path
        self.start_time = start_time
        self.stop_time = stop_time
        self.process: Optional[QProcess] = None
        self._output_buffer = ""
        
    def start(self):
        """Start the simulation process."""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            return
            
        # Create QProcess instance
        self.process = QProcess(self)
        
        # Connect signals
        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)
        self.process.stateChanged.connect(self._on_state_changed)
        
        # Build arguments for OpenModelica executable
        arguments = self._build_arguments()
        
        # Set working directory
        executable_dir = os.path.dirname(self.executable_path)
        if executable_dir:
            self.process.setWorkingDirectory(executable_dir)
        
        # Log process start
        self.output_received.emit(
            f"Process started with arguments: {' '.join(arguments)}\n"
        )
        
        # Start the process
        self.process.start(self.executable_path, arguments)
        
    def _build_arguments(self) -> List[str]:
        """
        Build command line arguments for the executable.
        
        Returns:
            List[str]: List of arguments
        """
        # OpenModelica simulation flags
        # Format: -override=startTime=X,stopTime=Y
        override_string = f"startTime={self.start_time},stopTime={self.stop_time}"
        
        arguments = [
            f"-override={override_string}",
            f"-r={os.path.splitext(self.executable_path)[0]}_res.json",
            "-outputFormat=mat"
        ]
        
        return arguments
        
    @pyqtSlot()
    def _read_stdout(self):
        """Read and emit standard output."""
        if self.process:
            data = self.process.readAllStandardOutput()
            text = bytes(data).decode('utf-8', errors='replace')
            if text:
                self.output_received.emit(text)
                
    @pyqtSlot()
    def _read_stderr(self):
        """Read and emit standard error."""
        if self.process:
            data = self.process.readAllStandardError()
            text = bytes(data).decode('utf-8', errors='replace')
            if text:
                self.output_received.emit(f"[STDERR] {text}")
                
    @pyqtSlot(QProcess.ProcessState)
    def _on_state_changed(self, state: QProcess.ProcessState):
        """
        Handle process state changes.
        
        Args:
            state (QProcess.ProcessState): New process state
        """
        state_names = {
            QProcess.ProcessState.NotRunning: "Not Running",
            QProcess.ProcessState.Starting: "Starting",
            QProcess.ProcessState.Running: "Running"
        }
        self.output_received.emit(f"Process state: {state_names.get(state, 'Unknown')}\n")
        
    @pyqtSlot(int, QProcess.ExitStatus)
    def _on_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        """
        Handle process completion.
        
        Args:
            exit_code (int): Process exit code
            exit_status (QProcess.ExitStatus): Exit status
        """
        status_names = {
            QProcess.ExitStatus.NormalExit: "Normal Exit",
            QProcess.ExitStatus.CrashExit: "Crash Exit"
        }
        
        self.output_received.emit(
            f"Process finished ({status_names.get(exit_status, 'Unknown')}) "
            f"with exit code: {exit_code}\n"
        )
        
        self.process_finished.emit(exit_code)
        
    @pyqtSlot(QProcess.ProcessError)
    def _on_error(self, error: QProcess.ProcessError):
        """
        Handle process errors.
        
        Args:
            error (QProcess.ProcessError): Error type
        """
        error_messages = {
            QProcess.ProcessError.FailedToStart: "Failed to start process",
            QProcess.ProcessError.Crashed: "Process crashed during execution",
            QProcess.ProcessError.Timedout: "Process timed out",
            QProcess.ProcessError.WriteError: "Error writing to process",
            QProcess.ProcessError.ReadError: "Error reading from process",
            QProcess.ProcessError.UnknownError: "Unknown process error"
        }
        
        error_message = error_messages.get(error, "Unknown error")
        self.process_error.emit(error_message)
        
    def terminate(self, timeout_ms: int = 5000):
        """
        Terminate the running process gracefully.
        
        Args:
            timeout_ms (int): Timeout in milliseconds before force kill
        """
        if self.process:
            if self.process.state() == QProcess.ProcessState.Running:
                self.output_received.emit("Terminating process...\n")
                self.process.terminate()
                
                # Wait for process to terminate
                if not self.process.waitForFinished(timeout_ms):
                    self.output_received.emit(
                        "Process did not terminate gracefully, killing...\n"
                    )
                    self.process.kill()
                    self.process.waitForFinished()
                    
    def is_running(self) -> bool:
        """
        Check if process is currently running.
        
        Returns:
            bool: True if process is running
        """
        return (
            self.process is not None and 
            self.process.state() == QProcess.ProcessState.Running
        )
        
    def get_process_info(self) -> dict:
        """
        Get information about the current process.
        
        Returns:
            dict: Process information
        """
        if not self.process:
            return {
                "running": False,
                "pid": None,
                "executable": self.executable_path,
                "start_time": self.start_time,
                "stop_time": self.stop_time
            }
            
        return {
            "running": self.is_running(),
            "pid": self.process.processId() if self.is_running() else None,
            "executable": self.executable_path,
            "start_time": self.start_time,
            "stop_time": self.stop_time,
            "state": self.process.state()
      }
