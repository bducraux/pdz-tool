# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.5] - 2025-09-18

### Fixed
- **CLI Bug Fixes**: Fixed critical runtime errors in CLI that were preventing proper execution after the v0.2.4 release
- **Mutable Default Argument**: Fixed bug in `save_csv()` method that could cause unpredictable CLI behavior
- **Image Processing**: Fixed runtime error in `get_images_bytes()` method that could crash the CLI when processing certain PDZ files
- **Exception Handling**: Fixed undefined variable references in error handling that masked real CLI errors
- **CLI Image Extraction**: Fixed CLI to automatically detect and extract embedded images from PDZ files

### Added
- **Enhanced Image Processing**: Comprehensive image handling capabilities with metadata extraction and smart filename generation
  - New `has_images()` method to check for embedded images
  - New `get_image_metadata()` method to extract image dimensions, annotations, and details
  - Enhanced `save_images()` method with automatic directory creation, annotation-based filenames, and detailed verbose output
- **File Summary System**: Complete file analysis and reporting functionality
  - New `get_summary()` method returns structured analysis of PDZ file contents
  - New `print_summary()` method provides formatted summary with file info, record types, multiphase detection, and content analysis
- **Modern Path Handling**: Migrated to `pathlib.Path` for all file operations with automatic directory creation
- **Enhanced Error Handling**: Improved type safety and defensive programming throughout the codebase

### Improved
- **Multi-Phase Support**: Enhanced multiphase detection and processing with better error messages
- **File Operations**: UTF-8 encoding for all text file operations and robust error handling
- **JSON Serialization**: Added `default=str` parameter to handle complex data types in JSON export
- **Code Quality**: Comprehensive type hints, better validation, and consistent naming conventions
- **CLI Integration**: All new features are automatically available through the CLI interface

### Technical Details
- Fixed `save_csv()` mutable default parameter: `record_names: List[str] = ["XRF Spectrum"]` → `record_names: Optional[List[str]] = None`
- Added comprehensive image processing with metadata support for dimensions, annotations, and file sizes
- Implemented file summary system with multiphase detection and content analysis
- Enhanced path handling using `pathlib.Path` with automatic directory creation
- Improved exception handling with proper variable initialization
- All multiphase functionality remains unchanged and working correctly

### Image Processing Features
- **Smart Filename Generation**: Automatically includes image annotations in filenames when available
- **Detailed Metadata**: Extracts image dimensions, annotations, and validates image data integrity
- **Verbose Output**: Shows image dimensions, file sizes, and annotations during processing
- **Format Support**: Configurable image format output (defaults to JPEG)

### File Summary Features
- **Comprehensive Analysis**: File info, version, size, record counts, and content detection
- **Multi-Phase Detection**: Automatically identifies and reports multiphase measurements
- **Spectrum Analysis**: Detailed voltage, current, and channel information for each phase
- **Image Analysis**: Reports image count, dimensions, and annotations when present

## [0.2.4] - 2025-09-18

### Fixed
- **Dual Phase Support**: Fixed a critical issue where dual-phase PDZ files would only parse the last phase, overwriting data from previous phases
- PDZ25 parser now correctly handles multiple occurrences of the same record type by storing them in arrays
- All phases are now preserved with their respective XRF Spectrum data (voltage, current, counts, etc.)
- Multiple Filter Layers and Calculated Results Details are now properly maintained

### Technical Details
- Modified `PDZ25Tool.parse()` method to detect and handle multiple record type occurrences
- When multiple records of the same type are found, they are automatically converted to Python lists
- Maintains backward compatibility with single-phase files
- Affects record types: XRF Spectrum (Type 3), Calculated Results Details (Type 6), Filter Layers (Type 11)

### Acknowledgments
- **Special thanks to Evan Sivil** for reporting the dual-phase issue and providing the sample PDZ file (`pdz25_example_dual_phase.pdz`) that enabled this fix
- This enhancement ensures proper analysis of complex samples with multiple measurement phases

## [0.2.3] - 2024-09-14

### Added
- **Comprehensive Type Hints**: Added type annotations throughout the entire codebase for better IDE support and code safety
- **New FieldParser Class**: Extracted shared field parsing utilities into dedicated `FieldParser` class
- **Expanded Test Suite**: Added comprehensive test coverage (43 tests total, all passing)
- **New Test Module**: Added `tests/test_field_parser.py` for comprehensive field parsing functionality testing

### Changed
- **Code Quality Enhancements**: Method refactoring following the Single Responsibility Principle
- **Architecture Improvements**: Improved separation of concerns across parsing modules
- **Centralized Configuration**: Moved constants and field definitions to `config.py` for better maintainability
- **Error Handling**: Replaced broad exception handling with specific exception types and improved error messages

### Technical Improvements
- **base_tool.py**: Enhanced type hints, refactored `save_csv()` method, improved file validation and path checking
- **pdz25_tool.py**: Integrated shared field parser, refactored parsing logic for better maintainability
- **pdz24_tool.py**: Integrated shared field parser with PDZ24-specific error handling
- **config.py**: Expanded configuration constants, added validation limits and error message templates

### Quality Assurance
- ✅ All existing API methods are preserved (full backward compatibility)
- ✅ 100% test success rate (43/43 tests passing)
- ✅ Comprehensive documentation with standardized docstrings
- ✅ No breaking changes to public interfaces

## [0.2.2] - 2025-02-06

### Added
- **Enhanced CSV Exports**: Added `channel_start_kev` as a calculated column for spectra in CSV exports
- Improved data usability with precise energy calibration information

### Acknowledgments
- Thanks to [@larsmaxfield](https://github.com/larsmaxfield) for implementing the enhancement in PR #8

## [0.2.1] - 2024-12-02

### Added
- **Image Handling**: New `save_images` and `get_image_bytes` methods for handling embedded images
- **Enhanced CSV Export**: Modified `save_csv` to accept a list of record names for exporting multiple records into a single CSV file
- Improved handling of image bytes with better PDZ compatibility

### Fixed
- **Verbose & Debug Mode**: Fixed issue where `verbose` and `debug` parameters weren't properly passed to parent classes in `PDZ25Tool` and `PDZ24Tool` initializations
- **Image Compatibility**: Improved handling of image bytes with new demo examples

### Acknowledgments
- Welcome to the new contributor [@larsmaxfield](https://github.com/larsmaxfield) for multiple contributions (PRs #2, #4, #6)

## [0.2.0] - 2024-10-04

### Added
- **Command Line Interface (CLI)**: Complete CLI implementation with `pdz-tool` command
- **Flexible Output Options**: Support for JSON, CSV, or both output formats
- **CLI Arguments**: 
  - `file_path` (required): Path to the PDZ file to be parsed
  - `--output-dir`: Specify output directory (defaults to current directory)
  - `--output-format`: Choose between `json`, `csv`, or `all` (default)
  - `--verbose`: Enable verbose mode for detailed processing logs
  - `--debug`: Enable debug mode with detailed PDZ structure information
  - `--version`: Display current version

### Improved
- **Enhanced User Interaction**: Easy parsing and format selection through CLI
- **Debug and Verbose Modes**: Improved debugging capabilities and informative logging
- **Error Handling**: Better error handling for parsing PDZ files without crashes
- **Data Formatting**: Fixed minor issues with CSV and JSON output formatting

### Documentation
- Updated `README.md` with CLI usage and options
- Added examples for effective CLI usage

## [0.1.0] - 2024-10-03

### Added
- **Initial Release**: First official release of pdz-tool
- **PDZ File Parsing**: Support for PDZ24 and PDZ25 file formats
- **Data Export**: Ability to save parsed data into JSON or CSV formats
- **Logging Options**: Verbose and debug modes for troubleshooting
- **Python 3.11+ Support**: Compatible with modern Python versions

### Features
- Parse PDZ files and extract key data and attributes
- Convert to CSV or JSON for easy analysis
- Flexible data export options
- Comprehensive error handling
