from abc import ABC, abstractmethod
import json
import csv
import os

from .utils import read_pdz_file, get_pdz_version, flatten_system_date_time

class BasePDZTool(ABC):
    def __init__(self, file_path: str, verbose: bool = False, debug: bool = False):
        self.verbose = verbose
        self.debug = debug
        self.file_path = file_path
        self.pdz_file_name: str = os.path.splitext(os.path.basename(self.file_path))[0]
        self.pdz_bytes: bytes = read_pdz_file(file_path)
        self.record_types: list = self.get_record_types()
        self.record_names: list = [record['record_name'] for record in self.record_types]
        self.pdz_version: str = get_pdz_version(self.pdz_bytes)


        if self.debug:
            self.verbose = True
            self._print_verbose("Debug mode enabled.")
            self._print_verbose(f"PDZ Version: {self.pdz_version}")

        self.parsed_data: dict = {}

    def _print_verbose(self, message):
        """Helper method to print messages when verbose is enabled."""
        if self.verbose:
            print(message)

    @abstractmethod
    def get_record_types(self):
        """Abstract method to extract blocks from the PDZ file."""
        pass

    @abstractmethod
    def parse(self):
        """Abstract method to parse the PDZ file. and set the parsed_data attribute."""
        pass

    def to_json(self):
        """Transform the parsed data to JSON."""
        try:
            return json.dumps(self.parsed_data, indent=4)
        except Exception as e:
            self._print_verbose(f"Error transforming data to JSON: {e}")


    def save_json(self, output_dir: str = '.'):
        """Save the parsed data to a JSON file."""
        try:
            output_file = os.path.join(output_dir, f"{self.pdz_file_name}.json")
            with open(output_file, 'w') as f:
                f.write(self.to_json())
            self._print_verbose(f"Data saved to {output_file}")
        except Exception as e:
            self._print_verbose(f"Error saving data to JSON: {e}")

    def save_csv(self, record_names: list[str] = ["XRF Spectrum"], output_dir: str = '.', output_suffix: str = None):
        """
        Save the parsed data to a CSV file for the records specified by `record_names`.
        :param record_names: list[str] Default is ["XRF Spectrum"], can be ["File Header", "XRF Instrument", etc.]
        :param output_dir: str Default is '.', the current directory.
        :param output_suffix: str If None (default), sets to `_lowercase_record_name` if one record name provided and `_multiple_records` if multiple record names provided.
        :return:
        """
        """
        Process a specific node in the data and write it to a CSV file.

        Args:
        - data (dict): The parsed data structure.
        - record_names (list[str]): The specific record name to process (e.g., ["File Header", "XRF Spectrum"]).
        - output_dir (str): Directory to save the output CSV file.
        - output_suffix (str): String to append to filename of CSV file before `.csv`.
        """
        if not record_names:
            self._print_verbose(f"No CSV file created because no record names were provided")
            return

        record_data = {}

        for record_name in record_names:
            if record_name not in self.parsed_data:
                raise ValueError(f"Node '{record_name}' not found in the provided data. File: {self.file_path}")
            record_data.update(self.parsed_data[record_name])

        if output_suffix is None:
            if len(record_names) == 1:
                output_suffix = f"_{record_names[0].replace(' ', '_').lower()}"  # Use record name as suffix if only one provided
            else:
                output_suffix = "_multiple_records"

        output_file = os.path.join(output_dir, f"{self.pdz_file_name}{output_suffix}.csv")

        with open(output_file, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)

            # Write all other key-value pairs first
            for key, value in record_data.items():
                if key == "acquisition_date_time":
                    # Combine acquisition_date_time into a single string
                    date_time_str = flatten_system_date_time(value)
                    csvwriter.writerow([key, date_time_str])
                elif key == "spectrum_data":
                    # Skip for now, handled separately
                    continue
                else:
                    csvwriter.writerow([key, value])

            # Handle spectrum_data as channel number and count
            if "spectrum_data" in record_data:
                csvwriter.writerow(['channel_number', 'channel_count'])
                spectrum_data = record_data["spectrum_data"]
                for index, count in enumerate(spectrum_data, start=1):
                    csvwriter.writerow([index, count])

        self._print_verbose(f"CSV file created: {output_file}")
