import struct
import traceback

from .base_tool import BasePDZTool
from .utils import decode_system_time, flatten_system_date_time

class PDZ25Tool(BasePDZTool):
    # Records for PDZ 25 format
    # { record_type: { name: str, fields: [(field_name, field_type), ...] } }
    # See /docs/pdz_version_25_file_format for more details
    RECORDS = {
        25: {
            "name": 'File Header',
            "fields": [
                ('file_type_id', 'wchar_t[5]'),   # wchar_t[5] (10 bytes)
                ('instrument_type', 'I'),  # unsigned int (4 byte)
            ]
        },
        1: {
            "name": 'XRF Instrument',
            "fields": [
                ('serial_number_length', 'I'),  # unsigned int (4 bytes)
                ('serial_number', 'wchar_t'),  # wchar_t[serial_number_length]
                ('build_number_length', 'I'),  # unsigned int (4 bytes)
                ('build_number', 'wchar_t'),  # wchar_t[build_number_length]
                ('tube_target_element', 'B'),  # byte (1 byte)
                ('anode_takeoff_angle', 'B'),  # byte (1 byte)
                ('sample_incidence_angle', 'B'),  # byte (1 byte)
                ('sample_takeoff_angle', 'B'),  # byte (1 byte)
                ('be_thickness', 'h'),  # short (2 bytes)
                ('detector_model_length', 'I'),  # unsigned int (4 bytes)
                ('detector_model', 'wchar_t'),  # wchar_t[detector_model_length]
                ('tube_type_length', 'I'),  # unsigned int (4 bytes)
                ('tube_type', 'wchar_t'),  # wchar_t[tube_type_length]
                ('hw_spot_size', 'B'),  # byte (1 byte)
                ('sw_spot_size', 'B'),  # byte (1 byte)
                ('collimator_type_length', 'I'),  # unsigned int (4 bytes)
                ('collimator_type', 'wchar_t'),  # wchar_t[collimator_type_length]
                ('num_versions', 'I'),  # unsigned int (4 bytes)
                ('sw_version_record_num', 'H'),  # unsigned short (2 bytes)
                ('sw_version_length', 'I'),  # unsigned int (4 bytes)
                ('sw_version', 'wchar_t'),  # wchar_t[sw_version_length]
                ('xilinx_version_record_num', 'H'),  # unsigned short (2 bytes)
                ('xilinx_fw_ver_length', 'I'),  # unsigned int (4 bytes)
                ('xilinx_fw_ver', 'wchar_t'),  # wchar_t[xilinx_fw_ver_length]
                ('sup_version_record_num', 'H'),  # unsigned short (2 bytes)
                ('sup_fw_ver_length', 'I'),  # unsigned int (4 bytes)
                ('sup_fw_ver', 'wchar_t'),  # wchar_t[sup_fw_ver_length]
                ('uup_version_record_num', 'H'),  # unsigned short (2 bytes)
                ('uup_fw_ver_length', 'I'),  # unsigned int (4 bytes)
                ('uup_fw_ver', 'wchar_t'),  # wchar_t[uup_fw_ver_length]
                ('xray_source_version_record_num', 'H'),  # unsigned short (2 bytes)
                ('xray_src_fw_ver_length', 'I'),  # unsigned int (4 bytes)
                ('xray_src_fw_ver', 'wchar_t'),  # wchar_t[xray_src_fw_ver_length]
                ('dpp_version_record_num', 'H'),  # unsigned short (2 bytes)
                ('dpp_fw_ver_length', 'I'),  # unsigned int (4 bytes)
                ('dpp_fw_ver', 'wchar_t'),  # wchar_t[dpp_fw_ver_length]
                ('header_version_record_num', 'H'),  # unsigned short (2 bytes)
                ('header_fw_ver_length', 'I'),  # unsigned int (4 bytes)
                ('header_fw_ver', 'wchar_t'),  # wchar_t[header_fw_ver_length]
                ('baseboard_version_record_num', 'H'),  # unsigned short (2 bytes)
                ('baseboard_fw_ver_length', 'I'),  # unsigned int (4 bytes)
                ('baseboard_fw_ver', 'wchar_t'),  # wchar_t[baseboard_fw_ver_length]
            ]
        },
        2: {
            "name": 'XRF Assay Summary',
            "fields": [
                ('number_of_phases', 'I'),  # unsigned int (4 bytes)
                ('raw_counts', 'L'),  # unsigned int (4 bytes)
                ('valid_counts', 'L'),  # unsigned int (4 bytes)
                ('valid_counts_in_range', 'L'),  # unsigned int (4 bytes)
                ('reset_counts', 'L'),  # unsigned int (4 bytes)
                ('total_real_time', 'f'),  # float (4 bytes)
                ('total_packet_time', 'f'),  # float (4 bytes)
                ('total_dead', 'f'),  # float (4 bytes)
                ('total_reset', 'f'),  # float (4 bytes)
                ('total_live', 'f'),  # float (4 bytes)
                ('elapsed_time', 'f'),  # float (4 bytes)
                ('application_name_length', 'I'),  # unsigned int (4 bytes)
                ('application_name', 'wchar_t'),  # wchar_t[application_name_length]
                ('application_part_number_length', 'I'),  # unsigned int (4 bytes)
                ('application_part_number', 'wchar_t'),  # wchar_t[application_part_number_length]
                ('user_id_length', 'I'),  # unsigned int (4 bytes)
                ('user_id', 'wchar_t'),  # wchar_t[user_id_length]
            ]
        },
        3: {
            "name": 'XRF Spectrum',
            "fields": [
                ('phase_number', 'I'),  # unsigned int (4 bytes)
                ('raw_counts', 'L'),  # unsigned long (4 bytes)
                ('valid_counts', 'L'),  # unsigned long (4 bytes)
                ('valid_counts_in_range', 'L'),  # unsigned long (4 bytes)
                ('reset_counts', 'L'),  # unsigned long (4 bytes)
                ('time_since_trigger', 'f'),  # float (4 bytes)
                ('total_packet_time', 'f'),  # float (4 bytes)
                ('total_dead', 'f'),  # float (4 bytes)
                ('total_reset', 'f'),  # float (4 bytes)
                ('total_live', 'f'),  # float (4 bytes)
                ('tube_voltage', 'f'),  # float (4 bytes)
                ('tube_current', 'f'),  # float (4 bytes)
                # Repeatable block for filters
                ('filters', {
                    'repeat': 3,  # We know there are exactly 3 filters to parse
                    'fields': [
                        ('filter_element', 'h'),  # short (2 bytes)
                        ('filter_thickness', 'h'),  # short (2 bytes)
                    ]
                }),
                ('filter_wheel_number', 'h'),  # short (2 bytes)
                ('detector_temp', 'f'),  # float (4 bytes)
                ('ambient_temp', 'f'),  # float (4 bytes)
                ('vacuum', 'l'),  # long (4 bytes)
                ('ev_per_channel', 'f'),  # float (4 bytes)
                ('gain_drift_algorithm', 'h'),  # short (2 bytes)
                ('channel_start', 'f'),  # float (4 bytes)
                ('acquisition_date_time', 'system_time'),  # SYSTEMTIME (16 bytes)
                ('atmospheric_pressure', 'f'),  # float (4 bytes)
                ('channels', 'h'),  # short (2 bytes)
                ('nose_temp', 'h'),  # short (2 bytes)
                ('environment', 'h'),  # short (2 bytes)
                ('illumination_length', 'I'),  # unsigned int (4 bytes)
                ('illumination', 'wchar_t'),  # wchar_t[illumination_length]
                ('normal_packet_start', 'h'),  # short (2 bytes)
                ('spectrum_data', 'spectrum_data')  # Special handling required
            ]
        },
        4: {
            "name": 'Raw XRF Spectrum Packet',
            "fields": [
                ('phase_number', 'I'),  # unsigned int (4 bytes)
                ('xilinx_fw_ver', 'B'),  # byte (1 byte)
                ('xilinx_fw_sub_ver', 'B'),  # byte (1 byte)
                ('packet_len', 'H'),  # unsigned short (2 bytes)
                ('time_since_trigger', 'L'),  # unsigned long (4 bytes)
                ('raw_count', 'L'),  # unsigned long (4 bytes)
                ('valid_count', 'L'),  # unsigned long (4 bytes)
                ('valid_count_in_range', 'L'),  # unsigned long (4 bytes)
                ('packet_time', 'L'),  # unsigned long (4 bytes)
                ('dead_time', 'L'),  # unsigned long (4 bytes)
                ('reset_time', 'L'),  # unsigned long (4 bytes)
                ('live_time', 'L'),  # unsigned long (4 bytes)
                ('service', 'L'),  # unsigned long (4 bytes)
                ('reset_count', 'H'),  # unsigned short (2 bytes)
                ('packet_count', 'H'),  # unsigned short (2 bytes)
                ('skip', '20s'),  # 20 bytes (unused data)
                ('xilinx_vars', '58s'),  # 58 bytes (internal state variables)
                ('detector_temp', 'h'),  # short (2 bytes) - divided by 2 for °C
                ('ambient_temp', 'H'),  # unsigned short (2 bytes) - divided by 10 for °F
                ('controller_fw_ver', 'B'),  # byte (1 byte)
                ('controller_fw_sub_ver', 'B'),  # byte (1 byte)
                ('total_raw_counts', 'L'),  # unsigned long (4 bytes)
                ('total_valid_counts', 'L'),  # unsigned long (4 bytes)
                ('total_valid_counts_in_range', 'L'),  # unsigned long (4 bytes)
                ('total_reset_counts', 'L'),  # unsigned long (4 bytes)
                ('total_time_since_trigger', 'f'),  # float (4 bytes)
                ('total_packet_time', 'f'),  # float (4 bytes)
                ('total_dead', 'f'),  # float (4 bytes)
                ('total_reset', 'f'),  # float (4 bytes)
                ('total_live', 'f'),  # float (4 bytes)
                ('spectrum_data', 'spectrum_data')  # Special handling for the array of data
            ]
        },
        5: {
            "name": 'Calculated Results',
            "fields": [
                ('analysis_mode', 'I'),  # unsigned int (4 bytes)
                ('analysis_type', 'I'),  # unsigned int (4 bytes)
                ('used_auto_cal_select', 'h'),  # short (2 bytes)
                ('result_type', 'h'),  # short (2 bytes)
                ('error_multiplier', 'H'),  # unsigned short (2 bytes)
                ('cal_file_length', 'I'),  # unsigned int (4 bytes)
                ('cal_file_name', 'wchar_t'),  # wchar_t[cal_file_length]
                ('cal_pkg_name_length', 'I'),  # unsigned int (4 bytes)
                ('cal_pkg_name', 'wchar_t'),  # wchar_t[cal_pkg_name_length]
                ('cal_pkg_pn_length', 'I'),  # unsigned int (4 bytes)
                ('cal_pkg_part_number', 'wchar_t'),  # wchar_t[cal_pkg_pn_length]
                ('type_std_set_name_length', 'I'),  # unsigned int (4 bytes)
                ('type_std_set_name', 'wchar_t')  # wchar_t[type_std_set_name_length]
            ]
        },
        6: {
            "name": 'Calculated Results Details',
            "fields": [
                ('name_length', 'I'),  # unsigned int (4 bytes)
                ('name', 'wchar_t'),  # wchar_t[name_length] - Unicode string of dynamic length
                ('atomic_number', 'I'),  # unsigned int (4 bytes)
                ('units', 'B'),  # byte (1 byte)
                ('result', 'f'),  # float (4 bytes)
                ('type_std_result', 'f'),  # float (4 bytes)
                ('error', 'f'),  # float (4 bytes)
                ('min', 'f'),  # float (4 bytes)
                ('max', 'f'),  # float (4 bytes)
                ('tramp', 'h'),  # short (2 bytes) - boolean flag
                ('nominal', 'h'),  # short (2 bytes) - boolean flag
            ]
        },
        7: {
            "name": 'Grade ID Results',
            "fields": [
                # Repeat Grade IDs - the fields are hard-coded because there's no count variable
                ('grades', {
                    'repeat': 3,  # We know there are exactly 3 Grade IDs to parse
                    'fields': [
                        ('grade_id_length', 'I'),  # Length of the Grade ID
                        ('grade_id', 'wchar_t'),   # Unicode string of Grade ID
                        ('confidence', 'f'),       # Confidence measure for this Grade ID
                    ]
                }),
                # Additional single fields
                ('match_spread_threshold', 'f'),  # float (4 bytes)
                ('process_tramp_elements', 'h'),  # short (2 bytes)
                ('nominal_chemistry', 'h'),       # short (2 bytes)

                # Repeat Grade Libraries based on `num_grade_libs`
                ('num_grade_libs', 'H'),  # unsigned short (2 bytes) - Number of Grade Libraries
                ('grade_libraries', {
                    'repeat': 'num_grade_libs',  # Repeat based on `num_grade_libs` count
                    'fields': [
                        ('grade_lib_file_name_length', 'I'),  # Length of Grade Library file name
                        ('grade_lib_file_name', 'wchar_t'),   # Unicode string of Grade Library file name
                        ('grade_lib_ver_length', 'I'),        # Length of Grade Library version
                        ('grade_lib_version', 'wchar_t'),     # Unicode string of Grade Library version
                    ]
                }),
            ]
        },
        8: {
            "name": 'Pass/Fail Results',
            "fields": [
                ('record_type', 'H'),  # unsigned short (2 bytes)
                ('data_length', 'I'),  # unsigned int (4 bytes)
                ('passed', 'H'),  # unsigned short (2 bytes)
                ('limit_file_name_length', 'I'),  # unsigned int (4 bytes)
                ('limit_file_name', 'wchar_t'),  # Unicode string of `limit_file_name_length`
                ('material_name_length', 'I'),  # unsigned int (4 bytes)
                ('material_name', 'wchar_t')  # Unicode string of `material_name_length`
            ]
        },
        9: {
            "name": 'User Custom Fields',
            "fields": [
        ('num_fields', 'h'),  # short (2 bytes)
        # This will loop over the `num_fields` count
        ('fields', {
            'repeat': 'num_fields',
            'fields': [
                ('field_name_length', 'I'),  # Length of the field name
                ('field_name', 'wchar_t'),  # Unicode string field name
                ('field_value_length', 'I'),  # Length of the field value
                ('field_value', 'wchar_t'),  # Unicode string field value
            ]
        })
    ]
        },
        10: {
            "name": 'Average Details',
            "fields": [
                ('num_assays', 'I'),
                ('assays', {
                    'repeat': 'num_assays',
                    'fields': [
                        ('assay_number', 'I'),
                    ]
                }),
            ]
        },
        11: {
            "name": 'Filter Layers',
            "fields": [
                ('phase_number', 'H'),  # unsigned short (2 bytes)
                ('layers_number', 'H'),  # unsigned short (2 bytes)
                ('filter_layer_element', 'H'),  # unsigned short array
                ('filter_layer_thickness', 'I'),  # unsigned int array
            ]
        },
        137: {
            "name": 'Image Details',
            "fields": [
                ('num_images', 'i'),
                ('images', {
                    'repeat': 'num_images',
                    'fields': [
                        ('image_length', 'I'),  # unsigned int (4 bytes) - length of the first image data
                        ('image', 'bytes'),  # image_length bytes - Image in JPEG format
                        ('x_dimension', 'I'),  # unsigned int (4 bytes) - Width
                        ('y_dimension', 'I'),  # unsigned int (4 bytes) - Height
                        ('annotation_length', 'I'),  # unsigned int (4 bytes) - Length of the annotation
                        ('annotation', 'wchar_t'),  # wchar_t[annotation_length] - Annotation text
                    ]
                }),

            ]
        },
        138: {
            "name": 'GPS Details',
            "fields": [
                ('gps_valid', 'i'),  # int (4 bytes) - indicates if GPS data is valid
                ('latitude', 'd'),  # double (8 bytes) - Latitude
                ('longitude', 'd'),  # double (8 bytes) - Longitude
                ('altitude', 'f'),  # float (4 bytes) - Altitude
            ]
        },
        139: {
            "name": 'Miscellaneous Information',
            "fields": [
                ('std_multiplier', 'i'),  # int (4 bytes) - 1-5
                ('active_cal_length', 'I'),  # unsigned int (4 bytes) - Unicode string length
                ('active_cal', 'wchar_t'),  # Unicode string
                ('sample_id_length', 'I'),  # unsigned int (4 bytes) - Unicode string length
                ('sample_id', 'wchar_t'),  # Unicode string
            ]
        },
        900: {
            "name": 'Trace Log',
            "fields": [
                ('log_length', 'I'),       # unsigned int (4 bytes) - Length of the trace log
                ('log', 'wchar_t'),    # Unicode string for the trace log contents
            ]
        },
        1001: {
            "name": 'Libs Alloy Results',
            "fields": [
                ('is_auto_selected', 'h'),  # bool (2 bytes)
                ('std_dev_multiplier', 'H'),  # unsigned short (2 bytes)
                ('library_name_length', 'I'),  # unsigned int (4 bytes)
                ('library_name', 'wchar_t'),  # wchar_t string
                ('created', 'system_time'),  # SYSTEMTIME (16 bytes)
                ('created_by_length', 'I'),  # unsigned int (4 bytes)
                ('created_by', 'wchar_t'),  # wchar_t string
                ('num_elements', 'h'), # short (2 bytes) - number of elements to repeat
                ('elements', {
                    'repeat': 'num_elements',
                    'fields': [
                        ('element_name', 'wchar_t'),
                        ('element_percentage', 'f'),
                        ('element_lod', 'f'),
                        ('element_std_dev', 'f'),
                        ('element_max', 'f'),
                        ('element_min', 'f'),
                    ]
                }),
            ]
        },
        1002: {
            "name": 'Libs Grade ID Results',
            "fields": [
                ('num_grade_ids', 'H'),  # unsigned short (2 bytes) - Number of Grade IDs
                ('grade_ids', {
                    'repeat': 'num_elements',
                    'fields': [
                        ('grade_id_length', 'I'),
                        ('grade_id', 'wchar_t'),
                        ('confidence', 'f'),
                    ]
                }),
                ('match_spread_threshold', 'f'),
                ('num_grade_libs', 'H'),  # unsigned short (2 bytes) - Number of Grade Libraries
                ('grade_libs', {
                    'repeat': 'num_grade_libs',
                    'fields': [
                        ('file_name_length', 'I'),
                        ('file_name', 'wchar_t'),
                        ('ver_length', 'I'),
                        ('version', 'wchar_t'),
                    ]
                }),

            ]
        },
        1003: {
            "name": 'Libs Alloy Method',
            "fields": [
                ('model_name_length', 'I'),  # unsigned int (4 bytes)
                ('model_name', 'wchar_t'),  # Model name from LID
                ('base_length', 'I'),  # unsigned int (4 bytes)
                ('base', 'wchar_t'),  # Base name
                ('integration_time', 'H'),  # unsigned int (2 bytes)
                ('created', 'system_time'),  # SYSTEMTIME (16 bytes)
                ('created_by_length', 'I'),  # unsigned int (4 bytes)
                ('created_by', 'wchar_t'),  # User name who created the method
            ]
        },
        1004: {
            "name": 'Libs Alloy Sample',
            "fields": [
                ('scan_index', 'Q'),  # long long (8 bytes)
                ('name_length', 'I'),  # unsigned int (4 bytes)
                ('name', 'wchar_t'),  # Sample name
                ('scan_id_length', 'I'),  # unsigned int (4 bytes)
                ('scan_id', 'wchar_t'),  # Saved for barcode use
                ('created', 'system_time'),  # SYSTEMTIME (16 bytes)
                ('created_by_length', 'I'),  # unsigned int (4 bytes)
                ('created_by', 'wchar_t'),  # User name who created the sample
                ('num_fields', 'h'),  # short (2 bytes) - Number of custom fields
                ('field_name_length', 'I'),  # unsigned int (4 bytes)
                ('field_name', 'wchar_t'),  # Name of the field
                ('field_value_length', 'I'),  # unsigned int (4 bytes)
                ('field_value', 'wchar_t'),  # Value of the field
                ('spectrum_data_length', 'I'),  # unsigned int (4 bytes)
                ('spectrum_data', 'float_array')  # Spectrum’s x and y values in format {x, y, x, y, ...}
            ]
        }
    }

    def __init__(self, file_path: str, verbose: bool = False, debug: bool = False):
        super().__init__(file_path, verbose, debug)

    def get_record_types(self):
        """
        Extracts blocks from PDZ 25 format.
        """
        offset = 0
        total_length = len(self.pdz_bytes)
        record_types = []

        while offset < total_length:
            # Ensure we have at least 6 bytes to read block type and size
            if offset + 6 > total_length:
                self._print_verbose("Insufficient bytes for reading block header.")
                break

            # Extract record_type (2 bytes) and data_length (4 bytes)
            try:
                record_type, data_length = struct.unpack_from('<HI', self.pdz_bytes, offset)
            except struct.error as e:
                self._print_verbose(f"Error unpacking block at offset {offset}: {e}")
                if self.debug:
                    traceback.print_exc()
                break

            self._print_verbose(f"Found block - Type: {record_type}, Size: {data_length}, Offset: {offset}")

            if data_length <= 0 or data_length > total_length:
                self._print_verbose(f"Invalid block size detected: {data_length} for block type {record_type}.")
                break

            offset += 6  # Move the offset to the start of the block data
            if offset + data_length > total_length:
                self._print_verbose(f"Insufficient bytes for block {record_type}: required {data_length}, available {total_length - offset}")
                break

            # Extract block data
            block_data = self.pdz_bytes[offset:offset + data_length]

            # Store the block info
            record_types.append({
                'record_type': record_type,
                'record_name': self.RECORDS.get(record_type, {}).get('name', f'Unknown Record Type {record_type}'),
                'data_length': data_length,
                'bytes': block_data
            })

            offset += data_length  # Move offset to the next block

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

        for field in fields:
            if offset >= total_byte_length:
                self._print_verbose(f"Warning: Reached end of data before parsing {field}")
                break

            field_name, field_type = field

            # Handle repeatable blocks if `field_type` is a dict
            if isinstance(field_type, dict):
                field_details = field_type
                repeat_count = field_details['repeat']

                # Resolve `repeat_count` if it's a string (dynamic count)
                if isinstance(repeat_count, str):
                    repeat_count = int(result.get(repeat_count, 0))

                if repeat_count == 0:
                    self._print_verbose(f"Skipping repeatable block {field_name} with {repeat_count} repeats")
                    continue

                sub_fields = field_details['fields']
                repeated_data = []

                for _ in range(repeat_count):
                    sub_result = {}
                    for sub_field_name, sub_field_type in sub_fields:
                        sub_value, sub_size = self._parse_field(sub_field_name, sub_field_type, block_bytes, offset,
                                                                sub_result)
                        if sub_value is None:
                            break
                        sub_result[sub_field_name] = sub_value
                        offset += sub_size
                    repeated_data.append(sub_result)

                # Store repeated data
                result[field_name] = repeated_data

                continue

            # Handle normal tuple field
            field_name, field_type = field

            # Use _parse_field for normal tuple fields
            field_value, field_size = self._parse_field(field_name, field_type, block_bytes, offset, result)
            if field_value is None:
                break
            result[field_name] = field_value
            offset += field_size

        return result

    def _parse_field(self, field_name, field_type, block_bytes, offset, result):
        total_byte_length = len(block_bytes)

        try:
            # Handle wchar_t strings
            if 'wchar_t' in field_type:
                if field_type == 'wchar_t':
                    length_field_name = field_name + '_length'
                    length = result.get(length_field_name, 0)
                    n_bytes = length * 2
                else:
                    length = int(field_type.split('[')[1].split(']')[0])
                    n_bytes = length * 2

                if offset + n_bytes > total_byte_length:
                    self._print_verbose(f"Error: Insufficient bytes for {field_name}")
                    return None, 0

                string_data_bytes = block_bytes[offset:offset + n_bytes]
                string_data = string_data_bytes.decode('utf-16').strip('\x00')
                return string_data, n_bytes

            # Handle system_time fields
            elif field_type == 'system_time':
                n_bytes = 16
                if offset + n_bytes > total_byte_length:
                    self._print_verbose(f"Error: Insufficient bytes for {field_name}")
                    return None, 0

                year, month, day_of_week, day, hour, minute, second, milliseconds = struct.unpack_from('<8H',
                                                                                                       block_bytes, offset)
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

            # Handle spectrum_data fields
            elif field_type == 'spectrum_data':
                num_channels = result.get('channels', 0)
                n_bytes = num_channels * 4  # 4 bytes per channel

                if offset + n_bytes > total_byte_length:
                    self._print_verbose(f"Error: Insufficient bytes for {field_name}")
                    return None, 0

                fmt = f'<{num_channels}L'  # Little-endian unsigned long array
                spectrum_data = struct.unpack_from(fmt, block_bytes, offset)
                return list(spectrum_data), n_bytes
            
            elif field_type == 'bytes':

                # Handle image bytes
                if field_name == 'image':
                    length_field_name = field_name + '_length'
                    length = result.get(length_field_name, 0)
                    n_bytes = length

                    if offset + n_bytes > total_byte_length:
                        self._print_verbose(f"Error: Insufficient bytes for {field_name}")
                        return None, 0
                    
                    jpg_bytes = block_bytes[offset:offset+n_bytes]
                    return jpg_bytes, len(jpg_bytes)

            # Regular struct unpacking
            fmt = '<' + field_type
            size = struct.calcsize(fmt)

            if offset + size > total_byte_length:
                self._print_verbose(f"Error: Insufficient bytes for {field_name}")
                return None, 0

            value = struct.unpack_from(fmt, block_bytes, offset)[0]
            return value, size

        except struct.error as e:
            self._print_verbose(f"Struct error in field {field_name}: {e}")
            if self.debug:
                traceback.print_exc()
            return None, 0

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
