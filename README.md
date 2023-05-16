# GriffeyeCrawler

> For english version visit `README_en.md`

## Überblick

Analysiert eine exportierte Dateiliste aus Griffeye pro Gerät & Kategorie
- Summiert die Bilder und Videos (Total & binary unique)
- Fasst die Dateipfade zusammen und unterteilt diese in Cache- & Nicht-Cache-Pfade auf
- Ermittelt die Pfade mit den meisten Inhalten
- Ermittelt den gesamten Zeitraum der Dateierstellung
- Ermittelt die prozentuelle Verteilung der Dateierstellung im betroffenen Zeitraum pro Jahr
- Ermittelt das prozentuelle Verhältnis im Browsercache und der übrigen Ablage
- Ermittelt sämtliche oben erwähnten Punkte auch als Total über alle Geräte + die Anzahl der betroffenen Geräte
- Generiert eine Ergebnisdatei im DOCX, JSON oder TXT Format


## Export aus Griffeye

- Menütab *Report / Export*
- *CSV*
- *Illegal Files*
  - Folgende Spalten deaktivieren
    - *Exif Comment*
    - *User Comment*
    - *Bookmarks*
  - Für das Script benötigt (Standardeinstellungen): *Category*, *File Path*, *File Type*, *Created Date* (evtl. *Last Write Time*), *Source ID*, *MD5* (oder *SHA-1*)


## Installation

- Python 3.x installieren (www.python.org)
  - Sichergehen, dass "pip" ebenfalls installiert wird (ist standardmässig aktiviert)
  - Ob die Installationen erfolgreich waren mittels `python --version` & `pip --version` in der Kommandozeile kontrollieren
  - evtl. müssen Python und pip in den Umgebungsvariablen erfasst werden (In Windows meistens unter *%APPDATA%\Local\Programs\Python\Python\\{Version}* für Python & *..\Scripts* für pip)
- Das Package *docx* mit `pip install python-docx` oder `pip install -r requirements.txt` installieren

> Sollte die Installation von Python und Python-Paketen auf dem ausführenden System nicht möglich sein, kann mit Hilfe von **PyInstaller** eine EXE-Datei erstellt werden.
> - Installation: `pip install pyinstaller`
> - EXE-Erstellung: `pyinstaller --onefile gc-cli.py`
> - Aufruf von gc-cli.py in GriffeyeCrawler.py auf *gc-cli.exe* anpassen 
> - Angepasstes GriffeyeCrawler.py mit `pyinstaller --onefile GriffeyeCrawler.py` in EXE umwandeln
> - Beide EXE-Dateien und die Dateien *config.json* und *labels.json* in dasselbe Verzeichnis kopieren 


## Verwendung

### Ausführung Standardfall

- *GriffeyeCrawler.py* doppelklicken
- Name der zu verarbeitenden CSV-Datei angeben oder via Drag-n-Drop hineinziehen.
- Das Ergebnis wird im Verzeichnis der angegebenen CSV-Datei mit demselben Namen als DOCX erstellt. Ausserdem wird bei jeder Verarbeitung die Datei *{name}_pathdetails.txt* erstellt, welche detailliertere Informationen zu den ausgewerteten Daten enthält.

**Bestehende Dateien werden ohne Warnung überschrieben!**

### Ausführung via CLI

In der Kommandozeile kann eine CSV-Datei folgendermassen verarbeitet werden:

`python gc-cli.py {csv-datei}`

Dabei kann die Datei auch mittels Drag-n-Drop in die Kommandozeile gezogen werden. Mit Hilfe der Optionen können diverse Anpassungen bei der Verarbeitung vorgenommen werden. Die angegebenen Optionen überschreiben die definierten Konfigurationen aus *config.json*.

Folgende Optionen stehen zur Verfügung (Hilfe mittels Option `-h` aufrufbar):

```
usage: gc-cli [options] file

Commandline version of 'GriffeyeCrawler'
Analyze an exported filelist of Griffeye

positional arguments:
  file            export csv of Griffeye

optional arguments:
  -h, --help       show this help message and exit
  -v, --version    show program's version number and exit
  -o output        defines the output path/filename
                   could be only a path or can include a filename too
                   (default: input directory and input filename with the extension of the format)
                   defines the format too based on the file extension and overwrites -f
  -f format        defines the output format
                   overwritten by -o if a file extension is defined
                   possible values: docx, json, txt (default: docx)
  -l language      language for output documents (only partially for json) in locale format (e.g. en_US, de_DE)
                   if locale is not found, only the first part of the locale is checked (e.g. en, de)
                   languages are based on labels.json
                   (default from config.json, result/number_of_showed_paths)
  -n number        number of paths to show per category
  -s separator     defines the column separator
                   (default: automatically detected > comma or semicolon by Griffeye)
  -d dateformat    defines the format of the input date with format codes > see python help for more details
                   %d  Day of the month (e.g. 01)
                   %m  Month (e.g. 12)
                   %y  Year without century (e.g. 23)
                   %Y  Year with century (e.g. 2023)
                   needs to be wrapped in quotes if it contains a space
                   (default from config.json, input/date_format)
  --date dates     list of datefields to get the dates from separated by comma without space (case insensitive)
                   if a date is empty (01.01.0001, 01.01.1970 or '') the next field in the list is checked
                   needs to be wrapped in quotes if it contains a space
                   (default from config.json, needed_columns/col_date & other/alternative_date_column)
  --exclude path   list of textparts in the filepath field to be excluded from the analysis
                   separated by comma without space (case insensitive)
                   needs to be wrapped in quotes if it contains a space
  --nodetails      don't generate the pathdetails file
  --includethumbs  include thumbcaches in the process (counts & dateranges) instead of listing them separately
```

Beispiele:

- JSON erstellen mit den Datumsfeldern nach folgender Reihenfolge priorisiert: 'EXIF Datum' dann 'Letzte Änderung' dann 'Erstelldatum'

  `python gc-cli.py --date "exif: createdate,last write time,created date" -f json metadata.csv`

- DOCX in englischer Sprache ohne Dateien in Pfaden mit 'unallocated' und 'unwantedfolder' im Pfadnamen erstellen

  `python gc-cli.py --exclude unallocated,unwantedfolder -l en_us metadata.csv`

- JSON mit einem neuen Namen in einem Unterordner erstellen, ohne Detail-Datei dafür mit den 10 häufigsten Speicherorten

  `python gc-cli.py -o mysubfolder/mynew.json -n 10 --nodetails metadata.csv`



## Allgemeine Hinweise
- Ist die gleiche Datei mehrfach vorhanden, wird sie auch mehrfach gezählt und in den entsprechenden Tabellen angezeigt. Die anschliessend angegebene Zahl in Klammern entspricht jeweils der Anzahl gefundener Dateien ohne Duplikate (binary unique).
- Die zusätzlich generierte Datei *{name}_pathdetails.txt* enthält sämtliche Pfade mit der Anzahl enthaltener Dateien. Bei Bedarf kann hier Ersatz für "unerwünschte" meistverwendet Pfade entnommen werden (z.B. bei Wiederholungen, etc.). Ausserdem sind die erkannten Caches mit Anzahl enthaltener Dateien sowie deren Pfade ersichtlich.
- Im Bericht werden standardmässig die Vorschaubilder (`is_thumbcache: true`) separat ausgewiesen. D.h. sie werden nicht in die Auswertung (Dateianzahl, Datumsbereich etc.) miteinbezogen. Soll dies dennoch geschehen, kann die Option `--includethumbs` verwendet oder in der Konfiguration `other` - `include_thumbcache` eingestellt werden.
- Wie bei den Vorschaubildern, werden im Bericht auch die Browser-Caches (`is_browser: true`) - jedoch pro Browser - gesammelt angezeigt.
- Ein leeres Datum (z.B. gecarvte Dateien) wird als `undefiniert` ausgegeben. Dasselbe gilt für den Unix-Timestamp 01.01.1970.
- Der Separator innerhalb der CSV-Datei wird aufgrund der Headerzeile ermittelt (Basierend auf Griffeye nur `;` oder `,` möglich). Es kann vorkommen, dass eine Spalte einen Separator enthält. Betroffene Spalten werden durch Griffeye in Anführungszeichen (`"`) gepackt. Dies kann normal verarbeitet werden. Wird jedoch eine CSV-Eintrag mit einer unpassenden Anzahl Semikolon ausserhalb von Anführungszeichen festgestellt, wird der entsprechende Eintrag bei der Verarbeitung ignoriert und eine entsprechende Meldung inkl. betroffener Zeilennummern ausgegeben.
- Beim Datenexport aus Griffeye müssen die Spalten *Exif Comment*, *User Comment* & *Bookmarks* **deaktiviert** sein. Diese können aufgrund der teilweise exotischen Inhalte zu Problemen führen.
- Werte unter 1% (z.B. 0.3%) werden in der prozentuellen Verteilung als *<1%* dargestellt.


## Konfiguration

Bei Bedarf können diverse Einstellungen in der Datei *config.json* vorgenommen werden. Weiter kann die Sprache der Ergebnisdateien via Konfigurationsdatei angepasst werden. Es stehen Englisch und Deutsch zur Verfügung. Weiter Sprachen können in der Datei *labels.json* definiert werden. Diese Dateien müssen sich im selben Verzeichnis wie die Python-Dateien befinden.

### Eingabedatei

config.json: `input`

Eine Anpassung des Encoding-Formats `encoding` (Default *utf8* durch Griffeye) ist hier möglich.

### Ergebnisdatei

config.json: `result`

Eine Anpassung des Encoding-Formats `encoding` (Default *utf8*) ist hier möglich. Ausserdem die gewünschte Anzahl der meist vorkommenden Pfade `number_of_showed_paths` sowie die Sprache der Ergebnisdatei `language`. Es kann definiert werden, ob die Detaildatei erstellt werden soll `generate_pathdetails` sowie deren Name `pathdetails_name` und Encoding-Format `pathdetails_encoding` (Default *utf8*).

### Benötigte Spalten

config.json: `needed_columns`

> Diverse Konfigurationen bzgl. benötigte Spalten stehen in direktem Zusammenhang mit der internen Verarbeitung der Daten. Aus diesem Grund sollten **keine Änderungen ohne Konsultation des SourceCodes** vorgenommen werden.

Die Werte werden aufgrund des Namens in `columnname` aus der CSV-Datei ausgelesen. Die interne Verarbeitung läuft über den `key`.
Entweder-Oder-Spalten (siehe Hashes *MD5* oder *SHA-1*) können mit der Option `alt` der entsprechenden Spalte definiert werden.

Die Einstellungen zur alternativen Datumsspalte (siehe *Created Date*) finden sich unter `other` - `alternative_date_*`.

#### Zur Zeit definiert

* *Category*: Steuert Einteilung in die entsprechende Kategorie
* *File Path*: Steuert Einteilung in die meist verwendeten Pfade & Erkennung als Browser Cache, Thumbnail, etc.
* *File Type*: Steuert Einteilung in "Picture" oder "Video" 
* *Created Date*: Steuert Festlegung des Zeitraums & prozentuelle Verteilung auf die Jahre 
  * Ist *Created Date* leer (`01.01.0001`) wird nach der alternativen Datumsspalte *Last Write Time* gesucht. Sonst wird der Wert `undefiniert` verwendet.
  Dieses Verhalten wurde bisher meistens bei Daten aus Mobiles festgestellt.
* *Source ID*: Steuert Einteilung zum entsprechenden Gerät
* *MD5* oder *SHA-1*: Steuert Erkennung des binary unique-Wertes
  * Wird *MD5* in den vorhandenen Spalten nicht gefunden muss *SHA-1* vorhanden sein.

### Kategorien

config.json: `categories`

Der Kategoriename in `name` muss der Definition in Griffeye entsprechen. Ausserdem kann mit `legality` definiert werden, ob diese Kategorie als "illegal" gilt. 
Der Sortierungswert `sort` der Kategorie bezieht sich auf die Reihenfolge der Ausgabe in der Ergebnisdatei und kann ebenfalls eingestellt werden. Durch `show_in_report` kann eine Kategorie in der Ergebnisdatei ein- oder ausgeblendet werden.

### Pfade, Caches, Thumbnails

config.json: `caches`

Die Einteilung in Caches kann mittels der Option `path` definiert werden. Nach diesem Wert wird im Dateipfad gesucht, um die entsprechende Einteilung vorzunehmen. `name` definiert das entsprechende Produkt, während `is_browser` eine Definition als Browser-Cache ermöglicht (Berechung des prozentuellen Browser-Cache-Anteils & Sammlung pro Browser in den meist vorkommenden Pfaden analog *is_thumbcache*). `is_thumbcache` definiert einen Thumbcache (Vorschaubilder), wodurch diese gesammelt als einen Wert ebenfalls in den meist vorkommenden Pfaden aufgeführt werden. Der dafür anzuzeigenden Namen sind unter `other` - `name_for_thumbcache` bzw. `other` - `name_for_browsercache` definiert.

> **ACHTUNG:** Windows-Pfade müssen unter *path* mittels `\\` getrennt werden. Unix-basierte Dateisysteme (Linux, Apple, etc.) sind davon nicht betroffen. 
> (z.B. Windows: `Firefox\\Profiles`, Apple: `Firefox/Profiles`)
