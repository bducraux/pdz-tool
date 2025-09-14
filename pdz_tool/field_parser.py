"""
Common field parsing utilities for PDZ files.

This module provides a shared FieldParser class that consolidates parsing logic
used by both PDZ24 and PDZ25 tools, reducing code duplication and improving
maintainability.
"""

import struct
import traceback
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from .utils import flatten_system_date_time
from .config import (
    SYSTEM_TIME_SIZE, WCHAR_SIZE, BYTES_PER_CHANNEL_PDZ24, BYTES_PER_CHANNEL_PDZ25,
    BYTES_PER_FLOAT, FieldTypes, PDZ24Config, PDZ25Config, ErrorMessages
)


class FieldParser:
    """
    Common field parser for PDZ file formats.
    
    This class provides shared parsing functionality used by both PDZ24 and PDZ25
    tools, including struct field parsing, bounds checking, and error handling.
    """
    
    def __init__(self, verbose: bool = False, debug: bool = False):
        """
        Initialize the field parser.
        
        Args:
            verbose: Enable verbose output
            debug: Enable debug output and stack traces
        """
        self.verbose = verbose
        self.debug = debug
        
        # Registry for field type parsers
        self._parsers: Dict[str, Callable] = {
            FieldTypes.STRUCT: self._parse_struct_field,
            FieldTypes.SPECTRUM_DATA: self._parse_spectrum_data_field,
            FieldTypes.WCHAR_T: self._parse_wchar_field,
            FieldTypes.SYSTEM_TIME: self._parse_system_time_field,
            FieldTypes.BYTES: self._parse_bytes_field,
            FieldTypes.SKIP: self._parse_skip_field,
        }
    
    def _print_verbose(self, message: str) -> None:
        """Print verbose messages if verbose mode is enabled."""
        if self.verbose:
            print(message)
    
    def parse_field(
        self, 
        field_name: str, 
        field_type: str, 
        block_bytes: bytes, 
        offset: int, 
        result: Dict[str, Any]
    ) -> Tuple[Optional[Any], int]:
        """
        Parse a single field based on its type.
        
        Args:
            field_name: Name of the field being parsed
            field_type: Type specification of the field
            block_bytes: Raw bytes containing the field data
            offset: Current offset in the bytes
            result: Previously parsed fields (for context)
            
        Returns:
            Tuple of (parsed_value, bytes_consumed) or (None, 0) on error
        """
        try:
            # Determine parser type
            parser_type = self._get_parser_type(field_name, field_type)
            parser = self._parsers.get(parser_type, self._parsers['struct'])
            
            return parser(field_name, field_type, block_bytes, offset, result)
            
        except struct.error as e:
            self._print_verbose(f"Struct error in field {field_name}: {e}")
            if self.debug:
                traceback.print_exc()
            return None, 0
        except Exception as e:
            self._print_verbose(f"Unexpected error parsing field {field_name}: {e}")
            if self.debug:
                traceback.print_exc()
            return None, 0
    
    def _get_parser_type(self, field_name: str, field_type: str) -> str:
        """Determine which parser to use for a field."""
        if field_name == 'skip':
            return FieldTypes.SKIP
        elif field_name == 'spectrum_data':
            return FieldTypes.SPECTRUM_DATA
        elif 'wchar_t' in field_type:
            return FieldTypes.WCHAR_T
        elif field_type == 'system_time':
            return FieldTypes.SYSTEM_TIME
        elif field_type == 'bytes':
            return FieldTypes.BYTES
        else:
            return FieldTypes.STRUCT
    
    def _check_bounds(
        self, 
        block_bytes: bytes, 
        offset: int, 
        required_bytes: int, 
        field_name: str
    ) -> bool:
        """
        Check if there are sufficient bytes available.
        
        Args:
            block_bytes: The byte buffer
            offset: Current offset
            required_bytes: Number of bytes needed
            field_name: Field name for error reporting
            
        Returns:
            True if sufficient bytes available, False otherwise
        """
        if offset + required_bytes > len(block_bytes):
            self._print_verbose(f"Error: Insufficient bytes for {field_name}")
            return False
        return True
    
    def _parse_struct_field(
        self, 
        field_name: str, 
        field_type: str, 
        block_bytes: bytes, 
        offset: int, 
        result: Dict[str, Any]
    ) -> Tuple[Optional[Any], int]:
        """Parse regular struct fields (most common case)."""
        fmt = '<' + field_type
        size = struct.calcsize(fmt)
        
        if not self._check_bounds(block_bytes, offset, size, field_name):
            return None, 0
        
        value = struct.unpack_from(fmt, block_bytes, offset)[0]
        return value, size
    
    def _parse_spectrum_data_field(
        self, 
        field_name: str, 
        field_type: str, 
        block_bytes: bytes, 
        offset: int, 
        result: Dict[str, Any]
    ) -> Tuple[Optional[List[int]], int]:
        """Parse spectrum data fields (common to both PDZ formats)."""
        # PDZ25 uses 'channels', PDZ24 uses 'num_channels'
        num_channels = result.get('channels', result.get('num_channels', 0))
        
        # Use appropriate byte count and format character based on PDZ version
        if 'channels' in result:  # PDZ25 format
            bytes_per_channel = BYTES_PER_CHANNEL_PDZ25
            fmt_char = PDZ25Config.SPECTRUM_FORMAT_CHAR
        else:  # PDZ24 format
            bytes_per_channel = BYTES_PER_CHANNEL_PDZ24
            fmt_char = PDZ24Config.SPECTRUM_FORMAT_CHAR
            
        total_bytes = num_channels * bytes_per_channel
        
        if not self._check_bounds(block_bytes, offset, total_bytes, field_name):
            return None, 0
        
        fmt = f'<{num_channels}{fmt_char}'
        spectrum_data = struct.unpack_from(fmt, block_bytes, offset)
        return list(spectrum_data), total_bytes
    
    def _parse_wchar_field(
        self, 
        field_name: str, 
        field_type: str, 
        block_bytes: bytes, 
        offset: int, 
        result: Dict[str, Any]
    ) -> Tuple[Optional[str], int]:
        """Parse wide character string fields (PDZ25 specific)."""
        if field_type == 'wchar_t':
            # Dynamic length from previously parsed length field
            length_field_name = field_name + '_length'
            length = result.get(length_field_name, 0)
            n_bytes = length * WCHAR_SIZE
        else:
            # Fixed length from field type specification
            length = int(field_type.split('[')[1].split(']')[0])
            n_bytes = length * WCHAR_SIZE
        
        if not self._check_bounds(block_bytes, offset, n_bytes, field_name):
            return None, 0
        
        string_data_bytes = block_bytes[offset:offset + n_bytes]
        string_data = string_data_bytes.decode('utf-16').strip('\x00')
        return string_data, n_bytes
    
    def _parse_system_time_field(
        self, 
        field_name: str, 
        field_type: str, 
        block_bytes: bytes, 
        offset: int, 
        result: Dict[str, Any]
    ) -> Tuple[Optional[str], int]:
        """Parse Windows SYSTEMTIME fields (PDZ25 specific)."""
        n_bytes = SYSTEM_TIME_SIZE
        
        if not self._check_bounds(block_bytes, offset, n_bytes, field_name):
            return None, 0
        
        year, month, day_of_week, day, hour, minute, second, milliseconds = struct.unpack_from(
            '<8H', block_bytes, offset
        )
        
        acquisition_datetime = {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "second": second,
            "milliseconds": milliseconds
        }
        
        return flatten_system_date_time(acquisition_datetime), n_bytes
    
    def _parse_bytes_field(
        self, 
        field_name: str, 
        field_type: str, 
        block_bytes: bytes, 
        offset: int, 
        result: Dict[str, Any]
    ) -> Tuple[Optional[bytes], int]:
        """Parse raw bytes fields (e.g., image data in PDZ25)."""
        if field_name == 'image':
            length_field_name = field_name + '_length'
            length = result.get(length_field_name, 0)
            n_bytes = length
            
            if not self._check_bounds(block_bytes, offset, n_bytes, field_name):
                return None, 0
            
            raw_bytes = block_bytes[offset:offset + n_bytes]
            return raw_bytes, n_bytes
        
        return None, 0
    
    def _parse_skip_field(
        self, 
        field_name: str, 
        field_type: str, 
        block_bytes: bytes, 
        offset: int, 
        result: Dict[str, Any]
    ) -> Tuple[Optional[Any], int]:
        """Parse skip fields (PDZ24 specific - bytes to ignore)."""
        size = struct.calcsize(field_type)
        
        if not self._check_bounds(block_bytes, offset, size, field_name):
            return None, -1  # Signal error to calling code
        
        return None, size  # Return None with size to skip
    
    def parse_repeatable_field(
        self,
        field_name: str,
        field_config: Dict[str, Any],
        block_bytes: bytes,
        offset: int,
        result: Dict[str, Any]
    ) -> Tuple[Optional[List[Dict[str, Any]]], int]:
        """
        Parse repeatable/array fields (PDZ25 specific).
        
        Args:
            field_name: Name of the repeatable field
            field_config: Configuration with 'repeat' count and 'fields' list
            block_bytes: Raw bytes containing the field data
            offset: Current offset in the bytes
            result: Previously parsed fields (for context)
            
        Returns:
            Tuple of (list_of_parsed_items, bytes_consumed)
        """
        repeat_count = field_config['repeat']
        
        # Resolve dynamic repeat count if it's a string reference
        if isinstance(repeat_count, str):
            repeat_count = int(result.get(repeat_count, 0))
        
        if repeat_count == 0:
            self._print_verbose(f"Skipping repeatable block {field_name} with {repeat_count} repeats")
            return None, offset
        
        sub_fields = field_config['fields']
        repeated_data = []
        
        for _ in range(repeat_count):
            sub_result = {}
            for sub_field_name, sub_field_type in sub_fields:
                sub_value, sub_size = self.parse_field(
                    sub_field_name, sub_field_type, block_bytes, offset, sub_result
                )
                if sub_value is None and sub_size == 0:
                    break
                if sub_value is not None:
                    sub_result[sub_field_name] = sub_value
                offset += sub_size
            repeated_data.append(sub_result)
        
        return repeated_data, offset


class PDZ24FieldParser(FieldParser):
    """Specialized field parser for PDZ24 format."""
    
    def parse_field_with_error_codes(
        self,
        field_name: str,
        field_type: str,
        block_bytes: bytes,
        offset: int,
        result: Dict[str, Any]
    ) -> Tuple[Optional[Any], int]:
        """
        Parse field with PDZ24-specific error codes.
        
        Returns:
            Tuple of (value, size) where size can be:
            - positive: normal parsing, advance offset by size
            - 0: skip field (for None values)
            - -1: error occurred, stop parsing
        """
        value, size = self.parse_field(field_name, field_type, block_bytes, offset, result)
        
        if value is None and field_name == 'skip':
            return None, size if size > 0 else struct.calcsize(field_type)
        elif value is None and size == 0:
            return None, -1  # Error condition
        else:
            return value, size


class PDZ25FieldParser(FieldParser):
    """Specialized field parser for PDZ25 format."""
    
    def __init__(self, verbose: bool = False, debug: bool = False):
        """Initialize PDZ25-specific parser."""
        super().__init__(verbose, debug)
        
        # Add PDZ25-specific parsers
        self._parsers.update({
            FieldTypes.FLOAT_ARRAY: self._parse_float_array_field,
        })
    
    def _parse_float_array_field(
        self,
        field_name: str,
        field_type: str,
        block_bytes: bytes,
        offset: int,
        result: Dict[str, Any]
    ) -> Tuple[Optional[List[float]], int]:
        """Parse float array fields (PDZ25 LIBS spectrum data)."""
        if field_name == 'spectrum_data' and field_type == 'float_array':
            # Get array length from previously parsed field
            length_field_name = field_name + '_length'
            array_length = result.get(length_field_name, 0)
            
            # Each float is BYTES_PER_FLOAT bytes, but this field contains x,y pairs
            # so actual count is array_length / 2 pairs * 2 values * BYTES_PER_FLOAT bytes = array_length * BYTES_PER_FLOAT
            total_bytes = array_length * BYTES_PER_FLOAT
            
            if not self._check_bounds(block_bytes, offset, total_bytes, field_name):
                return None, 0
            
            # Unpack as float array
            num_floats = array_length
            fmt = f'<{num_floats}f'
            float_data = struct.unpack_from(fmt, block_bytes, offset)
            return list(float_data), total_bytes
        
        return None, 0