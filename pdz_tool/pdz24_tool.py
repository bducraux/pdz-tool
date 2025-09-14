import struct
import traceback
from typing import List, Dict, Any, Union, Optional, Tuple

from .base_tool import BasePDZTool
from .field_parser import PDZ24FieldParser

class PDZ24Tool(BasePDZTool):
    RECORDS = {
        0: {
            "name": 'File Header',
            "fields": [
                ('file_type', 'h'), # Short (2 bytes)
                ('version', 'i'),  # Integer (4 bytes)
            ]
        },
        1: {
            "name": 'XRF Spectrum',
            "fields": [
                ('num_channels', 'h'),  # Short (2 bytes) - Number of channels
                ('skip', '42s'),  # Skip 42 bytes
                ('ev_per_channel', 'd'),  # Double (8 bytes)
                ('skip', '104s'),  # Skip 104 bytes
                ('xray_voltage_kv', 'f'),  # Float (4 bytes)
                ('xray_filament_current', 'f'),  # Float (4 bytes)
                ('skip', '184s'),  # Skip 184 bytes
                ('live_time', 'f'),  # Float (4 bytes)
                # The 'remaining_data' here represents the dynamic spectrum data
                ('spectrum_data', 'Z'),  # Remaining data
            ]
        },
    }

    def __init__(self, file_path: str, verbose: bool = False, debug: bool = False) -> None:
        super().__init__(file_path, verbose, debug)
        self._field_parser = PDZ24FieldParser(verbose=verbose, debug=debug)

    def get_record_types(self) -> List[Dict[str, Any]]:
        """
        Extracts blocks from PDZ 24 format and splits into two records:
        - The first 6 bytes as record_type 0.
        - The remaining bytes as record_type 1.
        """
        total_length = len(self.pdz_bytes)
        record_types = []

        # Ensure we have at least 6 bytes to extract the first record
        if total_length < 6:
            self._print_verbose("Insufficient bytes for reading the first 6-byte header.")
            return record_types

        # Extract the first 6 bytes as the first record
        first_record_bytes = self.pdz_bytes[:6]
        record_types.append({
            'record_type': 0,
            'record_name': 'File Header',
            'data_length': 6,
            'bytes': first_record_bytes
        })

        # Remaining bytes are treated as the second record
        remaining_bytes = self.pdz_bytes[6:]
        remaining_length = total_length - 6

        if remaining_length > 0:
            record_types.append({
                'record_type': 1,
                'record_name': 'XRF Spectrum',
                'data_length': remaining_length,
                'bytes': remaining_bytes
            })
        else:
            self._print_verbose("No remaining bytes for the second record.")

        return record_types

    def parse_record_type(self, record_type: int, block_bytes: bytes) -> Union[str, Dict[str, Any]]:
        """
        Parse a specific record type.
        :param record_type: int Record type Id that is being parsed
        :param block_bytes: bytes Block data
        :return:
        """
        fields = self.RECORDS.get(record_type, {}).get('fields', [])
        if not fields:
            return "No fields to parse"

        total_byte_length = len(block_bytes)
        offset = 0
        result = {}

        for field_name, field_type in fields:
            if offset >= total_byte_length:
                self._print_verbose(f"Warning: Reached end of data before parsing {field_name}")
                break

            try:
                # Use shared field parser with PDZ24-specific error handling
                field_value, field_size = self._field_parser.parse_field_with_error_codes(
                    field_name, field_type, block_bytes, offset, result
                )
                
                if field_value is None and field_size == -1:
                    # Error occurred during parsing
                    break
                elif field_value is None and field_size == 0:
                    # Skip field, just update offset
                    offset += field_size if field_size > 0 else struct.calcsize(field_type)
                    continue
                else:
                    # Normal field parsing
                    result[field_name] = field_value
                    offset += field_size

            except Exception as e:
                self._print_verbose(f"Error parsing field {field_name}: {e}")
                if self.debug:
                    traceback.print_exc()
                break

        return result

    def parse(self) -> Optional[Dict[str, Any]]:
        """
        Parse the PDZ file and set the parsed data.
        :return:
        """
        try:
            parsed_data = {}
            for record in self.record_types:
                record_type = record['record_type']
                block_bytes = record['bytes']
                record_type_name = self.RECORDS.get(record_type, {}).get('name', 'Unknown')

                self._print_verbose(f"Parsing record type: {record_type} - {record_type_name}")

                parsed_record_type = self.parse_record_type(record_type, block_bytes)

                parsed_data[record_type_name] = parsed_record_type

            self.parsed_data = parsed_data

            return self.parsed_data
        except (struct.error, ValueError) as e:
            self._print_verbose(f"Error parsing PDZ24 file structure: {e}")
            if self.debug:
                traceback.print_exc()
            return None
        except (KeyError, AttributeError) as e:
            self._print_verbose(f"Error accessing PDZ24 record data: {e}")
            if self.debug:
                traceback.print_exc()
            return None
        except Exception as e:
            self._print_verbose(f"Unexpected error parsing PDZ24 file: {e}")
            if self.debug:
                traceback.print_exc()
            return None
