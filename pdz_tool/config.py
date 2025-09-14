"""
Config file for PDZ tool

This module contains configuration constants and field definitions for
PDZ file parsing, including magic numbers, field sizes, and format specifications.
"""

"""
PDZ Tool version
"""
VERSION = "0.2.0"

"""
Supported PDZ versions
{
    record_type: version
}
"""
SUPPORTED_PDZ_VERSIONS = {
    25: "pdz25",
    257: "pdz24"
}

# =============================================================================
# PARSING CONSTANTS
# =============================================================================

"""
Common field sizes and magic numbers used throughout the parsing code
"""

# System time and date constants
SYSTEM_TIME_SIZE = 16  # Windows SYSTEMTIME structure size in bytes
SYSTEM_TIME_FIELDS = 8  # Number of unsigned short fields in SYSTEMTIME

# String encoding constants
WCHAR_SIZE = 2  # Wide character size in bytes (UTF-16)

# Channel and spectrum data constants
BYTES_PER_CHANNEL_PDZ24 = 4  # PDZ24 spectrum data: 4 bytes per channel (signed int)
BYTES_PER_CHANNEL_PDZ25 = 4  # PDZ25 spectrum data: 4 bytes per channel (unsigned long)
BYTES_PER_FLOAT = 4  # Float data: 4 bytes per float value

# PDZ file structure constants
PDZ_HEADER_SIZE = 6  # PDZ file header size (2 bytes type + 4 bytes length)
PDZ_VERSION_SIZE = 2  # PDZ version identifier size in bytes

# Record type and data length field sizes
RECORD_TYPE_SIZE = 2  # Record type field size in bytes
DATA_LENGTH_SIZE = 4  # Data length field size in bytes

# =============================================================================
# FIELD TYPE CONSTANTS
# =============================================================================

"""
Field type identifiers for parsing
"""

class FieldTypes:
    """Constants for different field types used in parsing."""
    STRUCT = 'struct'
    SPECTRUM_DATA = 'spectrum_data'
    WCHAR_T = 'wchar_t'
    SYSTEM_TIME = 'system_time'
    BYTES = 'bytes'
    SKIP = 'skip'
    FLOAT_ARRAY = 'float_array'

# =============================================================================
# PDZ FORMAT SPECIFICATIONS
# =============================================================================

"""
Format specifications for different PDZ versions
"""

class PDZ24Config:
    """Configuration constants specific to PDZ24 format."""
    FILE_HEADER_SIZE = 6  # First 6 bytes as file header
    SPECTRUM_FORMAT_CHAR = 'i'  # Signed integer format for spectrum data
    
class PDZ25Config:
    """Configuration constants specific to PDZ25 format."""
    SPECTRUM_FORMAT_CHAR = 'L'  # Unsigned long format for spectrum data
    FILTER_COUNT = 3  # Number of filters in filter block
    
# =============================================================================
# ERROR MESSAGES
# =============================================================================

"""
Standard error messages for consistent error handling
"""

class ErrorMessages:
    """Standard error messages used throughout the parsing code."""
    INSUFFICIENT_BYTES = "Insufficient bytes for field '{field_name}': required {required}, available {available}"
    INVALID_RECORD_TYPE = "Unknown record type: {record_type}"
    PARSING_FAILED = "Failed to parse {format} file: {error}"
    FILE_NOT_FOUND = "PDZ file not found: {file_path}"
    INVALID_FILE_PATH = "Invalid file path: {file_path}"
    STRUCT_ERROR = "Struct unpacking error in field '{field_name}': {error}"
    
# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

"""
Constants for data validation and bounds checking
"""

class ValidationLimits:
    """Limits for data validation."""
    MAX_CHANNELS = 8192  # Maximum expected number of channels
    MAX_STRING_LENGTH = 1024  # Maximum expected string length
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # Maximum expected image size (10MB)
    MAX_RECORD_SIZE = 100 * 1024 * 1024  # Maximum expected record size (100MB)