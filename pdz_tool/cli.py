import argparse
import os
from pdz_tool import PDZTool
from .config import VERSION

def print_verbose(msg, verbose=False):
    if verbose:
        print(msg)

def parse_pdz_file(file_path, output_dir, verbose=False, debug=False):
    try:
        print_verbose(f"PDZ Tool v{VERSION}", verbose=verbose)
        print_verbose(f"Processing {file_path}...", verbose=verbose)

        pdz_tool = PDZTool(file_path, verbose=verbose, debug=debug)

        print_verbose("Parsing file...", verbose=verbose)
        parsed_pdz = pdz_tool.parse()

        print_verbose(f"Saving JSON to {output_dir}...", verbose=verbose)
        pdz_tool.save_json(output_dir=output_dir)

        print_verbose("Saving CSV for XRF Spectrum to CSV...", verbose=verbose)
        pdz_tool.save_csv(output_dir=output_dir)

        print(f"File {file_path} processed successfully.")
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="PDZ Tool CLI - Parse and convert PDZ files to JSON and CSV formats.")

    parser.add_argument('file_path', type=str, help='Path to the PDZ file')
    parser.add_argument('--output-dir', type=str, default=os.getcwd(), help='Output directory for JSON and CSV files')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--version', action='version', version=f'PDZ Tool v{VERSION} CLI')

    args = parser.parse_args()

    parse_pdz_file(args.file_path, args.output_dir, verbose=args.verbose, debug=args.debug)

if __name__ == '__main__':
    main()
