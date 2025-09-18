import argparse
import os
from pdz_tool import PDZTool
from .config import VERSION

def print_verbose(msg, verbose=False):
    if verbose:
        print(msg)

def parse_pdz_file(file_path, output_dir, output_format, verbose=False, debug=False):
    try:
        print(f"PDZ Tool v{VERSION} CLI\n")

        if debug:
            verbose = True
            print("Debug mode enabled.")


        print_verbose(f"Processing {file_path} ...", verbose=verbose)

        pdz_tool = PDZTool(file_path, verbose=verbose, debug=debug)

        print_verbose("Parsing file ...", verbose=verbose)
        parsed_pdz = pdz_tool.parse()

        if debug:
            print_verbose(f"PDZ Version: {pdz_tool.pdz_version}", verbose=verbose)
            print_verbose(f"PDZ Bytes: {pdz_tool.pdz_bytes[:10]}...", verbose=verbose)
            print_verbose(f"PDZ Record Types Count: {len(pdz_tool.record_types)}", verbose=verbose)
            print_verbose(f"Record Names: {pdz_tool.record_names}", verbose=verbose)

        # Check for images and extract them automatically
        if pdz_tool.has_images():
            print_verbose("Extracting embedded images ...", verbose=verbose)
            saved_images = pdz_tool.save_images(output_dir=output_dir)
            if saved_images:
                print(f"Extracted {len(saved_images)} image(s) to {output_dir}")
                if verbose:
                    for img_path in saved_images:
                        print(f"  - {os.path.basename(img_path)}")
        else:
            print_verbose("No embedded images found in PDZ file", verbose=verbose)

        if output_format == 'json' or output_format == 'all':
            print_verbose(f"Saving JSON to {output_dir} ...", verbose=verbose)
            pdz_tool.save_json(output_dir=output_dir)

        if output_format == 'csv' or output_format == 'all':
            print_verbose("Saving XRF Spectrum to CSV ...", verbose=verbose)
            pdz_tool.save_csv(output_dir=output_dir)

        # Print summary information if verbose
        if verbose:
            print_verbose("\n=== File Summary ===", verbose=True)
            pdz_tool.print_summary()

        print(f"File {file_path} processed successfully.")
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="PDZ Tool CLI - Parse and convert PDZ files to JSON and CSV formats.")

    parser.add_argument('file_path', type=str, help='Path to the PDZ file')
    parser.add_argument('--output-dir', type=str, default=os.getcwd(), help='Output directory for parsed files')
    parser.add_argument('--output-format', type=str, default='all', choices=['json', 'csv', 'all'], help='Output format for parsed files')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--version', action='version', version=f'PDZ Tool v{VERSION} CLI')

    args = parser.parse_args()

    parse_pdz_file(args.file_path, args.output_dir, args.output_format, verbose=args.verbose, debug=args.debug)

if __name__ == '__main__':
    main()
