# PDZ-Tool

**PDZ-Tool** is a Python library for reading PDZ files and converting them into CSV or JSON formats. PDZ files are commonly used to store data from X-ray fluorescence (XRF) instruments, and this tool allows easy extraction and transformation of the data for analysis.

## 🚀 Features

- **Read PDZ files in version 24 and 25 formats.**
- **Parse and extract important information from the PDZ file into JSON format.**
- **Convert the parsed data to CSV format for further analysis.**
- **Save the parsed data to a JSON file.**
- **CLI tool for parsing and converting PDZ files.**
- **Demo script to help you get started.**
- **Verbose and debug modes to help troubleshoot issues during parsing.**

## 📥 Installation

You can install `pdz-tool` via `pip`.

```bash
pip install pdz-tool
```

## 📖 Usage

```python
#### 1. Importing and Initializing PDZTool
from pdz_tool import PDZTool

# Initialize a PDZTool object
pdz_tool = PDZTool('path/to/pdz_file.pdz')

#### 2. Parsing a PDZ File
parsed_data = pdz_tool.parse()

#### 3. Accessing Parsed Data as a Dictionary
record_names = pdz_tool.record_names  # Record names found on the pdz file
for record_name in record_names:
    print(f"Record Name: {record_name}")
    print(parsed_data[record_name])
    
#### 4. Converting Parsed Data to JSON
json_data = pdz_tool.to_json()
print(json_data)

#### 5. Saving Parsed Data to JSON File
pdz_tool.to_json('output.json')

#### 6. Saving Parsed Data to CSV
pdz_tool.to_csv('output.csv')
```

### 💻 CLI Usage:
```bash
pdz-tool path/to/pdz_file.pdz
```
see `pdz-tool --help` for more options.

## 🎓 Demo
 Demo folder is included in the project, containing example PDZ files to help you get started. 
 You can run the demo script to test the functionality of the PDZ-Tool:

```bash
python demo/demo_script.py
```
## ⚙️ Development
### Cloning the Repository
If you wish to modify or extend the tool, clone the repository:
    
```bash
git clone git@github.com:bducraux/pdz-tool.git
cd pdz-tool
``` 

### 📦 Dependencies
#### Installing Poetry
This project uses Poetry for dependency management. If you don't have Poetry installed, you can install it by running:

```bash
pip install poetry
```
#### Installing Dependencies
To install the dependencies, run:

```bash
poetry install
```

## 🤝 Contributing
Contributions are welcome! If you find any bugs or have suggestions for new features, feel free to open an issue or submit a pull request.

## 📜  License
This project is licensed under the MIT License. See the LICENSE file for details.

## 📧 Contact
For any inquiries or support, please reach out at [bruno.drx@gmail.com](mailto:bruno.drx@gmail.com).

Thank you for using PDZ-Tool! 🎉😊