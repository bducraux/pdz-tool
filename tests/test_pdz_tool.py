import os
import pytest
from pdz_tool.pdz_tool import PDZTool

# Directory containing the demo PDZ files
DEMO_DIR = os.path.join(os.path.dirname(__file__), '..', 'demo')


def test_pdz25_example():
    pdz_file = os.path.join(DEMO_DIR, 'pdz25_example.pdz')
    pdz_tool = PDZTool(pdz_file)

    assert pdz_tool.version == "pdz25"
    blocks = pdz_tool.parse()
    assert len(blocks) > 0  # Ensure at least one block is parsed


def test_pdz24_example():
    pdz_file = os.path.join(DEMO_DIR, 'pdz24_example.pdz')
    pdz_tool = PDZTool(pdz_file)

    assert pdz_tool.version == "pdz24"
    with pytest.raises(NotImplementedError):
        pdz_tool.parse()
