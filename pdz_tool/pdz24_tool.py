from .base_tool import BasePDZTool

class PDZ24Tool(BasePDZTool):
    def __init__(self, file_path: str, verbose: bool = False, debug: bool = False):
        super().__init__(file_path)

    def get_record_types(self):
        raise NotImplementedError("PDZ 24 format tool is not implemented yet.")

    def parse(self):
        raise NotImplementedError("PDZ 24 format tool is not implemented yet.")
