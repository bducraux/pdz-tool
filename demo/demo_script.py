import os
import traceback

from pdz_tool import PDZTool

def main():
    # Debugging
    debug_mode = True

    # Directory containing the demo PDZ files
    demo_dir = os.path.dirname(__file__)

    # Example files
    pdz_files = [
        os.path.join(demo_dir, 'pdz24_example.pdz'),
        os.path.join(demo_dir, 'pdz24_example_2.pdz'),
        os.path.join(demo_dir, 'pdz25_example.pdz'),
        os.path.join(demo_dir, 'pdz25_example_2.pdz'),
        os.path.join(demo_dir, 'pdz25_example_images.pdz')
    ]

    # Process each PDZ file
    for pdz_file in pdz_files:
        try:
            print(f"Processing {pdz_file}...")

            pdz_tool = PDZTool(pdz_file, verbose=True, debug=debug_mode)
            pdz_file_name = os.path.splitext(os.path.basename(pdz_file))[0]

            print(f"PDZ Version: {pdz_tool.pdz_version}")
            print(f"PDZ Bytes: {pdz_tool.pdz_bytes[:10]}...")
            print(f"PDZ Record Types Count: {len(pdz_tool.record_types)}")

            print("Parsing file...")
            parsed_pdz = pdz_tool.parse()  # dict with parsed pdz data

            parsed_json = pdz_tool.to_json()
            if parsed_json:
                print(f"Parsed pdz JSON: {parsed_json[0:100]}...")
                print("Saving JSON...")
                pdz_tool.save_json(output_dir=demo_dir + "/output")

            print("Saving CSV for XRF Spectrum...")
            print(f"Possible Record Names: {pdz_tool.record_names}")
            pdz_tool.save_csv(output_dir=demo_dir + "/output")  # use include_channel_start_kev=True to add calculated column for spectra

            print("Saving CSV for File Header and XRF Instrument...")
            pdz_tool.save_csv(output_dir=demo_dir + "/output", record_names=['File Header', 'XRF Instrument'], output_suffix="_header_and_instrument")

            image_record = parsed_pdz.get('Image Details', 0)
            if image_record:
                print(f"Saving {image_record['num_images']} images as JPEGs...")
                pdz_tool.save_images(
                    output_dir=demo_dir + "/output",
                    output_suffix='-')  # filename-0.jpeg, filename-1.jpeg, etc.


        except Exception as e:
            print(f"An error occurred while processing {pdz_file}: {e}")
            if debug_mode:
                traceback.print_exc()
            continue

if __name__ == '__main__':
    main()