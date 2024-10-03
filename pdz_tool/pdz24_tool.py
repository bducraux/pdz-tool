import struct
import traceback

from .base_tool import BasePDZTool

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

    def __init__(self, file_path: str, verbose: bool = False, debug: bool = False):
        super().__init__(file_path)
        self.verbose = verbose
        self.debug = debug

    def get_record_types(self):
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

    def parse_record_type(self, record_type: int, block_bytes: bytes):
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
                # Skip bytes based on the 's' indicator in the format
                if field_name == 'skip':
                    size = struct.calcsize(field_type)
                    offset += size
                    continue

                # Handle dynamic spectrum data
                if field_name == 'spectrum_data':
                    num_channels = result.get('num_channels', 0)
                    size = num_channels * 4  # Assuming each intensity value is a 4-byte float

                    if offset + size > total_byte_length:
                        self._print_verbose(f"Error: Insufficient bytes for {field_name}")
                        break

                    # Read the spectrum data as a list of floats
                    fmt = f'<{num_channels}i'
                    spectrum_data = struct.unpack_from(fmt, block_bytes, offset)
                    result['spectrum_data'] = list(spectrum_data)
                    offset += size
                    continue

                # Regular struct unpacking
                fmt = '<' + field_type
                size = struct.calcsize(fmt)

                if offset + size > total_byte_length:
                    self._print_verbose(f"Error: Insufficient bytes for {field_name}")
                    break

                value = struct.unpack_from(fmt, block_bytes, offset)[0]
                result[field_name] = value
                offset += size

            except Exception as e:
                self._print_verbose(f"Error parsing field {field_name}: {e}")
                if self.debug:
                    traceback.print_exc()
                break

        return result

    def parse(self):
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
        except Exception as e:
            self._print_verbose(f"Error parsing PDZ file: {e}")
            if self.debug:
                traceback.print_exc()
            return None
