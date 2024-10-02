import os
from pdz_tool import PDZTool

def main():
    # Directory containing the demo PDZ files
    demo_dir = os.path.dirname(__file__)

    # Example files
    pdz_files = [
        os.path.join(demo_dir, 'pdz25_example.pdz'),
    ]

    # Process each PDZ file
    for pdz_file in pdz_files:
        print(f"Processing {pdz_file}...")

        pdz_tool = PDZTool(pdz_file, verbose=True)
        pdz_file_name = os.path.splitext(os.path.basename(pdz_file))[0]

        print(f"PDZ Version: {pdz_tool.pdz_version}")
        print(f"PDZ Bytes: {pdz_tool.pdz_bytes[:10]}...")

        print("Parsing file...")
        pdz_tool.parse()

        print(f"Parsed data JSON: {pdz_tool.to_json()}")
        print("Saving JSON...")
        pdz_tool.save_json(output_dir=demo_dir + "/output")

        print("Saving CSV for XRF Spectrum...")
        pdz_tool.save_csv(output_dir=demo_dir + "/output")

        print("Saving CSV for XRF Instrument...")
        pdz_tool.save_csv(record_name="XRF Instrument", output_dir=demo_dir + "/output")

if __name__ == '__main__':
    main()