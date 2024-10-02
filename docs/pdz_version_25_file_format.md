# PDZ Version 25 File Format

The PDZ version 25 file format is composed of an unspecified number of variable-length records. Each record has a two-part structure: a **header** and a **data section**.

### Structure of a Record

- **Header**: The header is 6 bytes long and contains:
  - A **Record Type** (2 bytes), which indicates the type of data contained in the record.
  - A **Data Length** (4 bytes, unsigned integer), which specifies the length of the data section in bytes. This length does not include the size of the header.
- **Data Section**: Follows the header and contains the actual record data. The length of this section is defined by the **Data Length** field.

### File Composition

- The **first record** in every PDZ file must be the **File Header Record** (Record Type `25`).
- Subsequent records can be of any valid record type, and there is no required order for these records beyond the initial header.
- To understand the full contents of the file, a reader must process and examine all records, as the file structure does not impose any ordering or specific content beyond the File Header.

<hr style="width: 100%; border: 1px solid darkblue" />

**Record Name:** ***File Header***  
**Record Type:** ***25***

| **Type**           | **Size (bytes)** | **Name**        | **Description**                                  |
|--------------------|------------------|-----------------|--------------------------------------------------|
| unsigned short (H) | 2                | record_type     | Contains 25 (compatible with prior PDZ versions) |
| unsigned int (I)   | 4                | data_length     | Contains 14                                      |
| wchar_t[5] (10s)   | 10               | file_type_id    | Contains “pdz25” in Unicode                      |
| unsigned int (I)   | 4                | instrument_type | Instrument type identifier (1-XRF, 2-LIBS, 3-?)  |

---

**Record Name:** ***XRF Instrument***  
**Block Type:** ***1***

| **Type**           | **Size (bytes)** | **Name**                           | **Description**                                                                            |
|--------------------|:----------------:|------------------------------------|--------------------------------------------------------------------------------------------|
| unsigned short (H) |        2         | record_type                        | Contains 1                                                                                 |
| unsigned int (I)   |        4         | data_length                        | Contains size of the data                                                                  |
| unsigned int (I)   |        4         | serial_number_length               | SerialNumber Unicode string length                                                         |
| wchar_t[]          |        -         | serial_number                      | Unique serial number like 600N0516 in Unicode characters                                   |
| unsigned int (I)   |        4         | build_number_length                | BuildNumber Unicode string length                                                          |
| wchar_t[]          |        -         | build_number                       | Unique build number like SMX-0516 in Unicode characters                                    |
| byte (B)           |        1         | tube_target_element                | Atomic number of x-ray tube target (47 – Ag, 45 – Rh)                                      |
| byte (B)           |        1         | anode_takeoff_angle                | X-rays emerge from the x-ray tube at this angle to the surface (0-90)                      |
| byte (B)           |        1         | sample_incidence_angle             | X-rays impact the analyte at this angle to the surface (0-90)                              |
| byte (B)           |        1         | sample_takeoff_angle               | Detected x-rays leave the analyte at this angle to the surface (0-90)                      |
| short (h)          |        2         | be_thickness                       | Thickness of the x-ray tube’s beryllium window in micro-meters                             |
| unsigned int (I)   |        4         | detector_model_length              | DetectorModel Unicode string length                                                        |
| wchar_t[]          |        -         | detector_model                     | xFlash, Amptek, AmptekFast, SiPin, Ketek, etc.                                             |
| unsigned int (I)   |        4         | tube_type_length                   | TubeType Unicode string length                                                             |
| wchar_t[]          |        -         | tube_type                          | RxBox, NSI, etc.                                                                           |
| byte (B)           |        1         | hw_spot_size                       | Spot size in mm as indicated by hardware switches                                          |
| byte (B)           |        1         | sw_spot_size                       | Spot size in mm as requested by illumination or external program                           |
| unsigned int (I)   |        4         | collimator_type_length             | CollimatorType Unicode string length                                                       |
| wchar_t[]          |        -         | collimator_type                    | “Movable” or “Fixed”                                                                       |
| unsigned int (I)   |        4         | versions                           | How many Firmware Versions are recorded, not all instruments will have the same processors |
| unsigned short (H) |        2         | record_number                      | Contains 1                                                                                 |
| unsigned int (I)   |        4         | sw_version_length                  | SWVersion Unicode string length                                                            |
| wchar_t[]          |        -         | sw_version                         | Version string for BrukerS1                                                                |
| unsigned short (H) |        2         | record_number_for_xilinx           | Contains 2                                                                                 |
| unsigned int (I)   |        4         | xilinx_fw_ver_length               | Xilinx Unicode string length                                                               |
| wchar_t[]          |        -         | xilinx_fw_ver                      | Xilinx FPGA (DSP) Firmware version                                                         |
| unsigned short (H) |        2         | record_number_for_sup              | Contains 3                                                                                 |
| unsigned int (I)   |        4         | sup_fw_ver_length                  | Safety processor Unicode string length                                                     |
| wchar_t[]          |        -         | sup_fw_ver                         | Safety processor firmware version                                                          |
| unsigned short (H) |        2         | record_number_for_uup_fw_ver       | Contains 4                                                                                 |
| unsigned int (I)   |        4         | uup_fw_ver_length                  | Utility processor firmware version Unicode string length                                   |
| wchar_t[]          |        -         | uup_fw_ver                         | Utility processor firmware version                                                         |
| unsigned short (H) |        2         | record_number_for_xray_src_fw_ver  | Contains 5                                                                                 |
| unsigned int (I)   |        4         | xray_src_fw_ver_length             | X-Ray Source firmware major version Unicode string length                                  |
| wchar_t[]          |        -         | xray_src_fw_ver                    | X-Ray Source firmware major version                                                        |
| unsigned short (H) |        2         | record_number_for_dpp_fw_ver       | Contains 6                                                                                 |
| unsigned int (I)   |        4         | dpp_fw_ver_length                  | DPP Processor firmware version Unicode string length                                       |
| wchar_t[]          |        -         | dpp_fw_ver                         | DPP Processor firmware version                                                             |
| unsigned short (H) |        2         | record_number_for_header_fw_ver    | Contains 7                                                                                 |
| unsigned int (I)   |        4         | header_fw_ver_length               | HeaderBoard processor firmware version Unicode string length aka HuP                       |
| wchar_t[]          |        -         | header_fw_ver                      | HeaderBoard processor firmware version (opt)                                               |
| unsigned short (H) |        2         | record_number_for_baseboard_fw_ver | Contains 8                                                                                 |
| unsigned int (I)   |        4         | baseboard_fw_ver_length            | Baseboard processor firmware version Unicode string length                                 |
| wchar_t[]          |        -         | baseboard_fw_ver                   | Baseboard processor firmware version (opt)                                                 |

---

**Record Name:** ***XRF Assay Summary***  
**Block Type:** ***2***

| **Type**           | **Size (bytes)** | **Name**                       | **Description**                                                                                           |
|--------------------|:----------------:|--------------------------------|-----------------------------------------------------------------------------------------------------------|
| unsigned short (H) |        2         | record_type                    | Contains 2                                                                                                |
| unsigned int (I)   |        4         | data_length                    | Contains size of the data                                                                                 |
| unsigned int (I)   |        4         | number_of_phases               | Active phase when this data was collected                                                                 |
| unsigned long (L)  |        4         | raw_counts                     | Accumulated total of all detectable photons                                                               |
| unsigned long (L)  |        4         | valid_counts                   | Accumulated total of all photons whose energy was measured                                                |
| unsigned long (L)  |        4         | valid_counts_in_range          | Accumulated total of all photons whose energy was measured and fell within the range set in the DPP board |
| unsigned long (L)  |        4         | reset_counts                   | Accumulated total count of resets done                                                                    |
| float (f)          |        4         | total_real_time                | Time since trigger pulled in seconds; accumulated duration from most recent packet                        |
| float (f)          |        4         | total_packet_time              | Accumulated total duration = Live + Dead + Reset time in seconds                                          |
| float (f)          |        4         | total_dead                     | Accumulated total of dead time in seconds                                                                 |
| float (f)          |        4         | total_reset                    | Accumulated total of reset time in seconds                                                                |
| float (f)          |        4         | total_live                     | Accumulated total of live time in seconds                                                                 |
| float (f)          |        4         | elapsed_time                   | User perceived time in seconds                                                                            |
| unsigned int (I)   |        4         | application_name_length        | Length of ApplicationName string in bytes                                                                 |
| wchar_t[]          |        -         | application_name               | Application name in Unicode                                                                               |
| unsigned int (I)   |        4         | application_part_number_length | Length of ApplicationPartNumber string in bytes                                                           |
| wchar_t[]          |        -         | application_part_number        | Application part number (like 730.0081.02)                                                                |
| unsigned int (I)   |        4         | user_id_length                 | Length of UserID string in bytes                                                                          |
| wchar_t[]          |        -         | user_id                        | User ID (e.g., "Factory", "Supervisor", "Bob")                                                            |

---

**Record Name:** ***XRF Spectrum***  
**Block Type:** ***3***

| **Type**                | **Size (bytes)** | **Name**              | **Description**                                                                                        |
|:------------------------|:----------------:|-----------------------|--------------------------------------------------------------------------------------------------------|
| unsigned short          |        2         | record_type           | Contains 3                                                                                             |
| unsigned int            |        4         | data_length           | Contains size of the data                                                                              |
| unsigned int            |        4         | phase_number          | Active phase when this data was collected                                                              |
| unsigned long           |        4         | raw_counts            | Accumulated total of all detectable photons                                                            |
| unsigned long           |        4         | valid_counts          | Accumulated total of all photons whose energy was measured                                             |
| unsigned long           |        4         | valid_counts_in_range | Accumulated total of all photons whose energy was measured that fell within the range set in DPP board |
| unsigned long           |        4         | reset_counts          | Accumulated total count of resets done                                                                 |
| float                   |        4         | time_since_trigger    | Number of packets in this phase                                                                        |
| float                   |        4         | total_packet_time     | Accumulated total of duration = Live + Dead + Reset time in seconds                                    |
| float                   |        4         | total_dead            | Accumulated total of dead time in seconds                                                              |
| float                   |        4         | total_reset           | Accumulated total of reset time in seconds                                                             |
| float                   |        4         | total_live            | Accumulated total of live time in seconds                                                              |
| float                   |        4         | tube_voltage          | X-ray tube voltage in kV                                                                               |
| float                   |        4         | tube_current          | X-ray tube current in micro-amps                                                                       |
| short                   |        2         | filter1_element       | Atomic number of filter layer 1                                                                        |
| short                   |        2         | filter1_thickness     | Thickness of filter layer 1 in micro-meters                                                            |
| short                   |        2         | filter2_element       | Atomic number of filter layer 2                                                                        |
| short                   |        2         | filter2_thickness     | Thickness of filter layer 2 in micro-meters                                                            |
| short                   |        2         | filter3_element       | Atomic number of filter layer 3                                                                        |
| short                   |        2         | filter3_thickness     | Thickness of filter layer 3 in micro-meters                                                            |
| short                   |        2         | filter_wheel_number   | Number on the filter wheel                                                                             |
| float                   |        4         | detector_temp         | Temperature reported by detector at the end in °C                                                      |
| float                   |        4         | ambient_temp          | Temperature inside instrument at end in °F                                                             |
| long                    |        4         | vacuum                | Unknown vacuum-related information                                                                     |
| float                   |        4         | ev_per_channel        | eV per channel/bin. Defaults to 20.                                                                    |
| short                   |        2         | gain_drift_algorithm  | Method used to determine EVPerChannel and ChannelStart                                                 |
| float                   |        4         | channel_start         | eV of the bottom/lower edge of the first channel/bin                                                   |
| SYSTEMTIME              |        16        | acquisition_date_time | Date and time spectrum was acquired                                                                    |
| float                   |        4         | atmospheric_pressure  | Atmospheric pressure (units unknown)                                                                   |
| short                   |        2         | channels              | Number of channels in the spectrum                                                                     |
| short                   |        2         | nose_temp             | Nose temperature in °C                                                                                 |
| short                   |        2         | environment           | Vacuum, Air, Helium, etc.                                                                              |
| unsigned int            |        4         | illumination_length   | Length of the Illumination string in Unicode                                                           |
| wchar_t[]               |        -         | illumination          | Illumination ID used during the assay                                                                  |
| short                   |        2         | normal_packet_start   | Ordinal number of packet when data collection started                                                  |
| unsigned long[channels] |        -         | spectrum_data         | Counts for each channel (default size is 2048 channels, can be larger)                                 |

---

**Record Name:** ***Raw XRF Spectrum Packet***  
**Block Type:** 4

| **Type**        | **Size (bytes)** | **Name**                    | **Description**                                                                                            |
|-----------------|:----------------:|-----------------------------|------------------------------------------------------------------------------------------------------------|
| unsigned short  |        2         | record_type                 | Contains 4                                                                                                 |
| unsigned int    |        4         | data_length                 | Contains size of the data                                                                                  |
| unsigned int    |        4         | phase_number                | Active phase when this data was collected                                                                  |
| byte            |        1         | xilinx_fw_ver               | Xilinx FPGA (DSP) Firmware version                                                                         |
| byte            |        1         | xilinx_fw_sub_ver           | Xilinx FPGA (DSP) Firmware version                                                                         |
| unsigned short  |        2         | packet_len                  | Byte length of DPP header plus spectrum as shorts                                                          |
| unsigned long   |        4         | time_since_trigger          | Time since trigger pulled in 0.1 sec units (user or accumulated duration?)                                 |
| unsigned long   |        4         | raw_count                   | Count of all detectable photons                                                                            |
| unsigned long   |        4         | valid_count                 | Count of all photons whose energy was measured                                                             |
| unsigned long   |        4         | valid_count_in_range        | Count of all photons whose energy was measured that fell within the range set in the DPP board             |
| unsigned long   |        4         | packet_time                 | Duration = Live + Dead + Reset time in milliseconds                                                        |
| unsigned long   |        4         | dead_time                   | Dead time in milliseconds                                                                                  |
| unsigned long   |        4         | reset_time                  | Reset time in milliseconds                                                                                 |
| unsigned long   |        4         | live_time                   | Live time in milliseconds                                                                                  |
| unsigned long   |        4         | service                     | Vassili mystery data                                                                                       |
| unsigned short  |        2         | reset_count                 | Count of resets done                                                                                       |
| unsigned short  |        2         | packet_count                | Serial number of packet from trigger pull, 1-based                                                         |
| byte            |        20        |                             | Unused                                                                                                     |
| byte            |        58        | xilinx_vars                 | Internal state variables in Xilinx FPGA (DSP)                                                              |
| short           |        2         | detector_temp               | Temperature reported by detector - divide by 2 = °C                                                        |
| unsigned short  |        2         | ambient_temp                | Temperature inside instrument - divide by 10 = °F                                                          |
| byte            |        1         | controller_fw_ver           | Micro-controller on DPP board firmware version                                                             |
| byte            |        1         | controller_fw_sub_ver       | Micro-controller on DPP board firmware version                                                             |
| unsigned long   |        4         | total_raw_counts            | Accumulated total of all detectable photons                                                                |
| unsigned long   |        4         | total_valid_counts          | Accumulated total of all photons whose energy was measured                                                 |
| unsigned long   |        4         | total_valid_counts_in_range | Accumulated total of all photons whose energy was measured that fell within the range set in the DPP board |
| unsigned long   |        4         | total_reset_counts          | Accumulated total count of resets done                                                                     |
| float           |        4         | total_time_since_trigger    | Time since trigger pulled in 0.1 sec units (user or accumulated duration?) from most recent packet         |
| float           |        4         | total_packet_time           | Accumulated total of duration = Live + Dead + Reset time in seconds                                        |
| float           |        4         | total_dead                  | Accumulated total of dead time in seconds                                                                  |
| float           |        4         | total_reset                 | Accumulated total of reset time in seconds                                                                 |
| float           |        4         | total_live                  | Accumulated total of live time in seconds                                                                  |
| unsigned long[] |        -         | spectrum_data               | Counts for each of the channels, default is 2048 channels, can be as large as 8196 channels                |

---

**Record Name:** ***Calculated Results***  
**Block Type:** 5

| **Type**        | **Size (bytes)** | **Name**                 | **Description**                                               |
|-----------------|:----------------:|--------------------------|---------------------------------------------------------------|
| unsigned short  |        2         | record_type              | Contains 5                                                    |
| unsigned int    |        4         | data_length              | Contains size of the data                                     |
| unsigned int    |        4         | analysis_mode            | Display format of the instrument **                           |
| unsigned int    |        4         | analysis_type            | How to calculate the results **                               |
| short           |        2         | used_auto_cal_select     | Was AutoCalSelect used to select the calibration              |
| short           |        2         | result_type              | ConcentrationWeightPercent, ConcentrationPPM, Arbitrary, etc. |
| unsigned short  |        2         | error_multiplier         | Multiplier for StdError used in results details               |
| unsigned int    |        4         | cal_file_length          | Calibration file name Unicode string length                   |
| wchar_t[]       |        ?         | cal_file_name            | File name of the .calibration file used                       |
| unsigned int    |        4         | cal_pkg_name_length      | Package name Unicode string length                            |
| wchar_t[]       |        ?         | cal_pkg_name             | Package name/Directory in which .calibration file resides     |
| unsigned int    |        4         | cal_pkg_pn_length        | Package part number Unicode string length                     |
| wchar_t[]       |        ?         | cal_pkg_part_number      | Calibration package part number                               |
| unsigned int    |        4         | type_std_set_name_length | Type standardization set name Unicode length                  |
| wchar_t[]       |        ?         | type_std_set_name        | Name of type standardization set                              |

** The `analysisMode` and `analysisType` values are defined as follows:

| analysisMode       | Value | | analysisType  | Value |
|--------------------|:-----:|-|---------------|:-----:|
| METAL_PASSFAIL     |   1   | | PMI_FP        |   1   |
| METAL_MATCH        |   2   | | GRADEID_EMP   |   2   |
| METAL_ANALYZE      |   4   | | AUTO          |   4   |
| ROHS_ANALYZE       |   8   | | DUAL          |   8   |
| UTILITY            |  16   | | SMART_GRADE   |  16   |
| METAL_ANALYZE_NONE |  32   | | SPECTRUM_ONLY |  32   |
|                    |       | | SPECTROMETER  |  64   |
|                    |       | | NON_QUANT     |  128  |
|                    |       | | SPECTRUMONLY  |  224  |

---

**Record Name:** ***Calculated Results Details***  
**Block Type:** 6

| **Type**       | **Size (bytes)** | **Name**        | **Description**                                                                                                         |
|----------------|:----------------:|-----------------|-------------------------------------------------------------------------------------------------------------------------|
| unsigned short |        2         | record_type     | Contains 6                                                                                                              |
| unsigned int   |        4         | data_length     | Contains size of the data                                                                                               |
| unsigned int   |        4         | name_length     | Entry name Unicode string length                                                                                        |
| wchar_t[]      |        -         | name            | Entry name string Unicode                                                                                               |
| unsigned int   |        4         | atomic_number   | Atomic number of the primary element                                                                                    |
| byte           |        1         | units           | Unit type for the result (0, 1, 2) **                                                                                   |
| float          |        4         | result          | Value of the result (Never in PPM)                                                                                      |
| float          |        4         | type_std_result | Result after type standardization is applied, should match result if type standardization is not active. (Never in PPM) |
| float          |        4         | error           | Calculated error (1*STD) (Never in PPM)                                                                                 |
| float          |        4         | min             | Minimum value for defined range  (grade or limit) (Never in PPM)                                                        |
| float          |        4         | max             | Maximum value for defined range (grade or limit) (Never in PPM)                                                         |
| short          |        2         | tramp           | Indicates if the element was tagged as a tramp (bool)                                                                   |
| short          |        2         | nominal         | Indicates if the element result is nominal. 0 = false (bool)                                                            |

\* The results themselves( Result, TypeStdResult,
error, min, max) are stored as percent  
** The `Units` values are defined as follows:

| Units       | Value |
|-------------|:-----:|
| USERDEFINED |   0   |
| PPM         |   1   |
| PERC        |   2   |

---

**Record Name:** ***Grade ID Results***  
**Block Type:** 7

| **Type**       | **Size (bytes)** | **Name**                   | **Description**                                    |
|----------------|:----------------:|----------------------------|----------------------------------------------------|
| unsigned short |        2         | record_type                | Contains 7                                         |
| unsigned int   |        4         | data_length                | Contains size of the data                          |
| unsigned int   |        4         | grade_id1_length           | Grade ID1 length                                   |
| wchar_t[]      |        -         | grade_id1                  | GradeID1 string Unicode                            |
| float          |        4         | confidence1                | GradeID1 measure of confidence                     |
| unsigned int   |        4         | grade_id2_length           | Grade ID2 length                                   |
| wchar_t[]      |        -         | grade_id2                  | GradeID2 string Unicode                            |
| float          |        4         | confidence2                | GradeID2 measure of confidence                     |
| unsigned int   |        4         | grade_id3_length           | Grade ID3 length                                   |
| wchar_t[]      |        -         | grade_id3                  | GradeID3 string Unicode                            |
| float          |        4         | confidence3                | GradeID3 measure of confidence                     |
| float          |        4         | match_spread_threshold     | Threshold for matching spread                      |
| short          |        2         | process_tramp_elements     | Was ProcessTrampElements enabled. 0 = false (bool) |
| short          |        2         | nominal_chemistry          | Was NominalChemistry enabled. 0 = false (bool)     |
| unsigned short |        2         | num_grade_libs             | Can select multiple Grade Libraries                |
| unsigned int   |        4         | grade_lib_file_name_length | Grade Library file name Unicode string length      |
| wchar_t[]      |        ?         | grade_lib_file_name        | Grade Library file name                            |
| unsigned int   |        4         | grade_lib_ver_length       | Grade Library version length                       |
| wchar_t[]      |        -         | grade_lib_version          | Grade Library version                              |
| ...            |       ...        | ...                        | Repeat previous for each lib                       |

---

**Record Name:** ***Pass/Fail Results***  
**Block Type:** 8

| **Type**       | **Size (bytes)** | **Name**               | **Description**                        |
|----------------|:----------------:|------------------------|----------------------------------------|
| unsigned short |        2         | record_type            | Contains 8                             |
| unsigned int   |        4         | data_length            | Contains size of the data              |
| unsigned short |        2         | passed                 | Result was Pass/Fail/Inconclusive      |
| unsigned int   |        4         | limit_file_name_length | Length of LimitFileName Unicode string |
| wchar_t[]      |        -         | limit_file_name        | Limit file name                        |
| unsigned int   |        4         | material_name_length   | Material name Unicode string length    |
| wchar_t[]      |        -         | material_name          | Material name used to select limi      |

---

**Record Name:** ***User Custom Fields***  
**Block Type:** 9

| **Type**       | **Size (bytes)** | **Name**           | **Description**                            |
|----------------|:----------------:|--------------------|--------------------------------------------|
| unsigned short |        2         | record_type        | Contains 9                                 |
| unsigned int   |        4         | data_length        | Contains size of the data                  |
| short          |        2         | num_fields         | Number of User Custom Fields               |
| unsigned int   |        4         | field_name_length  | Length of Field 1 Name Unicode string      |
| wchar_t[]      |        -         | field_name         | Field 1 Name                               |
| unsigned int   |        4         | field_value_length | Length of Field 1 Value Unicode string     |
| wchar_t[]      |        -         | field_value        | Field 1 Value                              |
| ...            |       ...        | ...                | Continues with four entries for each field |

---

**Record Name:** ***Average Details***  
**Block Type:** 10

| **Type**       | **Size (bytes)** | **Name**     | **Description**                   |
|----------------|:----------------:|--------------|-----------------------------------|
| unsigned short |        2         | record_type  | Contains 10                       |
| unsigned int   |        4         | data_length  | Contains size of the data         |
| unsigned int   |        4         | num_assays   | Number of assays averaged         |
| unsigned int   |        4         | assay_number | Assay numbers included in average |
| ...            |       ...        | ...          | Continues for each assay          |
---

**Record Name:** ***Filter Layers***  
**Block Type:** 11

| **Type**         | **Size (bytes)** | **Name**               | **Description**                           |
|------------------|:----------------:|------------------------|-------------------------------------------|
| unsigned short   |        2         | record_type            | Contains 11                               |
| unsigned int     |        4         | data_length            | Contains size of the data                 |
| unsigned short   |        2         | phase_number           | Active phase when this data was collected |
| unsigned short   |        2         | layers_number          | Number of filter layers                   |
| unsigned short[] |        -         | filter_layer_element   | Z-number(s) #4 and up                     |
| unsigned int[]   |        -         | filter_layer_thickness | In micro-meters, #4 and up                |

---

**Record Name:** ***Image Details***  
**Block Type:** 137

| **Type**       | **Size (bytes)**  | **Name**                | **Description**                   |
|----------------|:-----------------:|-------------------------|-----------------------------------|
| unsigned short |         2         | record_type             | Contains 137                      |
| unsigned int   |         4         | data_length             | Contains size of the data         |
| int            |         4         | num_images              | Number of images in the file      |
| unsigned int   |         4         | image_length            | Length of the image data in bytes |
| byte[]         |   image_length    | image                   | Image in jpeg format              |
| unsigned int   |         4         | image_x_dimension       | Width of the image                |
| unsigned int   |         4         | image_y_dimension       | Height of the image               |
| unsigned int   |         4         | image_annotation_length | Length of the annotation in bytes |
| wchar_t[]      | annotation_length | image_annotation        | Annotation text for the image     |
|   ...          |        ...        | ...                     | Continues for each image          |

---

**Record Name:** ***GPS Details***  
**Block Type:** 138

| **Type**       | **Size (bytes)** | **Name**     | **Description**                    |
|----------------|:----------------:|--------------|------------------------------------|
| unsigned short |        2         | record_type  | Contains 138                       |
| unsigned int   |        4         | data_length  | Contains 24                        |
| int            |        4         | gps_valid    | Indicates if the GPS data is valid |
| double         |        8         | latitude     | Latitude of the GPS data           |
| double         |        8         | longitude    | Longitude of the GPS data          |
| float          |        4         | altitude     | Altitude of the GPS data           |

---

**Record Name:** ***Miscellaneous Information***  
**Block Type:** 139

| **Type**       | **Size (bytes)** | **Name**          | **Description**                                |
|----------------|:----------------:|-------------------|------------------------------------------------|
| unsigned short |        2         | record_type       | Contains 139                                   |
| unsigned int   |        4         | data_length       | Contains size of the data                      |
| int            |        4         | std_multiplier    | 1-5                                            |
| unsigned int   |        4         | active_cal_length | Active calibration Unicode string length       |
| wchar_t[]      |        -         | active_cal        | User interface version of the calibration name |
| unsigned int   |        4         | sample_id_length  | SampleID Unicode string length                 |
| wchar_t[]      |        -         | sample_id         | SampleID specified in a sequence run           |

---

**Record Name:** ***Trace Log***
**Block Type:** 900

| **Type**       | **Size (bytes)** | **Name**    | **Description**                                                                                             |
|----------------|:----------------:|-------------|-------------------------------------------------------------------------------------------------------------|
| unsigned short |        2         | record_type | Contains 900                                                                                                |
| unsigned int   |        4         | log_length  | Contains size of the data                                                                                   |
| unsigned int   |        4         |             |                                                                                                             |
| wchar_t[]      |        -         | log         | Trace log contents in Unicode, consists of lines of text separated by a line terminator such as CR/LF or NL |

---

**Record Name:** ***Libs Alloy Results***  
**Block Type:** 1001

| **Type**       | **Size (bytes)** | **Name**            | **Description**                                                                           |
|----------------|:----------------:|---------------------|-------------------------------------------------------------------------------------------|
| unsigned short |        2         | record_type         | Contains 1001                                                                             |
| unsigned int   |        4         | data_length         | Contains size of the data                                                                 |
| bool           |        2         | is_auto_selected    | Was “Automatic Selection” used to determine the base; otherwise, it was manually selected |
| unsigned short |        2         | std_dev_multiplier  | Multiplier for standard deviation (not currently used)                                    |
| unsigned int   |        4         | library_name_length |                                                                                           |
| wchar_t[]      |        -         | library_name        | Name of the alloy library used                                                            |
| SYSTEMTIME     |        16        | created             | Date and time the result was created                                                      |
| unsigned int   |        4         | created_by_length   |                                                                                           |
| wchar_t[]      |        -         | created_by          | User name who created the result                                                          |
| short          |        2         | num_elements        | Number of elements                                                                        |
| wchar_t[]      |        4         | element_name        | Name of the first element                                                                 |
| float          |        4         | element_percentage  | Percentage of the first element                                                           |
| float          |        4         | element_lod         | Limit of detection for the first element                                                  |
| float          |        4         | element_std_dev     | Standard deviation for the first element (not currently used)                             |
| float          |        4         | element_max         | Maximum value for the first element                                                       |
| float          |        4         | element_min         | Minimum value for the first element                                                       |
| ...            |       ...        | ...                 | Continues for subsequent elements                                                         |

---

**Record Name:** ***Libs Grade ID Results***  
**Block Type:** 1002

| **Type**       | **Size (bytes)** | **Name**                   | **Description**                                          |
|----------------|:----------------:|----------------------------|----------------------------------------------------------|
| unsigned short |        2         | record_type                | Contains 1002                                            |
| unsigned int   |        4         | data_length                | Contains size of the data                                |
| unsigned short |        2         | num_grade_ids              | Number of Grade IDs                                      |
| unsigned int   |        4         | grade_id_length            | Length of the first Grade ID                             |
| wchar_t[]      |        -         | grade_id                   | Unicode string of the first Grade ID                     |
| float          |        4         | grade_id_confidence        | Measure of confidence for the first Grade ID             |
| ...            |       ...        | ...                        | Continues for subsequent Grade IDs and confidence values |
| float          |        4         | match_spread_threshold     |                                                          |
| unsigned short |        2         | num_grade_libs             | Number of Grade Libraries                                |
| unsigned int   |        4         | grade_lib_file_name_length | Length of the first Grade Library file name              |
| wchar_t[]      |        -         | grade_lib_file_name        | Name of the first Grade Library                          |
| unsigned int   |        4         | grade_lib_ver_length       | Length of the version of the first Grade Library         |
| wchar_t[]      |        -         | grade_lib_version          | Version of the first Grade Library                       |
| ...            |       ...        | ...                        | Repeat previous four fields for each Grade Library       |

---

**Record Name:** ***Libs Alloy Method***  
**Block Type:** 1003

| **Type**       | **Size (bytes)** | **Name**          | **Description**                                |
|----------------|:----------------:|-------------------|------------------------------------------------|
| unsigned short |        2         | record_type       | Contains 1003                                  |
| unsigned int   |        4         | data_length       | Contains size of the data                      |
| unsigned int   |        4         | model_name_length | Length of the model name used                  |
| wchar_t[]      |        -         | model_name        | Model name from LID                            |
| unsigned int   |        4         | base_length       | Length of the base                             |
| wchar_t[]      |        -         | base              | Base name                                      |
| unsigned int   |        2         | integration_time  | Integration time                               |
| SYSTEMTIME     |        16        | created           | Date and time the method was created           |
| unsigned int   |        4         | created_by_length | Length of the user name who created the method |
| wchar_t[]      |        -         | created_by        | User name who created the method               |

---

**Record Name:** ***Libs Alloy Sample***  
**Block Type:** 1004

| **Type**       | **Size (bytes)** | **Name**             | **Description**                                                                 |
|----------------|:----------------:|----------------------|---------------------------------------------------------------------------------|
| unsigned short |        2         | record_type          | Contains 1004                                                                   |
| unsigned int   |        4         | data_length          | Contains size of the data                                                       |
| long long      |        8         | scan_index           | Scan index                                                                      |
| unsigned int   |        4         | name_length          | Length of the sample name                                                       |
| wchar_t[]      |        -         | name                 | Sample name                                                                     |
| unsigned int   |        4         | scan_id_length       | Length of the Scan ID                                                           |
| wchar_t[]      |        -         | scan_id              | Saved for barcode use                                                           |
| SYSTEMTIME     |        16        | created              | Date and time the sample was created                                            |
| unsigned int   |        4         | created_by_length    | Length of the user name who created the sample                                  |
| wchar_t[]      |        -         | created_by           | User name who created the sample                                                |
| short          |        2         | num_fields           | Number of fields                                                                |
| unsigned int   |        4         | field_name_length    | Length of the first field name                                                  |
| wchar_t[]      |        -         | field_name           | Name of the first field                                                         |
| unsigned int   |        4         | field_value_length   | Length of the first field value                                                 |
| wchar_t[]      |        -         | field_value          | Value of the first field                                                        |
| ...            |       ...        |                      | Repeat field name and value until num_fields is met                             |
| unsigned int   |        4         | spectrum_data_length | Length of SpectrumData (2 * Point Counts)                                       |
| float[]        |        -         | spectrum_data        | Spectrum’s x and y values, format: float SpectrumData[] = {x, y, x, y, x, y...} |
