# GriffeyeCrawler
Analysiert eine exportierte Dateiliste aus Griffeye pro Gerät &amp; Kategorie
- Summiert die Bilder und Videos (Total & binary unique)
- Fasst die Dateipfade zusammen und unterteilt diese in Cache- & Nicht-Cache-Pfade auf
- Ermittelt die Pfade mit den meisten Inhalten
- Ermittelt den gesamten Zeitraum der Dateierstellung
- Ermittelt die prozentuelle Verteilung der Dateierstellung im betroffenen Zeitraum pro Jahr
- Ermittelt das prozentuelle Verhältnis im Browsercache und der übrigen Ablage
- Ermittelt sämtliche erwähnten Punkte auch als Total über alle Geräte + die Anzahl der betroffenen Geräte
- Generiert eine Ergebnisdatei im TXT oder DOCX-Format

## Verwendung
### Mit EXE
Es ist **keine** Installation notwendig...
Start/Ausführung verhalten sich gleich wie unter *Ohne EXE - Start/Ausführung* beschrieben, mit dem Unterschied, dass *GriffeyeCrawler.exe* ausgeführt werden muss.

### Ohne EXE
#### Installation
- Python 3.x herunterladen (www.python.org) und installieren.
  - Sichergehen, dass "pip" ebenfalls installiert wird (ist standardmässig aktiviert)
  - Ob die Installationen erfolgreich waren mittels ``python --version`` & ``pip --version`` kontrollieren
  - evtl. muss *%APPDATA%\Local\Programs\Python\Python\<Version>* (Python) & *..\Scripts* (pip) in den Umgebungsvariablen erfasst werden
- Das Package *docx* mit ``pip install python-docx`` installieren

#### Start/Ausführung
- *GriffeyeCrawler.py* doppelklicken
- Name der zu verarbeitenden CSV-Datei angeben. Der Standardwert (report_all.csv) kann einfach mit Enter bestätigt werden. Die entsprechende Datei kann auch mittels Drag-and-Drop ins Terminal gezogen werden.
- Name der Ergebnisdatei angeben. Der Standardwert (result.docx) kann einfach mit Enter bestätigt werden. Es sind die Formate .txt & .docx möglich.
- Das Ergebnis wird im Verzeichnis *_files* erstellt (Standardeinstellung). Ausserdem wird bei jeder Verarbeitung die Datei *pathdetails.txt* erstellt, welche detailliertere Informationen zu den ausgewerteten Daten enthält.
**Bestehende Dateien werden ohne Warnung überschrieben!**


## Konfiguration
Bei Bedarf können diverse Einstellungen in der Datei *config.json* vorgenommen werden. Diese Datei muss sich im selben Verzeichnis wie *GriffeyeCrawler.py* bzw. *GriffeyeCrawler.exe* befinden.

### Eingabedatei
config.json: `input`

Anpassungen des Default-Namens der CSV-Datei `filename`, deren Encoding-Formats `encoding` (Default *utf16* durch Griffeye) und des Default-Verzeichnisses (ohne Drag-n-Drop) `directory` sind hier möglich.

### Ergebnisdatei
config.json: `result`

Anpassungen des Default-Namens `filename`, des Encoding-Formats `encoding` (Default *utf8*) und des Verzeichnisses `directory` der Ergebnisdatei sind hier möglich. Ausserdem die gewünschte Anzahl der meist vorkommenden Pfade `number_of_showed_paths`. Es kann definiert werden, ob die Detaildatei erstellt werden soll `generate_pathdetails` sowie deren name `pathdetails_name`, Encoding-Format `pathdetails_encoding` (Default *utf8*) und Verzeichnis `pathdetails_directory`.

### Benötigte Spalten
config.json: `needed_columns`

> Diverse Konfigurationen bzgl. benötigte Spalten stehen in direktem Zusammenhang mit der internen Verarbeitung der Daten. Aus diesem Grund bitte **keine Änderungen ohne Konsultation des SourceCodes vornehmen**.

Die Werte werden aufgrund des Namens in `columnname` aus der CSV-Datei ausgelesen. Die interne Verarbeitung läuft über den `key`.
Entweder-Oder-Spalten (siehe Hashes *MD5* oder *SHA-1*) können mit der Option `alt` der entsprechenden Spalte definiert werden.

Die Einstellungen zur alternativen Datumsspalte (siehe *Created Date*) finden sich unter `other` - `alternative_date_*`.

#### Zur Zeit definiert
* *Category*: Einteilung in die entsprechende Kategorie
* *File Path*: Einteilung in die meist verwendeten Pfade & Erkennung als Browser Cache, Thumbnail, etc.
* *File Type*: Einteilung in "Picture" oder "Video" 
* *Created Date*: Festlegung des Zeitraums & prozentuelle Verteilung auf die Jahre 
  * Ist *Created Date* leer (`01.01.0001`) wird nach der alternativen Datumsspalte *Last Write Time* gesucht. Sonst wird der Wert `undefiniert` verwendet.
  Dieses Verhalten wurde bisher erst bei Mobiles festgestellt.
* *Source ID*: Einteilung zum entsprechenden Gerät
* *MD5* oder *SHA-1*: Erkennung des binary unique-Wertes
  * Wird *MD5* in den vorhandenen Spalten nicht gefunden **muss** *SHA-1* vorhanden sein.

### Kategorien
config.json: `categories`

Der Kategoriename in `name` muss der Definition in Griffeye entsprechen. Ausserdem kann mit `legality` definiert werden, ob diese Kategorie als "illegal" gilt. 
Der Sortierungswert `sort` der Kategorie bezieht sich auf die Reihenfolge der Ausgabe in der Ergebnisdatei und kann ebenfalls eingestellt werden.

### Pfade, Caches, Thumbnails
config.json: `caches`

Die Einteilung in Caches kann mittels der Option `path` definiert werden. Nach diesem Wert wird im Dateipfad gesucht, um die entsprechende Einteilung vorzunehmen. `name` definiert das entsprechende Produkt, während `is_browser` eine Definition als Browser-Cache ermöglicht (Berechung des prozentuellen Browser-Cache-Anteils).
