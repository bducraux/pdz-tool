import struct
import os
from typing import Any, Union
from .pdz25_tool import PDZ25Tool
from .pdz24_tool import PDZ24Tool
from .utils import read_pdz_file, get_pdz_version


class PDZTool:
    def __init__(self, file_path: str, verbose: bool = False, debug: bool = False) -> None:
        self.file_path = file_path
        self.verbose = verbose
        self.tool: Union[PDZ25Tool, PDZ24Tool]

        # Validate file path before attempting to read
        if not file_path:
            raise ValueError("File path cannot be empty")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDZ file not found: {file_path}")
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")

        # Read bytes and detect version before instantiating the correct tool
        try:
            pdz_bytes = read_pdz_file(file_path)
        except IOError as e:
            raise IOError(f"Failed to read PDZ file '{file_path}': {e}")
        
        pdz_version = get_pdz_version(pdz_bytes)

        # Now instantiate the correct tool
        if pdz_version == "pdz25":
            self.tool = PDZ25Tool(file_path, verbose, debug)
        elif pdz_version == "pdz24":
            self.tool = PDZ24Tool(file_path, verbose, debug)
        else:
            raise ValueError(f"Unknown PDZ version: {pdz_version}")

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the appropriate tool.
        This method is called only if `name` is not found in `PDZTool`.
        """
        return getattr(self.tool, name)