"""
Tests for the field_parser module.

This module tests the shared field parsing functionality used by both
PDZ24 and PDZ25 tools.
"""

import pytest
import struct
from pdz_tool.field_parser import FieldParser, PDZ24FieldParser, PDZ25FieldParser


class TestFieldParser:
    """Test the base FieldParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = FieldParser(verbose=False, debug=False)
        self.verbose_parser = FieldParser(verbose=True, debug=True)
    
    def test_parser_initialization(self):
        """Test that parser initializes correctly."""
        assert self.parser.verbose is False
        assert self.parser.debug is False
        assert 'struct' in self.parser._parsers
        assert 'spectrum_data' in self.parser._parsers
        assert 'wchar_t' in self.parser._parsers
        assert 'system_time' in self.parser._parsers
        assert 'bytes' in self.parser._parsers
        assert 'skip' in self.parser._parsers
    
    def test_get_parser_type(self):
        """Test parser type detection."""
        assert self.parser._get_parser_type('skip', 'any') == 'skip'
        assert self.parser._get_parser_type('spectrum_data', 'any') == 'spectrum_data'
        assert self.parser._get_parser_type('test', 'wchar_t') == 'wchar_t'
        assert self.parser._get_parser_type('test', 'wchar_t[10]') == 'wchar_t'
        assert self.parser._get_parser_type('test', 'system_time') == 'system_time'
        assert self.parser._get_parser_type('test', 'bytes') == 'bytes'
        assert self.parser._get_parser_type('test', 'I') == 'struct'
    
    def test_check_bounds_sufficient(self):
        """Test bounds checking with sufficient bytes."""
        data = b'\x01\x02\x03\x04\x05'
        assert self.parser._check_bounds(data, 0, 3, 'test_field') is True
        assert self.parser._check_bounds(data, 2, 3, 'test_field') is True
    
    def test_check_bounds_insufficient(self):
        """Test bounds checking with insufficient bytes."""
        data = b'\x01\x02\x03'
        assert self.parser._check_bounds(data, 0, 5, 'test_field') is False
        assert self.parser._check_bounds(data, 2, 5, 'test_field') is False
    
    def test_parse_struct_field_integer(self):
        """Test parsing integer struct fields."""
        data = struct.pack('<I', 12345)
        result = {}
        
        value, size = self.parser._parse_struct_field('test_int', 'I', data, 0, result)
        assert value == 12345
        assert size == 4
    
    def test_parse_struct_field_float(self):
        """Test parsing float struct fields."""
        test_value = 123.456
        data = struct.pack('<f', test_value)
        result = {}
        
        value, size = self.parser._parse_struct_field('test_float', 'f', data, 0, result)
        assert abs(value - test_value) < 0.001
        assert size == 4
    
    def test_parse_struct_field_insufficient_bytes(self):
        """Test struct field parsing with insufficient bytes."""
        data = b'\x01\x02'  # Only 2 bytes, but need 4 for integer
        result = {}
        
        value, size = self.parser._parse_struct_field('test_int', 'I', data, 0, result)
        assert value is None
        assert size == 0
    
    def test_parse_spectrum_data_field_pdz25_style(self):
        """Test spectrum data parsing for PDZ25 format (with 'channels')."""
        num_channels = 3
        test_data = [100, 200, 300]
        data = struct.pack(f'<{num_channels}L', *test_data)
        result = {'channels': num_channels}
        
        value, size = self.parser._parse_spectrum_data_field('spectrum_data', 'spectrum_data', data, 0, result)
        assert value == test_data
        assert size == num_channels * 4
    
    def test_parse_spectrum_data_field_pdz24_style(self):
        """Test spectrum data parsing for PDZ24 format (with 'num_channels')."""
        num_channels = 3
        test_data = [100, 200, 300]
        data = struct.pack(f'<{num_channels}i', *test_data)
        result = {'num_channels': num_channels}
        
        value, size = self.parser._parse_spectrum_data_field('spectrum_data', 'spectrum_data', data, 0, result)
        assert value == test_data
        assert size == num_channels * 4
    
    def test_parse_wchar_field_dynamic_length(self):
        """Test parsing wchar_t fields with dynamic length."""
        test_string = "Hello"
        data = test_string.encode('utf-16le')
        result = {'test_string_length': len(test_string)}
        
        value, size = self.parser._parse_wchar_field('test_string', 'wchar_t', data, 0, result)
        assert value == test_string
        assert size == len(test_string) * 2
    
    def test_parse_wchar_field_fixed_length(self):
        """Test parsing wchar_t fields with fixed length."""
        test_string = "Hi"
        # Pad to length 5 with null characters
        padded_string = test_string + '\x00' * (5 - len(test_string))
        data = padded_string.encode('utf-16le')
        result = {}
        
        value, size = self.parser._parse_wchar_field('test_string', 'wchar_t[5]', data, 0, result)
        assert value == test_string  # Should strip null characters
        assert size == 10  # 5 wide characters * 2 bytes each
    
    def test_parse_system_time_field(self):
        """Test parsing SYSTEMTIME fields."""
        # Create a SYSTEMTIME structure: year=2023, month=12, day_of_week=5, day=25, hour=14, minute=30, second=45, ms=123
        data = struct.pack('<8H', 2023, 12, 5, 25, 14, 30, 45, 123)
        result = {}
        
        value, size = self.parser._parse_system_time_field('test_time', 'system_time', data, 0, result)
        assert "2023-12-25 14:30:45" in value
        assert size == 16
    
    def test_parse_bytes_field_image(self):
        """Test parsing bytes fields for images."""
        test_bytes = b'\xFF\xD8\xFF\xE0'  # JPEG header
        result = {'image_length': len(test_bytes)}
        
        value, size = self.parser._parse_bytes_field('image', 'bytes', test_bytes, 0, result)
        assert value == test_bytes
        assert size == len(test_bytes)
    
    def test_parse_skip_field(self):
        """Test parsing skip fields."""
        data = b'\x01\x02\x03\x04\x05'
        result = {}
        
        value, size = self.parser._parse_skip_field('skip', '3s', data, 0, result)
        assert value is None
        assert size == 3
    
    def test_parse_skip_field_insufficient_bytes(self):
        """Test skip field with insufficient bytes."""
        data = b'\x01\x02'  # Only 2 bytes, but trying to skip 4
        result = {}
        
        value, size = self.parser._parse_skip_field('skip', '4s', data, 0, result)
        assert value is None
        assert size == -1  # Error signal
    
    def test_parse_repeatable_field(self):
        """Test parsing repeatable fields."""
        # Create data for 2 repeatable items, each with a short (2 bytes)
        data = struct.pack('<HH', 100, 200)
        result = {}
        field_config = {
            'repeat': 2,
            'fields': [('value', 'H')]
        }
        
        value, new_offset = self.parser.parse_repeatable_field('test_array', field_config, data, 0, result)
        assert len(value) == 2
        assert value[0]['value'] == 100
        assert value[1]['value'] == 200
        assert new_offset == 4
    
    def test_parse_repeatable_field_dynamic_count(self):
        """Test parsing repeatable fields with dynamic count."""
        # Create data for 3 items based on previously parsed count
        data = struct.pack('<HHH', 10, 20, 30)
        result = {'item_count': 3}
        field_config = {
            'repeat': 'item_count',
            'fields': [('value', 'H')]
        }
        
        value, new_offset = self.parser.parse_repeatable_field('items', field_config, data, 0, result)
        assert len(value) == 3
        assert value[0]['value'] == 10
        assert value[1]['value'] == 20
        assert value[2]['value'] == 30
    
    def test_parse_repeatable_field_zero_count(self):
        """Test parsing repeatable fields with zero count."""
        data = b''
        result = {}
        field_config = {
            'repeat': 0,
            'fields': [('value', 'H')]
        }
        
        value, new_offset = self.parser.parse_repeatable_field('empty_array', field_config, data, 0, result)
        assert value is None
        assert new_offset == 0


class TestPDZ24FieldParser:
    """Test the PDZ24-specific field parser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDZ24FieldParser(verbose=False, debug=False)
    
    def test_parse_field_with_error_codes_normal(self):
        """Test normal field parsing with error codes."""
        data = struct.pack('<I', 12345)
        result = {}
        
        value, size = self.parser.parse_field_with_error_codes('test_field', 'I', data, 0, result)
        assert value == 12345
        assert size == 4
    
    def test_parse_field_with_error_codes_skip(self):
        """Test skip field parsing with error codes."""
        data = b'\x01\x02\x03\x04'
        result = {}
        
        value, size = self.parser.parse_field_with_error_codes('skip', '4s', data, 0, result)
        assert value is None
        assert size == 4
    
    def test_parse_field_with_error_codes_error(self):
        """Test error handling in field parsing."""
        data = b'\x01\x02'  # Insufficient bytes for integer
        result = {}
        
        value, size = self.parser.parse_field_with_error_codes('test_field', 'I', data, 0, result)
        assert value is None
        assert size == -1  # Error condition


class TestPDZ25FieldParser:
    """Test the PDZ25-specific field parser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDZ25FieldParser(verbose=False, debug=False)
    
    def test_pdz25_parser_has_float_array(self):
        """Test that PDZ25 parser includes float_array parser."""
        assert 'float_array' in self.parser._parsers
    
    def test_parse_float_array_field(self):
        """Test parsing float array fields."""
        test_floats = [1.5, 2.5, 3.5, 4.5]
        data = struct.pack(f'<{len(test_floats)}f', *test_floats)
        result = {'spectrum_data_length': len(test_floats)}
        
        value, size = self.parser._parse_float_array_field('spectrum_data', 'float_array', data, 0, result)
        assert len(value) == len(test_floats)
        for i, expected in enumerate(test_floats):
            assert abs(value[i] - expected) < 0.001
        assert size == len(test_floats) * 4


class TestFieldParserErrorHandling:
    """Test error handling in field parsers."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = FieldParser(verbose=False, debug=True)
    
    def test_parse_field_struct_error(self):
        """Test handling of struct.error exceptions."""
        # Create malformed data that will cause struct.error
        data = b'\x01'  # Only 1 byte, but trying to parse 4-byte integer
        result = {}
        
        value, size = self.parser.parse_field('test_field', 'I', data, 0, result)
        assert value is None
        assert size == 0
    
    def test_parse_field_unknown_type(self):
        """Test parsing field with unknown type (should use struct parser)."""
        data = struct.pack('<H', 42)
        result = {}
        
        value, size = self.parser.parse_field('unknown_field', 'H', data, 0, result)
        assert value == 42
        assert size == 2


if __name__ == '__main__':
    pytest.main([__file__])