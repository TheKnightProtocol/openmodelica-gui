"""
Unit Tests for Input Validation.

This module contains comprehensive tests for the InputValidator class.
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.validators import InputValidator


class TestInputValidator(unittest.TestCase):
    """Test cases for InputValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = InputValidator
        
    def test_valid_time_ranges(self):
        """Test various valid time range combinations."""
        valid_cases = [
            (0, 1),
            (0, 4),
            (1, 2),
            (1, 4),
            (2, 3),
            (3, 4),
            (0, 3),
            (2, 4),
        ]
        
        for start, stop in valid_cases:
            with self.subTest(start=start, stop=stop):
                self.assertTrue(
                    self.validator.validate_time_range(start, stop),
                    f"Expected ({start}, {stop}) to be valid"
                )
                
    def test_invalid_time_ranges(self):
        """Test various invalid time range combinations."""
        invalid_cases = [
            # Start >= Stop
            (0, 0),
            (1, 1),
            (2, 1),
            (3, 2),
            (4, 3),
            (4, 4),
            # Out of bounds (start)
            (-1, 1),
            (-2, 2),
            (-10, 0),
            # Out of bounds (stop)
            (0, 5),
            (1, 6),
            (3, 7),
            (4, 5),
            # Both out of bounds
            (-1, 5),
            (-2, 6),
            (5, 6),
            (10, 20),
        ]
        
        for start, stop in invalid_cases:
            with self.subTest(start=start, stop=stop):
                self.assertFalse(
                    self.validator.validate_time_range(start, stop),
                    f"Expected ({start}, {stop}) to be invalid"
                )
                
    def test_valid_executable_paths(self):
        """Test valid executable paths."""
        valid_paths = [
            "model/executable",
            "/usr/local/bin/model",
            "C:\\Program Files\\model.exe",
            "./executable",
            "../model/TwoConnectedTanks",
            "executable",
        ]
        
        for path in valid_paths:
            with self.subTest(path=path):
                self.assertTrue(
                    self.validator.validate_executable_path(path),
                    f"Expected '{path}' to be valid"
                )
                
    def test_invalid_executable_paths(self):
        """Test invalid executable paths."""
        invalid_paths = [
            "",
            "   ",
            None,
            123,
            [],
            {},
        ]
        
        for path in invalid_paths:
            with self.subTest(path=path):
                self.assertFalse(
                    self.validator.validate_executable_path(path),
                    f"Expected '{path}' to be invalid"
                )
                
    def test_parse_arguments_valid(self):
        """Test parsing valid command line arguments."""
        valid_args = [
            ["program", "0", "4"],
            ["program", "1", "3"],
            ["program", "2", "4"],
            ["program", "0", "1"],
        ]
        
        for args in valid_args:
            with self.subTest(args=args):
                success, error = self.validator.parse_arguments(args)
                self.assertTrue(success, f"Expected {args} to be valid")
                self.assertEqual(error, "")
                
    def test_parse_arguments_invalid_insufficient(self):
        """Test parsing with insufficient arguments."""
        test_cases = [
            [],
            ["program"],
            ["program", "0"],
        ]
        
        for args in test_cases:
            with self.subTest(args=args):
                success, error = self.validator.parse_arguments(args)
                self.assertFalse(success)
                self.assertIn("Insufficient", error)
                
    def test_parse_arguments_invalid_types(self):
        """Test parsing with non-integer time values."""
        test_cases = [
            ["program", "abc", "def"],
            ["program", "1.5", "2.5"],
            ["program", "one", "two"],
            ["program", "0", "four"],
        ]
        
        for args in test_cases:
            with self.subTest(args=args):
                success, error = self.validator.parse_arguments(args)
                self.assertFalse(success)
                self.assertIn("integers", error)
                
    def test_parse_arguments_invalid_range(self):
        """Test parsing with invalid time ranges."""
        test_cases = [
            ["program", "4", "3"],
            ["program", "-1", "2"],
            ["program", "0", "5"],
            ["program", "3", "3"],
        ]
        
        for args in test_cases:
            with self.subTest(args=args):
                success, error = self.validator.parse_arguments(args)
                self.assertFalse(success)
                self.assertIn("time range", error.lower())
                
    def test_valid_time_value(self):
        """Test single time value validation."""
        valid_values = [0, 1, 2, 3, 4]
        
        for value in valid_values:
            with self.subTest(value=value):
                self.assertTrue(
                    self.validator.is_valid_time_value(value),
                    f"Expected {value} to be valid"
                )
                
    def test_invalid_time_value(self):
        """Test invalid single time values."""
        invalid_values = [-1, 5, 6, 10, -10]
        
        for value in invalid_values:
            with self.subTest(value=value):
                self.assertFalse(
                    self.validator.is_valid_time_value(value),
                    f"Expected {value} to be invalid"
                )
                
    def test_validate_all(self):
        """Test comprehensive validation."""
        # Valid case
        success, error = self.validator.validate_all("model/exec", 0, 4)
        self.assertTrue(success)
        self.assertEqual(error, "")
        
        # Invalid executable
        success, error = self.validator.validate_all("", 0, 4)
        self.assertFalse(success)
        self.assertIn("executable", error.lower())
        
        # Invalid time range
        success, error = self.validator.validate_all("model/exec", 4, 3)
        self.assertFalse(success)
        
    def test_get_valid_time_range(self):
        """Test time range description."""
        description = self.validator.get_valid_time_range()
        self.assertIsInstance(description, str)
        self.assertIn("0", description)
        self.assertIn("5", description)
        
    def test_boundary_values(self):
        """Test boundary value analysis."""
        # Minimum boundary
        self.assertTrue(self.validator.validate_time_range(0, 1))
        
        # Maximum boundary
        self.assertTrue(self.validator.validate_time_range(3, 4))
        
        # Just below minimum
        self.assertFalse(self.validator.validate_time_range(-1, 4))
        
        # Just above maximum
        self.assertFalse(self.validator.validate_time_range(0, 5))
        
        # Equal values (invalid)
        self.assertFalse(self.validator.validate_time_range(2, 2))
        
        # Start > Stop (invalid)
        self.assertFalse(self.validator.validate_time_range(4, 3))


class TestInputValidatorEdgeCases(unittest.TestCase):
    """Test edge cases for InputValidator."""
    
    def test_large_values(self):
        """Test very large time values."""
        self.assertFalse(InputValidator.validate_time_range(1000, 2000))
        self.assertFalse(InputValidator.validate_time_range(999, 1000))
        
    def test_negative_values(self):
        """Test negative time values."""
        self.assertFalse(InputValidator.validate_time_range(-1, 4))
        self.assertFalse(InputValidator.validate_time_range(-100, -50))
        
    def test_float_values(self):
        """Test float time values (should be invalid for integer validation)."""
        with self.assertRaises(TypeError):
            InputValidator.validate_time_range(0.5, 2.5)
            
    def test_string_values(self):
        """Test string time values."""
        self.assertFalse(InputValidator.validate_time_range("0", "4"))
        
    def test_none_values(self):
        """Test None values."""
        self.assertFalse(InputValidator.validate_time_range(None, None))


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
