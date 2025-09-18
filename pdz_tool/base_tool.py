import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any

from .utils import read_pdz_file, get_pdz_version, flatten_system_date_time


class BasePDZTool(ABC):
    def __init__(self, file_path: str, verbose: bool = False, debug: bool = False):
        self.verbose = verbose
        self.debug = debug
        
        # Validate file path
        self._validate_file_path(file_path)

        self.file_path = Path(file_path)
        self.pdz_file_name: str = self.file_path.stem

        try:
            self.pdz_bytes: bytes = read_pdz_file(str(self.file_path))
        except IOError as e:
            raise IOError(f"Failed to read PDZ file '{self.file_path}': {e}")

        try:
            self.record_types: List[Dict[str, Any]] = self.get_record_types()
            self.record_names: List[str] = [record['record_name'] for record in self.record_types]
            self.pdz_version: str = get_pdz_version(self.pdz_bytes)
        except Exception as e:
            raise ValueError(f"Failed to parse PDZ file structure '{self.file_path}': {e}")

        if self.debug:
            self.verbose = True
            self._print_verbose("Debug mode enabled.")
            self._print_verbose(f"PDZ Version: {self.pdz_version}")

        self.parsed_data: Dict[str, Any] = {}

    @staticmethod
    def _validate_file_path(file_path: str) -> None:
        """Validate the provided file path."""
        if not file_path:
            raise ValueError("File path cannot be empty")

        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"PDZ file not found: {file_path}")
        if not path_obj.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

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
        """Abstract method to parse the PDZ file and set the parsed_data attribute."""
        pass

    def to_json(self) -> Optional[str]:
        """Transform the parsed data to JSON."""
        try:
            return json.dumps(self.parsed_data, indent=4, default=str)
        except (TypeError, ValueError, OverflowError) as e:
            self._print_verbose(f"Error serializing data to JSON: {e}")
            return None

    def has_images(self) -> bool:
        """Check if the PDZ file contains images."""
        if not hasattr(self, 'parsed_data') or not self.parsed_data:
            return False

        image_record = self.parsed_data.get('Image Details')
        if not image_record or not isinstance(image_record, dict):
            return False

        images = image_record.get('images', [])
        return isinstance(images, list) and len(images) > 0

    def get_images_bytes(self) -> List[bytes]:
        """Get bytes of images as a list."""
        if not hasattr(self, 'parsed_data') or not self.parsed_data:
            return []  # Return an empty list when no data is parsed yet

        image_record = self.parsed_data.get('Image Details')
        images_bytes = []

        if image_record and isinstance(image_record, dict):
            images = image_record.get('images', [])
            if isinstance(images, list):
                for i, image in enumerate(images):
                    if isinstance(image, dict) and 'image' in image:
                        image_data = image['image']
                        if isinstance(image_data, bytes):
                            images_bytes.append(image_data)
                        else:
                            self._print_verbose(f"Warning: Image {i} data is not bytes, skipping")
                    else:
                        self._print_verbose(f"Warning: Image {i} is not a valid dict with 'image' key, skipping")
            else:
                self._print_verbose("Warning: 'images' field is not a list")
        else:
            self._print_verbose(f"No images found in: {self.file_path}")

        return images_bytes

    def get_image_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata for all images in the PDZ file."""
        if not hasattr(self, 'parsed_data') or not self.parsed_data:
            raise ValueError("PDZ data not yet parsed and set. Run method `.parse()` before attempting to get image metadata.")

        image_record = self.parsed_data.get('Image Details')
        metadata_list = []

        if image_record and isinstance(image_record, dict):
            images = image_record.get('images', [])
            if isinstance(images, list):
                for i, image in enumerate(images):
                    if isinstance(image, dict):
                        metadata = {
                            'index': i,
                            'x_dimension': image.get('x_dimension', 'Unknown'),
                            'y_dimension': image.get('y_dimension', 'Unknown'),
                            'annotation': image.get('annotation', ''),
                            'image_length': image.get('image_length', 0),
                            'has_image_data': 'image' in image and isinstance(image['image'], bytes)
                        }
                        metadata_list.append(metadata)

        return metadata_list

    def save_json(self, output_dir: str = '.') -> None:
        """Save the parsed data to a JSON file."""
        output_file = ""
        try:
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)

            output_file = output_dir_path / f"{self.pdz_file_name}.json"
            json_data = self.to_json()

            if json_data is None:
                self._print_verbose("Cannot save JSON: data serialization failed")
                return

            output_file.write_text(json_data, encoding='utf-8')
            self._print_verbose(f"Data saved to {output_file}")

        except (OSError, IOError) as e:
            self._print_verbose(f"Error writing JSON file '{output_file}': {e}")
        except PermissionError as e:
            self._print_verbose(f"Permission denied writing JSON file '{output_file}': {e}")

    def save_csv(
            self,
            record_names: Optional[List[str]] = None,
            output_dir: str = '.',
            output_suffix: Optional[str] = None,
            include_channel_start_kev: bool = False
            ) -> None:
        """Save the parsed data to a CSV file for the records specified by record_names.
        
        Args:
            record_names: List of record names to include. Defaults to ["XRF Spectrum"].
            output_dir: Directory to save the CSV file. Defaults to the current directory.
            output_suffix: Custom suffix for filename. If None, uses record name or "_multiple_records".
            include_channel_start_kev: Whether to include calculated channel start keV values.
        """
        if record_names is None:
            record_names = ["XRF Spectrum"]

        if not record_names:
            self._print_verbose("No CSV file created because no record names were provided")
            return

        # Ensure output directory exists
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        # Check if we have multiphase data that should be split into separate files
        has_multi_phase = self._has_multi_phase_data(record_names)

        if has_multi_phase:
            self._save_csv_multi_phase(record_names, str(output_dir_path), output_suffix, include_channel_start_kev)
        else:
            # Original single file logic
            record_data = self._collect_record_data(record_names)
            output_file = self._determine_csv_output_file(str(output_dir_path), output_suffix, record_names)
            self._write_csv_content(output_file, record_data, include_channel_start_kev)
            self._print_verbose(f"CSV file created: {output_file}")

    def _has_multi_phase_data(self, record_names: List[str]) -> bool:
        """Check if any of the record names contains multiphase data (list format)."""
        for record_name in record_names:
            if record_name in self.parsed_data:
                record_content = self.parsed_data[record_name]
                if isinstance(record_content, list) and len(record_content) > 1:
                    return True
        return False

    def _save_csv_multi_phase(
            self,
            record_names: List[str], 
            output_dir: str, 
            output_suffix: Optional[str], 
            include_channel_start_kev: bool
            ) -> None:
        """Save multiphase data to separate CSV files for each phase."""
        for record_name in record_names:
            if record_name not in self.parsed_data:
                raise ValueError(f"Record '{record_name}' not found in the parsed data. File: {self.file_path}")

            record_content = self.parsed_data[record_name]
            
            if isinstance(record_content, list):
                # Create a separate CSV file for each phase
                for phase_index, phase_data in enumerate(record_content):
                    if isinstance(phase_data, dict):
                        # Determine a phase-specific output file
                        phase_number = phase_data.get('phase_number', phase_index)
                        phase_suffix = f"_phase_{phase_number}"

                        if output_suffix:
                            phase_output_suffix = f"{output_suffix}{phase_suffix}"
                        else:
                            base_suffix = f"_{record_name.replace(' ', '_').lower()}"
                            phase_output_suffix = f"{base_suffix}{phase_suffix}"
                        
                        output_file = Path(output_dir) / f"{self.pdz_file_name}{phase_output_suffix}.csv"

                        # Write CSV content for this phase
                        self._write_csv_content(str(output_file), phase_data, include_channel_start_kev)
                        self._print_verbose(f"CSV file created for phase {phase_number}: {output_file}")
                    else:
                        self._print_verbose(f"Warning: Expected dict in phase data for '{record_name}', got {type(phase_data)}")
            elif isinstance(record_content, dict):
                # Single phase data - use original logic
                output_file = self._determine_csv_output_file(output_dir, output_suffix, record_names)
                self._write_csv_content(output_file, record_content, include_channel_start_kev)
                self._print_verbose(f"CSV file created: {output_file}")

    def _collect_record_data(self, record_names: List[str]) -> Dict[str, Any]:
        """Collect and validate record data from parsed_data."""
        record_data = {}
        for record_name in record_names:
            if record_name not in self.parsed_data:
                raise ValueError(f"Node '{record_name}' not found in the provided data. File: {self.file_path}")

            record_content = self.parsed_data[record_name]
            
            # Handle multiphase data: if it's a list, merge all phases
            if isinstance(record_content, list):
                for phase_data in record_content:
                    if isinstance(phase_data, dict):
                        record_data.update(phase_data)
                    else:
                        self._print_verbose(f"Warning: Expected dict in phase data for '{record_name}', got {type(phase_data)}")
            elif isinstance(record_content, dict):
                record_data.update(record_content)
            else:
                self._print_verbose(f"Warning: Expected dict or list for '{record_name}', got {type(record_content)}")
        return record_data

    def _determine_csv_output_file(self, output_dir: str, output_suffix: Optional[str], record_names: List[str]) -> str:
        """Determine the output file path for CSV."""
        if output_suffix is None:
            if len(record_names) == 1:
                output_suffix = f"_{record_names[0].replace(' ', '_').lower()}"
            else:
                output_suffix = "_multiple_records"
        return str(Path(output_dir) / f"{self.pdz_file_name}{output_suffix}.csv")

    def _write_csv_content(self, output_file: str, record_data: Dict[str, Any], include_channel_start_kev: bool) -> None:
        """Write the CSV content to the file."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)

                # Write metadata fields
                self._write_csv_metadata(csvwriter, record_data)

                # Write spectrum data if present
                if "spectrum_data" in record_data:
                    self._write_csv_spectrum_data(csvwriter, record_data, include_channel_start_kev)
        except (OSError, IOError) as e:
            self._print_verbose(f"Error writing CSV file '{output_file}': {e}")

    @staticmethod
    def _write_csv_metadata(csvwriter: Any, record_data: Dict[str, Any]) -> None:
        """Write metadata fields to CSV."""
        for key, value in record_data.items():
            if key == "acquisition_date_time":
                date_time_str = flatten_system_date_time(value)
                csvwriter.writerow([key, date_time_str])
            elif key == "spectrum_data":
                continue  # Skip spectrum_data, handled separately
            else:
                csvwriter.writerow([key, value])

    @staticmethod
    def _write_csv_spectrum_data(csvwriter: Any, record_data: Dict[str, Any], include_channel_start_kev: bool) -> None:
        """Write spectrum data to CSV."""
        spectrum_data = record_data.get("spectrum_data", [])

        if not spectrum_data:
            return

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

    def save_images(
            self,
            output_dir: str = '.',
            output_suffix: str = '_image_',
            image_format: str = 'jpeg'
            ) -> List[str]:
        """Save the parsed images to individual image files.

        Args:
            output_dir: Directory to save the images. Defaults to the current directory.
            output_suffix: String to append to filename before image number. Defaults to '_image_'.
            image_format: Image format extension (without a dot). Defaults to 'jpeg'.

        Returns:
            List of file paths where images were saved.
        """
        saved_files = []

        try:
            # Ensure output directory exists
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)

            if not self.has_images():
                self._print_verbose(f"No images found in: {self.file_path}")
                return saved_files

            images_bytes = self.get_images_bytes()
            image_metadata = self.get_image_metadata()

            self._print_verbose(f"Found {len(images_bytes)} image(s) to save")

            for i, (image_bytes, metadata) in enumerate(zip(images_bytes, image_metadata)):
                # Create filename with metadata if available
                annotation = metadata.get('annotation', '').strip()
                if annotation:
                    # Clean annotation for use in filename
                    clean_annotation = ''.join(c for c in annotation if c.isalnum() or c in (' ', '-', '_')).strip()
                    clean_annotation = clean_annotation.replace(' ', '_')[:50]  # Limit length
                    filename = f"{self.pdz_file_name}{output_suffix}{i}_{clean_annotation}.{image_format}"
                else:
                    filename = f"{self.pdz_file_name}{output_suffix}{i}.{image_format}"

                output_file = output_dir_path / filename

                try:
                    output_file.write_bytes(image_bytes)
                    saved_files.append(str(output_file))

                    # Print detailed info about saved image
                    dimensions = f"{metadata.get('x_dimension', '?')}x{metadata.get('y_dimension', '?')}"
                    size_kb = len(image_bytes) / 1024
                    self._print_verbose(f"Image {i+1}/{len(images_bytes)} saved: {output_file}")
                    self._print_verbose(f"  Dimensions: {dimensions}, Size: {size_kb:.1f} KB")
                    if annotation:
                        self._print_verbose(f"  Annotation: {annotation}")

                except (OSError, IOError) as e:
                    self._print_verbose(f"Error writing image file '{output_file}': {e}")
                except PermissionError as e:
                    self._print_verbose(f"Permission denied writing image file '{output_file}': {e}")

        except ValueError as e:
            self._print_verbose(f"Error retrieving image data: {e}")

        return saved_files

    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the PDZ file contents."""
        if not hasattr(self, 'parsed_data') or not self.parsed_data:
            raise ValueError("PDZ data not yet parsed and set. Run method `.parse()` before attempting to get summary.")

        summary = {
            'file_info': {
                'filename': self.pdz_file_name,
                'file_path': str(self.file_path),
                'file_size_bytes': len(self.pdz_bytes),
                'pdz_version': self.pdz_version
            },
            'record_summary': {
                'total_records': len(self.record_types),
                'record_types_found': list(set(record['record_name'] for record in self.record_types)),
                'multi_phase_records': []
            },
            'content_summary': {
                'has_spectrum_data': 'XRF Spectrum' in self.parsed_data,
                'has_images': self.has_images(),
                'has_calculated_results': 'Calculated Results' in self.parsed_data,
                'has_grade_id': 'Grade ID Results' in self.parsed_data
            }
        }

        # Check for multiphase data
        for record_name, record_data in self.parsed_data.items():
            if isinstance(record_data, list) and len(record_data) > 1:
                summary['record_summary']['multi_phase_records'].append({
                    'record_name': record_name,
                    'phase_count': len(record_data)
                })

        # Add image details if present
        if self.has_images():
            image_metadata = self.get_image_metadata()
            summary['content_summary']['image_details'] = {
                'image_count': len(image_metadata),
                'images': image_metadata
            }

        # Add spectrum details if present
        spectrum_data = self.parsed_data.get('XRF Spectrum')
        if spectrum_data:
            if isinstance(spectrum_data, list):
                summary['content_summary']['spectrum_details'] = {
                    'phase_count': len(spectrum_data),
                    'phases': [
                        {
                            'phase_number': phase.get('phase_number', i),
                            'tube_voltage': phase.get('tube_voltage'),
                            'tube_current': phase.get('tube_current'),
                            'channels': len(phase.get('spectrum_data', []))
                        }
                        for i, phase in enumerate(spectrum_data)
                        if isinstance(phase, dict)
                    ]
                }
            elif isinstance(spectrum_data, dict):
                summary['content_summary']['spectrum_details'] = {
                    'phase_count': 1,
                    'tube_voltage': spectrum_data.get('tube_voltage'),
                    'tube_current': spectrum_data.get('tube_current'),
                    'channels': len(spectrum_data.get('spectrum_data', []))
                }

        return summary

    def print_summary(self) -> None:
        """Print a formatted summary of the PDZ file contents."""
        try:
            summary = self.get_summary()

            print(f"\n=== PDZ File Summary ===")
            print(f"File: {summary['file_info']['filename']}")
            print(f"Version: {summary['file_info']['pdz_version']}")
            print(f"Size: {summary['file_info']['file_size_bytes']:,} bytes")

            print(f"\n--- Records ---")
            print(f"Total records: {summary['record_summary']['total_records']}")
            print(f"Record types: {', '.join(summary['record_summary']['record_types_found'])}")

            if summary['record_summary']['multi_phase_records']:
                print(f"\n--- Multi-Phase Data ---")
                for mp_record in summary['record_summary']['multi_phase_records']:
                    print(f"  {mp_record['record_name']}: {mp_record['phase_count']} phases")

            print(f"\n--- Content ---")
            content = summary['content_summary']
            print(f"Has Spectrum: {'Yes' if content['has_spectrum_data'] else 'No'}")
            print(f"Has Images: {'Yes' if content['has_images'] else 'No'}")
            print(f"Has Calculated Results: {'Yes' if content['has_calculated_results'] else 'No'}")
            print(f"Has Grade ID: {'Yes' if content['has_grade_id'] else 'No'}")

            if content.get('spectrum_details'):
                spec_details = content['spectrum_details']
                print(f"\n--- Spectrum Details ---")
                if spec_details['phase_count'] > 1:
                    print(f"Phases: {spec_details['phase_count']}")
                    for phase in spec_details.get('phases', []):
                        print(f"  Phase {phase['phase_number']}: {phase['tube_voltage']}V, {phase['tube_current']}mA, {phase['channels']} channels")
                else:
                    print(f"Voltage: {spec_details.get('tube_voltage')}V")
                    print(f"Current: {spec_details.get('tube_current')}mA")
                    print(f"Channels: {spec_details.get('channels')}")

            if content.get('image_details'):
                img_details = content['image_details']
                print(f"\n--- Image Details ---")
                print(f"Images: {img_details['image_count']}")
                for img in img_details['images']:
                    dims = f"{img['x_dimension']}x{img['y_dimension']}"
                    annotation = img['annotation'] or 'No annotation'
                    print(f"  Image {img['index']}: {dims}, {annotation}")

            print(f"=" * 25)

        except Exception as e:
            self._print_verbose(f"Error generating summary: {e}")
