import struct
from .pdz25_tool import PDZ25Tool
from .pdz24_tool import PDZ24Tool
from .utils import read_pdz_file, get_pdz_version


class PDZTool:
    def __init__(self, file_path, verbose=False, debug=False):
        self.file_path = file_path
        self.verbose = verbose

        # Read bytes and detect version before instantiating the correct tool
        pdz_bytes = read_pdz_file(file_path)
        pdz_version = get_pdz_version(pdz_bytes)

        # Now instantiate the correct tool
        if pdz_version == "pdz25":
            self.tool = PDZ25Tool(file_path, verbose, debug)
        elif pdz_version == "pdz24":
            self.tool = PDZ24Tool(file_path, verbose, debug)
        else:
            raise ValueError(f"Unknown PDZ version: {pdz_version}")

    def __getattr__(self, name):
        """
        Delegate attribute access to the appropriate tool.
        This method is called only if `name` is not found in `PDZTool`.
        """
        return getattr(self.tool, name)