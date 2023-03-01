# GriffeyeCrawler

> Für die Version in Deutsch bitte `README.md` konsultieren

## Overview

Analyzes an exported file list of Griffeye per device & category
- Totals the images and videos (total & binary unique)
- Summarizes the file paths and separates them into cached & non-cached paths
- Finds the paths with the most content
- Determines the total period of file creation
- Determines the percentage distribution of file creation in the affected period per year
- Determines the percentage ratio in the browser cache and the rest of the storage
- Determines all of the points mentioned above as a total across all devices + the number of affected devices
- Generates a result file in DOCX, JSON or TXT format


## Export from Griffeye
- Menu *Report / Export*
- *CSV*
- *Illegal Files*
  - Deactivate *EXIF* - *Comment*
  - Needed for the script (default configuration): *Category*, *File Path*, *File Type*, *Created Date* (eventually *Last Write Time*), *Source ID*, *MD5* (or *SHA-1*)


## Installation

- Install Python 3.x (www.python.org)
  - Make sure "pip" is also installed (enabled by default)
  - Check if the installation was successful (``python --version`` & ``pip --version``)
  - Eventually python and pip have to be defined in the environment variables (In Windows mostly under *%APPDATA%\Local\Programs\Python\Python\\{Version}* for python & *..\Scripts* for pip)
- Das Package *docx* mit ``pip install python-docx`` installieren

> If it is not possible to install Python and Python packages on the executing system, an EXE file can be created using **PyInstaller**.
> - Installation: `pip install pyinstaller`
> - Creation of exe: `pyinstaller --onefile gc-cli.py`
> - The call of gc-cli.py in GriffeyeCrawler.py has to be changed to *gc-cli.exe*
> - Convert changed GriffeyeCrawler.py with `pyinstaller --onefile GriffeyeCrawler.py` to an exe file
> - Both exe files and the files *config.json* and *labels.json* have to be in the same directory 


## Usage

### Default case (GriffeyeCrawler.py)

- Double click on *GriffeyeCrawler.py*
- Define the name of the csv file to analyze or drop it with drag-n-drop in the console
- The result file will be created in the same location of the csv file with the same name in DOCX format. Additionally a file named *{name}_pathdetails.txt* will be created, who contains detailed informations about the analyzed data.

**Existing files will be overwritten without a warning!**

### Usage in command line (gc-cli.py)

A CSV file can be processed in the command line as follows:

`python gc-cli.py {csv-datei}`

The file can also be dropped with drag-n-drop in the console. Different configurations can be done via options. The specified options overwrite the defined configurations from *config.json*.

The following options are available (help can be called with the `-h` option):

```shell
usage: gc-cli [options] file

Commandline version of 'GriffeyeCrawler'
Analyze an exported filelist of Griffeye

positional arguments:
  file            export csv of Griffeye

optional arguments:
  -h, --help      show this help message and exit
  -v, --version   show program's version number and exit
  -o output       defines the output path/filename
                  could be only a path or can include a filename too
                  (default: input directory and input filename with the extension of the format)
                  defines the format too based on the file extension and overwrites -f
  -f format       defines the output format
                  overwritten by -o if a file extension is defined
                  possible values: docx, json, txt (default: docx)
  -l language     language for output documents (only partially for json) in locale format (e.g. en_US, de_DE)
                  if locale is not found, only the first part of the locale is checked (e.g. en, de)
                  languages are based on labels.json
                  (default from config.json)
  -n number       number of paths to show per category
  -s separator    defines the column separator
                  (default: automatically detected > comma or semicolon by Griffeye)
  --date dates    list of datefields to get the dates from separated by comma without space (case insensitive)
                  if a date is empty (01.01.0001, 01.01.1970 or '') the next field in the list is checked
                  needs to be wrapped in quotes if it contains a space
                  (default from config.json)
  --exclude path  list of textparts in the filepath field to be excluded from the analysis
                  separated by comma without space (case insensitive)
                  needs to be wrapped in quotes if it contains a space
  --nodetails     don't generate the pathdetails file
```

**Examples:**

- JSON with dates from datefields prioritized as follows: 'exif dates' then 'last write time' then 'created date'

  `python gc-cli.py metadata.csv --date "exif: createdate,last write time,created date" -f json`

- DOCX in english excluding files in pathes including the texts 'unallocated' and 'thumbcache'

  `python gc-cli.py metadata.csv --exclude unallocated,thumbcache -l en_us`

- JSON with new name in subfolder without details file but with max. 10 most common paths

  `python gc-cli.py metadata.csv -o mysubfolder/mynew.json -n 10 --nodetails`



## General information

- If the same file exists more than once, it will be counted more than once and displayed in the corresponding tables. The number given in brackets corresponds to the number of files found without duplicates (binary unique).
- The additionally generated file *{name}_pathdetails.txt* contains all paths with the number of files contained. If necessary, replacements for "undesirable" most common paths can be found here (e.g. for repetitions, etc.). In addition, the detected caches with the number of files they contain and their paths are visible.
- The report shows the thumbnails (`is_thumbcache: true`) collected as a single entry. The same applies to the browser caches (`is_browser: true`), which are displayed collectively for each browser.
- An empty date (e.g. carved files) is shown as `undefined`. The same applies to the unix timestamp 01/01/1970.
- The separator within the CSV file is determined based on the header line (based on Griffeye only `;` or `,` possible). It can happen that a column itself contains a separator. Affected columns are packed in quotation marks (`"`) by Griffeye. This can be processed normally. However, if a CSV entry with an inappropriate number of semicolons outside of quotation marks is detected, the corresponding entry is ignored during processing and a corresponding message incl. affected line numbers are shown.
- When exporting data from Griffeye, the *EXIF - Comment* column must be **deactivated**. This can lead to problems due to the sometimes exotic content.
- Values below 1% (e.g. 0.3%) are shown as *<1%* in the percentage distribution.


## Configuration

If necessary, various settings can be made in the *config.json* file. The language of the result files can also be adjusted via the configuration file. English and German are currently available. Other languages can be defined in the *labels.json* file. These files must be in the same directory as the Python files.

### Input file

config.json: `input`

An adaptation of the encoding format `encoding` (default *utf8* by Griffeye) is possible here.

### Result file

config.json: `result`

An adaptation of the encoding format `encoding` (default *utf8*) is possible here. In addition, the desired number of the most common paths `number_of_showed_paths` and the language of the result file `language`. It can be defined whether the detail file should be created `generate_pathdetails` and its name `pathdetails_name` and encoding format `pathdetails_encoding` (default *utf8*).

### Needed columns

config.json: `needed_columns`

> Various configurations regarding required columns are directly related to the internal processing of the data. For this reason **no changes should be made without consulting the source code**.

The values are read from the CSV file based on the name in `columnname`. The internal processing runs via the `key`.
Values of two possible columns (see hashes *MD5* or *SHA-1*) can be defined with the `alt` option of the corresponding column.

DThe settings for the alternative date column (see *Created Date*) can be found under `other` - `alternative_date_*`.

#### Currently defined

* *Category*: Controls classification into the appropriate category
* *File Path*: Controls classification into the most used paths & detection as browser cache, thumbnail, etc.
* *File Type*: Controls classification into "Picture" or "Video"
* *Created Date*: Controls the definition of the period & percentage distribution over the years
  * If *Created Date* is empty (`01.01.0001`) the alternative date column *Last Write Time* is searched for. Otherwise the value `undefined` is used.
  So far, this behavior has mostly been observed with data from mobiles.
* *Source ID*: Controls classification to the corresponding device
* *MD5* oder *SHA-1*: Controls detection of the binary unique value
  * If *MD5* is not found in the existing columns, *SHA-1* must be present.

### Categories

config.json: `categories`

The category name in `name` must match the definition in Griffeye. In addition, `legality` can be used to define whether this category is considered "illegal".
The sorting value `sort` of the category refers to the order of the output in the result file and can also be set. With `show_in_report` a category can be shown or hidden in the result file.

### Paths, Caches, Thumbnails

config.json: `caches`

The classification into caches can be defined using the `path` option. This value is searched for in the file path in order to make the appropriate classification. `name` defines the corresponding product, while `is_browser` allows a definition as a browser cache (calculation of the percentage browser cache share & collection per browser in the most common paths like in *is_thumbcache*). `is_thumbcache` defines a thumbcache (thumbnails), whereby these are also listed as one value in the most common paths. The names to be displayed are defined under `other` - `name_for_thumbcache` or `other` - `name_for_browsercache`.

> **CAUTION:** Windows paths must be separated under *path* with ``\\``. Unix-based file systems (Linux, Apple, etc.) are not affected.
> (e.g. Windows: `Firefox\\Profiles`, Apple: `Firefox/Profiles`)
