import os
import pytest
import tempfile
import json
from pdz_tool.pdz_tool import PDZTool
from pdz_tool.base_tool import BasePDZTool
from pdz_tool.pdz25_tool import PDZ25Tool
from pdz_tool.pdz24_tool import PDZ24Tool

# Directory containing the demo PDZ files
DEMO_DIR = os.path.join(os.path.dirname(__file__), '..', 'demo')


def test_pdz25_example():
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')
    pdz_tool = PDZTool(pdz_file)

    assert pdz_tool.version == "pdz25"
    blocks = pdz_tool.parse()

    # Ensure all blocks are parsed
    assert len(blocks) == 10

    assert blocks['File Header']['file_type_id'] == 'pdz25'

    # Ensure Spectrum data is parsed
    xrf_spectrum = blocks['XRF Spectrum']

    assert xrf_spectrum['channels'] == 2048
    assert xrf_spectrum['ev_per_channel'] == 20.0

    spectrum_data = xrf_spectrum['spectrum_data']
    assert len(spectrum_data) == 2048


def test_pdz25_example_dual_phase():
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example_dual_phase.pdz')
    pdz_tool = PDZTool(pdz_file)

    assert pdz_tool.version == "pdz25"
    blocks = pdz_tool.parse()

    # Ensure all blocks are parsed
    assert len(blocks) == 11

    assert blocks['File Header']['file_type_id'] == 'pdz25'

    # Ensure Spectrum data is parsed
    xrf_spectrum = blocks['XRF Spectrum']

    # Ensure the two phases are parsed
    assert len(xrf_spectrum) == 2

    # Phase 0
    assert xrf_spectrum[0]['channels'] == 2048
    assert xrf_spectrum[0]['ev_per_channel'] == 20.015518188476562

    spectrum_data = xrf_spectrum[0]['spectrum_data']
    assert len(spectrum_data) == 2048

    # Phase 1
    assert xrf_spectrum[1]['channels'] == 2048
    assert xrf_spectrum[1]['ev_per_channel'] == 20.015518188476562

    spectrum_data = xrf_spectrum[1]['spectrum_data']
    assert len(spectrum_data) == 2048

def test_pdz24_example():
    pdz_file = os.path.join(DEMO_DIR, 'pdz24_example.pdz')
    pdz_tool = PDZTool(pdz_file)

    assert pdz_tool.version == "pdz24"
    blocks = pdz_tool.parse()
    assert len(blocks) == 2

    assert blocks['File Header']['version'] == 23

    xrf_spectrum = blocks['XRF Spectrum']
    assert xrf_spectrum['num_channels'] == 2048
    assert xrf_spectrum['ev_per_channel'] == 20.085

    spectrum_data = xrf_spectrum['spectrum_data']
    assert len(spectrum_data) == 2048


# Error Handling Tests
def test_file_not_found():
    """Test that FileNotFoundError is raised for non-existent files."""
    with pytest.raises(FileNotFoundError, match="PDZ file not found"):
        PDZTool("non_existent_file.pdz")


def test_empty_file_path():
    """Test that ValueError is raised for empty file path."""
    with pytest.raises(ValueError, match="File path cannot be empty"):
        PDZTool("")


def test_directory_instead_of_file():
    """Test that ValueError is raised when path is a directory."""
    with pytest.raises(ValueError, match="Path is not a file"):
        PDZTool(DEMO_DIR)


def test_invalid_pdz_file():
    """Test handling of invalid PDZ file content."""
    with tempfile.NamedTemporaryFile(suffix='.pdz', delete=False) as temp_file:
        temp_file.write(b"invalid content")
        temp_file.flush()
        
        try:
            # Should raise ValueError for an unknown PDZ version
            with pytest.raises(ValueError, match="Unknown PDZ version"):
                PDZTool(temp_file.name)
        finally:
            os.unlink(temp_file.name)


# Refactored Methods Tests
def test_collect_record_data():
    """Test the _collect_record_data method."""
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')
    tool = PDZTool(pdz_file)
    tool.parse()
    
    # Test collecting a single record
    record_data = tool._collect_record_data(['XRF Spectrum'])
    assert 'channels' in record_data
    assert 'spectrum_data' in record_data
    
    # Test collecting multiple records
    record_data = tool._collect_record_data(['File Header', 'XRF Spectrum'])
    assert 'file_type_id' in record_data  # From File Header
    assert 'channels' in record_data      # From XRF Spectrum


def test_collect_record_data_invalid_record():
    """Test _collect_record_data with an invalid record name."""
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')
    tool = PDZTool(pdz_file)
    tool.parse()
    
    with pytest.raises(ValueError, match="Node 'Invalid Record' not found"):
        tool._collect_record_data(['Invalid Record'])


def test_determine_csv_output_file():
    """Test the _determine_csv_output_file method."""
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')
    tool = PDZTool(pdz_file)
    
    # Test single record name
    output_file = tool._determine_csv_output_file('.', None, ['XRF Spectrum'])
    assert output_file.endswith('_xrf_spectrum.csv')
    
    # Test multiple record names
    output_file = tool._determine_csv_output_file('.', None, ['File Header', 'XRF Spectrum'])
    assert output_file.endswith('_multiple_records.csv')
    
    # Test custom suffix
    output_file = tool._determine_csv_output_file('.', '_custom', ['XRF Spectrum'])
    assert output_file.endswith('_custom.csv')


def test_csv_export_functionality():
    """Test CSV export functionality with the refactored methods."""
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')
    tool = PDZTool(pdz_file)
    tool.parse()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test CSV export
        tool.save_csv(['XRF Spectrum'], output_dir=temp_dir)
        
        # Check that the CSV file was created
        csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
        assert len(csv_files) == 1
        
        # Verify CSV content has the expected structure
        csv_file_path = os.path.join(temp_dir, csv_files[0])
        with open(csv_file_path, 'r') as f:
            content = f.read()
            assert 'channels' in content
            assert 'spectrum_data' not in content  # Should be replaced with channel data
            assert 'channel_number' in content
            assert 'channel_count' in content


def test_json_export_functionality():
    """Test JSON export functionality."""
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')
    tool = PDZTool(pdz_file)
    tool.parse()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test JSON export
        tool.save_json(output_dir=temp_dir)
        
        # Check that JSON file was created
        json_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
        assert len(json_files) == 1
        
        # Verify JSON content is valid
        json_file_path = os.path.join(temp_dir, json_files[0])
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            assert 'File Header' in data
            assert 'XRF Spectrum' in data


def test_type_hints_compatibility():
    """Test that type hints don't break functionality."""
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')
    
    # Should work with proper types
    tool = PDZTool(pdz_file, verbose=True, debug=False)
    assert isinstance(tool.version, str)
    
    parsed_data = tool.parse()
    assert isinstance(parsed_data, dict)
    
    # Test return type of get_images_bytes
    tool.parse()  # Ensure data is parsed
    images = tool.get_images_bytes()
    assert isinstance(images, list)


def test_image_extraction_functionality():
    """Test image extraction from PDZ files with image data."""
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example_images.pdz')
    tool = PDZTool(pdz_file)
    tool.parse()
    
    # Test get_images_bytes method
    images = tool.get_images_bytes()
    assert isinstance(images, list)
    
    # If images are present, they should be bytes objects
    if len(images) > 0:
        for image in images:
            assert isinstance(image, bytes)
            assert len(image) > 0
            # Check for common image file headers
            # JPEG files start with 0xFFD8
            # PNG files start with 0x89504E47
            assert image[:2] == b'\xFF\xD8' or image[:4] == b'\x89PNG'


def test_save_images_functionality():
    """Test saving images to files."""
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example_images.pdz')
    tool = PDZTool(pdz_file)
    tool.parse()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test save_images method
        tool.save_images(output_dir=temp_dir, output_suffix='_test')
        
        # Check if image files were created
        image_files = [f for f in os.listdir(temp_dir) if f.endswith('.jpeg')]
        
        # Verify files were created
        images = tool.get_images_bytes()
        expected_count = len(images)
        assert len(image_files) == expected_count
        
        # If images were saved, verify file contents
        if len(image_files) > 0:
            for i, image_file in enumerate(sorted(image_files)):
                file_path = os.path.join(temp_dir, image_file)
                assert os.path.exists(file_path)
                assert os.path.getsize(file_path) > 0
                
                # Verify file content matches original bytes
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    assert file_content == images[i]


def test_get_images_bytes_no_parsing():
    """Test get_images_bytes before parsing returns empty list."""
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')
    tool = PDZTool(pdz_file)
    
    # Should return empty list when called before parsing (parsed_data is empty dict)
    images = tool.get_images_bytes()
    assert images == []


def test_image_extraction_no_images():
    """Test image extraction from PDZ files without image data."""
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')  # No images in this file
    tool = PDZTool(pdz_file)
    tool.parse()
    
    # Should return empty list for files without images
    images = tool.get_images_bytes()
    assert images == []


def test_save_images_no_images():
    """Test save_images when no images are present."""
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')  # No images in this file
    tool = PDZTool(pdz_file)
    tool.parse()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Should not create any files when no images are present
        tool.save_images(output_dir=temp_dir)
        
        # Check that no image files were created
        image_files = [f for f in os.listdir(temp_dir) if f.endswith('.jpeg')]
        assert len(image_files) == 0


def test_image_extraction_different_formats():
    """Test image extraction works with different PDZ file formats."""
    # Test PDZ25 format
    pdz25_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')
    tool25 = PDZTool(pdz25_file)
    tool25.parse()
    images25 = tool25.get_images_bytes()
    assert isinstance(images25, list)
    
    # Test PDZ24 format (likely no images, but should not error)
    pdz24_file = os.path.join(DEMO_DIR, 'pdz24_example.pdz')
    tool24 = PDZTool(pdz24_file)
    tool24.parse()
    images24 = tool24.get_images_bytes()
    assert isinstance(images24, list)