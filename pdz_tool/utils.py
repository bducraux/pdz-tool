import struct
from .config import SUPPORTED_PDZ_VERSIONS

def read_pdz_file(file_path):
    """Reads the PDZ file and returns its bytes."""
    with open(file_path, 'rb') as opened_file:
        return opened_file.read()

def get_pdz_version(pdz_bytes):
    """Extracts the PDZ version from the first two bytes of `pdz_bytes`."""
    if len(pdz_bytes) < 2:
        raise ValueError("Insufficient bytes for PDZ version")

    version = struct.unpack_from('<H', pdz_bytes, offset=0)[0]

    return SUPPORTED_PDZ_VERSIONS.get(version, "unknown")

def decode_system_time(system_time_bytes):
    """
    Decode SYSTEMTIME structure into a dictionary.
    """
    system_time_format = '<8H'  # 8 unsigned shorts
    fields = struct.unpack(system_time_format, system_time_bytes)

    system_time = {
        'year': fields[0],
        'month': fields[1],
        'day': fields[3],
        'hour': fields[4],
        'minute': fields[5],
        'second': fields[6]
    }
    return system_time

def flatten_system_date_time(date_time_data: dict):
    """
    Converts a nested acquisition date/time dict into a single formatted string.
    """
    if isinstance(date_time_data, str):  # Already flattened
        return date_time_data

    return f"{date_time_data['year']}-{date_time_data['month']:02}-{date_time_data['day']:02} " \
           f"{date_time_data['hour']:02}:{date_time_data['minute']:02}:{date_time_data['second']:02}"
