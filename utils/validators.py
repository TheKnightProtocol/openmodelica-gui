"""
Input Validation Utilities.

This module provides validation functions for user inputs
in the OpenModelica Simulation Runner application.
"""

from typing import Tuple, List, Optional
import os


class InputValidator:
    """
    Validates user inputs for the simulation application.
    
    This class provides static methods for validating:
    - Time ranges (ensuring 0 <= start < stop < 5)
    - Executable paths
    - Command line arguments
    
    Attributes:
        MIN_TIME (int): Minimum allowed time value
        MAX_TIME (int): Maximum allowed time value
    """
    
    # Class constants
    MIN_TIME = 0
    MAX_TIME = 5
    
    @classmethod
    def validate_time_range(cls, start_time: int, stop_time: int) -> bool:
        """
        Validate time range satisfies: 0 <= start < stop < 5.
        
        Args:
            start_time (int): Simulation start time
            stop_time (int): Simulation stop time
            
        Returns:
            bool: True if valid, False otherwise
            
        Examples:
            >>> InputValidator.validate_time_range(0, 4)
            True
            >>> InputValidator.validate_time_range(4, 3)
            False
            >>> InputValidator.validate_time_range(-1, 2)
            False
        """
        # Check types
        if not isinstance(start_time, int) or not isinstance(stop_time, int):
            return False
            
        # Check bounds and ordering
        return (
            cls.MIN_TIME <= start_time < stop_time < cls.MAX_TIME
        )
        
    @classmethod
    def validate_executable_path(cls, path: str) -> bool:
        """
        Validate executable path.
        
        Args:
            path (str): Path to executable
            
        Returns:
            bool: True if path is valid
            
        Examples:
            >>> InputValidator.validate_executable_path("model/executable")
            True
            >>> InputValidator.validate_executable_path("")
            False
        """
        if not path or not isinstance(path, str):
            return False
            
        # Check if path is not just whitespace
        if not path.strip():
            return False
            
        return True
        
    @classmethod
    def parse_arguments(cls, arguments: List[str]) -> Tuple[bool, str]:
        """
        Parse and validate command line arguments.
        
        Args:
            arguments (List[str]): List of command line arguments
            
        Returns:
            Tuple[bool, str]: (success, error_message)
            
        Examples:
            >>> InputValidator.parse_arguments(["prog", "0", "4"])
            (True, "")
            >>> InputValidator.parse_arguments(["prog"])
            (False, "Insufficient arguments...")
        """
        if len(arguments) < 3:
            return False, (
                "Insufficient arguments. "
                "Usage: program <executable> <start_time> <stop_time>"
            )
            
        try:
            start_time = int(arguments[1])
            stop_time = int(arguments[2])
        except ValueError:
            return False, "Start and stop times must be integers"
            
        if not cls.validate_time_range(start_time, stop_time):
            return False, (
                f"Invalid time range. Must satisfy: "
                f"{cls.MIN_TIME} <= start < stop < {cls.MAX_TIME}"
            )
            
        return True, ""
        
    @classmethod
    def get_valid_time_range(cls) -> str:
        """
        Get description of valid time range.
        
        Returns:
            str: Human-readable time range description
        """
        return (
            f"Valid time range: {cls.MIN_TIME} <= start < stop < {cls.MAX_TIME}"
        )
        
    @classmethod
    def is_valid_time_value(cls, value: int) -> bool:
        """
        Check if a single time value is within bounds.
        
        Args:
            value (int): Time value to check
            
        Returns:
            bool: True if value is within bounds
        """
        return cls.MIN_TIME <= value < cls.MAX_TIME
        
    @classmethod
    def validate_executable_exists(cls, path: str) -> Tuple[bool, str]:
        """
        Validate that executable file exists.
        
        Args:
            path (str): Path to executable
            
        Returns:
            Tuple[bool, str]: (exists, error_message)
        """
        if not cls.validate_executable_path(path):
            return False, "Invalid executable path"
            
        if not os.path.exists(path):
            return False, f"Executable not found: {path}"
            
        if not os.path.isfile(path):
            return False, f"Path is not a file: {path}"
            
        return True, ""
        
    @classmethod
    def validate_all(
        cls, 
        executable_path: str, 
        start_time: int, 
        stop_time: int
    ) -> Tuple[bool, str]:
        """
        Validate all inputs together.
        
        Args:
            executable_path (str): Path to executable
            start_time (int): Start time
            stop_time (int): Stop time
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Validate executable path
        if not cls.validate_executable_path(executable_path):
            return False, "Please select an executable file"
            
        # Validate time range
        if not cls.validate_time_range(start_time, stop_time):
            return False, cls.get_valid_time_range()
            
        return True, ""
