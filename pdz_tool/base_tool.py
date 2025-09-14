from abc import ABC, abstractmethod
import json
import csv
import os
from typing import Dict, List, Optional, Any, Union

from .utils import read_pdz_file, get_pdz_version, flatten_system_date_time

class BasePDZTool(ABC):
    def __init__(self, file_path: str, verbose: bool = False, debug: bool = False):
        self.verbose = verbose
        self.debug = debug
        
        # Validate file path
        if not file_path:
            raise ValueError("File path cannot be empty")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDZ file not found: {file_path}")
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
        
        self.file_path = file_path
        self.pdz_file_name: str = os.path.splitext(os.path.basename(self.file_path))[0]
        
        try:
            self.pdz_bytes: bytes = read_pdz_file(file_path)
        except IOError as e:
            raise IOError(f"Failed to read PDZ file '{file_path}': {e}")
        
        try:
            self.record_types: list = self.get_record_types()
            self.record_names: list = [record['record_name'] for record in self.record_types]
            self.pdz_version: str = get_pdz_version(self.pdz_bytes)
        except Exception as e:
            raise ValueError(f"Failed to parse PDZ file structure '{file_path}': {e}")


        if self.debug:
            self.verbose = True
            self._print_verbose("Debug mode enabled.")
            self._print_verbose(f"PDZ Version: {self.pdz_version}")

        self.parsed_data: dict = {}

    def _print_verbose(self, message: str) -> None:
        """Helper method to print messages when verbose is enabled."""
        if self.verbose:
            print(message)

    @property
    def version(self) -> str:
        """Return the PDZ version for compatibility with tests."""
        return self.pdz_version

    @abstractmethod
    def get_record_types(self) -> List[Dict[str, Any]]:
        """Abstract method to extract blocks from the PDZ file."""
        pass

    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """Abstract method to parse the PDZ file. and set the parsed_data attribute."""
        pass

    def to_json(self) -> Optional[str]:
        """Transform the parsed data to JSON."""
        try:
            return json.dumps(self.parsed_data, indent=4)
        except (TypeError, ValueError, OverflowError) as e:
            self._print_verbose(f"Error serializing data to JSON: {e}")
            return None

    def get_images_bytes(self) -> List[bytes]:
        """Get bytes of images as a list."""
        if hasattr(self, 'parsed_data'):
            image_record = self.parsed_data.get('Image Details', 0)
            images_bytes = []
            if image_record:
                for image in image_record.get('images'):
                    images_bytes.append(image['image'])
            else:
                self._print_verbose(f"No images found: {self.file_path}")
            return images_bytes
        else:
            raise ValueError(f"PDZ data not yet parsed and set. Run method `.parse()` before attempting to get images.")

    def save_json(self, output_dir: str = '.') -> None:
        """Save the parsed data to a JSON file."""
        try:
            output_file = os.path.join(output_dir, f"{self.pdz_file_name}.json")
            json_data = self.to_json()
            if json_data is None:
                self._print_verbose("Cannot save JSON: data serialization failed")
                return
            with open(output_file, 'w') as f:
                f.write(json_data)
            self._print_verbose(f"Data saved to {output_file}")
        except (OSError, IOError) as e:
            self._print_verbose(f"Error writing JSON file '{output_file}': {e}")
        except PermissionError as e:
            self._print_verbose(f"Permission denied writing JSON file '{output_file}': {e}")

    def save_csv(
            self,
            record_names: List[str] = ["XRF Spectrum"],
            output_dir: str = '.',
            output_suffix: Optional[str] = None,
            include_channel_start_kev: bool = False
            ) -> None:
        """Save the parsed data to a CSV file for the records specified by record_names.
        
        Args:
            record_names: List of record names to include. Defaults to ["XRF Spectrum"].
            output_dir: Directory to save the CSV file. Defaults to current directory.
            output_suffix: Custom suffix for filename. If None, uses record name or "_multiple_records".
            include_channel_start_kev: Whether to include calculated channel start keV values.
        """
        if not record_names:
            self._print_verbose(f"No CSV file created because no record names were provided")
            return

        # Collect and validate record data
        record_data = self._collect_record_data(record_names)
        
        # Determine output file path
        output_file = self._determine_csv_output_file(output_dir, output_suffix, record_names)
        
        # Write CSV content
        self._write_csv_content(output_file, record_data, include_channel_start_kev)
        
        self._print_verbose(f"CSV file created: {output_file}")

    def _collect_record_data(self, record_names: List[str]) -> Dict[str, Any]:
        """Collect and validate record data from parsed_data."""
        record_data = {}
        for record_name in record_names:
            if record_name not in self.parsed_data:
                raise ValueError(f"Node '{record_name}' not found in the provided data. File: {self.file_path}")
            record_data.update(self.parsed_data[record_name])
        return record_data

    def _determine_csv_output_file(self, output_dir: str, output_suffix: Optional[str], record_names: List[str]) -> str:
        """Determine the output file path for CSV."""
        if output_suffix is None:
            if len(record_names) == 1:
                output_suffix = f"_{record_names[0].replace(' ', '_').lower()}"
            else:
                output_suffix = "_multiple_records"
        return os.path.join(output_dir, f"{self.pdz_file_name}{output_suffix}.csv")

    def _write_csv_content(self, output_file: str, record_data: Dict[str, Any], include_channel_start_kev: bool) -> None:
        """Write the CSV content to file."""
        with open(output_file, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            
            # Write metadata fields
            self._write_csv_metadata(csvwriter, record_data)
            
            # Write spectrum data if present
            if "spectrum_data" in record_data:
                self._write_csv_spectrum_data(csvwriter, record_data, include_channel_start_kev)

    def _write_csv_metadata(self, csvwriter: Any, record_data: Dict[str, Any]) -> None:
        """Write metadata fields to CSV."""
        for key, value in record_data.items():
            if key == "acquisition_date_time":
                date_time_str = flatten_system_date_time(value)
                csvwriter.writerow([key, date_time_str])
            elif key == "spectrum_data":
                continue  # Skip spectrum_data, handled separately
            else:
                csvwriter.writerow([key, value])

    def _write_csv_spectrum_data(self, csvwriter: Any, record_data: Dict[str, Any], include_channel_start_kev: bool) -> None:
        """Write spectrum data to CSV."""
        spectrum_data = record_data["spectrum_data"]
        
        if include_channel_start_kev:
            csvwriter.writerow(['channel_number', 'channel_start_kev (calculated)', 'channel_count'])
            channel_start_kev = record_data.get("channel_start", 0) / 1000
            kev_per_channel = record_data.get("ev_per_channel", 0) / 1000
            for index, count in enumerate(spectrum_data, start=1):
                csvwriter.writerow([
                    index,
                    channel_start_kev + (index - 1) * kev_per_channel,
                    count
                ])
        else:
            csvwriter.writerow(['channel_number', 'channel_count'])
            for index, count in enumerate(spectrum_data, start=1):
                csvwriter.writerow([index, count])

    def save_images(self, output_dir: str = '.', output_suffix: str = '_') -> None:
        """Save the parsed images to individual JPEG files.
        
        Args:
            output_dir: Directory to save the images as JPEG files. Defaults to current directory.
            output_suffix: String to append to filename of JPEG file before `#.jpeg`. Defaults to '_'.
        """
        try:
            images_bytes = self.get_images_bytes()
            n = len(images_bytes)
            for i, image_bytes in enumerate(images_bytes):
                output_file = os.path.join(output_dir, f"{self.pdz_file_name}{output_suffix}{i}.jpeg")
                try:
                    with open(output_file, 'wb') as f:
                        f.write(image_bytes)
                    self._print_verbose(f"Image {i+1} of {n} saved to {output_file}")
                except (OSError, IOError) as e:
                    self._print_verbose(f"Error writing image file '{output_file}': {e}")
                except PermissionError as e:
                    self._print_verbose(f"Permission denied writing image file '{output_file}': {e}")
        except ValueError as e:
            self._print_verbose(f"Error retrieving image data: {e}")
